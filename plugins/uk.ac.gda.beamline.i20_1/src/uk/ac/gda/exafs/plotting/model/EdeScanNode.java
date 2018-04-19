/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.plotting.model;

import org.apache.commons.lang.StringUtils;

import gda.scan.ede.EdeExperimentProgressBean;
import uk.ac.gda.client.plotting.model.ITreeNode;
import uk.ac.gda.client.plotting.model.Node;
import uk.ac.gda.client.plotting.model.ScanNode;

/**
 *
 * Stores a list of {@link SpectraNode}s. i.e. all data for a single scan - a list of top level nodes (one list item for each type of data).
 */
public class EdeScanNode extends ScanNode {

	private final boolean multiCollection;
	private String label;
	private int totalNumPlots;

	/**
	 * @param parent
	 * @param scanIdentifier - unique identifier for the scan (e.g. full path to nexus file)
	 * @param label - label for scan in plot view
	 * @param multiCollection
	 */
	public EdeScanNode(ITreeNode parent, String scanIdentifier, String label, boolean multiCollection) {
		super(parent, scanIdentifier, scanIdentifier);
		this.label = label;
		this.multiCollection = multiCollection;
		totalNumPlots = 0;
	}

	public Node updateData(final EdeExperimentProgressBean arg) {
		String dataLabel = arg.getDataLabel();
		String nodeKey = this.toString() + "@" + dataLabel;
		SpectraNode dataNode;
		// Make new SpectraNode to store the data of this type
		if (!hasChild(nodeKey)) {
			final SpectraNode newNode = new SpectraNode(this, nodeKey, dataLabel);
			newNode.setUncalibratedXAxisData(arg.getUncalibratedXAxisData());
			newNode.setXAxisData(arg.getEnergyData());
			addChildNode(newNode);
			dataNode = newNode;
		} else {
			dataNode = (SpectraNode) getChild(nodeKey);
		}
		// plotIdentifier is the key for the spectrum (should be unique for each scan datapoint).
		String plotIdentifier =  nodeKey + "@" + arg.getProgress().getGroupNumOfThisSDP() + "@" + arg.getProgress().getFrameNumOfThisSDP();

		// plotLabel is used for the spectrum label in the tree view.
		String plotLabel = "Group " + arg.getProgress().getGroupNumOfThisSDP() + " spectrum " + arg.getProgress().getFrameNumOfThisSDP();

		// Use custom label and identifier for the plot if one has been set
		String customLabel = arg.getProgress().getCustomLabelForSDP();
		if (StringUtils.isNotEmpty(customLabel)) {
			plotLabel = customLabel;
			plotIdentifier = nodeKey + ":" + customLabel;
		}

		dataNode.updateData(arg.getData(), plotIdentifier, plotLabel);
		totalNumPlots++;
		return dataNode;
	}

	public boolean isMultiCollection() {
		return multiCollection;
	}

	@Override
	public String toString() {
		return "Scan:" + label;
	}

	public int getTotalNumPlots() {
		return totalNumPlots;
	}
}
