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

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.dawnsci.plotting.api.trace.ILineTrace.PointStyle;
import org.eclipse.dawnsci.plotting.api.trace.ILineTrace.TraceType;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.nebula.visualization.xygraph.figures.XYGraph;

import uk.ac.gda.client.plotting.model.ITreeNode;
import uk.ac.gda.client.plotting.model.LineTraceProviderNode;

/**
 * Stores data for single spectrum
 */
public class ScanDataItemNode extends LineTraceProviderNode {
	private final DoubleDataset data;
	private final String label;

	public ScanDataItemNode(ITreeNode parent, String identifier, String label, DoubleDataset data) {
		super(parent, false, null);
		setIdentifier(identifier);
		this.data = data;
		this.label = label;
		setTraceStyle(getDefaultTraceStyle());
//		setPlotByDefault(getParent().getLabel().equals(EdeDataConstants.LN_I0_IT_COLUMN_NAME));
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
		ITreeNode rootNode = getRootNode();

		if (rootNode instanceof ExperimentRootNode) {
			ExperimentRootNode experimentRootNode = (ExperimentRootNode) rootNode;
			if (experimentRootNode.isUseStripsAsXaxis()) {
				DoubleDataset positionData = ((SpectraNode) getParent()).getUncalibratedXAxisData();
				if (positionData != null) {
					return positionData;
				} else {
					return experimentRootNode.getStripsData();
				}
			}
			return ((SpectraNode) getParent()).getXAxisData();
		}
		return ((SpectraNode) getParent()).getXAxisData();

	}

	public TraceStyleDetails getTraceStyleForEdeScanNode(EdeScanNode scanDataNode) {
		ExperimentRootNode experimentDataNode = (ExperimentRootNode) scanDataNode.getParent();
		TraceStyleDetails traceStyle = new TraceStyleDetails();

		// set the color from list of standard ones
//		int numPlots = scanDataNode.getTotalNumPlots();
		traceStyle.setColor(scanDataNode.getNextColour());

		if (!scanDataNode.isMultiCollection()) {
			if ((experimentDataNode.getChildren().size() - experimentDataNode.getChildren().indexOf(scanDataNode))
					% 2 == 0) {
				traceStyle.setTraceType(TraceType.DASH_LINE);
				traceStyle.setPointStyle(PointStyle.DIAMOND);
				traceStyle.setPointSize(5);
			} else {
				traceStyle.setTraceType(TraceType.SOLID_LINE);
				traceStyle.setPointStyle(PointStyle.NONE);
				traceStyle.setPointSize(0);
			}
		} else {
			traceStyle.setTraceType(TraceType.SOLID_LINE);
			traceStyle.setLineWidth(1);
			// Set point plotting style for datasets with only 1 value
			if (data != null && data.getShape()[0] <= 1) {
				traceStyle.setPointStyle(PointStyle.CIRCLE);
				traceStyle.setPointSize(5);
			} else {
				traceStyle.setPointStyle(PointStyle.NONE);
				traceStyle.setPointSize(0);
			}
		}
		return traceStyle;
	}


	public TraceStyleDetails getDefaultTraceStyle() {

		ITreeNode possibleScanNode = getScanNode();
		if (possibleScanNode instanceof EdeScanNode) {
			return getTraceStyleForEdeScanNode((EdeScanNode) possibleScanNode);
		}

		int numChildren = getParent().getChildren().size();
		TraceStyleDetails traceStyle = TraceStyleDetails.createDefaultSolidTrace();
		traceStyle.setColor(XYGraph.DEFAULT_TRACES_COLOR[numChildren % XYGraph.DEFAULT_TRACES_COLOR.length]);
		return traceStyle;
	}
}
