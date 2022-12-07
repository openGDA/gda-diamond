/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package gda.device.scannable;

import java.util.Date;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.MotorException;
import gda.epics.connection.EpicsChannelManager;
import gda.epics.connection.EpicsController;
import gda.epics.connection.InitializationListener;
import gda.factory.FactoryException;
import gda.jython.JythonServerFacade;
import gda.jython.JythonStatus;
import gov.aps.jca.CAException;
import gov.aps.jca.Channel;
import gov.aps.jca.TimeoutException;

/**
 * Stop/starts the feedback control at the start of every scan on the B18 energy controller in Epics.
 * <p>
 * This is B18 specific with hacks to work around issues with the mono geo-brick.
 */
public class B18EnergyScannable extends ScannableMotor implements InitializationListener {

	private static final Logger logger = LoggerFactory.getLogger(B18EnergyScannable.class);

	private EpicsController controller;
	private EpicsChannelManager channelManager;
	private String energySwitchPVName = "BL18B-OP-DCM-01:ENERGY_SWITCH";
	private String braggMSTAPVName = "BL18B-OP-DCM-01:XTAL1:BRAGG.MSTA";
	private String braggSTATPVName = "BL18B-OP-DCM-01:XTAL1:BRAGG.STAT";
	private String braggSEVRPVName = "BL18B-OP-DCM-01:XTAL1:BRAGG.SEVR";
	private Channel energySwitch;
	private Channel braggMSTA;
	private Channel braggSTAT;
	private Channel braggSEVR;

	private Object targetPosition = null;

	private volatile Date pointStart;
	private volatile boolean isBusyOverride = false;
	private volatile boolean watchDogDuringMove = false;
	private volatile long timeout = 400; // s
	private volatile boolean doingSecondAttempt = false;

	@Override
	public void configure() throws FactoryException {
		if (isConfigured()) {
			return;
		}
		super.configure();

		controller = EpicsController.getInstance();
		channelManager = new EpicsChannelManager(this);
		try {
			energySwitch = channelManager.createChannel(energySwitchPVName);
			braggMSTA = channelManager.createChannel(braggMSTAPVName);
			braggSTAT = channelManager.createChannel(braggSTATPVName);
			braggSEVR = channelManager.createChannel(braggSEVRPVName);
		} catch (CAException e) {
			throw new FactoryException(e.getMessage(), e);
		}
		setConfigured(true);
	}

	@Override
	public void atScanLineStart() throws DeviceException {
		super.atScanLineStart();

		switchEnergyControlOffOn();
	}

	@Override
	public void initializationCompleted() {
	}

	@Override
	public boolean isBusy() throws DeviceException {
		if (isBusyOverride) {
			return true;
		}

		// if we are in a scan and the last move watchdogged then throw an exception to stop the scan
		if (JythonServerFacade.getInstance().getScanStatus() == JythonStatus.RUNNING && watchDogDuringMove) {
			throw new DeviceException(
					"Watchdog occurred - Mono Geobrick will need to be manually restarted. Energy scans should not proceed");
		}
		// return the actual motor status
		return super.isBusy();
	}

	@Override
	public void rawAsynchronousMoveTo(Object internalPosition) throws DeviceException {
		targetPosition = internalPosition;
		isBusyOverride = false;
		watchDogDuringMove = false;
		doingSecondAttempt = false;
		startMoveMonitor();

		performMove(internalPosition);

	}

