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

package uk.ac.gda.exafs.ui.data.experiment;

import java.util.Arrays;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.dialogs.ListSelectionDialog;

import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.exafs.ui.data.UIHelper;

public class SampleStageMotorSelectionComposite extends Composite {

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private final Text text;
	private final SampleStageMotors motors;

	public SampleStageMotorSelectionComposite(Composite parent, int style, SampleStageMotors motors) {
		super(parent, style);
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		text = new Text(this, SWT.None);
		text.addListener(SWT.MouseUp, motorSelectionListener);
		text.addListener(SWT.KeyUp, motorSelectionListener);
		text.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		this.motors = motors;
		this.layout();
		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(text),
				BeanProperties.value(SampleStageMotors.SELECTED_MOTORS).observe(motors),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						ExperimentMotorPostion[] motorScanableSetups = (ExperimentMotorPostion[]) value;
						StringBuilder stringBuilder = new StringBuilder();
						if (motorScanableSetups.length > 0) {
							for (ExperimentMotorPostion selected : motorScanableSetups) {
								stringBuilder.append(selected.getScannableSetup().getLabel());
								stringBuilder.append(",");
							}
							DataHelper.remoteLastComma(stringBuilder);
						}
						return stringBuilder.toString();
					}
				});
	}

	Listener motorSelectionListener = new Listener() {
		@Override
		public void handleEvent(Event event) {
			if (event.type == SWT.MouseUp | event.type == SWT.KeyUp) {
				showAvailableMotorsDialog();
			}
		}
	};

	private void showAvailableMotorsDialog() {
		ListSelectionDialog dialog =
				new ListSelectionDialog(
						Display.getDefault().getActiveShell(),
						SampleStageMotors.scannables,
						new ArrayContentProvider(),
						new LabelProvider() {
							@Override
							public String getText(Object element) {
								return ((ExperimentMotorPostion) element).getScannableSetup().getLabel();
							}
						},
						"Select motors to include in the scanning");
		dialog.setInitialSelections(motors.getSelectedMotors());
		if (dialog.open() == Window.OK) {
			motors.setSelectedMotors(Arrays.asList(dialog.getResult()).toArray(new ExperimentMotorPostion[dialog.getResult().length]));
		}
	}

	@Override
	public void dispose() {
		text.removeListener(SWT.MouseUp, motorSelectionListener);
		text.removeListener(SWT.KeyUp, motorSelectionListener);
		super.dispose();
	}
}
