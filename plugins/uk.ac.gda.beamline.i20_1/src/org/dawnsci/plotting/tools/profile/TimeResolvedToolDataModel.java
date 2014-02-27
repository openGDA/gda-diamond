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

public class TimeResolvedToolDataModel {

	private final IObservableList timingGroups = new WritableList(new ArrayList<TimingGroupToolDataModel>(), TimingGroupToolDataModel.class);

	public static final int NUMBER_OF_STRIPS = 1024;

	private int totalSpectra;

	public void setData(DoubleDataset timingGroupsDataset, DoubleDataset timeDataset) {
		// TODO Refactor this! This has hard coded index numbers!
		double[] timingGroupsData = ((DoubleDataset)timingGroupsDataset.getSlice(new int[]{0,0}, new int[]{timingGroupsDataset.getShape()[0],3}, new int[]{1,3})).getData();
		double[] timePerFrame = ((DoubleDataset) timingGroupsDataset.getSlice(new int[]{0,1}, new int[]{timingGroupsDataset.getShape()[0],3}, new int[]{1,3})).getData();
		totalSpectra = timingGroupsData.length;
		double[] time = timeDataset.getData();
		if (timingGroupsData.length > 0) {
			int groupCounter = 0;
			List<SpectrumToolDataModel> spectraList = new ArrayList<SpectrumToolDataModel>();
			for (int i = 0; i < timingGroupsData.length; i++) {
				if (timingGroupsData[i] > groupCounter) {
					double lastFrameDuration = timePerFrame[i - 1];
					timingGroups.add(new TimingGroupToolDataModel(Integer.toString(groupCounter), lastFrameDuration, spectraList));
					groupCounter = (int) timingGroupsData[i];
					spectraList = new ArrayList<SpectrumToolDataModel>();
				}
				spectraList.add(new SpectrumToolDataModel(i, time[i]));
			}
			double lastFrameDuration =timePerFrame[timePerFrame.length - 1];
			timingGroups.add(new TimingGroupToolDataModel(Integer.toString(groupCounter), lastFrameDuration, spectraList));
		}
	}

	public int getTotalSpetra() {
		return totalSpectra;
	}

	public IObservableList getTimingGroups() {
		return timingGroups;
	}

	public double getTotalTime() {
		TimingGroupToolDataModel lastGroup = (TimingGroupToolDataModel) timingGroups.get(timingGroups.size() - 1);
		SpectrumToolDataModel lastSpectrum = (SpectrumToolDataModel) lastGroup.getSpectra().get(lastGroup.getSpectra().size() - 1);
		return lastSpectrum.getStartTime();
	}

	public void clearData() {
		timingGroups.clear();
	}
}
