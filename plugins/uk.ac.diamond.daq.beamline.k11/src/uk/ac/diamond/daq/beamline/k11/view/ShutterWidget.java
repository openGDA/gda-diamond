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

import static java.util.function.Predicate.not;
import static java.util.stream.Collectors.joining;
import static uk.ac.gda.ui.tool.ClientSWTElements.composite;
import static uk.ac.gda.ui.tool.ClientSWTElements.label;

import java.util.Map;
import java.util.stream.Collectors;

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
 * by other hint scannables which return booleans indicating availability of the shutter.
 */
public class ShutterWidget {

	private static final Logger logger = LoggerFactory.getLogger(ShutterWidget.class);

	private final Scannable shutter;
	private final String shutterName;
	private final Map<Scannable, String> enablingScannables;

	private Label label;
	private SwitchButton shutterControl;

	/** Results of evaluation of individual enabling scannable */
	record EnablementResult(boolean enabled, String tooltip) {}

	public ShutterWidget(ShutterWidgetConfiguration config) {
		shutter = Finder.find(config.getShutterName());
		shutterName = config.getShutterDisplayName();
		enablingScannables = config.getEnablingScannableNamesAndMessages().entrySet().stream()
			.collect(Collectors.toMap(entry -> (Scannable) Finder.find(entry.getKey()), Map.Entry::getValue));
	}

	public Control createControls(Composite parent) {
		var composite = composite(parent, 1);
		label = label(composite, shutterName);

		shutterControl = new SwitchButton(composite, SWT.NONE);

		shutterControl.setTextForSelect("Open");
		shutterControl.setTextForUnselect("Closed");

		shutterControl.addListener(SWT.Selection, select -> toggleShutter());

		// update shutter control when scannable position changes
		IObserver stateUpdater = (source, arg) -> updateShutterState();
		shutter.addIObserver(stateUpdater);

		// recalculate shutter availability when receiving events from any of the enabling scannables
		IObserver autoEnablementToggle = (source, argument) -> evaluateShutterEnablement();

		enablingScannables.keySet().forEach(scannable -> scannable.addIObserver(autoEnablementToggle));

		// dispose scannable to widget listeners when the widget is disposed
		shutterControl.addDisposeListener(dispose -> {
			shutter.deleteIObserver(stateUpdater);
			enablingScannables.keySet().forEach(scannable -> scannable.deleteIObserver(autoEnablementToggle));
		});

		// set initial states
		updateShutterState();
		evaluateShutterEnablement();

		return composite;
	}

	private void evaluateShutterEnablement() {
		var results = enablingScannables.entrySet().stream()
			.map(entry -> evaluateCondition(entry.getKey(), entry.getValue())).toList();

		var enabled = results.stream().allMatch(EnablementResult::enabled);
		var tooltip = results.stream().map(EnablementResult::tooltip).filter(not(String::isBlank)).collect(joining("\n"));

		Display.getDefault().asyncExec(() -> {
			shutterControl.setEnabled(enabled);
			shutterControl.getParent().setToolTipText(tooltip);
			label.setText(shutterName + (enabled ? "" : " (disabled)"));
			shutterControl.getParent().pack(); // force refresh, sometimes needed
		});
	}

	private EnablementResult evaluateCondition(Scannable scannable, String reasonForDisabling) {
		try {
			boolean enabled = (boolean) scannable.getPosition();
			return new EnablementResult(enabled, enabled ? "" : reasonForDisabling);
		} catch (DeviceException e) {
			var msg = String.format("Error reading %s position", scannable.getName());
			logger.error(msg, e);
			return new EnablementResult(false, msg);
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
			boolean open = position.equalsIgnoreCase("Open");

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
		shutter.moveTo("Reset"); // TODO this logic should be moved to the scannable that requires it
		shutter.moveTo("Open");
	}

	private void close() throws DeviceException {
		shutter.moveTo("Close");
	}

}
