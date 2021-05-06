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

import org.apache.commons.lang.ArrayUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;

/**
 * A zero-input, zero-output Scannable which when used in a scan will pause the scan if a given PV does not match one member of a given array of Strings.
 * <p>
 * E.g. this will pause a scan if a shutter PV is not "open".
 */
public class StringPVConditionMonitor extends PVConditionMonitorBase {

	private static final Logger logger = LoggerFactory.getLogger(StringPVConditionMonitor.class);

	String[] okStrings; // strings which mean beam is on target

	@Override
	protected void testShouldPause() throws DeviceException {
		if (!isConnected()) {
			logger.error("Epics channels not connected.");
		}

		if (!machineIsRunning()) {
			return;
		}

		while (!beamOnTarget()) {
			try {
				sendAndPrintMessage("Port shutter closed : pausing until it is opened");
				Thread.sleep(60000);
			} catch (InterruptedException e) {
				// someone trying to kill the thread so re-throw to kill any scan
				throw new DeviceException(e.getMessage(), e);
			}
		}

	}

	private boolean beamOnTarget() {
		try {
			String value = controller.cagetString(theChannel);
			return ArrayUtils.contains(okStrings, value);
		} catch (InterruptedException e) {
			// Reset interrupt status
			Thread.currentThread().interrupt();
			logger.info("Interrupted while checking beam on target", e);
			return true;
		} catch (Exception e) {
			logger.error(e.getMessage(), e);
			return true;
		}
	}

	public String[] getOkStrings() {
		return okStrings;
	}

	public void setOkStrings(String[] okStrings) {
		this.okStrings = okStrings;
	}

}
