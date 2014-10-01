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

import org.dawnsci.plotting.tools.profile.model.SpectrumDataNode;
import org.dawnsci.plotting.tools.profile.model.TimeResolvedDataNode;
import org.dawnsci.plotting.tools.profile.model.TimingGroupDataNode;
import org.eclipse.dawnsci.analysis.api.roi.IROI;
import org.eclipse.dawnsci.analysis.dataset.impl.DatasetUtils;
import org.eclipse.dawnsci.analysis.dataset.impl.DoubleDataset;
import org.eclipse.dawnsci.analysis.dataset.roi.RectangularROI;
import org.eclipse.dawnsci.plotting.api.region.IROIListener;
import org.eclipse.dawnsci.plotting.api.region.IRegion;
import org.eclipse.dawnsci.plotting.api.region.ROIEvent;
import org.eclipse.dawnsci.plotting.api.trace.ITrace;

import uk.ac.gda.beans.ObservableModel;

public class SpectraRegionDataNode extends ObservableModel implements IROIListener {

	private final IRegion plotRegion;
	private final TimeResolvedDataNode parentTimeResolvedData;

	public static final String START = "start";
	public static final String END = "end";
	public static final String SPECTRA_CHANGED = "spectra";
	private List<SpectrumDataNode> spectraList;

	protected final List<ITrace> regionTraces = new ArrayList<ITrace>();

	private boolean adjusting;

	public SpectraRegionDataNode(IRegion plotRegion, TimeResolvedDataNode parent) {
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
			ArrayList<SpectrumDataNode> tempSpectraList = new ArrayList<SpectrumDataNode>();
			outerloop:
				for (Object timingObject : parentTimeResolvedData.getTimingGroups()) {
					TimingGroupDataNode group = (TimingGroupDataNode) timingObject;
					for (Object object1 : group.getSpectra()) {
						SpectrumDataNode spectrum = (SpectrumDataNode) object1;
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

	public List<SpectrumDataNode> getSpectra() {
		return spectraList;
	}

	public IRegion getRegion() {
		return plotRegion;
	}

	public SpectrumDataNode getStart() {
		return spectraList.get(0);
	}

	public SpectrumDataNode getEnd() {
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

	public DoubleDataset getDataset(DoubleDataset fullData) {
		DoubleDataset result = new DoubleDataset(new int[]{0, TimeResolvedDataNode.NUMBER_OF_STRIPS});
		for (SpectrumDataNode spectrum : this.getSpectra()) {
			DoubleDataset data = (DoubleDataset) fullData.getSliceView(new int[]{spectrum.getIndex(), 0}, new int[]{spectrum.getIndex() + 1, TimeResolvedDataNode.NUMBER_OF_STRIPS}, new int[]{1,1});
			result = (DoubleDataset) DatasetUtils.append(result, data, 0);
		}
		return result;
	}

	public ITrace[] getTraces() {
		return regionTraces.toArray(new ITrace[]{});
	}

	public void addTrace(ITrace trace) {
		regionTraces.add(trace);
	}


	public void clearTrace() {
		regionTraces.clear();
	}

	@Override
	public String toString() {
		return this.getStart() + ":" + this.getEnd();
	}
}
