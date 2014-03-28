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

package org.dawnsci.plotting.tools.profile;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.dataset.IntegerDataset;

public class TimeResolvedDataNode {

	private final IObservableList cycles = new WritableList(new ArrayList<CycleDataNode>(), CycleDataNode.class);

	public static final int NUMBER_OF_STRIPS = 1024;

	public IObservableList getCycles() {
		return cycles;
	}

	public void clearData() {
		for (Object obj : cycles) {
			((CycleDataNode) obj).getTimingGroups().clear();
		}
		cycles.clear();
	}

	// TODO Refactor this! This has hard coded index numbers!
	public void setData(DoubleDataset timingGroupsDataset, DoubleDataset timeDataset, IntegerDataset cycleDataset) {
		double[] timingGroupsData = ((DoubleDataset) timingGroupsDataset.getSlice(new int[]{0,0}, new int[]{timingGroupsDataset.getShape()[0],3}, new int[]{1,3})).getData();
		double[] timePerFrame = ((DoubleDataset) timingGroupsDataset.getSlice(new int[]{0,1}, new int[]{timingGroupsDataset.getShape()[0],3}, new int[]{1,3})).getData();
		double[] time = timeDataset.getData();
		if (timingGroupsData.length > 0) {

			int[] cycle;
			if (cycleDataset == null) {
				cycle = new int[timingGroupsData.length];
			} else {
				cycle = cycleDataset.getData();
			}

			int groupCounter = 0;
			int cycleCounter = 0;
			List<SpectrumDataNode> spectraList = new ArrayList<SpectrumDataNode>();
			List<TimingGroupDataNode> timingGroupList = new ArrayList<TimingGroupDataNode>();
			for (int i = 0; i < timingGroupsData.length; i++) {
				if (timingGroupsData[i] > groupCounter) {
					double lastFrameDuration = timePerFrame[i - 1];
					timingGroupList.add(new TimingGroupDataNode(Integer.toString(groupCounter), lastFrameDuration, spectraList));
					groupCounter = (int) timingGroupsData[i];
					spectraList = new ArrayList<SpectrumDataNode>();
				}
				if (cycle[i] > cycleCounter) {
					double lastFrameDuration = timePerFrame[timePerFrame.length - 1];
					timingGroupList.add(new TimingGroupDataNode(Integer.toString(groupCounter), lastFrameDuration, spectraList));
					cycles.add(new CycleDataNode(Integer.toString(cycleCounter), timingGroupList));
					cycleCounter = cycle[i];
					timingGroupList = new ArrayList<TimingGroupDataNode>();
					spectraList = new ArrayList<SpectrumDataNode>();
					groupCounter = 0;
				}
				spectraList.add(new SpectrumDataNode(i, time[i]));
			}
			double lastFrameDuration = timePerFrame[timePerFrame.length - 1];
			timingGroupList.add(new TimingGroupDataNode(Integer.toString(groupCounter), lastFrameDuration, spectraList));
			cycles.add(new CycleDataNode(Integer.toString(cycleCounter), timingGroupList));
		}
	}
}
