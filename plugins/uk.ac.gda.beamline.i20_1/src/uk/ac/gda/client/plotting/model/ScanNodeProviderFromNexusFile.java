/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

package uk.ac.gda.client.plotting.model;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.apache.commons.io.FilenameUtils;
import org.dawnsci.ede.EdeDataConstants;
import org.dawnsci.ede.EdePositionType;
import org.dawnsci.ede.EdeScanType;
import org.eclipse.dawnsci.analysis.api.tree.DataNode;
import org.eclipse.dawnsci.analysis.api.tree.GroupNode;
import org.eclipse.dawnsci.hdf5.nexus.NexusFileHDF5;
import org.eclipse.dawnsci.nexus.NexusFile;
import org.eclipse.dawnsci.plotting.api.trace.ILineTrace.PointStyle;
import org.eclipse.january.DatasetException;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DatasetUtils;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.january.dataset.IDataset;
import org.eclipse.january.dataset.ILazyDataset;
import org.eclipse.january.dataset.SliceND;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.scan.TurboXasNexusTree;
import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.client.plotting.model.LineTraceProviderNode.TraceStyleDetails;
import uk.ac.gda.exafs.plotting.model.EdeScanNode;
import uk.ac.gda.exafs.plotting.model.ExperimentRootNode;
import uk.ac.gda.exafs.plotting.model.ScanDataItemNode;
import uk.ac.gda.exafs.plotting.model.SpectraNode;

public class ScanNodeProviderFromNexusFile extends ObservableModel {
	private static final Logger logger = LoggerFactory.getLogger(ScanNodeProviderFromNexusFile.class);

	public void addEdeScanNode(String filename, Node rootNode) {

		try(NexusFile file = NexusFileHDF5.openNexusFileReadOnly(filename)) {
			logger.info("Loading data for 'Ede plot view' from Nexus file {}", filename);

			// Call getGroup for each group, so nodes are populated with the entries.
			GroupNode entryGroup = file.getGroup("/entry1", false);
			for(Entry<String, GroupNode> entry : entryGroup.getGroupNodeMap().entrySet() ) {
				file.getGroup("/entry1/"+entry.getKey(), false);
			}

			// See if Nexus file is from turboxas scan by looking for motor parameters dataset
			String scalerForZebraGroup = findParentOfDataNode(entryGroup, TurboXasNexusTree.MOTOR_PARAMS_COLUMN_NAME);
			ScanType scanType = scalerForZebraGroup.isEmpty() ? ScanType.Ede : ScanType.TurboXas;

			String uncalibratedAxisName;
			logger.info("Nexus file scan type : {}", scanType);
			List<String> detectorNames = new ArrayList<>();
			if (scanType == ScanType.TurboXas) {
				detectorNames.add(scalerForZebraGroup);

				// Check for dataset called 'FF_sumI0' to determine if Xspress3 data is available.
				String xspress3GroupName = findParentOfDataNode(entryGroup, TurboXasNexusTree.FF_SUM_IO_NAME);
				if (!xspress3GroupName.isEmpty()) {
					detectorNames.add(xspress3GroupName);
				}
				uncalibratedAxisName = TurboXasNexusTree.POSITION_COLUMN_NAME;
			} else {
				detectorNames = Arrays.asList( EdeDataConstants.LN_I0_IT_COLUMN_NAME,
						EdeDataConstants.LN_I0_IT_AVG_I0S_COLUMN_NAME,
						EdeDataConstants.LN_I0_IT_FINAL_I0_COLUMN_NAME,
						EdeDataConstants.LN_I0_IT_INTERP_I0S_COLUMN_NAME);
				uncalibratedAxisName = EdeDataConstants.PIXEL_COLUMN_NAME;
			}

			DoubleDataset energyAxisData = (DoubleDataset) findDataset(entryGroup, TurboXasNexusTree.ENERGY_COLUMN_NAME);
			DoubleDataset positionAxisData = DatasetUtils.cast(DoubleDataset.class, findDataset(entryGroup, uncalibratedAxisName));
			Dataset groupIndexDataset = findDataset(entryGroup, TurboXasNexusTree.SPECTRUM_GROUP);
			Dataset spectrumIndexDataset = findDataset(entryGroup, TurboXasNexusTree.SPECTRUM_INDEX); // num spectra
			int[] expectedShape = {groupIndexDataset.getShape()[0], energyAxisData.getShape()[0]};

			if (scanType==ScanType.Ede) {
				// spectrum index dataset is for *all* collected spectra (i.e.  dark I0, dark It as well as light It).
				// Extract values for just lightIt spectrum measurements as these are the ones being plotted.

				String frelonGroupName = findParentOfDataNode(entryGroup, EdeDataConstants.BEAM_IN_OUT_COLUMN_NAME);
				GroupNode frelonGroupNode = entryGroup.getGroupNode(frelonGroupName);
				int firstLighIt = getLightItStartIndex(frelonGroupNode);
				spectrumIndexDataset = spectrumIndexDataset.getSlice(new int[] {firstLighIt}, new int[] {firstLighIt+expectedShape[0]}, null);
			}

			// Create the EdeScan node - all data is child of this
			final EdeScanNode newNode = new EdeScanNode(rootNode, filename, FilenameUtils.getBaseName(filename), true);
			rootNode.addChildNode(0, newNode);
			this.firePropertyChange(ExperimentRootNode.SCAN_ADDED_PROP_NAME, null, newNode);

			for (String detectorName : detectorNames) {
				List<String> datasetsAdded = new ArrayList<>();

				String groupName = "/entry1/" + detectorName;

				logger.info("Adding data from group {}", groupName);

				// Add new node to the tree to contain all the data from the detector
				Node detectorNode = new Node(newNode, detectorName);
				detectorNode.setLabel(detectorName);
				newNode.addChildNode(detectorNode);

				GroupNode detGroup = file.getGroup(groupName, false);
				Map<String, DataNode> detDataMap = detGroup.getDataNodeMap();

				// Add new node to tree for each suitable dataset in detector group node
				for (Entry<String, DataNode> entryitem : detDataMap.entrySet()) {
					ILazyDataset fullDataset = entryitem.getValue().getDataset();
					logger.debug("\tDataset {} has shape = {}", fullDataset.getName(), Arrays.toString(fullDataset.getShape()));

					int[] shape = fullDataset.getShape();
					boolean shapeOk = Arrays.equals(shape, expectedShape) || shape.length == 1 && shape[0] == expectedShape[0];

					if (!shapeOk || datasetsAdded.contains(fullDataset.getName()) ) {
						continue;
					}
					datasetsAdded.add(fullDataset.getName());

					logger.debug("\tAdding dataset {}", fullDataset.getName());
					// Add nodes to tree, one for each spectrum of data
					addDataToTree(detectorNode, energyAxisData, positionAxisData, groupIndexDataset, spectrumIndexDataset, fullDataset);
				}
			}

		}catch(Exception e) {
			logger.warn("Problem loading Nexus data from file", e);
		}
	}