	/**
	 * Modified version of ScannableMotor.rawAsynchronousMoveTo()
	 *
	 * @param internalPosition
	 * @throws DeviceException
	 */
	private void performMove(Object internalPosition) throws DeviceException {
		Double internalDoublePosition;

		// check motor status. Throw an error if it is not idle. TODO: There is a race condition here
		if (!doingSecondAttempt && this.isBusy()) {
			throw new DeviceException("The motor " + getName() + " was already busy so could not be moved");
		}

		try {
			internalDoublePosition = PositionConvertorFunctions.toDouble(internalPosition);
			this.getMotor().moveTo(internalDoublePosition);
			notifyIObservers(this, ScannableStatus.BUSY);
		} catch (IllegalArgumentException e) {
			throw new DeviceException(getName() + ".rawAsynchronousMoveTo() could not convert "
					+ internalPosition.toString() + " to a double.");
		} catch (MotorException e) {
			throw new DeviceException(e.getMessage(), e);
		}
	}

	private void secondMoveAttempt() throws DeviceException {
		doingSecondAttempt = true;
		startMoveMonitor();
		performMove(targetPosition);
	}

	private void startMoveMonitor() {

		pointStart = new Date();

		// start a thread to look at the isBusy status
		Thread thread = new Thread(() -> {
				try {
					// give the move a chance to start
					Thread.sleep(500);

					// loop until move complete or a timeout
					Date now = new Date();
					long diffInS = (now.getTime() - pointStart.getTime()) / 1000;
					while (isBusy() && diffInS < timeout) {
						Thread.sleep(100);
						now = new Date();
						diffInS = (now.getTime() - pointStart.getTime()) / 1000;
					}

					// OK if move finished
					if (!isBusy()) {
						return;
					}

					// if a timeout then keep isBusy returning true until issue resolved
					if (diffInS >= timeout) {
						isBusyOverride = true;
						try {
							handleTimeout();
						} catch (Exception e) {
							logger.error("exception after a timeout of a move of " + getName(), e);
						} finally {
							if (!doingSecondAttempt) {
								isBusyOverride = false;
							}
						}
					}

				} catch (DeviceException e) {
					logger.error("exception in timeout loop of " + getName() + ". Leaving loop.", e);
				} catch (InterruptedException e) {
					logger.error("InterruptedException in timeout loop of " + getName() + ". Leaving loop.", e);
				}
		}, getName() + "_timeout_thread");
		thread.setDaemon(true);
		thread.start();
	}

	private String[] getBraggPVs() throws TimeoutException, CAException, InterruptedException {
		String[] values = new String[3];
		values[0] = controller.cagetString(braggMSTA);
		values[1] = controller.cagetString(braggSTAT);
		values[2] = controller.cagetString(braggSEVR);
		return values;
	}

	private boolean hasWatchDogged() throws TimeoutException, CAException, InterruptedException {
		String[] braggValues = getBraggPVs();
		return braggValues[1].equals("COMM") && braggValues[2].equals("INVALID");
	}

	private void switchEnergyControlOffOn() throws DeviceException {
		try {
			int startValue = controller.cagetInt(energySwitch);

			if (startValue == 1) {
				logger.info("Resetting the mono feedback control. This will take about 10s...");
				controller.caputWait(energySwitch, 0); // off
				controller.caputWait(energySwitch, 1); // on
			}

		} catch (TimeoutException e) {
			throw new DeviceException(e.getMessage(), e);
		} catch (CAException e) {
			throw new DeviceException(e.getMessage(), e);
		} catch (InterruptedException e) {
			throw new DeviceException(e.getMessage(), e);
		}
	}

	private void handleTimeout() throws Exception {

		if (hasWatchDogged()) {
			String[] braggValues = getBraggPVs();
			logger.info("Bragg MSTA after watchdog: " + braggValues[0]);
			logger.info("Bragg STAT after watchdog: " + braggValues[1]);
			logger.info("Bragg SEVR after watchdog: " + braggValues[2]);
			watchDogDuringMove = true;
			return;
		}

		logger.info("Timeout while waiting for mono move to complete.");
		switchEnergyControlOffOn();

		// try move again
		if (!doingSecondAttempt){
			logger.info("Reset complete do trying move again to: " + targetPosition.toString());
			secondMoveAttempt();
		} else {
			doingSecondAttempt = false;
		}
	}

}
