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

import gda.scan.ede.datawriters.EdeDataConstants;

import org.eclipse.dawnsci.plotting.api.trace.ILineTrace.PointStyle;
import org.eclipse.dawnsci.plotting.api.trace.ILineTrace.TraceType;
import org.eclipse.core.databinding.observable.list.IObservableList;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.client.plotting.model.DataNode;
import uk.ac.gda.client.plotting.model.LineTraceProvider;

public class ScanDataItemNode extends LineTraceProvider {
	private final String identifier;
	private final DoubleDataset data;
	private final String label;
	private String yaxisColorInHex;

	public ScanDataItemNode(String identifier, String label, DoubleDataset data, DataNode parent) {
		super(parent, null);
		this.identifier = identifier;
		this.data = data;
		this.label = label;
	}

	@Override
	public String getIdentifier() {
		return identifier;
	}

	@Override
	public String toString() {
		return label;
	}

	@Override
	public DoubleDataset getYAxisDataset() {
		return data;
	}

	@Override
	public IObservableList getChildren() {
		return null;
	}

	@Override
	public DoubleDataset getXAxisDataset() {
		ExperimentDataNode experimentDataNode = (ExperimentDataNode) parent.getParent().getParent();
		if (experimentDataNode.isUseStripsAsXaxis()) {
			return ExperimentDataNode.stripsData;
		}
		return ((SpectraNode) parent).getXAxisData();
	}

	public void setYaxisColorInHex(String yaxisColorInHex) {
		this.yaxisColorInHex = yaxisColorInHex;
	}

	@Override
	public TraceStyleDetails getTraceStyle() {
		TraceStyleDetails traceStyle = new TraceStyleDetails();
		ScanDataNode scanDataNode = (ScanDataNode) this.getParent().getParent();
		ExperimentDataNode experimentDataNode = (ExperimentDataNode) scanDataNode.getParent();
		if (!scanDataNode.isMultiCollection()) {
			if ((experimentDataNode.getChildren().size() - experimentDataNode.getChildren().indexOf(scanDataNode)) % 2 == 0) {
				traceStyle.setTraceType(TraceType.DASH_LINE);
				traceStyle.setPointStyle(PointStyle.DIAMOND);
				traceStyle.setPointSize(5);
			} else {
				traceStyle.setTraceType(TraceType.SOLID_LINE);
				traceStyle.setPointStyle(PointStyle.NONE);
				traceStyle.setPointSize(0);
			}
			traceStyle.setColorHexValue(yaxisColorInHex);
		} else {
			traceStyle.setTraceType(TraceType.SOLID_LINE);
			traceStyle.setPointStyle(PointStyle.NONE);
			traceStyle.setPointSize(0);
		}
		return  traceStyle;
	}

	@Override
	public boolean isPlotByDefault() {
		if (((SpectraNode) parent).getLabel().equals(EdeDataConstants.LN_I0_IT_COLUMN_NAME)) {
			return true;
		}
		return false;
	}

	@Override
	public void removeChild(DataNode dataNode) {
		// NOt supported
	}
}