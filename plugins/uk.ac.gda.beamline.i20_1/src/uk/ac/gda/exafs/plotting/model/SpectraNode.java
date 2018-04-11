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

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.january.dataset.DoubleDataset;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceReference;

import gda.rcp.GDAClientActivator;
import uk.ac.gda.client.liveplot.IPlotLineColorService;
import uk.ac.gda.client.plotting.model.Node;
import uk.ac.gda.client.plotting.model.ScanNode;

/**
 * Stores all spectra of particular type for a scan (e.g. lnI0It, It, ...).
 * Contains a list of {@link ScanDataItemNode} with the x-y data for a each spectrum.
 */
public class SpectraNode extends Node {

	private DoubleDataset xDoubleDataset;
	private DoubleDataset uncalibratedXAxisData; // e.g. strip number (for XH, XStrip), or position (for TurboXas)

	private final IObservableList dataItemNodeList = new WritableList(new ArrayList<ScanDataItemNode>(), ScanDataItemNode.class);
	private final String label;
	private final String identifier;
	private final String colorHexValue;

	public SpectraNode(ScanNode parent, String identifier, String label) {
		super(parent);
		this.label = label;
		this.identifier = identifier;
		colorHexValue = getColorInHex();
	}

	@Override
	public String toString() {
		return label;
	}

	@Override
	public String getIdentifier() {
		return identifier;
	}

	public void setXAxisData(DoubleDataset xDoubleDataset) {
		this.xDoubleDataset = xDoubleDataset;
		this.xDoubleDataset.setName("energy");
	}

	public DoubleDataset getXAxisData() {
		return xDoubleDataset;
	}

	public IObservableList getNodeList() {
		return dataItemNodeList;
	}

	/**
	 * Add new create new ScanDataItemNode object for the datasets and add to nodeList
	 * @param xDoubleDataset
	 * @param yDoubleDataset
	 * @param identifier Unique identifier for the data
	 * @param label Label used to identify the data in the tree view
	 * @return new ScanDataItemNode object created using yDoubleDataset, identifer, label etc.
	 */
	public ScanDataItemNode updateData(DoubleDataset xDoubleDataset, DoubleDataset yDoubleDataset, String identifier, String label) {
		this.xDoubleDataset = xDoubleDataset;
		this.xDoubleDataset = xDoubleDataset;
		ScanDataItemNode newnode = new ScanDataItemNode(this, identifier, label, yDoubleDataset);
		newnode.setYaxisColorInHex(colorHexValue);
		dataItemNodeList.add(newnode);
		return newnode;
	}

	public String getColorInHex() {
		BundleContext context = GDAClientActivator.getBundleContext();
		ServiceReference<IPlotLineColorService> serviceRef = context.getServiceReference(IPlotLineColorService.class);
		if (serviceRef != null) {
			String colorValue = (String) serviceRef.getProperty(label);
			if (colorValue != null) {
				return colorValue;
			}
		}
		return null;
	}

	@Override
	public IObservableList getChildren() {
		return dataItemNodeList;
	}

	@Override
	public void removeChild(Node dataNode) {
		// NOt supported
	}

	public DoubleDataset getUncalibratedXAxisData() {
		return uncalibratedXAxisData;
	}

	public void setUncalibratedXAxisData(DoubleDataset uncalibratedXAxisData) {
		this.uncalibratedXAxisData = uncalibratedXAxisData;
	}

}
