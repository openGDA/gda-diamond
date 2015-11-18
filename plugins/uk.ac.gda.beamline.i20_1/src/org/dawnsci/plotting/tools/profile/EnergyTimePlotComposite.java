/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package org.dawnsci.plotting.tools.profile;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import org.dawb.common.ui.widgets.ActionBarWrapper;
import org.dawnsci.plotting.tools.profile.model.TimeEnergyShiftingModel;
import org.dawnsci.plotting.tools.profile.model.ToolPageModel;
import org.eclipse.dawnsci.analysis.api.dataset.IDataset;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.PlotType;
import org.eclipse.dawnsci.plotting.api.PlottingFactory;
import org.eclipse.dawnsci.plotting.api.trace.ILineTrace;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EnergyTimePlotComposite extends Composite {
	private final TimeEnergyShiftingModel timeEnergyShiftingModel;
	private IPlottingSystem<Composite> plottingSystem;
	private final ToolPageModel toolPageModel;
	protected static final Logger logger = LoggerFactory.getLogger(EnergyTimePlotComposite.class);

	public EnergyTimePlotComposite(Composite parent, int style, ToolPageModel toolPageModel, TimeEnergyShiftingModel timeEnergyShiftingModel) {
		super(parent, style);
		setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		this.timeEnergyShiftingModel = timeEnergyShiftingModel;
		this.toolPageModel = toolPageModel;
		setup();
	}

	private void setup() {
		ActionBarWrapper actionbarWrapper = ActionBarWrapper.createActionBars(this, null);
		try {
			if (plottingSystem == null) {
				plottingSystem = PlottingFactory.createPlottingSystem();
				plottingSystem.createPlotPart(this,
						"Energy vs Time",
						actionbarWrapper,
						PlotType.XY,
						null);
				plottingSystem.getPlotComposite().setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
				plottingSystem.getSelectedXAxis().setAxisAutoscaleTight(true);
				plottingSystem.getSelectedXAxis().setTitle("Time");
				plottingSystem.getSelectedYAxis().setTitle("Energy");
				plottingSystem.setRescale(true);
				timeEnergyShiftingModel.addPropertyChangeListener(TimeEnergyShiftingModel.DATA_UPDATED_PROP_NAME, new PropertyChangeListener() {
					@Override
					public void propertyChange(PropertyChangeEvent evt) {
						plottingSystem.clear();
						ILineTrace trace = plottingSystem.createLineTrace("time_for_energy");
						trace.setData(toolPageModel.getImageTrace().getAxes().get(1), (IDataset) evt.getNewValue());
						plottingSystem.addTrace(trace);
						plottingSystem.repaint();
					}
				});
			}
		} catch (Exception e) {
			logger.error("Unable to create plotting system", e);
		}
	}
}
