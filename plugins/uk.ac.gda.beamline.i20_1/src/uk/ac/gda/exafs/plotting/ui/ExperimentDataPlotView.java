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
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.tool.IToolPageSystem;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.plotting.ScanDataPlotterComposite;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.DetectorModel.EnergyCalibrationSetObserver;
import uk.ac.gda.exafs.plotting.model.ExperimentRootNode;

public class ExperimentDataPlotView extends ViewPart {
	public static String ID = "uk.ac.gda.exafs.ui.views.dataplotview";
	ScanDataPlotterComposite scanDataPlotter;

	private static final Logger logger = LoggerFactory.getLogger(ExperimentDataPlotView.class);

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
		ExperimentRootNode rootNode = new ExperimentRootNode();
		scanDataPlotter = new ScanDataPlotterComposite(composite, SWT.None, this, rootNode);
		scanDataPlotter.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		Composite xAxisDataSwitchComposite = new Composite(composite, SWT.None);
		xAxisDataSwitchComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		xAxisDataSwitchComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		Button useStripsIndex = new Button(xAxisDataSwitchComposite, SWT.CHECK);
		useStripsIndex.setText("Use strips number for X axis");
		useStripsIndex.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		ctx.bindValue(
				WidgetProperties.selection().observe(useStripsIndex),
				BeanProperties.value(ExperimentRootNode.USE_STRIPS_AS_X_AXIS_PROP_NAME).observe(rootNode));
		ctx.bindValue(
				WidgetProperties.text().observe(useStripsIndex),
				BeanProperties.value(EnergyCalibrationSetObserver.ENERGY_CALIBRATION_PROP_NAME).observe(DetectorModel.INSTANCE.getEnergyCalibrationSetObserver()),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						StringBuilder text = new StringBuilder();
						try {
							text.append("Use uncalibrated X axis");
						} catch (Exception e) {
							logger.error("Unable to get calibration data", e);
							UIHelper.showError("Unable to get calibration data", e.getMessage());
						}
						return text.toString();
					}
				});
//		ctx.bindValue(
//				WidgetProperties.visible().observe(useStripsIndex),
//				BeanProperties.value(EnergyCalibrationSetObserver.ENERGY_CALIBRATION_PROP_NAME).observe(DetectorModel.INSTANCE.getEnergyCalibrationSetObserver()),
//				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
//				new UpdateValueStrategy() {
//					@Override
//					public Object convert(Object value) {
//						if (!((String) value).isEmpty()) {
//							return true;
//						}
//						return false;
//					}
//				});
	}

	@Override
	public void setFocus() {
		if (!scanDataPlotter.isDisposed()) {
			scanDataPlotter.setFocus();
		}
	}

	@SuppressWarnings({ "rawtypes", "unchecked" })
	@Override
	public Object getAdapter(Class adapter) {
		if (IPlottingSystem.class == adapter) return scanDataPlotter.getPlottingSystem();
		if (IToolPageSystem.class == adapter) return scanDataPlotter.getPlottingSystem().getAdapter(adapter);
		return super.getAdapter(adapter);
	}
}
