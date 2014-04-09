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

import gda.scan.ede.datawriters.EdeDataConstants;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;

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

	public void setData(DoubleDataset metadata) {
		int noOfGroups = metadata.getShape()[0];
		double startTime = 0.0;
		for (int i = 0; i < noOfGroups; i++) {
			int noOfSpectra = EdeDataConstants.TimingGroupMetaData.getNoOfSpectra(i, metadata);
			double timePerSpectrum = EdeDataConstants.TimingGroupMetaData.getTimePerSpectrum(i, metadata);
			List<SpectrumDataNode> spectraList = new ArrayList<SpectrumDataNode>();
			for (int j = 0; j < noOfSpectra; j++) {
				spectraList.add(new SpectrumDataNode(j + (i * noOfSpectra), startTime));
				startTime += timePerSpectrum;
			}
			timingGroups.add(new TimingGroupDataNode(Integer.toString(i), timePerSpectrum, spectraList));
		}
	}
}
