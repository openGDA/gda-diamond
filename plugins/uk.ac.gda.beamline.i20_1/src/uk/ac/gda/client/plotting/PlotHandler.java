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

package uk.ac.gda.client.plotting;

import java.util.HashMap;
import java.util.Map;

import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.trace.ILineTrace;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;

import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.plotting.model.LineTraceProviderNode;
import uk.ac.gda.client.plotting.model.LineTraceProviderNode.TraceStyleDetails;
import uk.ac.gda.client.plotting.model.Node;

/**
 * Class to handle adding, removing data to plotting system - used in {@link ScanDataPlotterComposite}.
 * Refactored from {@link ScanDataPlotterComposite}.
 * @since 12/4/2018
 */
public class PlotHandler {

	private IPlottingSystem<Composite> plottingSystem;
	private final Map<String, Color> nodeColors = new HashMap<>();
	private static final int HIGHLIGHTED_LINE_WIDTH = 2;

	public PlotHandler(IPlottingSystem<Composite>  plottingSystem) {
		this.plottingSystem = plottingSystem;
	}

	public void updateDataItemNode(Node dataItemNode, boolean isAdded) {
		if (dataItemNode instanceof LineTraceProviderNode) {
			LineTraceProviderNode lineTraceProvider = (LineTraceProviderNode) dataItemNode;
			if (isAdded) {
				addTrace(lineTraceProvider);
			} else {
				removeTrace(lineTraceProvider.getIdentifier());
			}
		}
	}

	public void updateTrace(LineTraceProviderNode lineTraceProvider) {
		ILineTrace trace = (ILineTrace) plottingSystem.getTrace(lineTraceProvider.getIdentifier());
		if (trace != null) {
			trace.setData(lineTraceProvider.getXAxisDataset(), lineTraceProvider.getYAxisDataset());
			plottingSystem.getAxes().get(0).setTitle(lineTraceProvider.getXAxisDataset().getName());
			plottingSystem.getAxes().get(1).setTitle(lineTraceProvider.getYAxisDataset().getName());
			plottingSystem.repaint();
		}
	}

	public void addTrace(LineTraceProviderNode lineTraceProvider) {
		ILineTrace trace = (ILineTrace) plottingSystem.getTrace(lineTraceProvider.getIdentifier());
		if (trace == null) {
			trace = plottingSystem.createLineTrace(lineTraceProvider.getIdentifier());
			TraceStyleDetails traceDetails = lineTraceProvider.getTraceStyle();
			if (traceDetails.getColorHexValue() != null) {
				trace.setTraceColor(getTraceColor(traceDetails.getColorHexValue()));
			}
			int lineWidth = traceDetails.getLineWidth();
			if (lineTraceProvider.isHighlighted()) {
				lineWidth += HIGHLIGHTED_LINE_WIDTH;
			}
			trace.setLineWidth(lineWidth);
			trace.setTraceType(traceDetails.getTraceType());
			trace.setPointSize(traceDetails.getPointSize());
			trace.setPointStyle(traceDetails.getPointStyle());
			plottingSystem.addTrace(trace);
		}
		trace.setData(lineTraceProvider.getXAxisDataset(), lineTraceProvider.getYAxisDataset());
		plottingSystem.getSelectedXAxis().setTitle(lineTraceProvider.getXAxisDataset().getName());
		plottingSystem.repaint();
	}

	public void removeTrace(String identifier) {
		ILineTrace trace = (ILineTrace) plottingSystem.getTrace(identifier);
		if (trace != null) {
			plottingSystem.removeTrace(trace);
		}
	}

	private Color getTraceColor(String colorValue) {
		Color color = null;
		if (!nodeColors.containsKey(colorValue)) {
			color = UIHelper.convertHexadecimalToColor(colorValue, Display.getDefault());
			nodeColors.put(colorValue, color);
		} else {
			color = nodeColors.get(colorValue);
		}
		return color;
	}

	public void dispose() {
		for (Color color : nodeColors.values()) {
			color.dispose();
		}
	}
}
