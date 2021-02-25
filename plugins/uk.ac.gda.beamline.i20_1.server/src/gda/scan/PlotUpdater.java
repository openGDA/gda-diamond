/*-
 * Copyright © 2017 Diamond Light Source Ltd.
 *
 * This file is part of GDA.
 *
 * GDA is free software: you can redistribute it and/or modify it under the
 * terms of the GNU General Public License version 3 as published by the Free
 * Software Foundation.
 *
 * GDA is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
 * details.
 *
 * You should have received a copy of the GNU General Public License along
 * with GDA. If not, see <http://www.gnu.org/licenses/>.
 */

package gda.scan;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.dawnsci.ede.EdeDataConstants;
import org.dawnsci.ede.EdePositionType;
import org.dawnsci.ede.EdeScanType;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.nexus.extractor.NexusExtractor;
import gda.data.nexus.extractor.NexusGroupData;
import gda.data.nexus.tree.INexusTree;
import gda.device.detector.NXDetectorData;
import gda.factory.Finder;
import gda.jython.scriptcontroller.ScriptControllerBase;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.EdeExperimentProgressBean;
import gda.scan.ede.EdeExperimentProgressBean.ExperimentCollectionType;
import gda.scan.ede.EdeScanProgressBean;

/**
 * Class used to send data from server to plot window in the client -
 * refactored from inner class of same name in {@link TurboXasScan}.
 * @since 28/10/2017
 */
public class PlotUpdater {

	private static final Logger logger = LoggerFactory.getLogger(PlotUpdater.class);

	private int currentGroupNumber;
	private int currentSpectrumNumber;
	private String energyAxisName;
	private ScriptControllerBase controller;
	private String filename;
	private Map<String, DoubleDataset> dataSets = new LinkedHashMap<>(); // set ketSet() returns keys in same order as they were added
	private List<String> dataNamesToIgnore = new ArrayList<>();
	private String positionColumnName;
	private String dataNameToSelectInPlot = EdeDataConstants.LN_I0_IT_COLUMN_NAME;
	private String extraLabel = "";

	public String getFilename() {
		return filename;
	}

	public void setFilename(String filename) {
		this.filename = filename;
	}

	public PlotUpdater() {
		controller = Finder.find(EdeExperiment.PROGRESS_UPDATER_NAME);
	}

	public void setCurrentGroupNumber(int currentGroupNumber) {
		this.currentGroupNumber = currentGroupNumber;
	}

	public void setCurrentSpectrumNumber(int currentSpectrumNumber) {
		this.currentSpectrumNumber = currentSpectrumNumber;
	}

	public void setEnergyAxisName(String energyAxisName) {
		this.energyAxisName = energyAxisName;
	}

	public void setPositionAxisName(String positionColumnName) {
		this.positionColumnName = positionColumnName;
	}

	DoubleDataset extractDoubleDatset(NexusGroupData groupData) {
		if (groupData!=null && groupData.getBuffer() instanceof double[]) {
			double[] originalData = (double[]) groupData.getBuffer();
			return (DoubleDataset) DatasetFactory.createFromObject(Arrays.copyOf(originalData, originalData.length), originalData.length);
		} else
			return null;
	}

	/**
	 * Extract detector data from scan data point and send spectra of I0, It, time etc to the progress updater.
	 * Only data from the first detector is extracted.
	 * @param scanDataPoint
	 */
	public void addDatasetsFromScanDataPoint(ScanDataPoint scanDataPoint) {
		for (int j = 0; j < scanDataPoint.getDetectorData().size(); j++) {
			NXDetectorData data = (NXDetectorData) scanDataPoint.getDetectorData().get(j);

			// Extract numerical (floating point) detector data from Nexus
			// data in scan data point
			INexusTree nexusDetData = data.getNexusTree().getChildNode(0);
			data.getNexusTree().getNumberOfChildNodes();

			String detectorName = data.getNexusTree().getChildNode(0).getName();

			for (int i = 0; i < nexusDetData.getNumberOfChildNodes(); i++) {
				String dataName = nexusDetData.getChildNode(i).getName();
				NexusGroupData groupData = data.getData(detectorName, dataName, NexusExtractor.SDSClassName);
				DoubleDataset dataset = extractDoubleDatset(groupData);
				if (dataset != null) {
					dataset.setName(dataName);
					dataSets.put(dataName, dataset);
				}
			}
		}

		final List<String> scnNames = scanDataPoint.getScannableNames();
		final List<Object> scnPositions = scanDataPoint.getScannablePositions();
		for(int i=0; i<scnNames.size(); i++) {
			String[] inputNames = scanDataPoint.getScannable(scnNames.get(i)).getInputNames();

			if (inputNames.length == 1) {
				// Position of scannable has one value
				DoubleDataset dataset = DatasetFactory.createFromObject(DoubleDataset.class, scnPositions.get(i), 1);
				dataset.setName(scnNames.get(i));
				dataSets.put(dataset.getName(), dataset);
			} else {
				// Position of scannable is an array, loop over inputnames add each value
				Object[] positions = (Object[]) scnPositions.get(i);
				for(int j=0; j<inputNames.length; j++) {
					DoubleDataset dataset = DatasetFactory.createFromObject(DoubleDataset.class, positions[j], 1);
					dataset.setName(inputNames[j]);
					dataSets.put(dataset.getName(), dataset);
				}
			}
		}
	}

	public void addDataset(String dataName, DoubleDataset dataset) {
		dataSets.put(dataName, dataset);
	}

	public void clearDatasets() {
		dataSets.clear();
	}

	public void addDatanameToIgnore(String name) {
		dataNamesToIgnore.add(name);
	}

	public void clearDatanamesToIgnore() {
		dataNamesToIgnore.clear();
	}

	public String getExtraLabel() {
		return extraLabel;
	}

	public void setExtraLabel(String extraLabel) {
		this.extraLabel = extraLabel;
	}

	private String createPlotLabel() {
		String groupSpectrumLabel = String.format("Group %d Spectrum %d %s", currentGroupNumber, currentSpectrumNumber, extraLabel == null ? "" : extraLabel);
		return groupSpectrumLabel.trim();
	}

	public void sendDataToController() {

		if (controller==null) {
			logger.warn("Controller not found");
			return;
		}
		// Determine index of dataset to use for energy axis
		if (!dataSets.containsKey(energyAxisName)) {
			logger.info("Could not find energy axis data (axis name = {})", energyAxisName);
			return;
		}

		// Create progress beans and notify plot controller
		EdeScanProgressBean scanProgressBean = new EdeScanProgressBean(currentGroupNumber, currentSpectrumNumber,
				EdeScanType.LIGHT, EdePositionType.INBEAM, filename);

		scanProgressBean.setCustomLabelForSDP(createPlotLabel());

		for (Entry<String,DoubleDataset> data : dataSets.entrySet()) {
			// Don't plot position column or energy datasets
			if (!dataNamesToIgnore.contains(data.getKey())) {
				EdeExperimentProgressBean progressBean =  new EdeExperimentProgressBean(ExperimentCollectionType.MULTI,
						scanProgressBean, data.getKey(), data.getValue(), dataSets.get(energyAxisName));

				progressBean.setUncalibratedXAxisData(dataSets.get(positionColumnName));
				progressBean.setSelectedByDefault(data.getKey().equals(dataNameToSelectInPlot));

				controller.update(null, progressBean);
			}
		}
	}

	public void setDatanameToSelectInPlot(String dataNameToSelectInPlot) {
		this.dataNameToSelectInPlot = dataNameToSelectInPlot;
	}
}
