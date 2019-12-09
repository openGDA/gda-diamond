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

package uk.ac.gda.exafs.experiment.ui.data;

import org.dawnsci.ede.DataHelper;

import com.google.gson.annotations.Expose;

import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;

public abstract class TimeIntervalDataModel extends ObservableModel { // extends IntervalImpl {

	protected static final double MIN_DURATION_TIME = 20;
	protected static final double INITIAL_START_TIME = 0.0;

	public static final String NAME_PROP_NAME = "name";
	@Expose
	private String name;

	public static final String START_TIME_PROP_NAME = "startTime";
	@Expose
	private double startTime;

	public static final String AVAILABLE_TIME_PROP_NAME = "availableTime";

	public static final String DELAY_PROP_NAME = "delay";
	@Expose
	protected double delay;

	public static final String DURATION_PROP_NAME = "duration";

	public static final String END_TIME_PROP_NAME = "endTime";

	@Expose
	private double endTime;

	public double getStartTime() {
		return startTime;
	}

	public void setTimes(double startTime, double eventDuration) {
		this.firePropertyChange(START_TIME_PROP_NAME, this.startTime, this.startTime = startTime);
		updateEndTimeAndInterval(eventDuration);
	}

	private void updateEndTimeAndInterval(double eventDuration) {
		this.firePropertyChange(END_TIME_PROP_NAME,  endTime, endTime = getIntervalStartTime() + eventDuration);
		this.firePropertyChange(DURATION_PROP_NAME, null, this.getDuration());
	}

	public String getName() {
		return name;
	}

	protected double getIntervalStartTime() {
		return startTime + delay;
	}

	public void setName(String name) {
		this.firePropertyChange(NAME_PROP_NAME, this.name, this.name = name);
	}

	public double getDelay() {
		return delay;
	}

	public void setDelay(double delay) {
		this.firePropertyChange(DELAY_PROP_NAME, this.delay, this.delay = delay);
		updateEndTimeAndInterval(this.getAvailableDurationAfterDelay());
	}

	public double getDuration() {
		return endTime - startTime;
	}

	protected double getAvailableDurationAfterDelay() {
		return endTime - startTime + delay;
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
