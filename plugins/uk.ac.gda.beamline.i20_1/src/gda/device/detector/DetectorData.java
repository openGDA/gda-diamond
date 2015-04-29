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

import gda.observable.IObserver;

import java.io.Serializable;

import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.exafs.calibration.data.CalibrationDetails;

public class DetectorData extends ObservableModel implements Serializable, IDetectorData{
	public static final String CALIBRATION_PROP_KEY = "calibration";
	public static final String ROIS_CHANGED = "rois_changed";
	private Integer[] excludedPixels = new Integer[]{}; //list of dead pixel locations
	private int lowerChannel; // lower bound for ROI in energy
	private int upperChannel; //Upper bound for ROI in energy
	private final EdeObservableComponent obsComp=new EdeObservableComponent();
	private Roi[] rois;
	private CalibrationDetails energyCalibration = new CalibrationDetails();
	private boolean energyCalibrationSet=false;
	private String name;

	@Override
	public int getLowerChannel() {
		return lowerChannel;
	}
	@Override
	public void setLowerChannel(int lowerChannel) {
		this.lowerChannel = lowerChannel;
	}
	@Override
	public int getUpperChannel() {
		return upperChannel;
	}
	@Override
	public void setUpperChannel(int upperChannel) {
		this.upperChannel = upperChannel;
	}
	@Override
	public Roi[] getRois() {
		return rois;
	}
	@Override
	public void setRois(Roi[] rois) {
		this.rois = rois;
		obsComp.notifyIObservers(this, ROIS_CHANGED);
	}
	@Override
	public CalibrationDetails getEnergyCalibration() {
		return energyCalibration;
	}

	@Override
	public void setEnergyCalibration(CalibrationDetails energyCalibration) {
		this.energyCalibration = energyCalibration;
		setEnergyCalibrationSet(true);
		//TODO why not pass the change as energyCalibration - CORBArise?
		obsComp.notifyIObservers(this, CALIBRATION_PROP_KEY);
	}

	@Override
	public boolean isEnergyCalibrationSet() {
		return energyCalibrationSet;
	}

	@Override
	public Integer[] getExcludedPixels() {
		return excludedPixels;
	}

	@Override
	public void setExcludedPixels(Integer[] excludedPixels) {
		this.excludedPixels = excludedPixels;
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
	public void addIObserver(IObserver observer) {
		obsComp.addIObserver(observer);
	}
	@Override
	public void deleteIObserver(IObserver observer) {
		obsComp.deleteIObserver(observer);
	}
	@Override
	public void deleteIObservers() {
		obsComp.deleteIObservers();
	}
	@Override
	public void setName(String name) {
		this.name=name;
	}
	@Override
	public String getName() {
		return name;
	}
	public void setEnergyCalibrationSet(boolean energyCalibrationSet) {
		this.energyCalibrationSet = energyCalibrationSet;
	}
}