/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package gda.exafs.ui.composites;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableUtils;
import gda.factory.Finder;

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Link;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.ui.data.ScanObjectManager;
import uk.ac.gda.richbeans.components.FieldBeanComposite;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;

public class RoomTemperatureComposite extends FieldBeanComposite {

	private static Logger logger = LoggerFactory.getLogger(RoomTemperatureComposite.class);

	private ScaleBox pitch;
	private ScaleBox roll;
	private ScaleBox rotation;
	private ScaleBox z;
	private ScaleBox y;
	private ScaleBox x;
	private ScaleBox fineRotation;
	private Button btnGetCurrentValues;

	public RoomTemperatureComposite(Composite parent, int style) {
		super(parent, style);
		final GridLayout gridLayout = new GridLayout();
		gridLayout.numColumns = 2;
		setLayout(gridLayout);

		final Label xLabel = new Label(this, SWT.NONE);
		xLabel.setText("x");

		x = new ScaleBox(this, SWT.NONE);
		x.setMinimum(-15);
		x.setMaximum(15);
		x.setUnit("mm");
		final GridData gd_x = new GridData(SWT.FILL, SWT.CENTER, true, false);
		x.setLayoutData(gd_x);

		final Label yLabel = new Label(this, SWT.NONE);
		yLabel.setText("y");

		y = new ScaleBox(this, SWT.NONE);
		y.setMinimum(-20.0);
		y.setMaximum(20.0);
		final GridData gd_y = new GridData(SWT.FILL, SWT.CENTER, true, false);
		y.setLayoutData(gd_y);
		y.setUnit("mm");

		final Label zLabel = new Label(this, SWT.NONE);
		zLabel.setText("z");

		z = new ScaleBox(this, SWT.NONE);
		z.setMinimum(-15.0);
		z.setMaximum(15);
		final GridData gd_z = new GridData(SWT.FILL, SWT.CENTER, true, false);
		z.setLayoutData(gd_z);
		z.setUnit("mm");

		final Label rotationLabel = new Label(this, SWT.NONE);
		rotationLabel.setText("Rotation");

		final GridData gd_rotation = new GridData(SWT.FILL, SWT.CENTER, true, false);
		rotation = new ScaleBox(this, SWT.NONE);
		rotation.setMaximum(360);
		rotation.setLayoutData(gd_rotation);
		rotation.setUnit("°");

		if (ScanObjectManager.isXESOnlyMode()) {
			// fine rotation when in XES position
			final Label fineRotationLabel = new Label(this, SWT.NONE);
			fineRotationLabel.setText("Fine Rotation");

			fineRotation = new ScaleBox(this, SWT.NONE);
			fineRotation.setMaximum(360);
			fineRotation.setLayoutData(gd_rotation);
			fineRotation.setUnit("°");
		} else {
			// roll and yaw when in XAS position
			final Label rollLabel = new Label(this, SWT.NONE);
			rollLabel.setText("Roll");

			roll = new ScaleBox(this, SWT.NONE);
			roll.setMinimum(-5);
			final GridData gd_roll = new GridData(SWT.FILL, SWT.CENTER, true, false);
			roll.setLayoutData(gd_roll);
			roll.setUnit("°");
			roll.setMaximum(5);

			final Link yawLabel = new Link(this, SWT.NONE);
			yawLabel.setText("Pitch");

			pitch = new ScaleBox(this, SWT.NONE);
			pitch.setMinimum(-5);
			final GridData gd_yaw = new GridData(SWT.FILL, SWT.CENTER, true, false);
			pitch.setLayoutData(gd_yaw);
			pitch.setUnit("°");
			pitch.setMaximum(5);
		}

		btnGetCurrentValues = new Button(this, SWT.NONE);
		btnGetCurrentValues.setText("Get current values");
		btnGetCurrentValues.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent arg0) {
				x.setValue(getValueAsString("sample_x"));
				y.setValue(getValueAsString("sample_y"));
				z.setValue(getValueAsString("sample_z"));
				rotation.setValue(getValueAsString("sample_rot"));
				if (ScanObjectManager.isXESOnlyMode()) {
					fineRotation.setValue(getValueAsString("sample_fine_rot"));
				} else {
					roll.setValue(getValueAsString("sample_roll"));
					pitch.setValue(getValueAsString("sample_pitch"));
				}
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent arg0) {
				widgetSelected(arg0);
			}
		});

	}

	private String getValueAsString(String scannableName) {

		final Scannable scannable = (Scannable) Finder.getInstance().find(scannableName);
		if (scannable == null) {
			logger.error("Scannable " + scannableName + " cannot be found");
			return "";
		}
		String[] position;
		try {
			position = ScannableUtils.getFormattedCurrentPositionArray(scannable);
		} catch (DeviceException e) {
			logger.error("Scannable " + scannableName + " position cannot be resolved.");
			return "";
		}
		String strPosition = ArrayUtils.toString(position);
		strPosition = strPosition.substring(1, strPosition.length() - 1);
		return strPosition;
	}

	public ScaleBox getX() {
		return x;
	}

	public ScaleBox getY() {
		return y;
	}

	public ScaleBox getZ() {
		return z;
	}

	public ScaleBox getRotation() {
		return rotation;
	}

	public ScaleBox getFineRotation() {
		return fineRotation;
	}

	public ScaleBox getRoll() {
		return roll;
	}

	public ScaleBox getYaw() {
		return pitch;
	}
}
