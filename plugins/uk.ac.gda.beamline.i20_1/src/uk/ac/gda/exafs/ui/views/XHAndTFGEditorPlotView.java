/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.ui.views;

import java.util.Vector;

import org.dawnsci.plotting.jreality.core.AxisMode;
import org.dawnsci.plotting.jreality.impl.Plot1DAppearance;
import org.dawnsci.plotting.jreality.impl.Plot1DStyles;
import org.dawnsci.plotting.jreality.impl.PlotException;
import org.dawnsci.plotting.jreality.tick.TickFormatting;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.action.ToolBarManager;
import org.eclipse.swt.SWT;
import org.eclipse.swt.SWTException;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.ui.part.ViewPart;

import uk.ac.diamond.scisoft.analysis.axis.AxisValues;
import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.DataSetPlotter;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.IPlotUI;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.Plot1DUIAdapter;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.PlottingMode;
import uk.ac.gda.exafs.ui.TimingGraphOverlay;

public class XHAndTFGEditorPlotView extends ViewPart {

	public static String ID = "uk.ac.gda.exafs.ui.views.xhandtfgeditorplotter";

	private Group plottingComposite;
	private DataSetPlotter plotter;
	private AxisValues xAxisValues;
	private TimingGraphOverlay timingOverlay;

	@Override
	public void createPartControl(Composite parent) {
		createPlotterComposite(parent);
	}

	@Override
	public void setFocus() {
		plotter.setFocusable(true);
	}

	private void createPlotterComposite(Composite comp) {

		plottingComposite = new Group(comp, SWT.NONE);
		plottingComposite.setText("Timing Graph");
		plottingComposite.setLayout(new GridLayout(1, false));
		plottingComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

		final ToolBar plotTools = new ToolBar(plottingComposite, SWT.FLAT);
		plotTools.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		this.plotter = new DataSetPlotter(PlottingMode.ONED, plottingComposite, false);
		plotter.getComposite().setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

		this.xAxisValues = new AxisValues();
		plotter.setAxisModes(AxisMode.CUSTOM, AxisMode.LINEAR, AxisMode.LINEAR);
		plotter.setXAxisValues(xAxisValues, 1);
		plotter.setYAxisLabel("Acquire (on/off)");
		plotter.setYTickLabelFormat(TickFormatting.roundAndChopMode);
		plotter.setXAxisLabel("Time (s)");
		plotter.setPlotActionEnabled(true);
		plotter.setPlotRightClickActionEnabled(true);

		final ToolBarManager toolBar = new ToolBarManager(plotTools);
		final IPlotUI plotUI = new Plot1DUIAdapter(toolBar, plotter, plottingComposite, getPartName()) {
			@Override
			public void buildToolActions(IToolBarManager manager) {
				manager.add(createShowLegend());
				super.buildToolActions(manager);
			}
		};
		toolBar.update(true);
		plotter.registerUI(plotUI);
	}

	public void updateEDEPoints(DoubleDataset[] points, String plotTitle) throws PlotException {

		try {

			plotter.getColourTable().clearLegend();

			Plot1DAppearance app = new Plot1DAppearance(java.awt.Color.BLACK, Plot1DStyles.SOLID, 1, "Acquire");
			plotter.getColourTable().pushEntryOnLegend(app);

			this.xAxisValues.setValues(points[0].getData());
			Vector<DoubleDataset> newPlot = new Vector<DoubleDataset>();
			newPlot.add(points[1]);
			plotter.replaceAllPlots(newPlot);

			addTriggerMarks(points[2], points[3]);

			// causes a run time exception if called too early...
			plotter.setTitle(plotTitle);
			plotter.setYAxisLabel("Acquire (on/off)");
			plotter.setXAxisLabel("Time (s)");
			plotter.refresh(true);

		} catch (SWTException disposed) {
			return;

		} catch (Exception ne) {
			if (!plotter.isDisposed()) {
				plotter.resetView();
				xAxisValues.setValues(new double[] { 3000d });
				plotter.replaceCurrentPlot(new DoubleDataset(new double[] { 1d }));
				plotter.refresh(false);
			}
		}
	}

	protected void addTriggerMarks(DoubleDataset inTrigPoints, DoubleDataset outTrigPoints) {
		if (timingOverlay != null) {
			plotter.unRegisterOverlay(timingOverlay);
		}
		timingOverlay = new TimingGraphOverlay(getSite().getShell().getDisplay());
		timingOverlay.setInputTriggers(inTrigPoints.getData());
		timingOverlay.setOutputTriggers(outTrigPoints.getData());
		plotter.registerOverlay(timingOverlay);
	}

	public void updateTFGPoints(AbstractDataset[] points, String plotTitle) throws PlotException {
		try {
			plotter.getColourTable().clearLegend();

			Plot1DAppearance app = new Plot1DAppearance(java.awt.Color.BLACK, Plot1DStyles.SOLID, 1, "Acquire");
			plotter.getColourTable().pushEntryOnLegend(app);

			this.xAxisValues.setValues(((DoubleDataset) points[0]).getData());
			Vector<DoubleDataset> newPlot = new Vector<DoubleDataset>();
			newPlot.add((DoubleDataset) points[1]);
			plotter.replaceAllPlots(newPlot);

			if (timingOverlay != null) {
				plotter.unRegisterOverlay(timingOverlay);
			}
			timingOverlay = new TimingGraphOverlay(getSite().getShell().getDisplay());
			timingOverlay.setInputTriggers(new double[]{0});
			
			plotter.registerOverlay(timingOverlay);

			// causes a run time exception if called too early...
			long lemoOutChannel = Math.round(Math.floor(points[3].getDouble(0)));
			plotter.setTitle(plotTitle);
			plotter.setYAxisLabel("Lemo Out " + lemoOutChannel +" (on/off)");
			plotter.setXAxisLabel("Time (ms)");
			plotter.refresh(true);

		} catch (SWTException disposed) {
			return;

		} catch (Exception ne) {
			if (!plotter.isDisposed()) {
				plotter.resetView();
				xAxisValues.setValues(new double[] { 3000d });
				plotter.replaceCurrentPlot(new DoubleDataset(new double[] { 1d }));
				plotter.refresh(false);
			}
		}
	}

}
