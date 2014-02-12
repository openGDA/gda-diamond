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
import org.dawnsci.plotting.api.region.IRegion;
import org.dawnsci.plotting.api.region.ROIEvent;
import org.dawnsci.plotting.api.trace.ITrace;

import uk.ac.diamond.scisoft.analysis.roi.IROI;
import uk.ac.diamond.scisoft.analysis.roi.RectangularROI;
import uk.ac.gda.beans.ObservableModel;

public class SpectraRegion extends ObservableModel implements IROIListener {

	private final IRegion region;
	private final TimeResolvedData timeResolvedData;

	public static final String START = "start";
	public static final String END = "end";
	public static final String SPECTRA_CHANGED = "spectra";
	private List<Spectrum> spectraList;

	private final List<ITrace> regionTraces = new ArrayList<ITrace>();

	private boolean adjusting;

	public SpectraRegion(IRegion region, TimeResolvedData timeResolvedData) {
		this.region = region;
		this.timeResolvedData = timeResolvedData;
		this.region.addROIListener(this);
		findSpectra();
	}

	private void findSpectra() {
		adjusting = true;
		IROI roi = region.getROI();
		if (roi instanceof RectangularROI) {
			RectangularROI boxRoi = (RectangularROI) roi;
			int firstIndex = (int) boxRoi.getPointY();
			int lastIndex = (int) (boxRoi.getPointY() + boxRoi.getLength(1));
			boolean started = false;
			boolean ended = false;
			ArrayList<Spectrum> tempSpectraList = new ArrayList<Spectrum>();
			outerloop:
				for (Object object : timeResolvedData.getTimingGroups()) {
					TimingGroup group = (TimingGroup) object;
					for (Object object1 : group.getSpectra()) {
						Spectrum spectrum = (Spectrum) object1;
						if (spectrum.getIndex() >= firstIndex) {
							started = true;
						}
						if (!ended && spectrum.getIndex() >= lastIndex) {
							ended = true;
						}
						if (started && !ended) {
							tempSpectraList.add(spectrum);
						}
						if (started && ended) {
							firePropertyChange(SPECTRA_CHANGED, spectraList, spectraList = tempSpectraList);
							firePropertyChange(START, null, this.getStart());
							firePropertyChange(END, null, this.getEnd());

							roi.setPoint(0, firstIndex);
							((RectangularROI) roi).setLengths(new double[]{boxRoi.getLength(0), lastIndex - firstIndex});
							region.setROI(roi);
							break outerloop;
						}
					}
				}
		}
		adjusting = false;
	}

	public List<Spectrum> getSpectra() {
		return spectraList;
	}

	public IRegion getRegion() {
		return region;
	}

	public Spectrum getStart() {
		return spectraList.get(0);
	}

	public Spectrum getEnd() {
		return spectraList.get(spectraList.size() - 1);
	}

	public List<ITrace> getRegionTraces() {
		return regionTraces;
	}

	@Override
	public void roiDragged(ROIEvent evt) {
		System.out.println("roiDragged");
	}

	@Override
	public void roiChanged(ROIEvent evt) {
		if (!adjusting) {
			findSpectra();
		}
		System.out.println("roiChanged");
	}

	@Override
	public void roiSelected(ROIEvent evt) {
		System.out.println("roiSelected");
	}
}
