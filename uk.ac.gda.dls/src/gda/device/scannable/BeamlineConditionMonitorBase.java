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

import org.apache.commons.lang.ArrayUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A base class for zero-input, zero-output scannables whose job is to automatically pause a scan if some condition is
 * met (say port shutter closed due to a beam dump) and resume when that condition has passed.
 * <p>
 * This provides such scannables with a way to ignore that condition when the machine is not running e.g. on machine
 * development days (Tuesdays) or shutdowns. So these scannables may be always added to the list of default scannables
 * and used in every scan.
 */
public abstract class BeamlineConditionMonitorBase extends ScannableBase {
	
	private static final Logger logger = LoggerFactory.getLogger(BeamlineConditionMonitorBase.class);

	private Monitor machineModeMonitor;
	private String[] modesToIgnore = new String[] { "Mach. Dev.", "Shutdown" };
	
	private boolean pauseBeforeScan = false;
	private boolean pauseBeforeLine = false;
	private boolean pauseBeforePoint = true;

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
	 * The test is performed inside this method. An inheriting class could either wait inside this method until the
	 * condition has passed, or throw an Exception to end the scan, or throw a RedoScanLineThrowable to repeat the
	 * current scan.
	 * @throws DeviceException 
	 * 
	 * @see gda.scan.ConcurrentScan
	 */
	protected abstract void testShouldPause() throws DeviceException;

	/**
	 * Returns false if not in a real running mode.
	 * 
	 * @return true if user mode, so this object should operate.
	 * @throws DeviceException
	 */
	protected boolean machineIsRunning() throws DeviceException {

		if (machineModeMonitor == null) {
			return true;
		}

		try {
			String value = machineModeMonitor.getPosition().toString();
			return !ArrayUtils.contains(modesToIgnore, value);
		} catch (DeviceException e) {
			throw new DeviceException(e.getMessage(), e);
		}

	}
	
	protected void sendAndPrintMessage(String message) {
		logger.info(message);
		InterfaceProvider.getTerminalPrinter().print(message);
	}

	public Monitor getMachineModeMonitor() {
		return machineModeMonitor;
	}

	public void setMachineModeMonitor(Monitor machineModeMonitor) {
		this.machineModeMonitor = machineModeMonitor;
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
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

}
