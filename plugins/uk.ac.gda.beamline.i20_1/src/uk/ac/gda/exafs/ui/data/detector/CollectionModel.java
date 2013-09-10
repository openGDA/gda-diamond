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

package uk.ac.gda.exafs.ui.data.detector;

import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import de.jaret.util.date.IntervalImpl;

public abstract class CollectionModel extends IntervalImpl {

	public static final String NAME_PROP_NAME = "name";
	private String name;

	public static final String START_TIME_PROP_NAME = "startTime";
	private double startTime;

	public static final String DELAY_PROP_NAME = "delay";
	private double delay;

	public static final String DURATION_PROP_NAME = "duration";
	private double duration;

	public static final String END_TIME_PROP_NAME = "endTime";

	public double getStartTime() {
		return startTime;
	}
	public void setStartTime(double startTime) {
		double previous = startTime + delay;
		this.firePropertyChange(START_TIME_PROP_NAME, this.startTime, this.startTime = startTime);
		this.firePropertyChange(END_TIME_PROP_NAME, previous, getEndTime());
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
		double previous = startTime + delay;
		this.firePropertyChange(DELAY_PROP_NAME, this.delay, this.delay = delay);
		this.firePropertyChange(END_TIME_PROP_NAME, previous, getEndTime());
	}
	public double getDuration() {
		return duration;
	}
	public void setDuration(double duration) {
		this.firePropertyChange(DURATION_PROP_NAME, this.duration, this.duration = duration);
	}
	public double getEndTime() {
		return startTime + duration;
	}

	@Override
	public String toString() {
		return this.getName() + " " + DataHelper.roundDoubletoString(getDuration()) + " " + UnitSetup.MILLI_SEC.getText();
	}

	public abstract void dispose();
}
