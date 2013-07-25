/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.data;

import gda.device.DeviceException;
import gda.device.detector.StripDetector;
import gda.device.detector.XHDetector;
import gda.device.detector.XHROI;
import gda.factory.Finder;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.observable.list.WritableList;

public class DetectorConfig extends ObservableModel {

	public static final DetectorConfig INSTANCE = new DetectorConfig();

	public static final String CURRENT_DETECTOR_SETUP_PROP_NAME = "currentDetector";
	public static final String DETECTOR_CONNECTED_PROP_NAME = "detectorConnected";
	private StripDetector currentDetector;

	private final List<StripDetector> availableDetectors = new ArrayList<StripDetector>();
	private final List<XHROI> roisModel = new ArrayList<XHROI>();
	private final WritableList rois = new WritableList(roisModel, XHROI.class);

	private Double biasCache;

	private Integer[] excludedStripsCache;

	private DetectorConfig() {
		this.addPropertyChangeListener(DETECTOR_CONNECTED_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if ((boolean) evt.getNewValue()) {
					reloadROIs();
				} else {
					rois.clear();
				}
			}
		});
	}

	public void reloadROIs() {
		rois.clear();
		for (XHROI roi : currentDetector.getRois()) {
			rois.add(roi);
		}
	}

	public void addRIO() {
		currentDetector.setNumberRois(rois.size() + 1);
		reloadROIs();
	}

	public void removeRIO() {
		if (rois.size() > 1) {
			currentDetector.setNumberRois(rois.size() - 1);
			reloadROIs();
		}
	}

	public StripDetector getCurrentDetector() {
		return currentDetector;
	}

	public void setCurrentDetector(StripDetector detector) throws Exception {
		try {
			try {
				if (currentDetector != null) {
					if (currentDetector.isConnected()) {
						currentDetector.disconnect();
					}
				}
				firePropertyChange(DETECTOR_CONNECTED_PROP_NAME, (currentDetector == null), false);
				firePropertyChange(CURRENT_DETECTOR_SETUP_PROP_NAME, currentDetector, currentDetector = null);
			} catch (DeviceException e) {
				throw new Exception("DeviceException when disconnecting detector " + currentDetector.getName(), e);
			}
			if (!detector.isConnected()) {
				detector.connect();
			}
			biasCache = null;
			excludedStripsCache = null;
			firePropertyChange(CURRENT_DETECTOR_SETUP_PROP_NAME, currentDetector, currentDetector = detector);
			firePropertyChange(DETECTOR_CONNECTED_PROP_NAME, false, true);
		} catch (DeviceException e) {
			firePropertyChange(DETECTOR_CONNECTED_PROP_NAME, false, false);
			firePropertyChange(CURRENT_DETECTOR_SETUP_PROP_NAME, null, null);
			throw new Exception("DeviceException when connecting detector " + detector.getName(), e);
		}
	}

	public boolean isDetectorConnected() {
		return (currentDetector != null);
	}

	public void setupDetectors() throws Exception {
		for (DetectorSetup detectorSetup : DetectorSetup.values()) {

			Object detectorBean = Finder.getInstance().find(detectorSetup.getDetectorName());
			if (detectorBean != null && detectorBean instanceof StripDetector) {
				StripDetector stripdetector = (StripDetector) detectorBean;
				availableDetectors.add(stripdetector);
				if (stripdetector.isConnected()) {
					setCurrentDetector(stripdetector);
				}
			}
		}
	}

	public List<StripDetector> getAvailableDetectors() {
		return availableDetectors;
	}

	public boolean isVoltageInRange(double value) {
		return (currentDetector.getMinBias() <= value & value <= currentDetector.getMaxBias());
	}

	public double getBias() throws DeviceException {
		if (biasCache == null) {
			biasCache = new Double(currentDetector.getBias());
		}
		return biasCache.doubleValue();
	}

	public static final String BIAS_PROP_NAME = "bias";
	public void setBias(double bias) throws DeviceException {
		double currentBias = currentDetector.getBias();
		currentDetector.setBias(bias);
		firePropertyChange(BIAS_PROP_NAME, currentBias, bias);
		biasCache = null;
	}

	public void setExcludedStrips(Integer[] excludedStrips) throws DeviceException {
		Integer[] currentExcludedStrips = currentDetector.getExcludedStrips();
		currentDetector.setExcludedStrips(excludedStrips);
		firePropertyChange(CURRENT_DETECTOR_EXCLUDED_STRIPS_PROP_NAME, currentExcludedStrips, excludedStrips);
		excludedStripsCache = null;
	}

	public static final String CURRENT_DETECTOR_EXCLUDED_STRIPS_PROP_NAME = "excludedStrips";
	public Integer[] getExcludedStrips() {
		// TODO Find out why we need cache
		if (excludedStripsCache == null) {
			excludedStripsCache = currentDetector.getExcludedStrips();
		}
		System.out.println("getExcludedStrips called " + excludedStripsCache + " for " + currentDetector.getName());
		return excludedStripsCache;
	}

	public Integer[] getStrips() {
		// TODO Refactor this!
		return XHDetector.getStrips();
	}

	public WritableList getRois() {
		return rois;
	}

	private static enum DetectorSetup {
		XH("xh"), XSTRIP("xstrip"), CCD("ccd");

		private final String detectorName;

		private DetectorSetup(String detectorName) {
			this.detectorName = detectorName;
		}

		public String getDetectorName() {
			return detectorName;
		}
	}
}
