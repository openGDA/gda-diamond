/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.IScannableMotor;
import gda.device.Scannable;
import gda.device.scannable.scannablegroup.IScannableGroupNamed;
import gda.factory.Finder;

public class XesSimulatedPositionsView extends HardwareDisplayComposite {

	private static final org.slf4j.Logger logger = LoggerFactory.getLogger(XesSimulatedPositionsView.class);

	private IScannableGroupNamed spectrometerGroup;
	private Scannable xesEnergy;
	private Scannable xesBragg;

	private List<IScannableMotor> spectrometerMotors = new ArrayList<>();
	private Map<IScannableMotor, Text> textBoxes;

	public XesSimulatedPositionsView(Composite parent, int style) {
		super(parent, style, new GridLayout(1, false));
	}

	@Override
	protected void createControls(Composite parent) throws Exception {
		setupScannables();
		if (spectrometerGroup == null || xesEnergy == null || xesBragg == null) {
			MessageDialog.openWarning(parent.getShell(), "Cannot open Simulated positions view",
					"Cannot open simulated positions view - required object(s) not found on server.");
			return;
		}
		setupGui(parent);
		spectrometerGroup.addIObserver((source, arg) -> updateGui());
	}

	private synchronized void updateGui() {
		Display.getDefault().asyncExec(this::updatePositionTextboxes);
	}

	private void setupScannables() {
		spectrometerGroup = Finder.find("dummy_spectrometer");
		if (spectrometerGroup != null) {
			spectrometerMotors = new ArrayList<>();
			for (String name : spectrometerGroup.getGroupMembersNamesAsArray()) {
				spectrometerMotors.add(Finder.find(name));
			}
		}
		xesEnergy = Finder.find("dummy_XESEnergy");
		xesBragg = Finder.find("dummy_XESBragg");
	}

	private void setupGui(Composite parent) throws DeviceException {
		setViewName("XES simulated positions view");
		final int positionTextboxWidth = 100;

		Composite comp = new Composite(parent, SWT.NONE);
		comp.setLayout(new GridLayout(1, false));
		GridData gridData = new GridData(SWT.CENTER, SWT.CENTER, false, false, 1, 1);
		gridData.widthHint = 250;
		comp.setLayoutData(gridData);

		// Add control for XES Energy
		int options = MotorControlsGui.COMPACT_LAYOUT | MotorControlsGui.HIDE_BORDER;
		MotorControlsGui xesEnergyControl = new MotorControlsGui(comp, xesEnergy.getName(), options);
		xesEnergyControl.setLabel("XES Energy");

		MotorControlsGui xesBraggControl = new MotorControlsGui(comp, xesBragg.getName(), options);
		xesBraggControl.setLabel("XES Bragg");

		Composite positionsComp = new Group(parent, SWT.NONE);
		positionsComp.setLayout(new GridLayout(2, false));

		// Add label and textbox for each motor
		textBoxes = new HashMap<>();
		for (IScannableMotor scn : spectrometerMotors) {
			// Make label from scannable name by removing 'dummy' and replacing "_"s with spaces :
			String labelForMotor = scn.getName().replaceAll("_", " ").replaceAll("dummy", "").trim();
			addLabel(positionsComp, labelForMotor);
			Text textBox = addTextBox(positionsComp, positionTextboxWidth);
			textBoxes.put(scn, textBox);
		}
		updatePositionTextboxes();
	}

	private Label addLabel(Composite parent, String labelText) {
		Label label = new Label(parent, SWT.NONE);
		label.setText(labelText);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, true, false, 1, 1));
		return label;
	}

	private Text addTextBox(Composite parent, int width) {
		Text textbox = new Text(parent, SWT.NONE);
		GridData gridData = new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1);
		gridData.widthHint = width;
		textbox.setLayoutData(gridData);
		textbox.setEditable(false);
		return textbox;
	}

	/**
	 * Update the text boxes with the current offset values from the motors.
	 *
	 * @return
	 */
	private Map<String, Double> updatePositionTextboxes() {
		logger.debug("Updating position text boxes");
		final Map<String, Double> offsetMap = new LinkedHashMap<>();
		textBoxes.entrySet().stream().forEach(entry -> {
			Double offset = getPosition(entry.getKey());
			Text textbox = entry.getValue();
			textbox.setText(String.format("%.5g", offset));
		});

		return offsetMap;
	}

	/**
	 *
	 * @param scnMotor
	 * @return Current position of scannable (assumed to be single floating point digit). Catches any exception throw
	 *         and returns 0.
	 */
	private Double getPosition(IScannableMotor scnMotor) {
		try {
			return Double.parseDouble(scnMotor.getPosition().toString());
		} catch (NumberFormatException | DeviceException e) {
			logger.error("Problem getting position for {}", scnMotor.getName(), e);
			return 0.0;
		}
	}

}
