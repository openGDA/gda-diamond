/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

import gda.device.DeviceException;
import gda.device.Monitor;
import gda.jython.InterfaceProvider;

import java.util.Date;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Scannable which will pause the scan if a machine top-up is imminent.
 * <p>
 * This must be given a Monitor object which returns the time in seconds until the next top-up, 0 if top-up in progress.
 * <p>
 * This replaces earlier classes which were not unit-testable.
 */
public class TopupChecker extends BeamlineConditionMonitorBase {

	private static final Logger logger = LoggerFactory.getLogger(TopupChecker.class);

	private double timeout = 30;
	private double tolerance = 0;
	private double waittime = 0;
	private double collectionTime = 0.0;// in seconds

	private Monitor scannableToBeMonitored;

	public TopupChecker() {
		this.inputNames = new String[0];
		this.extraNames = new String[0];
		this.outputFormat = new String[0];
		this.level = 1;
	}

	public Boolean topupImminent() throws DeviceException {
		double topupTime = getTopupTime();
		return topupTime >= 0 && topupTime < (collectionTime + tolerance);
	}

	/**
	 * protected so this method may be overridden
	 * 
	 * @throws DeviceException
	 */
	@Override
	protected void testShouldPause() throws DeviceException {

		if (!machineIsRunning()) {
			return;
		}

		if (!topupImminent())
			return;

		try {
			// check top up soon
			Long start = new Date().getTime();

			// If the monitor is topup:
			// topup is 0 for topup happening
			// topup is >0 for time to next top up in seconds.

			String message = "Pausing scan and waiting for " + getName() + "...";
			sendAndPrintMessage(message);
			while (topupImminent()) {

				if (InterfaceProvider.getCurrentScanController().isFinishEarlyRequested()) {
					return;
				}

				// check no timeout
				if ((new Date().getTime() - start) > (timeout * 1000)) {
					throw new DeviceException("timeout while waiting for top up to complete");
				}
				sendAndPrintMessage("Pausing scan and waiting for " + getName() + " to finish");
				Thread.sleep(1000);
			}

			if (waittime > 0) {
				message = getName() + ": pausing for " + waittime + "s to allow beam to stabilise...";
				sendAndPrintMessage(message);
				Thread.sleep(Double.valueOf(waittime).longValue() * 1000);
			}
			message = getName() + " now resuming scan.";
			sendAndPrintMessage(message);
		} catch (InterruptedException e) {
			// someone trying to kill the thread so re-throw to kill any scan
			logger.debug("InterruptedException received during testShouldPause, so rethrowing as DeviceException");
			throw new DeviceException(e.getMessage(), e);
		}
	}

	/**
	 * Meaning of return value: -1 for beam finished topup and is back up; 0 for topup happening; >0 for time to next
	 * topup in seconds.
	 */
	private double getTopupTime() throws DeviceException {

		if (scannableToBeMonitored == null) {
			throw new DeviceException("You must the topup scannable to be monitored");
		}

		Double topupTime = null;
		if (scannableToBeMonitored != null) {
			Object pos = scannableToBeMonitored.getPosition();
			if (pos instanceof Number) {
				topupTime = ((Number) pos).doubleValue();
			} else {
				logger.error("The scannable " + scannableToBeMonitored.getName()
						+ " does not have a numerical value! It cannot be checked with " + getClass().getName());
				return tolerance;
			}
		}

		if (topupTime == null)
			throw new DeviceException("Cannot determine value of " + getName());

		// If the monitor is topup:
		// topup is -1 for beam finished topup and is back up.
		// topup is 0 for topup happening
		// topup is >0 for time to next topup in seconds.
		return topupTime;

	}

	public double getTolerance() {
		return tolerance;
	}

	/**
	 * Sets the tolerance time in seconds. This is an extra 'fudge factor' to use on top of the data collection time to
	 * create the time before which the topup the scan will be paused. This tolerance time would be fixed for the
	 * beamline, whereas the collection time would vary for each scan.
	 * 
	 * @param scannableTolerance
	 */
	public void setTolerance(double scannableTolerance) {
		this.tolerance = scannableTolerance;
	}

	public Monitor getScannableToBeMonitored() {
		return scannableToBeMonitored;
	}

	public void setScannableToBeMonitored(Monitor scannableToBeMonitored) {
		this.scannableToBeMonitored = scannableToBeMonitored;
	}

	/**
	 * The data collection time to protect from topups using this scannable.
	 * 
	 * @param collectionTime
	 */
	public void setCollectionTime(double collectionTime) {
		this.collectionTime = collectionTime;
	}

	public double getCollectionTime() {
		return collectionTime;
	}

	/**
	 * @return the timeout in seconds to wait for the topup to finish
	 */
	public double getTimeout() {
		return timeout;
	}

	public void setTimeout(double timeout) {
		this.timeout = timeout;
	}

	/**
	 * @return the waittime after data collection can resume to allow beam to stabilise.
	 */
	public double getWaittime() {
		return waittime;
	}

	public void setWaittime(double waittime) {
		this.waittime = waittime;
	}

}
