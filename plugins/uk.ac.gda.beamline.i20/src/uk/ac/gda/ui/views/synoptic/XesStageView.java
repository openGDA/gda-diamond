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

public class XesStageView extends HardwareDisplayComposite {

	public XesStageView(Composite parent, int style) {
		super(parent, style);
	}

	@Override
	protected void createControls(Composite parent) throws Exception {
		setViewName("XES stage");

		setBackgroundImage(getImageFromPlugin("oe images/xes_main.bmp"), new Point(50,150));
		parent.setBackgroundMode(SWT.INHERIT_FORCE);

		createMotorControls(parent);
		createArrows(parent);
		addResizeListener(parent);
	}

	private void createArrows(Composite parent) throws IOException {
		HighlightImageLabel lineLabel = new HighlightImageLabel(parent, "det_x");
		lineLabel.setImage(getImageFromPlugin("arrow images/z.png"));
		lineLabel.setHighlightImage(getImageFromPlugin("arrow images/z_red.png"));
		setWidgetPosition(lineLabel.getControl(), 26, 3);

		lineLabel = new HighlightImageLabel(parent, "det_rot");
		lineLabel.setImage(getImageFromPlugin("arrow images/pitch.png"));
		lineLabel.setHighlightImage(getImageFromPlugin("arrow images/pitch_red.png"));
		setWidgetPosition(lineLabel.getControl(), 40, 5);

		lineLabel = new HighlightImageLabel(parent, "det_y");
		lineLabel.setImage(getImageFromPlugin("arrow images/y.png"));
		lineLabel.setHighlightImage(getImageFromPlugin("arrow images/y_red.png"));
		setWidgetPosition(lineLabel.getControl(), 29, 25);

		lineLabel = new HighlightImageLabel(parent, "table2_y");
		lineLabel.setImage(getImageFromPlugin("arrow images/y.png"));
		lineLabel.setHighlightImage(getImageFromPlugin("arrow images/y_red.png"));
		setWidgetPosition(lineLabel.getControl(), 3, 58);

		lineLabel = new HighlightImageLabel(parent, "table2_x");
		lineLabel.setImage(getImageFromPlugin("arrow images/z.png"));
		lineLabel.setHighlightImage(getImageFromPlugin("arrow images/z_red.png"));
		setWidgetPosition(lineLabel.getControl(), 47, 70);

		lineLabel = new HighlightImageLabel(parent, "spec_rot");
		lineLabel.setImage(getImageFromPlugin("arrow images/yaw2.png"));
		lineLabel.setHighlightImage(getImageFromPlugin("arrow images/yaw2_red.png"));
		setWidgetPosition(lineLabel.getControl(), 78, 62);
	}

	private void createMotorControls(Composite parent) throws DeviceException {
		MotorControlsGui motorControls = new MotorControlsGui(parent, "det_x");
		setWidgetPosition(motorControls.getControls(), 0, 0);

		motorControls = new MotorControlsGui(parent, "det_y");
		setWidgetPosition(motorControls.getControls(), -5, 25);

		motorControls = new MotorControlsGui(parent, "det_rot");
		setWidgetPosition(motorControls.getControls(), 45, 12);

		motorControls = new MotorControlsGui(parent, "det_slit");
		setWidgetPosition(motorControls.getControls(), 25, 25);

		motorControls = new MotorControlsGui(parent, "table2_y");
		setWidgetPosition(motorControls.getControls(), -5, 45);

		motorControls = new MotorControlsGui(parent, "table2_x");
		setBackGround(motorControls.getControls(), SWT.COLOR_WHITE);
		setWidgetPosition(motorControls.getControls(), 35, 75);

		motorControls = new MotorControlsGui(parent, "spec_rot");
		setBackGround(motorControls.getControls(), SWT.COLOR_WHITE);
		setWidgetPosition(motorControls.getControls(), 87, 60);

		motorControls = new MotorControlsGui(parent, "XESEnergy");
		setWidgetPosition(motorControls.getControls(), 75, 0, 150);

		motorControls = new MotorControlsGui(parent, "XESBragg");
		setWidgetPosition(motorControls.getControls(), 75, 12, 150);
	}
}
