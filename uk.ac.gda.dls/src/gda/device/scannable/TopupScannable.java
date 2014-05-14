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

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.epics.CAClient;
import gda.jython.JythonServerFacade;

import java.util.Date;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A scannable which will pause during a scan if top-up is imminent.
 * <p>
 * To use, simply include in a scan.
 * <p>
 * Deprecated, see TopupChecker.
 * <p>
 * This should be deleted for the GDA release after 8.36
 */
@Deprecated
public class TopupScannable extends ScannableBase implements Scannable {

	private static final Logger logger = LoggerFactory.getLogger(TopupScannable.class);

	private double timeout = 30;
	private double tolerance = 0;
	private double waittime = 0;
	private double collectionTime = 0.0;// in seconds
	private String topupPV = null;
	private boolean pauseBeforeScan = false;
	private boolean pauseBeforeLine = false;
	private boolean pauseBeforePoint = true;
	private Scannable scannableToBeMonitored;

	public TopupScannable() {
		this.inputNames = new String[0];
		this.extraNames = new String[0];
		this.outputFormat = new String[0];
		this.level = 1;
	}

	@Override
	public void atScanStart() throws DeviceException {
		if (pauseBeforeScan) {
			testShouldPause();
		}
	}

	@Override
	public void atPointStart() throws DeviceException {
		if (pauseBeforePoint) {
			testShouldPause();
		}
	}

	@Override
	public void atScanLineStart() throws DeviceException {
		if (pauseBeforeLine) {
			testShouldPause();
		}
	}

	/**
	 * protected so this method may be overridden
	 * 
	 * @throws DeviceException
	 */
	protected void testShouldPause() throws DeviceException {

		double topupTime = getTopupTime();

		// -1 or longer than tolerance - we allow the scan to happen without a pause.
		if (topupTime < 0 || topupTime > (collectionTime + tolerance))
			return;

		try {
			// check top up soon
			Long start = new Date().getTime();

			// If the monitor is topup:
			// topup is -1 for beam finished topup and is back up.
			// topup is 0 for topup happening
			// topup is >0 for time to next topup in seconds.

			String message = "Pausing scan and waiting for " + getName() + "...";
			sendAndPrintMessage(message);
			while (topupTime > -1 && topupTime < (collectionTime + tolerance)) { // We are inside the tolerance and
																					// should pause

				// check no timeout
				if ((new Date().getTime() - start) > (timeout * 1000)) {
					throw new DeviceException("timeout while waiting for top up to complete");
				}
				sendAndPrintMessage("Pausing scan and waiting for " + getName() + " to finish");
				Thread.sleep(1000);
				topupTime = getTopupTime();

			}

			if (waittime > 0) {
				message = getName() + ": pausing for " + waittime + "s to allow beam to stabilise...";
				sendAndPrintMessage(message);
				Thread.sleep(new Double(waittime).longValue() * 1000);
			}
			message = getName() + " now resuming scan.";
			sendAndPrintMessage(message);
		} catch (InterruptedException e) {
			// someone trying to kill the thread so re-throw to kill any scan
			logger.debug("InterruptedException received during testShouldPause, so rethrowing as DeviceException");
			throw new DeviceException(e.getMessage(), e);
		}
	}

	protected void sendAndPrintMessage(String message) {
		logger.info(message);
		JythonServerFacade.getInstance().print(message);
	}

	@Override
	public void asynchronousMoveTo(Object position) throws DeviceException {
		//
	}

	@Override
	public Object getPosition() throws DeviceException {
		return null;
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	@Override
	public String checkPositionValid(Object position) {
		return "";
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

	public String getTopupPV() {
		return topupPV;
	}

	public void setTopupPV(String topupPV) {
		this.topupPV = topupPV;
	}

	public boolean isPauseBeforeLine() {
		return pauseBeforeLine;
	}

	public boolean isPauseBeforeScan() {
		return pauseBeforeScan;
	}

	public void setPauseBeforeScan(boolean pauseBeforeScan) {
		this.pauseBeforeScan = pauseBeforeScan;
	}

	public void setPauseBeforeLine(boolean pauseBeforeLine) {
		this.pauseBeforeLine = pauseBeforeLine;
	}

	public boolean isPauseBeforePoint() {
		return pauseBeforePoint;
	}

	public void setPauseBeforePoint(boolean pauseBeforePoint) {
		this.pauseBeforePoint = pauseBeforePoint;
	}

	/**
	 * Meaning of return value: -1 for beam finished topup and is back up; 0 for topup happening; >0 for time to next
	 * topup in seconds.
	 */
	private double getTopupTime() throws DeviceException {

		if (topupPV == null && scannableToBeMonitored == null) {
			throw new DeviceException("You must define one of topupPv and topupScannable");
		}

		Double topupTime = null;
		if (topupPV != null) {
			try {
				CAClient ca = new CAClient();
				String value = ca.caget(topupPV);
				topupTime = new Double(value);
			} catch (Exception e) {
				logger.error("Cannot read pv " + topupPV, e);
				return tolerance; // so this scannable will always allow the scan in the event of Epics problem
			}
		} else if (scannableToBeMonitored != null) {
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

	public Scannable getScannableToBeMonitored() {
		return scannableToBeMonitored;
	}

	public void setScannableToBeMonitored(Scannable scannableToBeMonitored) {
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

}
