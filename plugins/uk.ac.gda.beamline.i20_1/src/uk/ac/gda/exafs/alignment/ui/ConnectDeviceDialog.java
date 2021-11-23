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

package uk.ac.gda.exafs.alignment.ui;

import java.util.concurrent.atomic.AtomicInteger;

import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.ProgressBar;
import org.eclipse.swt.widgets.Shell;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.Device;
import gda.device.detector.EdeDetector;
import gda.factory.FactoryException;
import uk.ac.diamond.daq.concurrent.Async;

/**
 * Dialog box to allow user to reconnect a device by calling it's {@link Device#reconfigure()} method.
 * Progress bar shows the progress - it increments from 0 to 100% over the 'max expected configuration time'
 * and is set to 100% when detector is configured.
 * Message is added to the dialog after configure has finished to inform user of the results (e.g. success/error/timeout).
 * User can close the dialog using OK button once configuration has finished or has taken too long.
 *
 * @since 5/10/2018
 */
public class ConnectDeviceDialog extends Dialog {

	private static Logger logger = LoggerFactory.getLogger(ConnectDeviceDialog.class);

	private Device deviceToConnect;

	private ProgressBar progressBar;
	private Label progressLabel;
	private Button okButton ;

	/** This is the maximum expected time device is expected to take to reconfigure **/
	private int maxExpectedConfigureTimeSecs = 60;

	private int pollIntervalSec = 1;

	/** Current running status of configure operation **/
	private volatile boolean configureInProgress = false;

	/** Message for user about result of configure. **/
	private volatile String configureMessage = "";

	protected ConnectDeviceDialog(Shell parentShell) {
		super(parentShell);
	}

	public static ConnectDeviceDialog create(Shell parentShell, EdeDetector detector) {
		ConnectDeviceDialog connectionDialog = new ConnectDeviceDialog(parentShell);
		connectionDialog.setDetector(detector);
		connectionDialog.setBlockOnOpen(true);
		// need to try with hardware to find realistic timeout value (xh is slow to configure...)
		// Might need to use different value for different detectors.
		connectionDialog.setMaxExpectedConfigureTimeSecs(20);
		return connectionDialog;
	}

	@Override
	protected Control createDialogArea(Composite parent) {
		Composite container = (Composite) super.createDialogArea(parent);
		container.setLayout(new GridLayout(1, false));
		Label label = new Label(container, SWT.NONE);
		label.setText("Please wait while " + deviceToConnect.getName() + " is configured...\n");

		progressBar = new ProgressBar(container, SWT.HORIZONTAL);
		progressBar.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false, 1, 1));
		progressBar.setMinimum(0);
		progressBar.setMaximum(maxExpectedConfigureTimeSecs);

		progressLabel = new Label(container, SWT.WRAP | SWT.LEFT);
		progressLabel.setText("\n\n\n\n"); // Make label large enough for several lines of wrapped text
		progressLabel.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false, 1, 1));

		Async.execute(this::configureDevice);
		Async.execute(this::updateGuiWhenConfiguring);

		return container;
	}

	/**
	 * Try to reconfigure the detector by calling {@link EdeDetector#reconfigure()}.
	 * Sets {@link configMessage} to something appropriate on failure/success.
	 */
	private void configureDevice() {
		String deviceName = deviceToConnect.getName();
		try {
			configureInProgress = true;
			logger.debug("Reconfiguring detector {}..", deviceName);
			deviceToConnect.reconfigure();
			if (deviceToConnect.isConfigured()) {
				configureMessage = deviceName+" configuration finished successfully.";
			} else {
				configureMessage = "Problem during "+deviceName+" configuration - see log for more information.";
			}
			logger.debug("Finished reconfiguring {}", deviceName);
		} catch (FactoryException e) {
			logger.warn("Problem configuring detector {} from BeamLineAlignmentView", deviceName, e);
			configureMessage = "Problem during "+deviceName+" configuration " + e.getMessage() + ".\n Check the log for more information";
		} finally {
			configureInProgress = false;
		}
	}

	/**
	 * Run something in GUI thread only if widget has not been disposed
	 * @param runnable
	 */
	private void runInGuiThread(Runnable runnable) {
		if (getDialogArea().isDisposed()) {
			logger.debug("Disposed");
			return;
		}
		Display.getDefault().asyncExec(runnable);
	}

	/**
	 * Update progress bar while device is being configured
	 * (using {@link #configureDevice()}, running in another thread).
	 * Update widget with text message showing result from configuring.
	 * If time taken for configure to complete exceeds {@link #maxExpectedConfigureTimeSecs},
	 */
	private void updateGuiWhenConfiguring() {
		configureInProgress = true;
		AtomicInteger timeTaken = new AtomicInteger(0);
		while(configureInProgress && timeTaken.get()<maxExpectedConfigureTimeSecs) {
			try {
				Thread.sleep(1000*pollIntervalSec);
			} catch (InterruptedException e) {
				logger.debug("Interrupted exception in updateGuiWhenConfiguring", e);
			}
			timeTaken.getAndAdd(pollIntervalSec);
			logger.debug("Time taken = {}", timeTaken.get());
			// Update the progress bar (in GUI thread)
			runInGuiThread( () -> progressBar.setSelection(timeTaken.get()));
		}
		final boolean timeout = timeTaken.get() >= maxExpectedConfigureTimeSecs;

		// Update Progress bar to 100%, add message to composite with configuration result.
		runInGuiThread(() -> {
			okButton.setEnabled(true);
			progressBar.setSelection(maxExpectedConfigureTimeSecs);

			if (timeout) {
				configureMessage = "Timeout of "+maxExpectedConfigureTimeSecs+" secs reached while waiting for "+deviceToConnect.getName()+" to configure\n"+
									"Device might not be behaving correctly - check the log";
			}
			progressLabel.setText(configureMessage);

			// Set the message colour to red if detector was not configured due to some problem
			if (!deviceToConnect.isConfigured() || timeout) {
				progressLabel.setForeground(progressLabel.getDisplay().getSystemColor(SWT.COLOR_RED));
			}
		});
	}

	public void setMaxExpectedConfigureTimeSecs(int timeOutSecs) {
		this.maxExpectedConfigureTimeSecs = timeOutSecs;
	}

	public void setPollIntervalSec(int pollIntervalSec) {
		this.pollIntervalSec = pollIntervalSec;
	}

	public void setDetector(EdeDetector detector) {
		this.deviceToConnect = detector;
	}

	// Dialog overrides
    @Override
    protected void configureShell(Shell newShell) {
        super.configureShell(newShell);
        newShell.setText("Configure detector");
    }

	@Override
	protected Point getInitialSize() {
		return new Point(450, 200);
	}

	/**
	 * Only want to show OK button in the dialog.
	 * Initially disabled - it gets re-enabled once configure has finished.
	 */
	@Override
	protected void createButtonsForButtonBar(Composite parent) {
		okButton = createButton(parent, IDialogConstants.OK_ID, IDialogConstants.OK_LABEL, true);
		okButton.setEnabled(false);
	}
}
