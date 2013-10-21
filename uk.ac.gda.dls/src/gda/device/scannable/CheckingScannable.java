/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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
import gda.jython.InterfaceProvider;
import gda.jython.ScriptBase;
import gda.scan.ScanBase;

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
public class CheckingScannable extends ScannableBase implements Scannable {

	private static final Logger logger = LoggerFactory.getLogger(CheckingScannable.class);

	private double timeout = 0;
	private Object value;
	private Scannable scannable;

	private boolean pauseBeforeLine = false;
	private boolean pauseBeforePoint = true;

	public CheckingScannable() {
		this.inputNames = new String[0];
		this.extraNames = new String[0];
		this.outputFormat = new String[0];
		this.level = 1;
	}

	@Override
	public void atPointStart() throws DeviceException {
		if (pauseBeforePoint) {
			pauseUntilValue();
		}
	}

	@Override
	public void atScanLineStart() throws DeviceException {
		if (pauseBeforeLine) {
			pauseUntilValue();
		}
	}

	private void pauseUntilValue() throws DeviceException {

		Object curVal = getCurrentValue();

		// -1 or longer than tolerance - we allow the scan to happen without a pause.
		if (checkValue(curVal))
			return;

		try {
			// check top up soon
			Long start = new Date().getTime();

			boolean first = true;
			while (!checkValue(curVal)) {
				if (timeout > 0) {
					if ((new Date().getTime() - start) > (timeout * 1000)) {
						throw new DeviceException("timeout while waiting for " + scannable.getName());
					}
				}
				if (first) {
					InterfaceProvider.getTerminalPrinter().print(
							"The scan is paused and waiting for " + scannable.getName());
					first = false;
				}
				Thread.sleep(1000);
				curVal = getCurrentValue();
				ScanBase.checkForInterrupts();
				if (ScriptBase.isInterrupted()) {
					throw new InterruptedException("Script interrupt called inside " + getName());
				}
			}
		} catch (InterruptedException e) {
			// someone trying to kill the thread so re-throw to kill any scan
			logger.debug("InterruptedException received during pauseUntilValue, so rethrowing as DeviceException");
			throw new DeviceException(e.getMessage(), e);
		}
	}

	private boolean checkValue(Object curVal) {
		if (curVal instanceof Integer && value instanceof String) {
			value = Integer.parseInt((String) value);

		} else if (curVal instanceof Double && value instanceof String) {
			value = Double.parseDouble((String) value);

		} else if (curVal instanceof Short && value instanceof String) {
			value = Short.parseShort((String) value);

		}
		return curVal.equals(value);
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

	public double getTimeout() {
		return timeout;
	}

	/**
	 * @param timeout
	 *            The timeout to set. In seconds.
	 */
	public void setTimeout(double timeout) {
		this.timeout = timeout;
	}

	public boolean isPauseBeforeLine() {
		return pauseBeforeLine;
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
	 * If the monitor is topup: - topup is -1 for beam finished topup and is back up. - topup is 0 for topup happening -
	 * topup is >0 for time to next topup in seconds.
	 */
	private Object getCurrentValue() throws DeviceException {

		if (scannable == null) {
			throw new DeviceException("You must define the scannable to check.");
		}

		if (scannable != null) {
			Object pos = scannable.getPosition();
			return pos;
		}

		return null;
	}

	public Object getValue() {
		return value;
	}

	public void setValue(Object scannableTolerance) {
		this.value = scannableTolerance;
	}

	public Scannable getScannable() {
		return scannable;
	}

	public void setScannable(Scannable topupScannable) {
		this.scannable = topupScannable;
	}

}
