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

package gda.device.detector;

import java.io.Serializable;

import uk.ac.gda.beans.ObservableModel;

public class DetectorData extends ObservableModel implements Serializable, IDetectorData{

	public static final String ROIS_CHANGED = "rois_changed";
	private Integer[] excludedPixels = new Integer[]{}; //list of dead pixel locations
	private int lowerChannel; // lower bound for ROI in energy
	private int upperChannel; //Upper bound for ROI in energy
	//	private final EdeObservableComponent obsComp=new EdeObservableComponent();
	private Roi[] rois=new Roi[EdeDetector.INITIAL_NO_OF_ROIS];
	private String name;

	@Override
	public int getLowerChannel() {
		return lowerChannel;
	}
	@Override
	public void setLowerChannel(int lowerChannel) {
		this.lowerChannel = lowerChannel;
		setNumberRois(getNumberOfRois());
	}
	@Override
	public int getUpperChannel() {
		return upperChannel;
	}
	@Override
	public void setUpperChannel(int upperChannel) {
		this.upperChannel = upperChannel;
		setNumberRois(getNumberOfRois());
	}
	@Override
	public Roi[] getRois() {
		return rois;
	}
	@Override
	public void setRois(Roi[] rois) {
		Roi[] oldRois=this.rois;
		this.rois = rois;
		this.firePropertyChange(IDetectorData.ROIS_PROP_NAME, oldRois, this.rois);
	}

	@Override
	public Integer[] getExcludedPixels() {
		return excludedPixels;
	}

	@Override
	public void setExcludedPixels(Integer[] excludedPixels) {
		this.excludedPixels = excludedPixels;
	}

	public int getNumberOfRois() {
		return rois.length;
	}
	@Override
	public void setNumberRois(int numberOfRois) {
		Roi[] rois = createRois(numberOfRois);
		setRois(rois);
	}

	private Roi[] createRois(int numberOfRois) {
		Roi[] rois = new Roi[numberOfRois];
		int useableRegion = upperChannel - (lowerChannel - 1); // Inclusive of the first
		int increment = useableRegion / numberOfRois;
		int start = lowerChannel;
		for (int i = 0; i < numberOfRois; i++) {
			Roi roi = new Roi();
			roi.setName("ROI_" + (i + 1));
			roi.setLowerLevel(start);
			roi.setUpperLevel(start + increment - 1);
			rois[i] = roi;
			start = start + increment;
		}
		if (rois[rois.length - 1].getUpperLevel() < upperChannel) {
			rois[rois.length - 1].setUpperLevel(upperChannel);
		}
		return rois;
	}

	@Override
	public int getRoiFor(int elementIndex) {
		for (int i = 0; i < getRois().length; i++) {
			if (getRois()[i].isInsideRio(elementIndex)) {
				return i;
			}
		}
		return -1;
	}

	@Override
	public void setName(String name) {
		this.name=name;
	}
	@Override
	public String getName() {
		return name;
	}

}