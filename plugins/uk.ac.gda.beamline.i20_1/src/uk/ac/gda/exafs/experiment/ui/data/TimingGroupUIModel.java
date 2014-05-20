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

package uk.ac.gda.exafs.experiment.ui.data;

import gda.device.DeviceException;
import gda.device.detector.StripDetector;
import gda.device.detector.XCHIPDetector;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.validation.IValidator;
import org.eclipse.core.databinding.validation.ValidationStatus;
import org.eclipse.core.runtime.IStatus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.ui.data.TimingGroup.InputTriggerLemoNumbers;

import com.google.gson.annotations.Expose;

import de.jaret.util.date.Interval;
import de.jaret.util.ui.timebars.model.DefaultRowHeader;
import de.jaret.util.ui.timebars.model.DefaultTimeBarRowModel;

public class TimingGroupUIModel extends TimeIntervalDataModel {

	private static final Logger logger = LoggerFactory.getLogger(TimingGroupUIModel.class);

	private final List<SpectrumModel> spectrumList = new ArrayList<SpectrumModel>();
	private final DefaultTimeBarRowModel spectraTimeBarRowModel;

	public static final String UNIT_PROP_NAME = "unit";
	private ExperimentUnit unit = ExperimentUnit.SEC;

	public static final String TIME_PER_SPECTRUM_PROP_NAME = "timePerSpectrum";
	@Expose
	private double timePerSpectrum;

	public static final String DELAY_BETWEEN_SPECTRUM_PROP_NAME = "delayBetweenSpectrum";
	@Expose
	private double delayBetweenSpectrum;

	public static final String INTEGRATION_TIME_PROP_NAME = "integrationTime";
	@Expose
	private double integrationTime;

	public static final String NO_OF_ACCUMULATION_PROP_NAME = "noOfAccumulations";
	@Expose
	private int noOfAccumulations;

	public static final String USE_EXTERNAL_TRIGGER_PROP_NAME = "useExernalTrigger";
	@Expose
	private boolean useExernalTrigger;

	public static final String EXTERNAL_TRIGGER_AVAILABLE_PROP_NAME = "exernalTriggerAvailable";
	@Expose
	private boolean exernalTriggerAvailable;

	public static final String EXTERNAL_TRIGGER_INPUT_LEMO_NUMBER_PROP_NAME = "exernalTriggerInputLemoNumber";
	@Expose
	private InputTriggerLemoNumbers exernalTriggerInputLemoNumber = InputTriggerLemoNumbers.ZERO;

	public static final String END_TIME_IS_LOCKED = "endTimeIsLocked";
	@Expose
	private boolean endTimeIsLocked;

	private final TimeResolvedExperimentModel parent;

	public static final String NO_OF_SPECTRUM_PROP_NAME = "numberOfSpectrum";

	public List<?> getSpectrumList() {
		return spectrumList;
	}

	public static class TimingGroupTimeBarRowModel extends DefaultTimeBarRowModel {
		public TimingGroupTimeBarRowModel(DefaultRowHeader header) {
			super(header);
		}
		@Override
		public void addInterval(Interval interval) {
			_intervals.add(interval);
			// Check min/max modifications by the added interval
			if (_minDate == null || _intervals.size() == 1) {
				_minDate = interval.getBegin().copy();
				_maxDate = interval.getEnd().copy();
			} else {
				if (_minDate.compareTo(interval.getBegin()) > 0) {
					_minDate = interval.getBegin().copy();
				}
				if (_maxDate.compareTo(interval.getEnd()) < 0) {
					_maxDate = interval.getEnd().copy();
				}
			}
			interval.addPropertyChangeListener(this);
			fireElementAdded(interval);
		}

		@Override
		public void remInterval(Interval interval) {
			if (_intervals.contains(interval)) {
				_intervals.remove(interval);
				// check min/max the hard way (optimize in custom implementations!)
				//updateMinMax();
				interval.removePropertyChangeListener(this);
				fireElementRemoved(interval);
			}
		}
	}

