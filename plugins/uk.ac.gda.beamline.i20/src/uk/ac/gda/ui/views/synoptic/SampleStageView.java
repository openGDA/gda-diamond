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
import gda.device.ScannableMotion;
import gda.device.ScannableMotionUnits;
import gda.device.scannable.ScannableMotionUnitsBase;
import gda.factory.Finder;
import uk.ac.gda.ui.viewer.RotationViewer;

public class SampleStageView extends HardwareDisplayComposite {
	public static final String ID = "uk.ac.gda.ui.views.synoptic.SampleStageView";

	public SampleStageView(final Composite parent, int style) {
		super(parent, style);
	}

	@Override
	protected void createControls(final Composite parent) throws Exception {
		setViewName("Sample stage");
		setBackgroundImage(getImageFromDalPlugin("oe images/stage_01.jpg"), new Point(200, 75));
		parent.getShell().setBackgroundMode(SWT.INHERIT_DEFAULT);

		createMotorControls();
		createArrows();
		addResizeListener(parent);
	}

	private void createMotorControls() throws DeviceException {
		MotorControlsGui motorControls = new MotorControlsGui(parent, "sample_roll");
		motorControls.setLabel("Roll");
		setWidgetPosition(motorControls.getControls(), -30, -5);

		motorControls = new MotorControlsGui(parent, "sample_x");
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

		motorControls = new MotorControlsGui(parent, "sample_pitch");
		motorControls.setLabel("Pitch");
		setWidgetPosition(motorControls.getControls(), 90, 15);
	}

	private void createArrows() throws IOException {
		HighlightImageLabel lineLabel = new HighlightImageLabel(parent, "sample_pitch");
		lineLabel.setImage(getImageFromDalPlugin("arrow images/pitch.png"));
		lineLabel.setHighlightImage(getImageFromDalPlugin("arrow images/pitch_red.png"));
		setWidgetPosition(lineLabel.getControl(), 60, 15);

		lineLabel = new HighlightImageLabel(parent, "sample_roll");
		lineLabel.setImage(getImageFromDalPlugin("arrow images/roll.png"));
		lineLabel.setHighlightImage(getImageFromDalPlugin("arrow images/roll_red.png"));
		setWidgetPosition(lineLabel.getControl(), 15, 3);

		lineLabel = new HighlightImageLabel(parent, "sample_x");
		lineLabel.setImage(getImageFromDalPlugin("arrow images/x.png"));
		lineLabel.setHighlightImage(getImageFromDalPlugin("arrow images/x_red.png"));
		setWidgetPosition(lineLabel.getControl(), 88, 65);

		lineLabel = new HighlightImageLabel(parent, "sample_y");
		lineLabel.setImage(getImageFromDalPlugin("arrow images/y2.png"));
		lineLabel.setHighlightImage(getImageFromDalPlugin("arrow images/y2_red.png"));
		setWidgetPosition(lineLabel.getControl(), 7,25);

		lineLabel = new HighlightImageLabel(parent, "sample_z");
		lineLabel.setImage(getImageFromDalPlugin("arrow images/z.png"));
		lineLabel.setHighlightImage(getImageFromDalPlugin("arrow images/z_red.png"));
		setWidgetPosition(lineLabel.getControl(), -5, 60);

		lineLabel = new HighlightImageLabel(parent, "sample_rot");
		lineLabel.setImage(getImageFromDalPlugin("arrow images/yaw.png"));
		lineLabel.setHighlightImage(getImageFromDalPlugin("arrow images/yaw_red.png"));
		setWidgetPosition(lineLabel.getControl(), 45, 80);

		lineLabel = new HighlightImageLabel(parent);
		lineLabel.setImage(getImageFromDalPlugin("oe images/beam_head.png"));
		setWidgetPosition(lineLabel.getControl(), 35, -10);

		lineLabel = new HighlightImageLabel(parent);
		lineLabel.setLabelText("X-ray beam");
		setWidgetPosition(lineLabel.getControl(), 35, -15);
	}
}
