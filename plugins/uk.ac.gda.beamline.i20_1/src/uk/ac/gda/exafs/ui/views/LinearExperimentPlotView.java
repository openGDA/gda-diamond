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
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.detector.LinearExperimentModel;

public class LinearExperimentPlotView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.LinearExperimentPlotView";

	private IPlottingSystem plottingSystem;

	public LinearExperimentPlotView() {
		LinearExperimentModel.INSTANCE.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if (evt.getPropertyName().equals(LinearExperimentModel.SCAN_DATA_SET_PROP_NAME)) {
					DoubleDataset[] scanDataSet = (DoubleDataset[]) evt.getNewValue();
					List<DoubleDataset> lnI0It = new ArrayList<DoubleDataset>();
					lnI0It.add(scanDataSet[1]);
					plottingSystem.getSelectedXAxis().setTicksAtEnds(false);
					plottingSystem.clear();
					plottingSystem.createPlot1D(scanDataSet[0], lnI0It, null);
				} else if (evt.getPropertyName().equals(LinearExperimentModel.SCANNING_PROP_NAME)) {
					if ((boolean) evt.getNewValue()) {
						try {
							PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(ID);
						} catch (PartInitException e) {
							UIHelper.showError("Unable to display linear experiment plot view", e.getMessage());
						}
					}
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

}
