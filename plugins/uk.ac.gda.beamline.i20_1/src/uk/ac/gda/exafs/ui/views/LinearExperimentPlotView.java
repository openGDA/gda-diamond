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

package uk.ac.gda.exafs.ui.views;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.List;

import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.PlotType;
import org.dawnsci.plotting.api.PlottingFactory;
import org.dawnsci.plotting.api.tool.IToolPageSystem;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.experiment.TimeResolvedExperimentModel;

public class LinearExperimentPlotView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.LinearExperimentPlotView";

	private static Logger logger = LoggerFactory.getLogger(LinearExperimentPlotView.class);

	private IPlottingSystem plottingSystem;

	public LinearExperimentPlotView() {
		TimeResolvedExperimentModel.INSTANCE.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if (evt.getPropertyName().equals(TimeResolvedExperimentModel.SCAN_DATA_SET_PROP_NAME)) {
					DoubleDataset[] scanDataSet = (DoubleDataset[]) evt.getNewValue();
					List<DoubleDataset> lnI0It = new ArrayList<DoubleDataset>();
					lnI0It.add(scanDataSet[1]);
					plottingSystem.getSelectedXAxis().setAxisAutoscaleTight(true);
					plottingSystem.clear();
					plottingSystem.createPlot1D(scanDataSet[0], lnI0It, null);
				}
			}
		});
	}

	@Override
	public void createPartControl(Composite parent) {
		try {
			if (plottingSystem == null) {
				plottingSystem = PlottingFactory.createPlottingSystem();
			}
		} catch (Exception e) {
			UIHelper.showError("Unable to create plotting system", e.getMessage());
			logger.error("Unable to create plotting system", e);
			return;
		}
		plottingSystem.createPlotPart(parent,
				getTitle(),
				// unique id for plot.
				getViewSite().getActionBars(),
				PlotType.XY,
				this);
	}

	@Override
	public void setFocus() {}

	@Override
	public Object getAdapter(@SuppressWarnings("rawtypes") Class clazz) {
		if (clazz == IToolPageSystem.class || clazz == IPlottingSystem.class) {
			return plottingSystem;
		}
		return super.getAdapter(clazz);
	}

}
