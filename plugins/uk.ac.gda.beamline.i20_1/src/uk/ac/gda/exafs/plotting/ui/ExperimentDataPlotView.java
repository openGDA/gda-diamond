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

package uk.ac.gda.exafs.plotting.ui;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;

import uk.ac.gda.client.plotting.ScanDataPlotter;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.DetectorModel.EnergyCalibrationSetObserver;
import uk.ac.gda.exafs.plotting.model.ExperimentDataNode;
import uk.ac.gda.exafs.ui.data.UIHelper;

public class ExperimentDataPlotView extends ViewPart {
	public static String ID = "uk.ac.gda.exafs.ui.views.dataplotview";
	ScanDataPlotter scanDataPlotter;

	protected DataBindingContext ctx;

	@Override
	public void dispose() {
		ctx.dispose();
		super.dispose();
	}

	@Override
	public void createPartControl(Composite parent) {
		ctx = new DataBindingContext();
		Composite composite = new Composite(parent, SWT.None);
		composite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		ExperimentDataNode rootNode = new ExperimentDataNode();
		scanDataPlotter = new ScanDataPlotter(composite, SWT.None, this, rootNode);
		scanDataPlotter.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		Composite xAxisDataSwitchComposite = new Composite(composite, SWT.None);
		xAxisDataSwitchComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		xAxisDataSwitchComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		Button useStripsIndex = new Button(xAxisDataSwitchComposite, SWT.CHECK);
		useStripsIndex.setText("Use strips number for X axis");
		useStripsIndex.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		ctx.bindValue(
				WidgetProperties.selection().observe(useStripsIndex),
				BeanProperties.value(ExperimentDataNode.USE_STRIPS_AS_X_AXIS_PROP_NAME).observe(rootNode));
		ctx.bindValue(
				WidgetProperties.text().observe(useStripsIndex),
				BeanProperties.value(EnergyCalibrationSetObserver.ENERGY_CALIBRATION_SET_PROP_NAME).observe(DetectorModel.INSTANCE.getEnergyCalibrationSetObserver()),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						StringBuilder text = new StringBuilder();
						try {
							text.append("Use strips number for X axis");
							if (((boolean) value) && DetectorModel.INSTANCE.getCurrentDetector() != null) {
								text.append(" (calibrated with " + DetectorModel.INSTANCE.getCurrentDetector().getEnergyCalibration().getSampleDataFileName() + ")");
							}
						} catch (Exception e) {
							//
						}
						return text.toString();
					}
				});
	}

	@Override
	public void setFocus() {
		if (!scanDataPlotter.isDisposed()) {
			scanDataPlotter.setFocus();
		}
	}
}
