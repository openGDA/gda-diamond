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

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.swt.widgets.Display;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.detector.EdeDetector;
import gda.device.detector.Roi;
import gda.factory.Finder;
import gda.observable.IObserver;
import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.ede.data.DetectorSetupType;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentUnit;
import uk.ac.gda.exafs.experiment.ui.data.TimingGroupUIModel;

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

	private final List<EdeDetector> availableDetectors = new ArrayList<>();
	private final List<Roi> roisModel = new ArrayList<>();
	private final WritableList<Roi> rois = new WritableList<>(roisModel, Roi.class);

	private Integer[] excludedStripsCache;

	private static final String DETECTOR_NAME_DATA_STORE_KEY = "currentSelectedDetectorName";

	private double accumulationReadoutTime;


	private DetectorModel() {
		this.addPropertyChangeListener(DETECTOR_CONNECTED_PROP_NAME, evt -> {
			if ((boolean) evt.getNewValue()) {
				reloadROIs();
			} else {
				rois.clear();
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

			Finder.findOptionalOfType(detectorSetup.getDetectorName(), EdeDetector.class)
					.ifPresent(ededetector -> {
						ededetector.setDetectorSetupType(detectorSetup);
						availableDetectors.add(ededetector);
					} );
		}
		loadDetectorNameFromPreferenceStore();
		if (currentDetector == null) {
			currentDetector = availableDetectors.get(availableDetectors.size()-1);
		}
		setCurrentDetector(currentDetector);
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
		return Finder.find("ss" + currentDetector.getName());
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
		saveDetectorNameToPreferenceStore();
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

	public WritableList<Roi> getRois() {
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
				Display.getDefault().asyncExec(() -> {
					String value = "";
					if (((EdeDetector) source).isEnergyCalibrationSet()) {
						value = ((EdeDetector) source).getEnergyCalibration().getFormattedPolinormal();
						EnergyCalibrationSetObserver.this.firePropertyChange(ENERGY_CALIBRATION_PROP_NAME, null, value);
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
		List<Roi> roisModel = new ArrayList<>();
		WritableList<Roi> rois = new WritableList<>(roisModel, Roi.class);
		@Override
		public void update(final Object source, Object arg) {
			if (arg.equals(EdeDetector.ROIS_PROP_NAME)) {
				Display.getDefault().asyncExec(() -> {
					rois.clear();
					for (Roi roi : ((EdeDetector) source).getRois()) {
						rois.add(roi);
					}
					ROIsSetObserver.this.firePropertyChange(ROIsSetObserver.ROIS_PROP_NAME, null, rois);
				});
			}
		}

		public WritableList<Roi> getRois() {
			if (rois.isEmpty()) {
				for (Roi roi : DetectorModel.INSTANCE.getCurrentDetector().getRois()) {
					rois.add(roi);
				}
			}
			return rois;
		}
	}

	/**
	 * Save name of current detector to preference store
	 */
	private void saveDetectorNameToPreferenceStore() {
		EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(DETECTOR_NAME_DATA_STORE_KEY, currentDetector.getName());
	}

	/**
	 * Load name of previously selected detector from preference store.
	 */
	private void loadDetectorNameFromPreferenceStore() {
		String detectorName = EdeDataStore.INSTANCE.getPreferenceDataStore().loadConfiguration(DETECTOR_NAME_DATA_STORE_KEY, String.class);
		if (detectorName != null && !detectorName.isEmpty()) {
			Optional<EdeDetector> selectedDet = availableDetectors.stream().filter( det -> det.getName().equals(detectorName)).findFirst();
			if (selectedDet.isPresent()) {
				currentDetector = selectedDet.get();
			}

		}
	}

	/**
	 * Set the accumulation readout time
	 * @param newReadoutTime - in default experiment units (ns)
	 */
	public void setAccumulationReadoutTime(double newReadoutTime) {
		this.firePropertyChange(TimingGroupUIModel.ACCUMULATION_READOUT_TIME_PROP_NAME, accumulationReadoutTime, accumulationReadoutTime = newReadoutTime);
		// Convert units to seconds and update the detector
		double timeSecs = ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertTo(newReadoutTime, ExperimentUnit.SEC);
		currentDetector.setAccumulationReadoutTime(timeSecs);
	}

	/**
	 *
	 * @return Accumulation readout time (default experiment units, ns)
	 */
	public double getAccumulationReadoutTime() {
		return ExperimentUnit.SEC.convertToDefaultUnit(currentDetector.getAccumulationReadoutTime());
	}

	/**
	 * Units to use in the GUI for accumulation time  (milliseconds for Frelon, microseconds for XH/XStrip)
	 * @return ExperimentUnit.MILLI_SEC or ExperimentUnit.MICRO_SEC
	 */
	public ExperimentUnit getUnitForAccumulationTime() {
		if (DetectorModel.INSTANCE.getCurrentDetector().getDetectorSetupType() == DetectorSetupType.FRELON) {
			return ExperimentUnit.MILLI_SEC;
		} else {
			return ExperimentUnit.MIRCO_SEC;
		}
	}
}
