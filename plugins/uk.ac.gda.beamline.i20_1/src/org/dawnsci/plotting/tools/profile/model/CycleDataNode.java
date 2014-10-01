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

package org.dawnsci.plotting.tools.profile.model;

import java.util.List;

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

public class CycleDataNode {
	private final IObservableList timingGroups;
	private final String name;

	public CycleDataNode(String number, List<TimingGroupDataNode> timingGroupList) {
		name = "Cycle " + number;
		timingGroups = new WritableList(timingGroupList, TimingGroupDataNode.class);
	}

	public double getCycleTime() {
		double cycleTime = 0.0;
		for (Object obj : timingGroups) {
			TimingGroupDataNode timingGroup = (TimingGroupDataNode) obj;
			cycleTime += timingGroup.getTimePerSpectrum() * timingGroup.getSpectra().size();
		}
		return cycleTime;
	}

	public IObservableList getTimingGroups() {
		return timingGroups;
	}

	public void clearData() {
		timingGroups.clear();
	}

	@Override
	public String toString() {
		return name;
	}
}
