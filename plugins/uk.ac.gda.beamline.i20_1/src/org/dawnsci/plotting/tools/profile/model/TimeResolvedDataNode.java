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

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

import gda.scan.ede.datawriters.EdeDataConstants.ItMetadata;
import gda.scan.ede.datawriters.EdeDataConstants.RangeData;
import gda.scan.ede.datawriters.EdeDataConstants.TimingGroupMetadata;

public class TimeResolvedDataNode {

	private final IObservableList timingGroups = new WritableList(new ArrayList<TimingGroupDataNode>(), TimingGroupDataNode.class);

	public static final int NUMBER_OF_STRIPS = 1024;

	public IObservableList getTimingGroups() {
		return timingGroups;
	}

	public void clearData() {
		for (Object obj : timingGroups) {
			((TimingGroupDataNode) obj).getSpectra().clear();
		}
		timingGroups.clear();
	}

	public void setData(ItMetadata itMetadata) {
		TimingGroupMetadata[] timingGroupsArray = itMetadata.getTimingGroups();
		RangeData[] avgSpectraList = null;
		int totalSpectra = 0;
		for (int i = 0; i < timingGroupsArray.length; i++) {
			totalSpectra += timingGroupsArray[i].getNoOfFrames();
		}
		if (itMetadata.getAvgSpectra() != null) {
			avgSpectraList = itMetadata.getAvgSpectra();
		}
		int currentGroupIndex = 0;
		int j = 0;
		int k = 0;
		RangeData avgRange = null;
		double time = 0.0d;
		int totalSpectraUptoCurrentGroup = timingGroupsArray[currentGroupIndex].getNoOfFrames();
		List<SpectrumDataNode> spectraList = new ArrayList<SpectrumDataNode>();
		boolean averaged = false;
		for (int i = 0; i < totalSpectra; i++) {
			if (avgSpectraList != null && j < avgSpectraList.length) {
				avgRange = avgSpectraList[j];
				if (avgRange.getStartIndex() == i) {
					while(i < avgRange.getEndIndex()) {
						time += timingGroupsArray[currentGroupIndex].getTimePerSpectrum();
						i++;
						if (i == totalSpectraUptoCurrentGroup) {
							timingGroups.add(new TimingGroupDataNode("", timingGroupsArray[currentGroupIndex].getTimePerSpectrum(), spectraList));
							spectraList = new ArrayList<SpectrumDataNode>();
							currentGroupIndex++;
							totalSpectraUptoCurrentGroup += timingGroupsArray[currentGroupIndex].getNoOfFrames();
						}
					}
					j++;
					averaged = true;
				}
			}
			time += timingGroupsArray[currentGroupIndex].getTimePerSpectrum();
			spectraList.add(new SpectrumDataNode(k, time, averaged));
			averaged = false;
			if (i == totalSpectraUptoCurrentGroup - 1) { // to index
				timingGroups.add(new TimingGroupDataNode("", timingGroupsArray[currentGroupIndex].getTimePerSpectrum(), spectraList));
				spectraList = new ArrayList<SpectrumDataNode>();
				currentGroupIndex++;
				if (currentGroupIndex < timingGroupsArray.length) {
					totalSpectraUptoCurrentGroup += timingGroupsArray[currentGroupIndex].getNoOfFrames();
				}
			}
			k++;
		}
		// timingGroups.add(new TimingGroupDataNode("", timingGroupsArray[currentGroupIndex].getTimePerSpectrum(), spectraList));
	}
}
