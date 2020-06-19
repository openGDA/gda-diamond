/*-
 * Copyright © 2016 Diamond Light Source Ltd.
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

package uk.ac.gda.ui.views.synoptic;

import java.io.IOException;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.widgets.Composite;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.Finder;

public class SampleStageView extends HardwareDisplayComposite {

	private boolean sampleStageForXes = false;

	public SampleStageView(final Composite parent, int style) {
		super(parent, style);
	}

	@Override
	protected void createControls(final Composite parent) throws Exception {
		setViewName("Sample stage");
		setBackgroundImage(getImageFromPlugin("oe images/stage_01.jpg"), new Point(200, 150));
		parent.setBackgroundMode(SWT.INHERIT_FORCE);
		// sampleStageForXes=true;
		createMotorControls(parent);
		createArrows(parent);
		addResizeListener(parent);
	}

	private void createMotorControls(Composite parent) throws DeviceException {
		MotorControlsGui motorControlsRoll = new MotorControlsGui(parent, "sample_roll");
		motorControlsRoll.setLabel("Roll");

		MotorControlsGui motorControlsPitch = new MotorControlsGui(parent, "sample_pitch");
		motorControlsPitch.setLabel("Pitch");

		// Sample pitch, roll controls are reversed between XES and XAS
		if (sampleStageForXes) {
			setWidgetPosition(motorControlsRoll.getControls(), -30, -5);
			setWidgetPosition(motorControlsPitch.getControls(), 90, 15);
		} else {
			setWidgetPosition(motorControlsRoll.getControls(), 90, 15);
			setWidgetPosition(motorControlsPitch.getControls(), -30, -5);
		}

		if (sampleStageForXes) {
			MotorControlsGui motorControlsFine = new MotorControlsGui(parent, "sample_fine_rot");
			motorControlsFine.setLabel("Fine rotation");
			setWidgetPosition(motorControlsFine.getControls(), 30, -30);
		}

		MotorControlsGui motorControls = new MotorControlsGui(parent, "sample_x");
		motorControls.setLabel("Translation (x)");
		setWidgetPosition(motorControls.getControls(), 95, 40);

		motorControls = new MotorControlsGui(parent, "sample_rot");
		motorControls.setLabel("Rotation");
		setWidgetPosition(motorControls.getControls(), 40, 100);

		motorControls = new MotorControlsGui(parent, "sample_z");
		motorControls.setLabel("Sample (Z)");
		setWidgetPosition(motorControls.getControls(), -45, 55);

		motorControls = new MotorControlsGui(parent, "sample_y");
		motorControls.setLabel("Height (Y)");
		setWidgetPosition(motorControls.getControls(), -40, 25);

	}

	private void createArrows(Composite parent) throws IOException {
		// Add 'fine motor' control rotation arrow
		if (sampleStageForXes) {
			HighlightImageLabel lineLabel = new HighlightImageLabel(parent, "sample_fine_rot");
			lineLabel.setImage(getImageFromPlugin("arrow images/yaw.png"));
			lineLabel.setHighlightImage(getImageFromPlugin("arrow images/yaw_red.png"));
			setWidgetPosition(lineLabel.getControl(), 40, -5);
		}

		Scannable samplePitchScannable = Finder.find("sample_pitch");
		Scannable sampleRollScannable = Finder.find("sample_roll");

		// NB sample stage for XAS : pitch and roll arrows are reversed.
		HighlightImageLabel lineLabel = new HighlightImageLabel(parent);
		lineLabel.setScannable(sampleStageForXes ? samplePitchScannable : sampleRollScannable);
		lineLabel.setImage(getImageFromPlugin("arrow images/pitch.png"));
		lineLabel.setHighlightImage(getImageFromPlugin("arrow images/pitch_red.png"));
		setWidgetPosition(lineLabel.getControl(), 60, 15);

		lineLabel = new HighlightImageLabel(parent);
		lineLabel.setScannable(sampleStageForXes ? sampleRollScannable : samplePitchScannable);
		lineLabel.setImage(getImageFromPlugin("arrow images/roll.png"));
		lineLabel.setHighlightImage(getImageFromPlugin("arrow images/roll_red.png"));
		setWidgetPosition(lineLabel.getControl(), 15, 3);

		lineLabel = new HighlightImageLabel(parent, "sample_x");
		lineLabel.setImage(getImageFromPlugin("arrow images/x.png"));
		lineLabel.setHighlightImage(getImageFromPlugin("arrow images/x_red.png"));
		setWidgetPosition(lineLabel.getControl(), 88, 65);

		lineLabel = new HighlightImageLabel(parent, "sample_y");
		lineLabel.setImage(getImageFromPlugin("arrow images/y2.png"));
		lineLabel.setHighlightImage(getImageFromPlugin("arrow images/y2_red.png"));
		setWidgetPosition(lineLabel.getControl(), 7,25);

		lineLabel = new HighlightImageLabel(parent, "sample_z");
		lineLabel.setImage(getImageFromPlugin("arrow images/z.png"));
		lineLabel.setHighlightImage(getImageFromPlugin("arrow images/z_red.png"));
		setWidgetPosition(lineLabel.getControl(), -5, 60);

		lineLabel = new HighlightImageLabel(parent, "sample_rot");
		lineLabel.setImage(getImageFromPlugin("arrow images/yaw.png"));
		lineLabel.setHighlightImage(getImageFromPlugin("arrow images/yaw_red.png"));
		setWidgetPosition(lineLabel.getControl(), 45, 80);

		lineLabel = new HighlightImageLabel(parent);
		lineLabel.setImage(getImageFromPlugin("oe images/beam_head.png"));
		setWidgetPosition(lineLabel.getControl(), 35, -10);

		lineLabel = new HighlightImageLabel(parent);
		lineLabel.setLabelText("X-ray beam");
		setWidgetPosition(lineLabel.getControl(), 35, -15);
	}

	public boolean getSampleStageForXes() {
		return sampleStageForXes;
	}

	public void setSampleStageForXes(boolean sampleStageForXes) {
		this.sampleStageForXes = sampleStageForXes;
	}
}
