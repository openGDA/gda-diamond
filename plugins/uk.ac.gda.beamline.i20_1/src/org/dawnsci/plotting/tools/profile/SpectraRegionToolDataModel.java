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

import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.region.IROIListener;
import org.dawnsci.plotting.api.region.IRegion;
import org.dawnsci.plotting.api.region.ROIEvent;
import org.dawnsci.plotting.api.trace.IImageTrace;
import org.dawnsci.plotting.api.trace.ILineTrace;
import org.dawnsci.plotting.api.trace.ITrace;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.dataset.IDataset;
import uk.ac.diamond.scisoft.analysis.roi.IROI;
import uk.ac.diamond.scisoft.analysis.roi.RectangularROI;
import uk.ac.gda.beans.ObservableModel;

public class SpectraRegionToolDataModel extends ObservableModel implements IROIListener {

	private final IRegion plotRegion;
	private final TimeResolvedToolDataModel parentTimeResolvedData;

	public static final String START = "start";
	public static final String END = "end";
	public static final String SPECTRA_CHANGED = "spectra";
	private List<SpectrumToolDataModel> spectraList;

	protected final List<ITrace> regionTraces = new ArrayList<ITrace>();

	private boolean adjusting;

	public SpectraRegionToolDataModel(IRegion plotRegion, TimeResolvedToolDataModel parent) {
		this.plotRegion = plotRegion;
		parentTimeResolvedData = parent;
		this.plotRegion.addROIListener(this);
		findSpectra();
		plotRegion.setUserObject(this);
	}

	private void findSpectra() {
		adjusting = true;
		IROI roi = plotRegion.getROI();
		if (roi instanceof RectangularROI) {
			RectangularROI boxRoi = (RectangularROI) roi;
			int firstIndex = (int) Math.round(boxRoi.getPointY());
			int lastIndex = (int) Math.round((boxRoi.getPointY() + boxRoi.getLength(1)));
			if (lastIndex > firstIndex) {
				lastIndex--;
			}
			boolean started = false;
			boolean ended = false;
			ArrayList<SpectrumToolDataModel> tempSpectraList = new ArrayList<SpectrumToolDataModel>();
			outerloop:
				for (Object object : parentTimeResolvedData.getTimingGroups()) {
					TimingGroupToolDataModel group = (TimingGroupToolDataModel) object;
					for (Object object1 : group.getSpectra()) {
						SpectrumToolDataModel spectrum = (SpectrumToolDataModel) object1;
						if (spectrum.getIndex() >= firstIndex) {
							started = true;
						}
						if ((started && !ended)) {
							tempSpectraList.add(spectrum);
							if (spectrum.getIndex() == lastIndex) {
								ended = true;
							}
						}

						if (started && ended) {
							firePropertyChange(SPECTRA_CHANGED, spectraList, spectraList = tempSpectraList);
							firePropertyChange(START, null, this.getStart());
							firePropertyChange(END, null, this.getEnd());
							roi.setPoint(0, firstIndex);
							((RectangularROI) roi).setLengths(new double[]{boxRoi.getLength(0), lastIndex - firstIndex + 1});
							plotRegion.setROI(roi);
							break outerloop;
						}
					}
				}
		}
		adjusting = false;
	}

	public List<SpectrumToolDataModel> getSpectra() {
		return spectraList;
	}

	public IRegion getRegion() {
		return plotRegion;
	}

	public SpectrumToolDataModel getStart() {
		return spectraList.get(0);
	}

	public SpectrumToolDataModel getEnd() {
		return spectraList.get(spectraList.size() - 1);
	}

	public int getTotalSpectra() {
		return getEnd().getIndex() - getStart().getIndex() + 1;
	}

	@Override
	public void roiDragged(ROIEvent evt) {}

	@Override
	public void roiChanged(ROIEvent evt) {
		if (!adjusting) {
			findSpectra();
		}
	}

	@Override
	public void roiSelected(ROIEvent evt) {}

	public ITrace[] createTraces(IPlottingSystem plottingSystem, IImageTrace imageTrace, IDataset energy) {
		for (SpectrumToolDataModel spectrum : this.getSpectra()) {
			DoubleDataset data = (DoubleDataset) imageTrace.getData().getSlice(new int[]{spectrum.getIndex(), 0}, new int[]{spectrum.getIndex() + 1, TimeResolvedToolDataModel.NUMBER_OF_STRIPS}, new int[]{1,1});
			ILineTrace trace = plottingSystem.createLineTrace(this.getRegion().getLabel() + " (" + spectrum.getIndex() + ")");
			trace.setData(energy, data);
			regionTraces.add(trace);
		}
		return regionTraces.toArray(new ITrace[]{});
	}

	public ITrace[] getTraces() {
		return regionTraces.toArray(new ITrace[]{});
	}


	public void clearTrace() {
		regionTraces.clear();
	}

	public String getDescription() {
		return "";
	}
}
