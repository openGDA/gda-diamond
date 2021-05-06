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

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;

/**
 * A zero-input, zero-output Scannable which when used in a scan will pause the scan if the machine ring current drops
 * below 1mA.
 * <p>
 * It will resume the scan once the machine current returns.
 * <p>
 * This should be used with something else which checks for shutters etc. as the ring current returning should not be the
 * only check to confirm beam is on target.
 */
public class RingCurrentMonitor extends PVConditionMonitorBase {
	private static final Logger logger = LoggerFactory.getLogger(RingCurrentMonitor.class);

	private String ringCurrentPV = "SR21C-DI-DCCT-01:SIGNAL";

	@Override
	protected void testShouldPause() throws DeviceException {

		if (!isConnected()) {
			logger.error("Epics channels not connected.");
		}

		if (!machineIsRunning()) {
			return;
		}

		while (!machineHasCurrent()) {
			try {
				sendAndPrintMessage("Ring has no current : pausing until it has returned");
				Thread.sleep(60000);
			} catch (InterruptedException e) {
				// someone trying to kill the thread so re-throw to kill any scan
				throw new DeviceException(e.getMessage(), e);
			}
		}
	}

	protected boolean machineHasCurrent() {
		try {
			Double current = controller.cagetDouble(theChannel);
			return current > 1.0;
		} catch (InterruptedException e) {
			// Reset interrupt status
			Thread.currentThread().interrupt();
			logger.info("Interrupted while checking current", e);
			return true;
		} catch (Exception e) {
			logger.error(e.getMessage(), e);
			return true;
		}
	}

	public void setRingCurrentPV(String ringCurrentPV) {
		this.ringCurrentPV = ringCurrentPV;
	}

	public String getRingCurrentPV() {
		return ringCurrentPV;
	}
}
