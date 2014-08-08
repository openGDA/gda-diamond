/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

import java.util.Timer;
import java.util.TimerTask;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Provides a simulation for the time until topup PV from the machine.
 */
public class DummyTopupScannable extends ScannableBase implements Scannable {
	private static final Logger logger = LoggerFactory.getLogger(DummyTopupScannable.class);
	private double topupInterval = 600.0;
	private double topupCount = topupInterval;
	private Timer topupTimer;

	public DummyTopupScannable() {
		topupTimer = new Timer();
		topupTimer.schedule(new CountDownTask(), 100, 100);
	}

	@Override
	public Object getPosition() throws DeviceException {
		return topupCount;
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	class CountDownTask extends TimerTask {
		@Override
		public void run() {
			topupCount = topupCount - 0.1;
			if (topupCount <= 0.0) {
				topupCount = 0.0;
				try {
					Thread.sleep(2000);
				} catch (InterruptedException e) {
					logger.error("Error sleeping for 2 seconds", e);
				}
				topupCount = topupInterval;
			}
			// logger.info("the topup time is " + topupCount);
		}
	}
}
