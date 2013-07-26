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

package uk.ac.gda.exafs.ui.data;

import gda.device.EnumPositioner;
import gda.device.Scannable;
import gda.observable.IObserver;

import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.forms.widgets.FormToolkit;

import uk.ac.gda.exafs.data.ClientConfig.ScannableSetup;
import uk.ac.gda.ui.viewer.EnumPositionViewer;
import uk.ac.gda.ui.viewer.MotorPositionViewer;
import uk.ac.gda.ui.viewer.RotationViewer;

public class UIHelper {
	private UIHelper() {}

	private static final int DEFAULT_DECIMAL_PLACES = 2;
	private static final double DEFAULT_STEP = 1.0;

	public static void showError(String message, String reason) {
		MessageDialog.openError(Display.getDefault().getActiveShell(), "Error", message  + "\n\nReason:\n" + reason);
	}

	public static void showWarning(String message, String reason) {
		MessageDialog.openWarning(Display.getDefault().getActiveShell(), "Warning", message  + "\n\nReason:\n" + reason);
	}

	public static enum UIMotorControl {ROTATION, POSITION, ENUM}

	// TODO Add flag for horizontal fill
	public static void createMotorViewer(FormToolkit toolkit, Composite parent, ScannableSetup scannable, UIMotorControl control, IObserver moveObserver) {
		try {
			final Scannable theScannable = scannable.getScannable();
			theScannable.addIObserver(moveObserver);
			if (control == UIMotorControl.ROTATION) {
				RotationViewer rotationViewer = new RotationViewer(theScannable, "", false);
				rotationViewer.configureStandardStep(DEFAULT_STEP);
				rotationViewer.setNudgeSizeBoxDecimalPlaces(DEFAULT_DECIMAL_PLACES);
				GridLayoutFactory rotationGroupLayoutFactory = GridLayoutFactory.swtDefaults().numColumns(3).spacing(0, 0).margins(0, 0);
				GridLayoutFactory layoutFactory = GridLayoutFactory.swtDefaults().numColumns(3).spacing(0, 0);
				rotationViewer.createControls(parent, SWT.SINGLE, true, rotationGroupLayoutFactory.create(), layoutFactory.create(), null);
				rotationViewer.setRestoreValueWhenFocusLost(true);
				scannable.setUiViewer(rotationViewer);
			} else if (control == UIMotorControl.POSITION) {
				MotorPositionViewer motorPositionViewer = new MotorPositionViewer(parent, theScannable, null, true);
				motorPositionViewer.setRestoreValueWhenFocusLost(true);
				scannable.setUiViewer(motorPositionViewer);
			} else {
				if (theScannable instanceof EnumPositioner) {
					EnumPositionViewer enumPositionViewer = new EnumPositionViewer(parent, (EnumPositioner) theScannable, "", true);
					scannable.setUiViewer(enumPositionViewer);
				} else {
					throw new Exception ("Unable to create EnumPositioner");
				}
			}
		} catch (Exception ex) {
			String errorLabel = "Unable to setup " + scannable.getLabel() + " configuration";
			UIHelper.showWarning(errorLabel, ex.getMessage());
			toolkit.createLabel(parent,errorLabel, SWT.NONE);
		}
	}
}
