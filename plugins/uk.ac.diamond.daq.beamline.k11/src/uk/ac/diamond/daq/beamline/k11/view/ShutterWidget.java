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

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.nebula.widgets.opal.switchbutton.SwitchButton;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.commandqueue.SimpleCommandProgress;
import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.EnumPositionerStatus;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.observable.IObserver;
import uk.ac.gda.ui.tool.WidgetUtilities;

/**
 * Label and switch button to open/close a shutter. Control can be enabled/disabled
 * by other hint scannables which return booleans indicating availability of the shutter.
 */
public class ShutterWidget {

	private static final Logger logger = LoggerFactory.getLogger(ShutterWidget.class);

	private final EnumPositioner shutter;
	private final String shutterName;
	private final Map<Scannable, String> enablingScannables;

	private Label label;
	private SwitchButton shutterControl;

	private Color idleSelectedBg;
	private Color idleSelectedFg;
	private Color idleUnselectedBg;
	private Color idleUnselectedFg;
	private Color movingBg = Display.getDefault().getSystemColor(SWT.COLOR_YELLOW);
	private Color movingFg = Display.getDefault().getSystemColor(SWT.COLOR_BLACK);

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

		idleSelectedBg = shutterControl.getSelectedBackgroundColor();
		idleSelectedFg = shutterControl.getSelectedForegroundColor();
		idleUnselectedBg = shutterControl.getUnselectedBackgroundColor();
		idleUnselectedFg = shutterControl.getUnselectedForegroundColor();

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

	private boolean enabledDueToInterlocks;

	private void evaluateShutterEnablement() {
		var results = enablingScannables.entrySet().stream()
			.map(entry -> evaluateCondition(entry.getKey(), entry.getValue())).toList();

		var enabled = results.stream().allMatch(EnablementResult::enabled);
		enabledDueToInterlocks = enabled;
		var tooltip = results.stream().map(EnablementResult::tooltip).filter(not(String::isBlank)).collect(joining("\n"));
		logger.info("About to set enabled to {} due to interlocks", enabled);
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
		var open = shutterControl.getSelection();
		if (open) {
			close();
		} else {
			open();
		}
	}

	private void updateShutterState() {
		try {

			var status = shutter.getStatus();
			if (status == EnumPositionerStatus.MOVING) {
				Display.getDefault().syncExec(() -> {
					setTransitionState();
					shutterControl.redraw(); // not needed from v 2.5
					shutterControl.getParent().pack();
				});
			} else {
				// https://github.com/eclipse/nebula/issues/300
				// Fixed in Nebula 2.5
				boolean counterIntuitiveSelection = !selectionFromScannable();

				Display.getDefault().syncExec(() -> {
					setSteadyState();
					toggleDecoration(status);
					shutterControl.setSelection(counterIntuitiveSelection);
					shutterControl.getParent().pack(); // force refresh, sometimes needed
				});
			}

		} catch (DeviceException e) {
			logger.error("Error reading shutter position", e);
		}
	}

	private void setSteadyState() {
		shutterControl.setTextForSelect("Open");
		shutterControl.setTextForUnselect("Closed");
		shutterControl.setSelectedBackgroundColor(idleSelectedBg);
		shutterControl.setSelectedForegroundColor(idleSelectedFg);
		shutterControl.setUnselectedBackgroundColor(idleUnselectedBg);
		shutterControl.setUnselectedForegroundColor(idleUnselectedFg);
		shutterControl.setEnabled(enabledDueToInterlocks);
	}

	private void setTransitionState() {
		shutterControl.setTextForSelect("Opening");
		shutterControl.setSelectedBackgroundColor(movingBg);
		shutterControl.setSelectedForegroundColor(movingFg);
		shutterControl.setTextForUnselect("Closing");
		shutterControl.setUnselectedBackgroundColor(movingBg);
		shutterControl.setUnselectedForegroundColor(movingFg);
		shutterControl.setEnabled(false);
	}

	/** Shows or hides error decoration. No effect if {@code MOVING} */
	private void toggleDecoration(EnumPositionerStatus status) {
		if (status == EnumPositionerStatus.IDLE) {
			WidgetUtilities.hideDecorator(shutterControl);
		} else if (status == EnumPositionerStatus.ERROR) {
			WidgetUtilities.addErrorDecorator(shutterControl, "Move did not complete normally - check logs");
		}
	}

	/**
	 * @return {@code true} if shutter is Open, else {@code false}
	 */
	private boolean selectionFromScannable() throws DeviceException {
		var position = shutter.getPosition().toString();
		return position.equalsIgnoreCase("Open");
	}

	private void open() {
		move("Open");
	}

	private void close() {
		move("Close");
	}

	/**
	 * Starts the move as an interruptible Eclipse Job.
	 * During execution, an observer is added to the scannable
	 * which filters for {@link SimpleCommandProgress} args
	 * and updates the {@link IProgressMonitor} with these
	 * messages (percentage is ignored).
	 */
	private void move(String position) {
		Job moveJob = Job.create("Moving " + shutterName, monitor -> {
			monitor.beginTask("", IProgressMonitor.UNKNOWN);

			IObserver observer = (source, argument) -> {
				if (argument instanceof SimpleCommandProgress progress) {
					monitor.subTask(progress.getMsg());
				}
			};

			shutter.addIObserver(observer);
			try {
				shutter.asynchronousMoveTo(position);

				// while busy, keep checking for user cancellation
				do {
					if (monitor.isCanceled()) {
						shutter.stop();
						return Status.CANCEL_STATUS;
					}
					Thread.sleep(100);
				} while (shutter.isBusy());

				shutter.deleteIObserver(observer);

				if (shutter.getStatus() == EnumPositionerStatus.IDLE) {
					monitor.done();
					return Status.OK_STATUS;
				} else {
					return Status.error("Shutter move failed");
				}
			} catch (DeviceException e) {
				return Status.error("Shutter move failed", e);
			} catch (InterruptedException e) {
				monitor.setCanceled(true);
				Thread.currentThread().interrupt();
				return Status.CANCEL_STATUS;
			}

		});

		moveJob.schedule();
	}



}
