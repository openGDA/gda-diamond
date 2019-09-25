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
import java.util.Optional;

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

			String uncalibratedAxisName;
			boolean isTurboXasScan = isTurboXasScan(entryGroup);
			if (isTurboXasScan) {
				logger.info("Nexus file scan type : TurboXas");
				uncalibratedAxisName = TurboXasNexusTree.POSITION_COLUMN_NAME;
			} else {
				logger.info("Nexus file scan type : Ede");
				uncalibratedAxisName = EdeDataConstants.PIXEL_COLUMN_NAME;
			}
			List<String> detectorNames = getDetectorNames(entryGroup);
			logger.info("Detector group names : {}", detectorNames);

			GroupNode detectorGroup = entryGroup.getGroupNode(detectorNames.get(0));
			DoubleDataset energyAxisData = (DoubleDataset) getDataset(detectorGroup, TurboXasNexusTree.ENERGY_COLUMN_NAME);
			DoubleDataset positionAxisData = DatasetUtils.cast(DoubleDataset.class, getDataset(detectorGroup, uncalibratedAxisName));
			Dataset groupIndexDataset = getDataset(detectorGroup, TurboXasNexusTree.SPECTRUM_GROUP);
			int[] expectedShape = {groupIndexDataset.getShape()[0], energyAxisData.getShape()[0]};
			Dataset spectrumIndexDataset = DatasetFactory.createRange(DoubleDataset.class, 0, expectedShape[0], 1.0);
			logger.info("Expected 1d, 2d data shapes : {}, {}", expectedShape[0], Arrays.toString(expectedShape));

			if (!isTurboXasScan) {
				// spectrum index dataset is for *all* collected spectra (i.e.  dark I0, dark It as well as light It).
				// Extract values for just lightIt spectrum measurements as these are the ones being plotted.

				Optional<Entry<String, GroupNode>> frelonGroup = findGroupNodeContainingDataNode(entryGroup, EdeDataConstants.BEAM_IN_OUT_COLUMN_NAME);
				if (frelonGroup.isPresent()) {
					GroupNode frelonGroupNode = frelonGroup.get().getValue();
					Dataset fullSpectrumIndexDataset = getDataset(frelonGroupNode, TurboXasNexusTree.SPECTRUM_INDEX);
					int firstLighIt = getLightItStartIndex(frelonGroupNode);
					spectrumIndexDataset = fullSpectrumIndexDataset.getSlice(new int[] {firstLighIt}, new int[] {firstLighIt+expectedShape[0]}, null);
				} else {
					logger.warn("Could not find {} data for frelon detector. Using automatically generated spectrum"
							+ "numbering instead (this will be incorrect for multiple timing groups)", EdeDataConstants.BEAM_IN_OUT_COLUMN_NAME);
				}
			}

			// Create the EdeScan node - all data is child of this
			final EdeScanNode newNode = new EdeScanNode(rootNode, filename, FilenameUtils.getBaseName(filename), true);
			rootNode.addChildNode(0, newNode);
			this.firePropertyChange(ExperimentRootNode.SCAN_ADDED_PROP_NAME, null, newNode);

			for (String detectorName : detectorNames) {

				String groupName = "/entry1/" + detectorName;

				if (!file.isPathValid(groupName)) {
					logger.info("Not adding data from {} - group does not exist", groupName);
					continue;
				}
				logger.info("Adding data from group {}", groupName);

				// Add new node to the tree to contain all the data from the detector
				Node detectorNode = new Node(newNode, detectorName);
				detectorNode.setLabel(detectorName);
				newNode.addChildNode(detectorNode);

				GroupNode detGroup = file.getGroup(groupName, false);
				Map<String, DataNode> detDataMap = detGroup.getDataNodeMap();

				// Add new node to tree for each suitable dataset in detector group node
				for (DataNode dataNode : detDataMap.values()) {
					ILazyDataset fullDataset = dataNode.getDataset();
					logger.debug("\tDataset {} has shape = {}", fullDataset.getName(), Arrays.toString(fullDataset.getShape()));
					if (!shapeIsOk(fullDataset, expectedShape )) {
						logger.debug("\tDataset shape does not match expected 1d, 2d shapes");
						continue;
					}
					addDetectorDataToTree(detectorNode, energyAxisData, positionAxisData, groupIndexDataset,
							spectrumIndexDataset, fullDataset, expectedShape);
				}
			}

		}catch(Exception e) {
			logger.warn("Problem loading Nexus data from file", e);
		}
	}

	private boolean shapeIsOk(ILazyDataset dataset, int[] expectedShape) {
		int[] shape = dataset.getShape();
		return Arrays.equals(shape, expectedShape) || shape.length == 1 && shape[0] == expectedShape[0];
	}

	private void addDetectorDataToTree(Node detectorNode, DoubleDataset energyData, DoubleDataset positionData,
			Dataset groupIndex, IDataset spectrumIndex, ILazyDataset fullDataset, int[] expectedShape) {

		try {
			logger.debug("\tAdding dataset {} to tree", fullDataset.getName());
			addDataToTree(detectorNode, energyData, positionData, groupIndex, spectrumIndex, fullDataset);
		} catch (DatasetException e) {
			logger.error("Problem adding dataset {} to tree,", fullDataset.getName(), e);
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
	private void addDataToTree(Node detectorNode, DoubleDataset energyAxis, DoubleDataset uncalibratedAxis, Dataset groupNumber, IDataset spectrumNumber,
			ILazyDataset fullDataset) throws DatasetException {

		// Don't add datasets that have strings as elements
		if (fullDataset.getElementClass() == String.class) {
			return;
		}

		int[] shape = fullDataset.getShape();
		int numSpectra = groupNumber.getShapeRef()[0];

		final SpectraNode newNode = new SpectraNode(detectorNode, fullDataset.getName(), fullDataset.getName());
		newNode.setUncalibratedXAxisData(uncalibratedAxis);
		newNode.setXAxisData(energyAxis);
		detectorNode.addChildNode(newNode);

		EdeScanNode edeScanNode = (EdeScanNode) detectorNode.getParent();

		// Get full dataset into memory if it is 1-dimensional. Much faster to do getDouble lots of times than take lots of 1-element slices
		IDataset fullData = null;
		if (shape.length == 1) {
			fullData = fullDataset.getSlice((SliceND)null);
		}

		// iterate over rows in the dataset, add value(s) in each each row as new node in the tree
		for(int i=0; i< numSpectra; i++) {
			// Get value(s) from row in the full dataset
			DoubleDataset dblDataset = null;
			if (shape.length==1) {
				dblDataset = DatasetFactory.zeros(1);
				dblDataset.setItem(fullData.getDouble(i));
			} else if (shape.length==2) {
				dblDataset = (DoubleDataset) fullDataset.getSlice(new int[] {i,0}, new int[] {i+1, shape[1]}, (int[]) null).squeeze();
			}

			// plotIdentifier is the key for the spectrum (should be unique for each scan datapoint).
			String plotIdentifier =  fullDataset.getName() + "@" + groupNumber.getInt(i) + "@" + spectrumNumber.getInt(i);

			// plotLabel is used for the spectrum label in the tree view.
			String plotLabel = "Group " + groupNumber.getInt(i) + " spectrum " + spectrumNumber.getInt(i);

			ScanDataItemNode dataItemNode = newNode.updateData(dblDataset, plotIdentifier, plotLabel, false);
			setTraceStyle(dataItemNode, edeScanNode);

		}
		firePropertyChange(ExperimentRootNode.DATA_ADDED_PROP_NAME, null, edeScanNode);
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

	private Dataset getDataset(GroupNode groupNode, String name) throws DatasetException {
		Dataset data = DatasetUtils.sliceAndConvertLazyDataset(groupNode.getDataNode(name).getDataset());
		if (data.getRank() > 1) {
			data = data.squeeze();
		}
		return data;
	}

	/**
	 * Search all child group nodes of entryNode, and return name of group Node containing named data node.
	 * @param entryNode
	 * @param nameOfDataNode name of datanode to search for
	 * @return String name of GroupNode containing specified DataNode
	 */
	private Optional<Entry<String, GroupNode>> findGroupNodeContainingDataNode(GroupNode entryNode, String nameOfDataNode) {
		for(Entry<String, GroupNode> entry : entryNode.getGroupNodeMap().entrySet() ) {
			DataNode dataNode = entry.getValue().getDataNodeMap().get(nameOfDataNode);
			if (dataNode != null) {
				return Optional.of(entry);
			}
		}
		return Optional.empty();
	}

	private boolean isTurboXasScan(GroupNode entryGroup) {
		Optional<Entry<String,GroupNode>> scalerForZebraGroup = getScalarForZebraGroup(entryGroup);
		return scalerForZebraGroup.isPresent();
	}

	private Optional<Entry<String,GroupNode>> getScalarForZebraGroup(GroupNode entryGroup) {
		return findGroupNodeContainingDataNode(entryGroup, TurboXasNexusTree.MOTOR_PARAMS_COLUMN_NAME);
	}

	private List<String> getDetectorNames(GroupNode entryGroup) {

		Optional<Entry<String,GroupNode>> scalerForZebraGroup = getScalarForZebraGroup(entryGroup);
		if (scalerForZebraGroup.isPresent()) {
			List<String> detectorNames = new ArrayList<>();
			detectorNames.add(scalerForZebraGroup.get().getKey());

			// Check for dataset called 'FF_sumI0' to determine if Xspress3 data is available.
			Optional<Entry<String,GroupNode>> xspress3Group = findGroupNodeContainingDataNode(entryGroup, TurboXasNexusTree.FF_SUM_IO_NAME);
			if (xspress3Group.isPresent()) {
				detectorNames.add(xspress3Group.get().getKey());
			}
			return detectorNames;

		} else {
			return Arrays.asList( EdeDataConstants.LN_I0_IT_COLUMN_NAME,
					EdeDataConstants.LN_I0_IT_AVG_I0S_COLUMN_NAME,
					EdeDataConstants.LN_I0_IT_FINAL_I0_COLUMN_NAME,
					EdeDataConstants.LN_I0_IT_INTERP_I0S_COLUMN_NAME);
		}
	}

	private int getLightItStartIndex(GroupNode frelonDetectorGroup) throws DatasetException {
		IDataset beamInOutDataset = getDataset(frelonDetectorGroup, EdeDataConstants.BEAM_IN_OUT_COLUMN_NAME);
		IDataset itDataset = getDataset(frelonDetectorGroup, EdeDataConstants.IT_COLUMN_NAME);
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
