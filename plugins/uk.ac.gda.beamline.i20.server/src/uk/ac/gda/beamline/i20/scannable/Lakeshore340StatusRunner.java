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

package uk.ac.gda.beamline.i20.scannable;

import java.util.Date;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;

public class Lakeshore340StatusRunner implements Runnable {
	private static final int updatePeriodinMilliSec = 1000;
	private static final Logger logger = LoggerFactory.getLogger(Lakeshore340StatusRunner.class);
	protected volatile boolean keepRunning = true;
	private volatile boolean stableTemperature = false;
	private final Lakeshore340Scannable lakeshore;
	private Date timeOfLastDeadbandChange = null;
	private boolean inDeadbandAfterLastDeadbandChange = false;

	protected Lakeshore340StatusRunner(Lakeshore340Scannable lakeshore) {
		this.lakeshore = lakeshore;
	}

	@Override
	public void run() {
		keepRunning = true;
		try {
			while (keepRunning) {
				boolean inDeadband = lakeshore.withinDeadband();
				if (timeOfLastDeadbandChange == null)
					updateLatestValues(inDeadband);
				// has changed?
				if (inDeadband != inDeadbandAfterLastDeadbandChange)
					updateLatestValues(inDeadband);
				else if (inDeadband) {
					long timeSinceChange = new Date().getTime() - timeOfLastDeadbandChange.getTime();
					int secsSinceChange = Math.round(timeSinceChange / 1000);
					if (secsSinceChange > lakeshore.getWaitTime()){
						lakeshore.setMoving(false);
						setStableTemperature(true);
					}
					else
						setStableTemperature(false);
				}
				else
					setStableTemperature(false);
				Thread.sleep(updatePeriodinMilliSec);
			}
		} catch (DeviceException e) {
			logger.error("DeviceException in loop reading out temperature of " + lakeshore.getName() + ". Loop will be aborted.", e);
		} catch (InterruptedException e) {
			logger.error("InterruptedException in loop reading out temperature of " + lakeshore.getName() + ". Loop will be aborted.", e);
		}
		keepRunning = false;
	}

	private void updateLatestValues(boolean inDeadband) {
		timeOfLastDeadbandChange = new Date();
		inDeadbandAfterLastDeadbandChange = inDeadband;
		// if we are updating, then something has changed, so the temperature cannot be stable
		setStableTemperature(false);
	}

	public boolean isStableTemperature() {
		return stableTemperature;
	}

	private void setStableTemperature(boolean stableTemperature) {
		this.stableTemperature = stableTemperature;
	}

}