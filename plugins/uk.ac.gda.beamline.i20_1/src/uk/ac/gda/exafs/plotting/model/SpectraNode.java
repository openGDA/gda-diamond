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

import org.eclipse.january.dataset.DoubleDataset;

import uk.ac.gda.client.plotting.model.ITreeNode;
import uk.ac.gda.client.plotting.model.Node;

/**
 * Stores all spectra of particular type for a scan (e.g. lnI0It, It, ...).
 * Contains a list of {@link ScanDataItemNode} with the x-y data for a each spectrum.
 */
public class SpectraNode extends Node {

	private DoubleDataset xDoubleDataset;
	private DoubleDataset uncalibratedXAxisData; // e.g. strip number (for XH, XStrip), or position (for TurboXas)

	private final String label;

	public SpectraNode(ITreeNode parent, String identifier, String label) {
		super(parent, identifier);
		this.label = label;
	}

	@Override
	public String toString() {
		return label;
	}

	public void setXAxisData(DoubleDataset xDoubleDataset) {
		this.xDoubleDataset = xDoubleDataset;
		this.xDoubleDataset.setName("energy");
	}

	public DoubleDataset getXAxisData() {
		return xDoubleDataset;
	}

	/**
	 * Add new create new ScanDataItemNode object for the datasets and add to nodeList
	 * @param yDoubleDataset
	 * @param identifier Unique identifier for the data
	 * @param label Label used to identify the data in the tree view
	 * @return new ScanDataItemNode object created using yDoubleDataset, identifer, label etc.
	 */
	public ScanDataItemNode updateData(DoubleDataset yDoubleDataset, String identifier, String label) {
		ScanDataItemNode newnode = new ScanDataItemNode(this, identifier, label, yDoubleDataset);
		addChildNode(newnode);
		return newnode;
	}

	public DoubleDataset getUncalibratedXAxisData() {
		return uncalibratedXAxisData;
	}

	public void setUncalibratedXAxisData(DoubleDataset uncalibratedXAxisData) {
		this.uncalibratedXAxisData = uncalibratedXAxisData;
	}

}