	/**
	 * Add new nodes to EdeScan node from fullDataset. Each row of values from fullDataset is added as new node to tree.
	 * Dataset shapes should all be consistent before calling this function
	 *
	 * @param scanNode
	 * @param plotUpdater
	 * @param groupNumber group number of each spectrum. dimensions=[num spectra]
	 * @param spectrumNumber index within each group of each spectrum. dimensions=[num spectra]
	 * @param fullDataset full dataset. dimensions=[num spectra, num energies]
	 * @throws DatasetException
	 */
	private void addDataToTree(Node detectorNode, DoubleDataset energyAxis, DoubleDataset uncalibratedAxis, Dataset groupNumber, Dataset spectrumNumber,
			ILazyDataset fullDataset) throws DatasetException {

		// Don't add datasets that have strings as elements
		if (fullDataset.getElementClass() == String.class) {
			return;
		}

		int[] shape = fullDataset.getShape();
		int numSpectra = groupNumber.getShape()[0];

		final SpectraNode newNode = new SpectraNode(detectorNode, fullDataset.getName(), fullDataset.getName());
		newNode.setUncalibratedXAxisData(uncalibratedAxis);
		newNode.setXAxisData(energyAxis);
		detectorNode.addChildNode(newNode);

		EdeScanNode edeScanNode = (EdeScanNode) detectorNode.getParent();
		// iterate over rows in the dataset, add value(s) in each each row as new node in the tree
		for(int i=0; i< numSpectra; i++) {
			// Get value(s) from row in the full dataset
			DoubleDataset dblDataset = null;
			if (shape.length==1) {
				double val = fullDataset.getSlice((SliceND)null).getDouble(i);
				dblDataset = DatasetFactory.zeros(1);
				dblDataset.set(val, 0);
			} else if (shape.length==2) {
				dblDataset = (DoubleDataset) fullDataset.getSlice(new int[] {i,0}, new int[] {i+1, shape[1]}, (int[]) null).squeeze();
			}

			// plotIdentifier is the key for the spectrum (should be unique for each scan datapoint).
			String plotIdentifier =  fullDataset.getName() + "@" + groupNumber.getInt(i) + "@" + spectrumNumber.getInt(i);

			// plotLabel is used for the spectrum label in the tree view.
			String plotLabel = "Group " + groupNumber.getInt(i) + " spectrum " + spectrumNumber.getInt(i);

			ScanDataItemNode dataItemNode = newNode.updateData(dblDataset, plotIdentifier, plotLabel, fullDataset.equals(EdeDataConstants.LN_I0_IT_COLUMN_NAME));
			setTraceStyle(dataItemNode, edeScanNode);

			firePropertyChange(ExperimentRootNode.DATA_ADDED_PROP_NAME, null, edeScanNode);
		}
	}

