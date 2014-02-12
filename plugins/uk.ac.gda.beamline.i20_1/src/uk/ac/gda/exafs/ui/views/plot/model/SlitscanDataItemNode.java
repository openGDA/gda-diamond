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

package uk.ac.gda.exafs.ui.views.plot.model;

import gda.rcp.GDAClientActivator;

import java.util.ArrayList;
import java.util.List;

import org.dawnsci.plotting.api.trace.ILineTrace.PointStyle;
import org.dawnsci.plotting.api.trace.ILineTrace.TraceType;
import org.eclipse.core.databinding.observable.list.IObservableList;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceReference;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.client.liveplot.IPlotLineColorService;

public class SlitscanDataItemNode extends DataNode implements LineTraceProvider {
	private final String identifier;
	private final String label;
	private final List<Double> data = new ArrayList<Double>();

	public SlitscanDataItemNode(String identifier, String label, DataNode parent) {
		super(parent);
		this.identifier = identifier;
		this.label = label;
	}

	@Override
	public DoubleDataset getYAxisDataset() {
		return (DoubleDataset) AbstractDataset.createFromList(data);
	}

	@Override
	public DoubleDataset getXAxisDataset() {
		return ((SlitsScanDataNode) parent).getData();
	}

	@Override
	public TraceStyleDetails getTraceStyleDetails() {
		TraceStyleDetails traceStyle = new TraceStyleDetails();
		SlitsScanDataNode scanDataNode = (SlitsScanDataNode) this.getParent();
		SlitsScanRootDataNode experimentDataNode = (SlitsScanRootDataNode) scanDataNode.getParent();
		if ((experimentDataNode.getChildren().size() - experimentDataNode.getChildren().indexOf(scanDataNode)) % 2 == 0) {
			traceStyle.setTraceType(TraceType.DASH_LINE);
			traceStyle.setPointStyle(PointStyle.DIAMOND);
			traceStyle.setPointSize(6);
		} else {
			traceStyle.setTraceType(TraceType.SOLID_LINE);
			traceStyle.setPointStyle(PointStyle.NONE);
			traceStyle.setPointSize(0);
		}
		traceStyle.setColorHexValue(getColorInHex());
		return  traceStyle;
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
		return null;
	}

	@Override
	public String getIdentifier() {
		return identifier;
	}

	@Override
	public String toString() {
		return label;
	}

	public void update(Double value) {
		data.add(value);
	}

	@Override
	public boolean isPlotByDefault() {
		return true;
	}
}
