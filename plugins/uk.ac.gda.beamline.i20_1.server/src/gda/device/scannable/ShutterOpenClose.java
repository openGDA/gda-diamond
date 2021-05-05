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

package gda.device.scannable;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.enumpositioner.ValvePosition;
import gda.factory.FactoryException;

/**
 * Scannable that simply open a shutter at the start of a scan and closes it at the end.
 * Shutter is also closed if scan finishes early for some reason.
 *
 */
public class ShutterOpenClose extends ScannableBase {
	private static final Logger logger = LoggerFactory.getLogger(ShutterOpenClose.class);

	/** Shutter to be controlled during the scan */
	private EnumPositioner shutter;

	private long sleepTimeMs = 0;

	public ShutterOpenClose() {
		inputNames = new String[] {};
		extraNames = new String[] {};
		outputFormat = new String[] {};
	}

	@Override
	public void configure() throws FactoryException {
		if (isConfigured()) {
			return;
		}
		if (shutter == null) {
			throw new FactoryException("Shutter has not been set");
		}
		super.configure();
		setConfigured(true);
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		return null;
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		// do nothing
	}

	@Override
	public void atScanStart() throws DeviceException {
		moveShutter(ValvePosition.RESET);
		moveShutter(ValvePosition.OPEN);
	}

	@Override
	public void atScanEnd() throws DeviceException {
		moveShutter(ValvePosition.RESET);
		moveShutter(ValvePosition.CLOSE);
	}

	private void moveShutter(String position) throws DeviceException {
		logger.debug("{} moving to '{}'", shutter.getName(), position);
		shutter.moveTo(position);
		if (sleepTimeMs > 0) {
			try {
				Thread.sleep(sleepTimeMs);
			} catch (InterruptedException e) {
				// Reset interrupt status
				Thread.currentThread().interrupt();
				logger.warn("Sleep interrupted when moving shutter", e);
			}
		}
		logger.debug("{} move to '{}' complete", shutter.getName(), position);
	}

	@Override
	public void atCommandFailure() throws DeviceException {
		atScanEnd();
	}

	@Override
	public void stop() throws DeviceException {
		atScanEnd();
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return shutter.isBusy();
	}

	public EnumPositioner getShutter() {
		return shutter;
	}

	public void setShutter(EnumPositioner shutter) {
		this.shutter = shutter;
	}

	public long getSleepTimeMs() {
		return sleepTimeMs;
	}

	/**
	 * Additional time to wait after moving shutter.
	 * @param sleepTimeMs
	 */
	public void setSleepTimeMs(long sleepTimeMs) {
		this.sleepTimeMs = sleepTimeMs;
	}
}
