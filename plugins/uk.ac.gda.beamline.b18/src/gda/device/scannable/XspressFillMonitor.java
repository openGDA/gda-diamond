/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

import java.text.DateFormat;
import java.text.DecimalFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

import javax.management.timer.Timer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;

public class XspressFillMonitor extends ScannableBase implements Scannable {

	private static final Logger logger = LoggerFactory.getLogger(XspressFillMonitor.class);

	private int waitTime = 600;

	private int startTimeHours = 9;

	private int startTimeMinutes = 15;

	private Date startPauseTime;
	private Date endPauseTime;

	/**
		 *
		 */
	public XspressFillMonitor() {
		this.inputNames = new String[0];
		this.extraNames = new String[0];
		this.outputFormat = new String[0];
		this.level = 1;
	}

	@Override
	public void atScanStart() throws DeviceException {
		try {
			pauseIfShould();
		} catch (Exception e) {
			throw new DeviceException(e.getMessage(),e);
		}
	}

	protected void pauseIfShould() throws Exception {

		Date now = new Date();

		boolean firstTime = true;
		while (shouldPause(now)){

			if (firstTime){
				logger.info("pausing data collection until " + endPauseTime.toString()+ " as the xspress Ge detector is being automatically refilled with LN");
				firstTime = false;
			}

			Thread.sleep(5000);
			now = new Date();
		}

		logger.info("resuming data collection");
	}

	protected boolean shouldPause(Date now) throws ParseException {

		if (endPauseTime == null || startPauseTime == null){
			calculatePauseTimes(now);
		}

		return endPauseTime.getTime() > now.getTime() && now.getTime() > startPauseTime.getTime();
	}

	protected void calculatePauseTimes(Date now) throws ParseException {
		DateFormat nowFormat = new SimpleDateFormat("yyyy-MM-dd");
		String today = nowFormat.format(now);

		DecimalFormat myFormatter = new DecimalFormat("##");
		String startTimeHoursString = myFormatter.format(startTimeHours);
		String startTimeMinutesString = myFormatter.format(startTimeMinutes);

		DateFormat startPauseFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm");
		startPauseTime = startPauseFormat.parse(today + " " + startTimeHoursString +":"+ startTimeMinutesString);
		endPauseTime = new Date(startPauseTime.getTime() + (Timer.ONE_SECOND * waitTime));
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

	public int getWaitTime() {
		return waitTime;
	}

	public void setWaitTime(int waitTime) {
		this.waitTime = waitTime;
	}

	public int getStartTimeHours() {
		return startTimeHours;
	}

	public void setStartTimeHours(int startTimeHours) {
		this.startTimeHours = startTimeHours;
	}

	public int getStartTimeMinutes() {
		return startTimeMinutes;
	}

	public void setStartTimeMinutes(int startTimeMinutes) {
		this.startTimeMinutes = startTimeMinutes;
	}

}