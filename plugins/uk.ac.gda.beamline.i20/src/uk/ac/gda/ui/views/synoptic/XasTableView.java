/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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
import org.eclipse.swt.custom.StyleRange;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;

import gda.device.DeviceException;

public class XasTableView extends HardwareDisplayComposite {

	public static final String ID = "uk.ac.gda.ui.views.synoptic.XasTableView";

	public XasTableView(Composite parent, int style) {
		super(parent, style);
	}

	@Override
	protected void createControls(Composite parent) throws Exception {
		setViewName("Xas table view (T1)");
		setBackgroundImage(getImageFromDalPlugin("oe images/table_right_scaled.jpg"), new Point(150, 200));
		parent.getShell().setBackgroundMode(SWT.INHERIT_FORCE);
		createStanfordControls(parent);
		createMotorControls(parent);
		createArrows(parent);
		createLabels(parent);

		addResizeListener(parent);
	}

	private void createStanfordControls(Composite parent) throws DeviceException {
		int widthOverride = 230;

		AmplifierConrolsGui ampGui = new AmplifierConrolsGui(parent, "Ion chamber - I0");
		ampGui.setSensitivity("i0_stanford_sensitivity", "i0_stanford_sensitivity_units");
		ampGui.setOffset("i0_stanford_offset", "i0_stanford_offset_units");
		ampGui.setCurrent("i0_stanford_offset_current");
		ampGui.createControls();
		setBackGround(ampGui.getGroup(), SWT.COLOR_WHITE);
		setWidgetPosition(ampGui.getGroup(), -25, -20, widthOverride);

		ampGui = new AmplifierConrolsGui(parent, "Ion chamber - It");
		ampGui.setSensitivity("it_stanford_sensitivity", "it_stanford_sensitivity_units");
		ampGui.setOffset("it_stanford_offset", "it_stanford_offset_units");
		ampGui.setCurrent("it_stanford_offset_current");
		ampGui.createControls();
		setBackGround(ampGui.getGroup(), SWT.COLOR_WHITE);
		setWidgetPosition(ampGui.getGroup(), 25, -30, widthOverride);

		ampGui = new AmplifierConrolsGui(parent, "Ion chamber - Iref");
		ampGui.setSensitivity("iref_stanford_sensitivity", "iref_stanford_sensitivity_units");
		ampGui.setOffset("iref_stanford_offset", "iref_stanford_offset_units");
		ampGui.setCurrent("iref_stanford_offset_current");
		ampGui.createControls();
		setBackGround(ampGui.getGroup(), SWT.COLOR_WHITE);
		setWidgetPosition(ampGui.getGroup(), 75, -35, widthOverride);
	}

	private void createMotorControls(Composite parent) throws DeviceException {
		MotorControlsGui motorControls = new MotorControlsGui(parent, "table1_x");
		motorControls.setLabel("X motion");
		setWidgetPosition(motorControls.getControls(), -15, 90);

		motorControls = new MotorControlsGui(parent, "table1_y");
		motorControls.setLabel("Height");
		setWidgetPosition(motorControls.getControls(), 53, 80);

		EnumPositionerGui enumpositioner = new EnumPositionerGui(parent,  "filterwheel");
		enumpositioner.createControls();
		enumpositioner.setLabel("Filter wheel");
		setBackGround(enumpositioner.getGroup(), SWT.COLOR_WHITE);
		setWidgetPosition(enumpositioner.getGroup(), 60, 20);
	}

	private void createArrows(Composite parent) throws IOException {
		HighlightImageLabel lineLabel = new HighlightImageLabel(parent, "table1_x");
		lineLabel.setImage(getImageFromDalPlugin("arrow images/x.png"));
		lineLabel.setHighlightImage(getImageFromDalPlugin("arrow images/x_red.png"));
		setWidgetPosition(lineLabel.getControl(), 15, 90);

		lineLabel = new HighlightImageLabel(parent, "table1_y");
		lineLabel.setImage(getImageFromDalPlugin("arrow images/y2.png"));
		lineLabel.setHighlightImage(getImageFromDalPlugin("arrow images/y2_red.png"));
		setWidgetPosition(lineLabel.getControl(), 45, 80);

		lineLabel = new HighlightImageLabel(parent);
		lineLabel.setImage(getImageFromDalPlugin("oe images/beam_head.png"));
		setWidgetPosition(lineLabel.getControl(), -18, 20);
	}

	private void createLabels(Composite parent) {
		StyledText titleText = new StyledText(parent, SWT.NONE);
		titleText.setText("T1 -XAS table - Transmission and Fluorescence");
		StyleRange style1 = new StyleRange();
		style1.start = 0;
		style1.length = titleText.getText().length();
		style1.fontStyle = SWT.BOLD;
		titleText.setStyleRange(style1);
		setWidgetPosition(titleText, 10, -42);

		Label label = new Label(parent, SWT.NONE);
		label.setText("I0");
		setWidgetPosition(label, 17, 21);

		label = new Label(parent, SWT.NONE);
		label.setText("It");
		setWidgetPosition(label, 52, 14);

		label = new Label(parent, SWT.NONE);
		label.setText("Iref");
		setWidgetPosition(label, 79, 10);
	}
}
