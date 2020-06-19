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
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.factory.Finder;

/**
 * Create GUI combo box controls for setting sensitivity and gain value and units and current on/off for Stanford amplifiers.
 * Built using {@link EnumPositionerGui} for the controls.
 */
public class AmplifierConrolsGui {
	private Composite parent;
	private Group group;
	private String label;

	private EnumPositioner sensValue, sensUnits;
	private EnumPositioner offsetValue, offsetUnits;
	private EnumPositioner currenOnOff;

	public AmplifierConrolsGui(Composite parent, String label) {
		this.parent = parent;
		this.label = label;
	}

	public void setSensitivity(String value, String units) {
		sensValue = Finder.find(value);
		sensUnits = Finder.find(units);
	}

	public void setOffset(String value, String units) {
		offsetValue = Finder.find(value);
		offsetUnits = Finder.find(units);
	}

	public void setCurrent(String current) {
		currenOnOff = Finder.find(current);
	}

	public void setLabel(String label) {
		this.label = label;
	}

	public Group getGroup() {
		return group;
	}
	public void createControls() throws DeviceException {
		group = new Group(parent, SWT.NONE);
		group.setText(label);
		group.setLayout(new GridLayout(3, false));
		group.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));

		Label lblSensitivity = new Label(group, SWT.NONE);
		lblSensitivity.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, true, false, 1, 1));
		lblSensitivity.setText("Sensitivity");
		EnumPositionerGui sensValueControl = EnumPositionerGui.getCombo(group, sensValue);
		EnumPositionerGui sensUnitControl = EnumPositionerGui.getCombo(group, sensUnits);

		Label offsetLabel = new Label(group, SWT.NONE);
		offsetLabel.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, true, false, 1, 1));
		offsetLabel.setText("Offset");
		EnumPositionerGui offsetValueControl = EnumPositionerGui.getCombo(group, offsetValue);
		EnumPositionerGui offsetUnitControl = EnumPositionerGui.getCombo(group, offsetUnits);

		Label currentLabel = new Label(group, SWT.NONE);
		currentLabel.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, true, false, 1, 1));
		currentLabel.setText("Current");
		EnumPositionerGui currentControl = EnumPositionerGui.getCombo(group, currenOnOff);
	}
}
