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

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import org.apache.commons.lang.StringUtils;
import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

import gda.scan.ede.EdeExperimentProgressBean;
import uk.ac.gda.client.plotting.model.Node;
import uk.ac.gda.client.plotting.model.ScanNode;

public class EdeScanNode extends ScanNode {
	private final Map<String, SpectraNode> scans = new HashMap<String, SpectraNode>();
	private final  IObservableList dataNodeList = new WritableList(new ArrayList<SpectraNode>(), SpectraNode.class);
	private final String scanIdentifier;

	private final boolean multiCollection;

	public EdeScanNode(String scanIdentifier, String fileName, boolean multiCollection, Node parent) {
		super(scanIdentifier, fileName, parent);
		this.scanIdentifier = scanIdentifier;
		this.multiCollection = multiCollection;
	}

	public IObservableList getNodeList() {
		return dataNodeList;
	}

	public Node updateData(final EdeExperimentProgressBean arg) {
		SpectraNode dataNode;
		String label = arg.getDataLabel();
		String scanIdentifier = this.toString() + "@" + label;
		if (!scans.containsKey(scanIdentifier)) {
			final SpectraNode newNode = new SpectraNode(scanIdentifier, label, this);
			scans.put(scanIdentifier, newNode);
			dataNodeList.add(newNode);
			dataNode = newNode;
		} else {
			dataNode = scans.get(scanIdentifier);
		}
		// plotIdentifier is the key for the spectrum (should be unique for each scan datapoint).
		String plotIdentifier =  scanIdentifier + "@" + arg.getProgress().getGroupNumOfThisSDP() + "@" + arg.getProgress().getFrameNumOfThisSDP();

		// plotLabel is used for the spectrum label in the tree view.
		String plotLabel = "Group " + arg.getProgress().getGroupNumOfThisSDP() + " spectrum " + arg.getProgress().getFrameNumOfThisSDP();

		// Use custom label and identifier for the plot if one has been set
		String customLabel = arg.getProgress().getCustomLabelForSDP();
		if (StringUtils.isNotEmpty(customLabel)) {
			plotLabel = customLabel;
			plotIdentifier = scanIdentifier + ":" + customLabel;
		}

		dataNode.updateData(arg.getEnergyData(), arg.getData(), plotIdentifier, plotLabel);
		return dataNode;
	}

	public boolean isMultiCollection() {
		return multiCollection;
	}

	@Override
	public String toString() {
		return "Scan:" + scanIdentifier;
	}

	@Override
	public IObservableList getChildren() {
		return dataNodeList;
	}

	@Override
	public String getIdentifier() {
		return scanIdentifier;
	}

	@Override
	public void removeChild(Node dataNode) {
		// NOt supported
	}
}