	private void setTraceStyle(ScanDataItemNode dataItemNode, EdeScanNode scanNode) {
			TraceStyleDetails traceStyle = TraceStyleDetails.createDefaultSolidTrace();
			if (dataItemNode.getYAxisDataset().getShape()[0] == 1) {
				traceStyle.setPointStyle(PointStyle.CIRCLE);
				traceStyle.setPointSize(5);
			}
			traceStyle.setColor(scanNode.getNextColour());
			dataItemNode.setTraceStyle(traceStyle);
	}

	private Dataset findDataset(GroupNode entryNode, String name) throws DatasetException {
		DataNode dataNode = findDataNode(entryNode, name);
		if (dataNode != null) {
			ILazyDataset lazyDataset = dataNode.getDataset().getSlice((SliceND)null);

			Dataset dataset = (Dataset) dataNode.getDataset().getSlice((SliceND)null).squeeze();
			// Workaround for new behaviour in January (bug?) - squeezing a 1-dimensional dataset that has
			// 1 element sets the shape to empty array for some reason...
			if (dataset.getSize()==1) {
				dataset.setShape(1);
			}
			return dataset;
		}
		return null;
	}

	/**
	 * Find named DataNode by searching through nodes belonging to each of the groups in entryNode
	 * @param entryNode
	 * @param name
	 * @return DataNode with specified name
	 */
	private DataNode findDataNode(GroupNode entryNode, String name) {
		for(Entry<String, GroupNode> entry : entryNode.getGroupNodeMap().entrySet() ) {
			DataNode dataNode = entry.getValue().getDataNodeMap().get(name);
			if (dataNode != null) {
				return dataNode;
			}
		}
		return null;
	}

	private Dataset getDataset(GroupNode groupNode, String name) throws DatasetException {
		return (Dataset) groupNode.getDataNode(name).getDataset().getSlice((SliceND)null).squeeze();
	}

	/**
	 *
	 * @param entryNode
	 * @param name name of datanode to search for
	 * @return String name of GroupNode containing specified DataNode
	 */
	private String findParentOfDataNode(GroupNode entryNode, String name) {
		for(Entry<String, GroupNode> entry : entryNode.getGroupNodeMap().entrySet() ) {
			DataNode dataNode = entry.getValue().getDataNodeMap().get(name);
			if (dataNode != null) {
				return entry.getKey();
			}
		}
		return "";
	}

	private enum ScanType {TurboXas, Ede}


	private int getLightItStartIndex(GroupNode entryGroup) throws DatasetException {
		IDataset beamInOutDataset = getDataset(entryGroup, EdeDataConstants.BEAM_IN_OUT_COLUMN_NAME);
		IDataset itDataset = getDataset(entryGroup, EdeDataConstants.IT_COLUMN_NAME);
		if (beamInOutDataset == null || itDataset == null) {
			logger.warn("Unable to get lightIt start spectrum index - could not get required data from Nexus file");
			return 0;
		}
		int totNumSpectra = itDataset.getShape()[0];
		int firstLightItIndex = 0;
		for(int i=0; i<totNumSpectra && firstLightItIndex==0; i++) {
			if (itDataset.getInt(i)==EdeScanType.LIGHT.getValue() &&
					beamInOutDataset.getInt(i)==EdePositionType.INBEAM.getValue() ) {
				firstLightItIndex = i;
			}
		}
		return firstLightItIndex;
	}
}
