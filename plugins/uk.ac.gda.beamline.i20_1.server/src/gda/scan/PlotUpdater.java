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
import java.util.List;

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
	private List<String> dataNames = new ArrayList<String>();
	private List<DoubleDataset> dataSets = new ArrayList<DoubleDataset>();
	private List<String> dataNamesToIgnore = new ArrayList<String>();

	public String getFilename() {
		return filename;
	}

	public void setFilename(String filename) {
		this.filename = filename;
	}

	public PlotUpdater() {
		controller = Finder.getInstance().find(EdeExperiment.PROGRESS_UPDATER_NAME);
	}

	public void setCurrentGroupNumber(int currentGroupNumber) {
		this.currentGroupNumber = currentGroupNumber;
	}

	public void incrementCurrentSpectrumNumber() {
		currentSpectrumNumber++;
	}

	public void setCurrentSpectrumNumber(int currentSpectrumNumber) {
		this.currentSpectrumNumber = currentSpectrumNumber;
	}

	public void setEnergyAxisName(String energyAxisName) {
		this.energyAxisName = energyAxisName;
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
					dataNames.add(dataName);
					dataSets.add(dataset);
				}
			}
		}
	}

	public void addDataset(String dataName, DoubleDataset dataset) {
		dataNames.add(dataName);
		dataSets.add(dataset);
	}

	public void clearDatasets() {
		dataNames.clear();
		dataSets.clear();
	}

	public void addDatanameToIgnore(String name) {
		dataNamesToIgnore.add(name);
	}

	public void clearDatanamesToIgnore() {
		dataNamesToIgnore.clear();
	}

	public void sendDataToController() {

		if (controller==null) {
			logger.warn("Controller not found");
			return;
		}
		// Determine index of dataset to use for energy axis
		int energyAxisIndex = dataNames.indexOf(energyAxisName);
		if (energyAxisIndex == -1) {
			logger.info("Could not find energy axis data (axis name = {})", energyAxisName);
			return;
		}

		// Create progress beans and notify plot controller
		EdeScanProgressBean scanProgressBean = new EdeScanProgressBean(currentGroupNumber, currentSpectrumNumber,
				EdeScanType.LIGHT, EdePositionType.INBEAM, filename);

		for (int i = 0; i < dataNames.size(); i++) {
			// Don't plot position column or energy datasets
			String dataName = dataNames.get(i);
			if (!dataNamesToIgnore.contains(dataName)) {
				controller.update(null, new EdeExperimentProgressBean(ExperimentCollectionType.MULTI,
						scanProgressBean, dataNames.get(i), dataSets.get(i), dataSets.get(energyAxisIndex)));
			}
		}
	}
}
