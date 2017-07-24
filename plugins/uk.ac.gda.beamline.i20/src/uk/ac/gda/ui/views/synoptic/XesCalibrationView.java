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

import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;

import gda.jython.InterfaceProvider;

public class XesCalibrationView extends HardwareDisplayComposite {

	public static final String ID = "uk.ac.gda.ui.views.synoptic.XesCalibrationView";

	public XesCalibrationView(Composite parent, int style) {
		super(parent, style, new GridLayout(1,false));
	}

	private Label addLabel(Composite parent, String labelText) {
		Label label = new Label(parent, SWT.NONE);
		label.setText(labelText);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, true, false, 1, 1));
		return label;
	}

	private Button addButton(Composite parent, String text) {
		Button button = new Button(parent, SWT.PUSH);
		button.setText(text);
		button.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		return button;
	}
	@Override
	protected void createControls(Composite parent) throws Exception {
		setViewName("XES calibration view");
		Composite comp = new Group(parent, SWT.NONE);
		comp.setLayout(new GridLayout(4, false));

		// First row : XES energy control, expected energy and calibrate button
		int options = MotorControlsGui.COMPACT_LAYOUT | MotorControlsGui.HIDE_BORDER | MotorControlsGui.HIDE_STOP_CONTROLS;
		MotorControlsGui xesEnergy = new MotorControlsGui(comp, "XESEnergy", options);
		xesEnergy.setLabel("XES energy");

		Label expectedEnergyLabel = addLabel(comp, "Expected energy");

		Text expectedEnergyTextbox = new Text(comp, SWT.NONE);
		expectedEnergyTextbox.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));

		Button calibrateButton = addButton(comp, "Calibrate");

		// Second row : filename, load save offset button
		Label fileNameLabel = addLabel(comp, "Filename");

		Text fileNameTextbox = new Text(comp, SWT.NONE);
		fileNameTextbox.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));

		Button loadFileButton = addButton(comp, "Load file");
		Button saveFile = addButton(comp, "Save file");

		// 3rd row : Load offset from file, remove offset button
		Label loadedOffsetLabel = addLabel(comp, "Loaded offset file");

		Text offsetFileTextbox = new Text(comp, SWT.NONE);
		offsetFileTextbox.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));

		Button removeOffsetsButton = addButton(comp, "Remove offsets");
	}

	volatile boolean threadBusy = false;

	private void runCommand(String command) {
		InterfaceProvider.getCommandRunner().runCommand(command);
	}
	private void applyCalibration(double expectedEnergy) {
		runCommand("xes_calculate.applyFromLive("+String.valueOf(expectedEnergy)+")");
	}

	private void loadFromFile(String filename) {
		runCommand("xes_offsets.apply("+filename+")");
	}

	private void saveToFile(String filename) {
		runCommand("xes_offsets.saveAs("+filename+")");
	}

	private void removeOffsets() {
		runCommand("xes_offsets.removeAll()");
	}
}
