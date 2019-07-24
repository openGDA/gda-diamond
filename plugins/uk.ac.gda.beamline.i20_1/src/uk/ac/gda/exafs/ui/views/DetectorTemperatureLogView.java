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

package uk.ac.gda.exafs.ui.views;

import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.PlotType;
import org.eclipse.dawnsci.plotting.api.PlottingFactory;
import org.eclipse.dawnsci.plotting.api.tool.IToolPageSystem;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.client.UIHelper;

public class DetectorTemperatureLogView extends ViewPart{

	public static final String ID = "uk.ac.gda.exafs.ui.views.DetectorTemperatureLogView";
	private static final Logger logger = LoggerFactory.getLogger(DetectorTemperatureLogView.class);

	private IPlottingSystem plottingSystem;

	public DetectorTemperatureLogView() {
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
		Composite composite = new Composite(parent, SWT.None);

		composite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		Composite plot = new Composite(composite, SWT.None);
		plot.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		plot.setLayout(new FillLayout());
		plottingSystem.createPlotPart(plot,
				getTitle(),
				// unique id for plot.
				getViewSite().getActionBars(),
				PlotType.XY,
				this);
	}

	@Override
	public void setFocus() {
	}

	@Override
	public Object getAdapter(@SuppressWarnings("rawtypes") Class clazz) {
		if (clazz == IToolPageSystem.class || clazz == IPlottingSystem.class) {
			return plottingSystem;
		}
		return super.getAdapter(clazz);
	}

}
