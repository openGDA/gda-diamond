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

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.swt.widgets.Display;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.detector.EdeDetector;
import gda.device.detector.Roi;
import gda.factory.Findable;
import gda.factory.Finder;
import gda.observable.IObserver;
import uk.ac.gda.beans.ObservableModel;

public class DetectorModel extends ObservableModel {

	public static final DetectorModel INSTANCE = new DetectorModel();

	public static final String CURRENT_DETECTOR_SETUP_PROP_NAME = "currentDetector";
	public static final String DETECTOR_CONNECTED_PROP_NAME = "detectorConnected";

	public static final String BIAS_PROP_NAME = "bias";

	public static final String UPPER_CHANNEL_PROP_NAME = "upperChannel";
	public static final String LOWER_CHANNEL_PROP_NAME = "lowerChannel";

	public static final String TOPUP_CHECKER = "topup";

	public static final String SHUTTER_NAME = "shutter2"; // the shutter to use to create darks

	public static final String FAST_SHUTTER_NAME = "fast_shutter"; // the fast shutter

	private static final Logger logger = LoggerFactory.getLogger(DetectorModel.class);

	private EdeDetector currentDetector;

	private final EnergyCalibrationSetObserver energyCalibrationSetObserver = new EnergyCalibrationSetObserver();

	private final ROIsSetObserver roisSetObserver=new ROIsSetObserver();

	public EnergyCalibrationSetObserver getEnergyCalibrationSetObserver() {
		return energyCalibrationSetObserver;
	}

	private final List<EdeDetector> availableDetectors = new ArrayList<EdeDetector>();
	private final List<Roi> roisModel = new ArrayList<Roi>();
	private final WritableList rois = new WritableList(roisModel, Roi.class);

	private Integer[] excludedStripsCache;

	private DetectorModel() {
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
		try {
			setupDetectors();
		} catch (Exception e) {
			logger.error("Unable to setup available detectors", e);
		}
	}

	private void setupDetectors() {
		for (DetectorSetupType detectorSetup : DetectorSetupType.values()) {

			Findable detector = Finder.getInstance().find(detectorSetup.getDetectorName());
			if (detector != null && detector instanceof EdeDetector) {
				EdeDetector ededetector = (EdeDetector) detector;
				ededetector.setDetectorSetupType(detectorSetup);
				availableDetectors.add(ededetector);
			}
		}
		setCurrentDetector(availableDetectors.get(availableDetectors.size()-1));
	}

