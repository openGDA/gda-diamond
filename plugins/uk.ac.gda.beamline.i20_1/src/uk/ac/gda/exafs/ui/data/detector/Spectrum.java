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

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.observable.list.WritableList;

import uk.ac.gda.beamline.i20_1.utils.TimebarHelper;

public class Spectrum extends CollectionModel {
	private static final long MIN_SPECTRUM_TIME = 20;
	private final Group parent;

	WritableList accumulationList = new WritableList(new ArrayList<Accumulation>(), Accumulation.class);
	public List<?> getAccumulationList() {
		return accumulationList;
	}

	public Spectrum(Group parent) {
		this.parent = parent;
	}

	@Override
	public void setStartTime(double startTime) {
		super.setStartTime(startTime);
		long startTimeInMilli = (long) startTime + (long) this.getDelay();
		this.setBegin(TimebarHelper.getTime().advanceMillis(startTimeInMilli));
		this.setEnd(this.getBegin().copy().advanceMillis(MIN_SPECTRUM_TIME));
	}

	@Override
	public void setDelay(double delay) {
		super.setDelay(delay);
		long delayInMilli = (long) delay;
		long startTimeInMilli = (long) this.getStartTime() + delayInMilli;
		this.setBegin(TimebarHelper.getTime().advanceMillis(startTimeInMilli));
	}

	@Override
	public void setDuration(double duration) {
		super.setDuration(duration);
		long gurationInMilli = (long) duration;
		long endTimeInMilli = (long) this.getStartTime() + (long) this.getDelay() + gurationInMilli;
		this.setEnd(TimebarHelper.getTime().advanceMillis(endTimeInMilli));
	}

	public Group getParent() {
		return parent;
	}

	@Override
	public void dispose() {
		//
	}
}
