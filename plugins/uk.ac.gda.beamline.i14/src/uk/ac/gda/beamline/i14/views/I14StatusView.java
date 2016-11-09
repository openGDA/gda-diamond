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

package uk.ac.gda.beamline.i14.views;

import java.util.HashMap;
import java.util.Map;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.layout.RowLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.ui.part.ViewPart;

import gda.device.Scannable;
import gda.factory.Finder;
import gda.jython.ICommandRunner;
import gda.jython.InterfaceProvider;
import uk.ac.gda.dls.client.views.ReadonlyScannableComposite;
import uk.ac.gda.dls.client.views.RunCommandComposite;


public class I14StatusView extends ViewPart {

	private final Map<String, Integer> colourMap = new HashMap<String, Integer>();
	private final Finder finder = Finder.getInstance();
	private final ICommandRunner commandRunner = InterfaceProvider.getCommandRunner();

	@Override
	public void createPartControl(Composite parent) {
		GridDataFactory.fillDefaults().applyTo(parent);
		RowLayoutFactory.fillDefaults().applyTo(parent);
		parent.setBackground(new Color(Display.getDefault(), 237, 237, 237));

		initialiseColourMap();

		// Machine status
		final Group grpMachine = new Group(parent, SWT.NONE);
		grpMachine.setText("Machine");
		grpMachine.setBackground(null);
		GridLayoutFactory.fillDefaults().margins(5, 5).numColumns(1).applyTo(grpMachine);

		createNumericComposite(grpMachine, getScannable("ringCurrent"), "Ring current", "mA", 2, 1000);
		createNumericComposite(grpMachine, getScannable("timeToRefill"), "Time to refill", "s", 0, 1000);

		// Beamline status
		final Group grpBeamline = new Group(parent, SWT.NONE);
		grpBeamline.setText("Beamline");
		GridLayoutFactory.fillDefaults().margins(5, 5).numColumns(2).applyTo(grpBeamline);

		createNumericComposite(grpBeamline, getScannable("idGap"), "ID Gap", "mm", 2, 1000);
		createNumericComposite(grpBeamline, getScannable("dcm_bragg"), "Bragg", "degrees", 4, 1000);
		createNumericComposite(grpBeamline, getScannable("dcm_energy"), "Energy", "KeV", 4, 1000);

		// OH1 shutter
		final Group grpOH1 = new Group(parent, SWT.NONE);
		grpOH1.setText("OH1 Shutter");
		GridLayoutFactory.fillDefaults().margins(5, 5).numColumns(1).applyTo(grpOH1);

		createShutterComposite(grpOH1, getScannable("oh1_shutter_status"), "State");
		createCommandComposite(grpOH1, commandRunner, "Open/Close", "toggle_oh1_shtr()", "OH1 Open/Close", "Opens or closes OH1 shutter");

		// OH2 shutter
		final Group grpOH2 = new Group(parent, SWT.NONE);
		grpOH2.setText("OH2 Shutter");
		GridLayoutFactory.fillDefaults().margins(5, 5).numColumns(1).applyTo(grpOH2);

		createShutterComposite(grpOH2, getScannable("oh2_shutter_status"), "State");
		createCommandComposite(grpOH2, commandRunner, "Open/Close", "toggle_oh2_shtr()", "OH2 Open/Close", "Opens or closes OH2 shutter");

		// OH3 shutter
		final Group grpOH3 = new Group(parent, SWT.NONE);
		grpOH3.setText("OH3 Shutter");
		GridLayoutFactory.fillDefaults().margins(5, 5).numColumns(1).applyTo(grpOH3);

		createShutterComposite(grpOH3, getScannable("oh3_shutter_status"), "State");
		createCommandComposite(grpOH3, commandRunner, "Open/Close", "toggle_oh3_shtr()", "OH3 Open/Close", "Opens or closes OH3 shutter");

		// EH2 Nano shutter
		final Group grpEH2Nano = new Group(parent, SWT.NONE);
		grpEH2Nano.setText("EH2 Nano Shutter");
		GridLayoutFactory.fillDefaults().margins(5, 5).numColumns(1).applyTo(grpEH2Nano);

		createShutterComposite(grpEH2Nano, getScannable("eh2_nano_shutter_status"), "State");
		createCommandComposite(grpEH2Nano, commandRunner, "Open/Close", "toggle_eh2_nano_shtr()", "EH2 Nano Open/Close", "Opens or closes EH2 Nano shutter");
	}

	@Override
	public void setFocus() {
	}

	private Scannable getScannable(final String name) {
		return (Scannable) finder.find(name);
	}

	private void createShutterComposite(final Composite parent, final Scannable scannable, final String label) {
		final ReadonlyScannableComposite composite = new ReadonlyScannableComposite(parent, SWT.NONE, scannable, label, null, null);
		composite.setColourMap(colourMap);
	}

	private static void createNumericComposite(final Composite parent, final Scannable scannable, final String label, final String units, final Integer decimalPlaces, final Integer minPeriodMS) {
		final ReadonlyScannableComposite composite = new ReadonlyScannableComposite(parent, SWT.NONE, scannable, label, units, decimalPlaces);
		composite.setMinPeriodMS(minPeriodMS);
	}

	@SuppressWarnings("unused")
	private void createCommandComposite(final Composite parent, final ICommandRunner commandRunner, final String label, final String command, final String jobTitle, final String tooltip) {
		new RunCommandComposite(parent, SWT.NONE, commandRunner, label, command, null, jobTitle, tooltip);
	}

	private void initialiseColourMap() {
		colourMap.put("Open", 6);
		colourMap.put("Closed", 3);
		colourMap.put("Close", 3);
		colourMap.put("Reset", 8);
	}
}
