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
import gda.jython.InterfaceProvider;
import gda.scan.RedoScanLineThrowable;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Similar to BeamMonitor except that it throws a RedoScanLineThrowable to repeat the line instead of pausing the
 * scan.
 * <p>
 * ScanBase will look for RedoScanLineThrowables being thrown.
 * @see gda.scan.ScanBase#run()
 */
public class LineRepeatingBeamMonitor extends BeamMonitor {

	private static final Logger logger = LoggerFactory.getLogger(LineRepeatingBeamMonitor.class);

	public LineRepeatingBeamMonitor() {
		this.inputNames = new String[0];
		this.extraNames = new String[0];
		this.outputFormat = new String[0];
		this.level = 1;
	}

	/**
	 * protected so this method may be overridden
	 * 
	 * @throws DeviceException
	 */
	@Override
	protected void testShouldPause() throws DeviceException {
		if (!isConnected()) {
			logger.error(getNotConnectedMessage());
			return;
		}

		if (!machineIsRunning()) {
			// its a Tuesday or a shutdown
			return;
		}

		if (!machineHasCurrent()) {
			try {
				while (!machineHasCurrent()) {
					sendAndPrintMessage("Ring has no current : waiting...");
					Thread.sleep(60000);
				}
			} catch (InterruptedException e) {
				// someone trying to kill the thread so re-throw to kill any scan
				throw new DeviceException(e.getMessage(), e);
			}
			// throw a RedoScanLineThrowable once current has returned
			sendAndPrintMessage("Ring has no current : redo this line");
			throwRedoScanLineThrowable();
		}

		if (!portShuttersAllOpen()) {
			try {
				while (!portShuttersAllOpen()) {
					sendAndPrintMessage("Port shutter not open : waiting...");
					Thread.sleep(30000);
				}
			} catch (InterruptedException e) {
				// someone trying to kill the thread so re-throw to kill any scan
				throw new DeviceException(e.getMessage(), e);
			}
			// throw a RedoScanLineThrowable once current has returned
			sendAndPrintMessage("Port shutter not open : redo this line");
			throwRedoScanLineThrowable();
		}
	}

	private void throwRedoScanLineThrowable() throws RedoScanLineThrowable {
		InterfaceProvider.getTerminalPrinter().print("***Restarting line***");
		throw new RedoScanLineThrowable("No beam on sample");
	}

}