	public void resetInitialTime(double startTime, double endTime, double delay, double timePerSpectrum) {
		super.setDelay(delay);
		this.setTimes(startTime, endTime);
		updateTimePerSpectrum(timePerSpectrum);
		setSpectrumAndAdjustEndTime(this.getTimePerSpectrum());
	}

	private void updateTimePerSpectrum(double timePerSpectrum) {
		this.firePropertyChange(TIME_PER_SPECTRUM_PROP_NAME, this.timePerSpectrum, this.timePerSpectrum = timePerSpectrum);
	}

	public TimingGroupUIModel(DefaultTimeBarRowModel spectraTimeBarRowModel, ExperimentUnit unit, TimeResolvedExperimentModel parent) {
		this.spectraTimeBarRowModel = spectraTimeBarRowModel;
		this.parent = parent;
		this.resetInitialTime(TimeIntervalDataModel.INITIAL_START_TIME, TimeIntervalDataModel.MIN_DURATION_TIME, 0.0, TimeIntervalDataModel.MIN_DURATION_TIME);
		setSpectrumAndAdjustEndTime(this.getTimePerSpectrum());
		this.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				String sourcePropName = evt.getPropertyName();
				if (sourcePropName.equals(TIME_PER_SPECTRUM_PROP_NAME) | sourcePropName.equals(INTEGRATION_TIME_PROP_NAME) | sourcePropName.equals(NO_OF_SPECTRUM_PROP_NAME)) {
					TimingGroupUIModel.this.updateMaxAccumulationForDetector();
				}
			}
		});
		this.unit = unit;
	}

	private void setSpectrumAndAdjustEndTime(double timePerSpectrum) {
		int requiredNumberOfSpectrum = (int) Math.ceil(this.getAvailableDurationAfterDelay() / timePerSpectrum);
		adjustEndTimeForNumberOfSpectrum(requiredNumberOfSpectrum);
		adjustSpectra(requiredNumberOfSpectrum);
	}

	private void adjustEndTimeForNumberOfSpectrum(int requiredNumberOfSpectrum) {
		double requriedAvailableTimeAfterDelay = requiredNumberOfSpectrum * this.getTimePerSpectrum();
		this.setTimes(this.getStartTime(), requriedAvailableTimeAfterDelay);
	}

	private void adjustSpectra(int numberOfSpectrum) {
		int current = spectrumList.size();
		for (int i = current; i > numberOfSpectrum; i--) {
			SpectrumModel itemToRemove = spectrumList.get(i - 1);
			spectraTimeBarRowModel.remInterval(itemToRemove);
			spectrumList.remove(itemToRemove);
		}
		double startTimeForSpectrum = this.getStartTimeForSpectra();
		for (int i = 0; i < numberOfSpectrum; i++) {
			SpectrumModel spectrum = null;
			if (i < current) {
				spectrum = spectrumList.get(i);
			} else {
				spectrum = new SpectrumModel(this);
			}

			spectrum.setTimes(startTimeForSpectrum, timePerSpectrum);
			startTimeForSpectrum += timePerSpectrum;
			spectrum.setName("Spectrum " + i);
			if (i >= current) {
				spectrumList.add(spectrum);
				spectraTimeBarRowModel.addInterval(spectrum);
			}
		}
		firePropertyChange(NO_OF_SPECTRUM_PROP_NAME, current, spectrumList.size());
	}

	public void removeSpectrum(SpectrumModel spectrum) {
		spectrumList.remove(spectrum);
	}

	public void setEndTime(double endTime) throws Exception {
		double availableSpectraTime = endTime - this.getStartTimeForSpectra();
		if (availableSpectraTime < this.getTimePerSpectrum()) {
			updateTimePerSpectrum(availableSpectraTime);
		}
		this.setTimes(this.getStartTime(), availableSpectraTime);
		if (endTimeIsLocked && this.getAvailableDurationAfterDelay() % this.getTimePerSpectrum() != 0.0) {
			this.setTimePerSpectrum(this.getAvailableDurationAfterDelay());
		} else {
			this.setSpectrumAndAdjustEndTime(this.getTimePerSpectrum());
		}
	}

	public void moveTo(double startTime) {
		double duration = this.getDuration();
		setTimes(startTime, duration);
		adjustSpectra(this.getNumberOfSpectrum());
	}

	public int getNumberOfSpectrum() {
		return spectrumList.size();
	}

	public void setNumberOfSpectrum(int numberOfSpectrum) {
		double newTimePerSpectrum = ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertToNearestFrame(this.getAvailableDurationAfterDelay() / numberOfSpectrum);
		updateTimePerSpectrum(newTimePerSpectrum);
		adjustEndTimeForNumberOfSpectrum(numberOfSpectrum);
		this.adjustSpectra(numberOfSpectrum);
	}

	private double getStartTimeForSpectra() {
		return this.getStartTime() + this.getDelay();
	}

	public double getIntegrationTime() {
		return integrationTime;
	}

	public void setIntegrationTime(double integrationTime) throws IllegalArgumentException {
		if (integrationTime > this.getTimePerSpectrum()) {
			throw new IllegalArgumentException("Accumulation time cannot be longer than time per spectrum");
		}
		this.firePropertyChange(INTEGRATION_TIME_PROP_NAME, this.integrationTime, this.integrationTime = integrationTime);
	}

	public double getTimePerSpectrum() {
		return timePerSpectrum;
	}

	public void setTimePerSpectrum(double timePerSpectrum) throws Exception {
		updateTimePerSpectrum(timePerSpectrum);
		setSpectrumAndAdjustEndTime(timePerSpectrum);
		if (integrationTime > timePerSpectrum) {
			this.setIntegrationTime(timePerSpectrum);
		}
	}

	public ExperimentUnit getUnit() {
		return unit;
	}

	public void setUnit(ExperimentUnit unit) {
		this.firePropertyChange(UNIT_PROP_NAME, this.unit, this.unit = unit);
	}

	public boolean isEndTimeIsLocked() {
		return endTimeIsLocked;
	}

	public void setEndTimeIsLocked(boolean endTimeIsLocked) {
		this.firePropertyChange(END_TIME_IS_LOCKED, this.endTimeIsLocked, this.endTimeIsLocked = endTimeIsLocked);
	}

	public double getDelayBetweenSpectrum() {
		return delayBetweenSpectrum;
	}

	public void setDelayBetweenSpectrum(double value) {
		this.firePropertyChange(DELAY_BETWEEN_SPECTRUM_PROP_NAME, delayBetweenSpectrum, delayBetweenSpectrum = value);
	}

	public int getNoOfAccumulations() {
		return noOfAccumulations;
	}

	@Override
	public void setDelay(double delay) {
		super.setDelay(delay);
		adjustEndTimeForNumberOfSpectrum(this.getNumberOfSpectrum());
		this.adjustSpectra(this.getNumberOfSpectrum());
	}

	public void setNoOfAccumulations(int value) {
		this.firePropertyChange(NO_OF_ACCUMULATION_PROP_NAME, noOfAccumulations, noOfAccumulations = value);
	}

	public boolean isUseExernalTrigger() {
		return useExernalTrigger;
	}

	public void setUseExernalTrigger(boolean value) {
		this.firePropertyChange(USE_EXTERNAL_TRIGGER_PROP_NAME, useExernalTrigger, useExernalTrigger = value);
	}

	public boolean isExernalTriggerAvailable() {
		return exernalTriggerAvailable;
	}

	public void setExernalTriggerAvailable(boolean exernalTriggerAvailable) {
		this.firePropertyChange(EXTERNAL_TRIGGER_AVAILABLE_PROP_NAME, this.exernalTriggerAvailable, this.exernalTriggerAvailable = exernalTriggerAvailable);
	}

	public InputTriggerLemoNumbers getExernalTriggerInputLemoNumber() {
		return exernalTriggerInputLemoNumber;
	}

	public void setExernalTriggerInputLemoNumber(InputTriggerLemoNumbers exernalTriggerInputLemoNumber) {
		this.firePropertyChange(EXTERNAL_TRIGGER_INPUT_LEMO_NUMBER_PROP_NAME, this.exernalTriggerInputLemoNumber, this.exernalTriggerInputLemoNumber = exernalTriggerInputLemoNumber);

	}

	public TimeResolvedExperimentModel getParent() {
		return parent;
	}

	@Override
	public void dispose() {
		for(SpectrumModel spectrum : spectrumList) {
			spectraTimeBarRowModel.remInterval(spectrum);
		}
		spectrumList.clear();
	}

	private void updateMaxAccumulationForDetector() {
		try {
			double timePerSpectrum = getTimePerSpectrum();
			double integrationTime = getIntegrationTime();
			int noOfSpectra = getNumberOfSpectrum();
			if (integrationTime > 0 & timePerSpectrum > 0) {
				StripDetector detector = DetectorModel.INSTANCE.getCurrentDetector();
				if (detector instanceof XCHIPDetector) {
					int numberScansInFrame = ((XCHIPDetector) detector).getNumberScansInFrame(ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertTo(timePerSpectrum, ExperimentUnit.SEC), ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertTo(integrationTime, ExperimentUnit.SEC), noOfSpectra);
					setNoOfAccumulations(numberScansInFrame);
				} else {
					throw new DeviceException("Detector not found to get number of scans in frame");
				}
			}
		} catch (DeviceException e) {
			logger.warn("Unable to update max accumulations");
		}
	}

	public double getTimeResolution() {
		return delayBetweenSpectrum + timePerSpectrum;
	}

	public void setTimePerSpectrumForGroup(double timePerSpectrum) {
		this.firePropertyChange(TIME_PER_SPECTRUM_PROP_NAME, this.timePerSpectrum, this.timePerSpectrum = timePerSpectrum);
	}

	public int getExternalTrigLemoNumber() {
		return exernalTriggerInputLemoNumber.getLemoNumber();
	}

	public IValidator getEndTimeValidator() {
		return new IValidator() {
			@Override
			public IStatus validate(Object value) {
				double availableSpectraTime = ((double) value) - getStartTimeForSpectra();
				if (availableSpectraTime <= 0) {
					return ValidationStatus.error("End time should be higher than Start time");
				}
				return ValidationStatus.ok();
			}
		};
	}

	public IValidator getTimePerSpectrumValidator() {
		return new IValidator() {
			@Override
			public IStatus validate(Object value) {
				if (!ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.canConvertToFrame((double) value)) {
					return ValidationStatus.error("Unable to convert into frame");
				}
				if (endTimeIsLocked && (getAvailableDurationAfterDelay() % timePerSpectrum) != 0) {
					return ValidationStatus.error("Unable to fit with fixed End time");
				}
				return ValidationStatus.ok();
			}
		};
	}

	public IValidator getNoOfSpectrumValidator() {
		return new IValidator() {
			@Override
			public IStatus validate(Object value) {
				if (!ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.canConvertToFrame(getAvailableDurationAfterDelay() / ((int) value))) {
					return ValidationStatus.info("The time per spectrum will be rounded to nearest " + ExperimentUnit.MAX_RESOLUTION_IN_NANO_SEC + " " + ExperimentUnit.NANO_SEC.getUnitText());
				}
				if (endTimeIsLocked && (getAvailableDurationAfterDelay() % ((int) value)) != 0.0) {
					return ValidationStatus.error("The number of spectrum does not fit with the locked End time.");
				}
				return ValidationStatus.ok();
			}
		};
	}
}
