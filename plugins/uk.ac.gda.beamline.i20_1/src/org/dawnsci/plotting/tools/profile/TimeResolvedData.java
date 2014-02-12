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

import org.dawnsci.plotting.api.region.IROIListener;
import org.dawnsci.plotting.api.region.ROIEvent;
import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;

public class TimeResolvedData implements IROIListener {

	private final IObservableList timingGroups = new WritableList(new ArrayList<TimingGroup>(), TimingGroup.class);

	private final int totalSpectra;

	public TimeResolvedData(DoubleDataset timingGroupsDataset, DoubleDataset timeDataset) {
		// TODO Refactor this! This has hard coded index numbers!
		double[] timingGroupsData = ((DoubleDataset)timingGroupsDataset.getSlice(new int[]{0,0}, new int[]{timingGroupsDataset.getShape()[0],3}, new int[]{1,3})).getData();
		double[] timePerFrame = ((DoubleDataset) timingGroupsDataset.getSlice(new int[]{0,1}, new int[]{timingGroupsDataset.getShape()[0],3}, new int[]{1,3})).getData();
		totalSpectra = timingGroupsData.length;
		double[] time = timeDataset.getData();
		if (timingGroupsData.length > 0) {
			int groupCounter = 0;
			List<Spectrum> spectraList = new ArrayList<Spectrum>();
			for (int i = 0; i < timingGroupsData.length; i++) {
				if (timingGroupsData[i] > groupCounter) {
					double lastFrameDuration = timePerFrame[i - 1];
					timingGroups.add(new TimingGroup(Integer.toString(groupCounter), lastFrameDuration, spectraList));
					groupCounter = (int) timingGroupsData[i];
					spectraList = new ArrayList<Spectrum>();
				}
				spectraList.add(new Spectrum(i, time[i]));
			}
			double lastFrameDuration =timePerFrame[timePerFrame.length - 1];
			timingGroups.add(new TimingGroup(Integer.toString(groupCounter), lastFrameDuration, spectraList));
		}
	}

	public int getTotalSpetra() {
		return totalSpectra;
	}

	public IObservableList getTimingGroups() {
		return timingGroups;
	}

	@Override
	public void roiDragged(ROIEvent evt) {
		// TODO Auto-generated method stub

	}

	@Override
	public void roiChanged(ROIEvent evt) {
		// TODO Auto-generated method stub

	}

	@Override
	public void roiSelected(ROIEvent evt) {
		// TODO Auto-generated method stub

	}


	public double getTotalTime() {
		TimingGroup lastGroup = (TimingGroup) timingGroups.get(timingGroups.size() - 1);
		Spectrum lastSpectrum = (Spectrum) lastGroup.getSpectra().get(lastGroup.getSpectra().size() - 1);
		return lastSpectrum.getStartTime();
	}
}
