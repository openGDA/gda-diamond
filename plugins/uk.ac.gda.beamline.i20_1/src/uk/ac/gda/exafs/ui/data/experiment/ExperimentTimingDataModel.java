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

package uk.ac.gda.exafs.ui.data.experiment;

import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.beamline.i20_1.utils.TimebarHelper;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;

import com.google.gson.annotations.Expose;

import de.jaret.util.date.IntervalImpl;

public abstract class ExperimentTimingDataModel extends IntervalImpl {

	private static final long MIN_DURATION_TIME = 20;
	public static final String NAME_PROP_NAME = "name";
	@Expose
	private String name;

	public static final String START_TIME_PROP_NAME = "startTime";
	@Expose
	private double startTime;

	public static final String DELAY_PROP_NAME = "delay";
	@Expose
	private double delay;

	public static final String DURATION_PROP_NAME = "duration";

	public static final String END_TIME_PROP_NAME = "endTime";
	@Expose
	private double endTime;

	public double getStartTime() {
		return startTime;
	}

	protected void setStartTime(double startTime) {
		long startTimeInMilli = (long) startTime + (long) this.getDelay();
		this.setBegin(TimebarHelper.getTime().advanceMillis(startTimeInMilli));
		this.firePropertyChange(START_TIME_PROP_NAME, this.startTime, this.startTime = startTime);
		double duration = this.getDuration();
		if (duration == 0) {
			setEndTime(this.getStartTime() + MIN_DURATION_TIME);
		} else {
			this.firePropertyChange(DURATION_PROP_NAME, duration,  this.getDuration());
		}
	}

	protected void setEndTime(double value) {
		long endTimeInMilli = (long) value;
		this.setEnd(TimebarHelper.getTime().advanceMillis(endTimeInMilli));
		double previous = this.getDuration();
		this.firePropertyChange(END_TIME_PROP_NAME,  endTime, endTime =  value);
		this.firePropertyChange(DURATION_PROP_NAME, previous,  this.getDuration());
	}

	public void setTimes(double startTime, double endTime) {
		long startTimeInMilli = (long) startTime + (long) this.getDelay();
		this.setBegin(TimebarHelper.getTime().advanceMillis(startTimeInMilli));
		this.firePropertyChange(START_TIME_PROP_NAME, this.startTime, this.startTime = startTime);
		this.setEnd(TimebarHelper.getTime().advanceMillis((long) endTime));
		double previous = this.getDuration();
		this.firePropertyChange(END_TIME_PROP_NAME,  this.endTime, this.endTime =  endTime);
		this.firePropertyChange(DURATION_PROP_NAME, previous,  this.getDuration());
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.firePropertyChange(NAME_PROP_NAME, this.name, this.name = name);
	}

	public double getDelay() {
		return delay;
	}

	public void setDelay(double delay) {
		long delayInMilli = (long) delay;
		long startTimeInMilli = (long) this.getStartTime() + delayInMilli;
		this.setBegin(TimebarHelper.getTime().advanceMillis(startTimeInMilli));
		this.firePropertyChange(DELAY_PROP_NAME, this.delay, this.delay = delay);
	}

	public double getDuration() {
		return endTime - startTime;
	}


	public double getEndTime() {
		return endTime;
	}

	@Override
	public String toString() {
		return this.getName() + "\nEnd: " + DataHelper.roundDoubletoString(getEndTime()) + " " + UnitSetup.MILLI_SEC.getText() +
				"\nDuration: " + DataHelper.roundDoubletoString(getDuration()) + " " + UnitSetup.MILLI_SEC.getText();
	}

	public abstract void dispose();
}
