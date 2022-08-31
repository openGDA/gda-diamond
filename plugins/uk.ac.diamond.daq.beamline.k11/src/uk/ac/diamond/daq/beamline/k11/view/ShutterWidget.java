/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.view;

import static uk.ac.gda.ui.tool.ClientSWTElements.composite;
import static uk.ac.gda.ui.tool.ClientSWTElements.label;

import java.util.Optional;

import org.eclipse.nebula.widgets.opal.switchbutton.SwitchButton;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.observable.IObserver;

/**
 * Label and switch button to open/close a shutter. Control can be enabled/disabled
 * by a second hint scannable which returns a boolean indicating availability of the shutter.
 */
public class ShutterWidget {

	private static final Logger logger = LoggerFactory.getLogger(ShutterWidget.class);

	private Scannable shutter;
	private Optional<Scannable> enablingScannable;

	private Label label;
	private SwitchButton shutterControl;


	/**
	 * @param shutterName		Name of shutter scannable. Moved to "Reset", then "Open" to open,
	 * 							and "Close" to close.
	 *
	 * @param enablingScannable Name of scannable returning {@code true} if shutter may be operated,
	 * 							otherwise {@code false}. May be {@code null}.
	 */
	public ShutterWidget(String shutterName, String enablingScannable) {
		shutter = Finder.find(shutterName);
		this.enablingScannable = Optional.ofNullable(Finder.find(enablingScannable));
	}

	public Control createControls(Composite parent) {
		var composite = composite(parent, 1);
		label = label(composite, "Shutter");

		shutterControl = new SwitchButton(composite, SWT.NONE);

		shutterControl.setTextForSelect("Open");
		shutterControl.setTextForUnselect("Closed");

		shutterControl.addListener(SWT.Selection, select -> toggleShutter());

		final IObserver stateUpdater = (source, arg) -> updateShutterState();
		shutter.addIObserver(stateUpdater);
		shutterControl.addDisposeListener(dispose -> shutter.deleteIObserver(stateUpdater));

		updateShutterState();

		enablingScannable.ifPresent(scannable -> {
			IObserver autoEnablementToggle = (source, argument) -> toggleEnablement();
			scannable.addIObserver(autoEnablementToggle);
			shutterControl.addDisposeListener(dispose -> scannable.deleteIObserver(autoEnablementToggle));
			toggleEnablement();
		});

		return composite;
	}

	private void toggleEnablement() {
		var scannable = enablingScannable.get();
		try {
			boolean enabled = (boolean) scannable.getPosition();
			Display.getDefault().asyncExec(() -> {
				shutterControl.setEnabled(enabled);
				label.setText(enabled ? "Shutter" : "Shutter (disabled)");
			});
		} catch (DeviceException e) {
			logger.error("Error reading {} position", scannable.getName(), e);
		}
	}

	private void toggleShutter() {
		try {
			var open = shutterControl.getSelection();
			if (open) {
				close();
			} else {
				open();
			}
		} catch (DeviceException e) {
			logger.error("Error moving shutter", e);
		}
	}

	private void updateShutterState() {
		try {
			var position = shutter.getPosition().toString();
			boolean open = position.equals("Open");

			// https://github.com/eclipse/nebula/issues/300
			// Fixed in Nebula 2.5
			boolean counterIntuitiveSelection = !open;

			Display.getDefault().syncExec(() -> {
				shutterControl.setSelection(counterIntuitiveSelection);
				shutterControl.redraw(); // not needed from v 2.5
			});

		} catch (DeviceException e) {
			logger.error("Error reading shutter position", e);
		}
	}


	private void open() throws DeviceException {
		shutter.moveTo("Reset");
		shutter.moveTo("Open");
	}

	private void close() throws DeviceException {
		shutter.moveTo("Close");
	}

}
