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

import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.PlotType;
import org.dawnsci.plotting.api.PlottingFactory;
import org.dawnsci.plotting.api.tool.IToolPageSystem;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.part.ViewPart;

import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.ui.composites.XHControlComposite;
import uk.ac.gda.exafs.ui.data.UIHelper;

public class DetectorLiveModeView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.DetectorLiveModeView";

	private XHControlComposite controlComposite;
	private IPlottingSystem plottingSystem;

	protected final DataBindingContext ctx = new DataBindingContext();

	public DetectorLiveModeView() {
		//
	}

	@Override
	public void createPartControl(Composite parent) {
		try {
			if (plottingSystem == null) {
				plottingSystem = PlottingFactory.createPlottingSystem();
			}
		} catch (Exception e) {
			// TODO Handle
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

		Composite controls = new Composite(composite, SWT.None);
		controls.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		controls.setLayoutData(new GridData(SWT.FILL, SWT.END, true, false));
		controlComposite = new XHControlComposite(controls, plottingSystem);
		// FIXME this is a hack to hide the margin!
		controlComposite.setBackground(Display.getDefault().getSystemColor(SWT.COLOR_WHITE));
		controlComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

		ctx.bindValue(WidgetProperties.enabled().observe(controlComposite),
				BeanProperties.value(DetectorModel.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorModel.INSTANCE));
	}

	@Override
	public void setFocus() {
		controlComposite.setFocus();
	}

	@Override
	public Object getAdapter(@SuppressWarnings("rawtypes") Class clazz) {
		if (clazz == IToolPageSystem.class || clazz == IPlottingSystem.class) {
			return plottingSystem;
		}
		return super.getAdapter(clazz);
	}
}
