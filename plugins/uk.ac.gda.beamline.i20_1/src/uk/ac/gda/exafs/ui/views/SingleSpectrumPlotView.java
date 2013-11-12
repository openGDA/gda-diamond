
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

import java.util.List;
import java.util.Vector;

import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.PlotType;
import org.dawnsci.plotting.api.PlottingFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.perspectives.AlignmentPerspective;

import com.swtdesigner.SWTResourceManager;

public class SingleSpectrumPlotView extends ViewPart {

	public static String ID = AlignmentPerspective.SINGLE_SPECTRUM_PLOT_VIEW_ID;

	private static Logger logger = LoggerFactory.getLogger(SingleSpectrumPlotView.class);

	private IPlottingSystem plottingSystem;
	List<SelectionListener> selectionListeners = new Vector<SelectionListener>();

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
		plottingSystem.createPlotPart(plot, getTitle(),
				// unique id for plot.
				getViewSite().getActionBars(), PlotType.XY, this);

		Composite controls = new Composite(composite, SWT.None);
		controls.setBackground(SWTResourceManager.getColor(SWT.COLOR_WHITE));
		controls.setLayout(UIHelper.createGridLayoutWithNoMargin(4, false));
		controls.setLayoutData(new GridData(SWT.FILL, SWT.END, true, false));
	}

	@Override
	public void setFocus() {
		plottingSystem.setFocus();
	}

	@Override
	public void dispose() {
		plottingSystem.dispose();
		super.dispose();
	}


}
