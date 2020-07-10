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
import java.util.Map;

import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.exafs.xes.IXesOffsets;
import gda.factory.Finder;

public class XesCalibrationView extends HardwareDisplayComposite {

	private static final Logger logger = LoggerFactory.getLogger(XesCalibrationView.class);

	private IXesOffsets offsets;
	private Text loadedOffsetFileTextbox;

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

	private void setupScannables() {
		Map<String, IXesOffsets> offsetObject = Finder.getFindablesOfType(IXesOffsets.class);
		if (!offsetObject.isEmpty()) {
			offsets = offsetObject.values().iterator().next();
			logger.debug("Using XesOffsets object {}", offsets.getName());
		}
	}

	@Override
	protected void createControls(Composite parent) throws Exception {
		setViewName("XES calibration view");

		setupScannables();
		if (offsets == null) {
			MessageDialog.openWarning(parent.getShell(), "Cannot open XES calibration view", "Cannot open XES calibration view - required XesOffset object not found on server.");
			return;
		}

		Composite comp = new Group(parent, SWT.NONE);
		comp.setLayout(new GridLayout(4, false));

		// First row : XES energy control, expected energy and calibrate button
		int options = MotorControlsGui.COMPACT_LAYOUT | MotorControlsGui.HIDE_BORDER;
		MotorControlsGui xesEnergy = new MotorControlsGui(comp, "XESEnergy", options);
		xesEnergy.setLabel("XES energy");

		addLabel(comp, "Expected energy");

		Text expectedEnergyTextbox = new Text(comp, SWT.NONE);
		expectedEnergyTextbox.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		expectedEnergyTextbox.setText(xesEnergy.getFormattedPosition());

		Button calibrateButton = addButton(comp, "Calibrate");
		calibrateButton.addListener(SWT.Selection, event -> applyCalibration(expectedEnergyTextbox.getText()));
		calibrateButton.setToolTipText("Calculate the offsets for the expected energy and apply to the spectrometer motors");

		// Second row : filename, load save offset button
		addLabel(comp, "Filename");

		Text offsetFileTextbox = new Text(comp, SWT.NONE);
		offsetFileTextbox.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));

		Button loadFileButton = addButton(comp, "Load file");
		loadFileButton.setToolTipText("Load offset values from the given file and apply to the spectrometer motors");
		loadFileButton.addListener(SWT.Selection, event -> loadFromFile(offsetFileTextbox.getText()));

		Button saveFile = addButton(comp, "Save file");
		saveFile.setToolTipText("Save the current offset values for all spectrometer motors to file with given name.");
		saveFile.addListener(SWT.Selection, event -> saveToFile(offsetFileTextbox.getText()));

		// 3rd row : Load offset from file, remove offset button
		addLabel(comp, "Loaded offset file");

		loadedOffsetFileTextbox = new Text(comp, SWT.NONE);
		loadedOffsetFileTextbox.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));

		Button removeOffsetsButton = addButton(comp, "Remove offsets");
		removeOffsetsButton.setToolTipText("Set the offsets for all spectrometer motors to zero");
		removeOffsetsButton.addListener(SWT.Selection, event -> removeOffsets());
	}

	private void applyCalibration(String expectedEnergy) {
		try {
			Double energy = Double.parseDouble(expectedEnergy);
			offsets.applyFromLive(energy);
		} catch (NumberFormatException e) {
			String message = "Could not run offset calculation - expected energy " + expectedEnergy	+ " is not recognised as a number";
			MessageDialog.openWarning(parent.getShell(), "Problem starting offset calculation", message);
		} catch (DeviceException | IOException e) {
			logger.error("Problem running XES offset calculation", e);
			String message = "Problem running calibration : " + e.getMessage() + ".\nSee log panel for more details";
			MessageDialog.openWarning(parent.getShell(), "Problem running offset calculation", message);
		}
	}

	private void loadFromFile(String filename) {
		try {
			offsets.apply(filename);
			loadedOffsetFileTextbox.setText(filename);
		} catch (IOException e) {
			logger.error("Problem loading offsets from file {}", filename, e);
			MessageDialog.openWarning(parent.getShell(), "Problem loading offsets from file", "Problem loading offsets from file : "+e.getMessage());
		}
	}

	private void saveToFile(String filename) {
		if (filename == null || filename.isEmpty()) {
			MessageDialog.openWarning(parent.getShell(), "Problem saving offsets to file", "File name to save offsets to is empty.");
			return;
		}
		try {
			offsets.saveAs(filename);
		} catch (IOException e) {
			logger.error("Problem saving offsets to file {}", filename, e);
			MessageDialog.openWarning(parent.getShell(), "Problem saving to file", "Problem saving offsets to file : "+e.getMessage()+".\nSee log panel for more information");
		}
	}

	private void removeOffsets() {
		offsets.removeAll();
	}
}