	public void reloadROIs() {
		rois.clear();
		for (Roi roi : currentDetector.getRois()) {
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

	public void setUpperChannel(int value) throws DetectorUnavailableException {
		if (currentDetector == null) {
			throw new DetectorUnavailableException();
		}
		int currentValue = currentDetector.getUpperChannel();
		currentDetector.setUpperChannel(value);
		this.firePropertyChange(UPPER_CHANNEL_PROP_NAME, currentValue, value);
		this.reloadROIs();
	}

	public void setLowerChannel(int value) throws DetectorUnavailableException {
		if (currentDetector == null) {
			throw new DetectorUnavailableException();
		}
		int currentValue = currentDetector.getLowerChannel();
		currentDetector.setLowerChannel(value);
		this.firePropertyChange(LOWER_CHANNEL_PROP_NAME, currentValue, value);
		this.reloadROIs();
	}

	public int getUpperChannel() throws DetectorUnavailableException {
		if (currentDetector == null) {
			throw new DetectorUnavailableException();
		}
		return currentDetector.getUpperChannel();
	}

	public int getLowerChannel() throws DetectorUnavailableException {
		if (currentDetector == null) {
			throw new DetectorUnavailableException();
		}
		return currentDetector.getLowerChannel();
	}

	public EdeDetector getCurrentDetector() {
		return currentDetector;
	}

	public EdeDetector getCurrentStepScanDetector() {
		// FIXME
		return Finder.getInstance().find("ss" + currentDetector.getName());
	}

	public void setCurrentDetector(EdeDetector detector) {
		if (currentDetector!=null) {
			currentDetector.deleteIObserver(energyCalibrationSetObserver);
			currentDetector.deleteIObserver(roisSetObserver);
		}
		excludedStripsCache = null;
		firePropertyChange(CURRENT_DETECTOR_SETUP_PROP_NAME, currentDetector, currentDetector = detector);
		firePropertyChange(DETECTOR_CONNECTED_PROP_NAME, false, true);
		firePropertyChange(LOWER_CHANNEL_PROP_NAME, null, currentDetector.getLowerChannel());
		firePropertyChange(UPPER_CHANNEL_PROP_NAME, null, currentDetector.getUpperChannel());
		currentDetector.addIObserver(energyCalibrationSetObserver);
		currentDetector.addIObserver(roisSetObserver);
	}

	public boolean isDetectorConnected() {
		return (currentDetector != null);
	}

	public List<EdeDetector> getAvailableDetectors() {
		return availableDetectors;
	}

	public void setExcludedStrips(Integer[] excludedStrips) {
		Integer[] currentExcludedStrips = currentDetector.getExcludedPixels();
		currentDetector.setExcludedPixels(excludedStrips);
		firePropertyChange(CURRENT_DETECTOR_EXCLUDED_STRIPS_PROP_NAME, currentExcludedStrips, excludedStrips);
		excludedStripsCache = null;
	}

	public static final String CURRENT_DETECTOR_EXCLUDED_STRIPS_PROP_NAME = "excludedStrips";
	public Integer[] getExcludedStrips() {
		// TODO Find out why we need cache
		if (excludedStripsCache == null) {
			excludedStripsCache = currentDetector.getExcludedPixels();
		}
		System.out.println("getExcludedStrips called " + excludedStripsCache + " for " + currentDetector.getName());
		return excludedStripsCache;
	}

	public Integer[] getStrips() {
		// TODO Refactor this!
		return currentDetector.getPixels();
	}

	public WritableList getRois() {
		return rois;
	}

	public ROIsSetObserver getRoisSetObserver() {
		return roisSetObserver;
	}

	public static class EnergyCalibrationSetObserver extends ObservableModel implements IObserver {
		public static final String ENERGY_CALIBRATION_PROP_NAME = "energyCalibration";
		@Override
		public void update(final Object source, Object arg) {
			if (arg.equals(EdeDetector.CALIBRATION_PROP_KEY)) {
				Display.getDefault().asyncExec(new Runnable() {
					@Override
					public void run() {
						String value = "";
						if (((EdeDetector) source).isEnergyCalibrationSet()) {
							value = ((EdeDetector) source).getEnergyCalibration().getFormattedPolinormal();
							EnergyCalibrationSetObserver.this.firePropertyChange(ENERGY_CALIBRATION_PROP_NAME, null, value);
						}
					}
				});
			}
		}

		public String getEnergyCalibration() {
			if (DetectorModel.INSTANCE.getCurrentDetector() != null &&  DetectorModel.INSTANCE.getCurrentDetector().isEnergyCalibrationSet()) {
				return DetectorModel.INSTANCE.getCurrentDetector().getEnergyCalibration().getFormattedPolinormal();
			}
			return "";
		}
	}
	public static class ROIsSetObserver extends ObservableModel implements IObserver {
		public static final String ROIS_PROP_NAME = EdeDetector.ROIS_PROP_NAME;
		List<Roi> roisModel = new ArrayList<Roi>();
		WritableList rois = new WritableList(roisModel, Roi.class);
		@Override
		public void update(final Object source, Object arg) {
			if (arg.equals(EdeDetector.ROIS_PROP_NAME)) {
				Display.getDefault().asyncExec(new Runnable() {
					@Override
					public void run() {
						rois.clear();
						for (Roi roi : ((EdeDetector) source).getRois()) {
							rois.add(roi);
						}
						ROIsSetObserver.this.firePropertyChange(ROIsSetObserver.ROIS_PROP_NAME, null, rois);
					}
				});
			}
		}

		public WritableList getRois() {
			if (rois.isEmpty()) {
				for (Roi roi : DetectorModel.INSTANCE.getCurrentDetector().getRois()) {
					rois.add(roi);
				}
			}
			return rois;
		}
	}

}
