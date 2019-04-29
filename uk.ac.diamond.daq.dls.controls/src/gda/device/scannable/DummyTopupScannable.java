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

import java.util.Timer;
import java.util.TimerTask;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Monitor;
import gda.factory.FactoryException;
import uk.ac.gda.api.remoting.ServiceInterface;

/**
 * Provides a simulation for the time until topup PV from the machine.
 */
@ServiceInterface(Monitor.class)
public class DummyTopupScannable extends ScannableBase implements Monitor {
	private static final Logger logger = LoggerFactory.getLogger(DummyTopupScannable.class);
	private double topupInterval = 600.0; // overall topup cycle including fill time
	private double fillTime = 15.0; // the time of the topup fill itself
	private double topupCount = topupInterval - fillTime; // count down to the start of the next fill
	private Timer topupTimer;
	private String unit = "";
	private int elementCount = 1;

	public DummyTopupScannable() {
		topupTimer = new Timer();
		topupTimer.schedule(new CountDownTask(), 100, 100);
	}

	@Override
	public void configure() throws FactoryException {
		super.configure();

		this.setInputNames(new String[0]);
		this.setExtraNames(new String[] { getName() });
	}

	@Override
	public Object getPosition() throws DeviceException {
		return topupCount;
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	public void setTopupInterval(double topupInterval) {
		this.topupInterval = topupInterval;
		this.topupCount = topupInterval - fillTime;
	}

	public void setFillTime(double fillTime) {
		this.fillTime = fillTime;
		this.topupCount = topupInterval - fillTime;
	}

	private class CountDownTask extends TimerTask {
		@Override
		public void run() {
			topupCount = topupCount - 0.1;
			notifyIObservers(DummyTopupScannable.this, topupCount);
			if (topupCount <= 0.0) {
				topupCount = 0.0;
				try {
					long fillTimeMs = (long) (fillTime * 1000);
					Thread.sleep(fillTimeMs);
				} catch (InterruptedException e) {
					logger.error("Error sleeping for " + fillTime + " seconds", e);
				}
				topupCount = topupInterval - fillTime;
			}
			// logger.info("the topup time is " + topupCount);
		}
	}

	@Override
	public String getUnit() {
		return unit;
	}

	public void setUnit(String unit) {
		this.unit = unit;
	}

	@Override
	public int getElementCount() {
		return elementCount;
	}

	public void setElementCount(int elementCount) {
		this.elementCount = elementCount;
	}

	@Override
	public String toFormattedString() {
		try {
			return String.format("%s %s", ScannableUtils.getFormattedCurrentPosition(this), unit);
		} catch (DeviceException e) {
			return valueUnavailableString();
		}
	}

}
