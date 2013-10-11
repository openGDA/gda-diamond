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

package uk.ac.gda.exafs.ui.data.experiment;

import java.util.ArrayList;
import java.util.List;

import com.google.gson.annotations.Expose;

import de.jaret.util.date.Interval;
import de.jaret.util.ui.timebars.model.DefaultRowHeader;
import de.jaret.util.ui.timebars.model.DefaultTimeBarRowModel;

public class TimingGroupModel extends ExperimentTimingDataModel {

	private final List<SpectrumModel> spectrumList = new ArrayList<SpectrumModel>();
	private final DefaultTimeBarRowModel timeBarRowModel;

	public static final String INTEGRATION_TIME_PROP_NAME = "integrationTime";
	@Expose
	private double integrationTime;

	public static final String TIME_PER_SPECTRUM_PROP_NAME = "timePerSpectrum";
	@Expose
	private double timePerSpectrum;

	public static final String DELAY_BETWEEN_SPECTRUM_PROP_NAME = "delayBetweenSpectrum";
	@Expose
	private double delayBetweenSpectrum;

	public static final String NO_OF_ACCUMULATION_PROP_NAME = "noOfAccumulations";
	@Expose
	private int noOfAccumulations;

	public static final String USE_EXTERNAL_TRIGGER_PROP_NAME = "useExernalTrigger";
	private boolean useExernalTrigger;

	public static final String MAX_ACCUMULATION_FOR_DETECTOR_PROP_NAME = "maxAccumulationforDetector";
	private int maxAccumulationforDetector;

	public static final String NO_OF_SPECTRUMS_PROP_NAME = "numberOfSpectrums";

	public List<?> getSpectrumList() {
		return spectrumList;
	}

	public static class Test extends DefaultTimeBarRowModel {
		public Test(DefaultRowHeader header) {
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
				updateMinMax();
				interval.removePropertyChangeListener(this);
				fireElementRemoved(interval);
			}
		}
	}

	public TimingGroupModel(DefaultTimeBarRowModel spectraTimeBarRowModel) {
		timeBarRowModel = spectraTimeBarRowModel;
	}

	public void removeSpectrum(SpectrumModel spectrum) {
		spectrumList.remove(spectrum);
	}

	@Override
	public void setStartTime(double startTime) {
		super.setStartTime(startTime);
		updateSpectrumsAndNoOfAccumulations();
	}

	@Override
	public void setDelay(double delay) {
		super.setDelay(delay);
		updateSpectrumsAndNoOfAccumulations();
	}

	@Override
	public void setEndTime(double duration) {
		super.setEndTime(duration);
		updateSpectrumsAndNoOfAccumulations();
	}

	public void setTimes(double startTime, double endTime) {
		super.setStartTime(startTime);
		super.setEndTime(endTime);
		updateSpectrumsAndNoOfAccumulations();
	}

	private void updateSpectrumsAndNoOfAccumulations() {
		if (timePerSpectrum <= 0) {
			return;
		} else if (timePerSpectrum + delayBetweenSpectrum > this.getAvailableTimeForSpectrum()) {
			this.setTimePerSpectrum(this.getAvailableTimeForSpectrum());
		}
		int numberOfSpectrums = (int) (this.getAvailableTimeForSpectrum() / (timePerSpectrum + delayBetweenSpectrum));
		int current = spectrumList.size();
		for (int i = current; i > numberOfSpectrums; i--){
			SpectrumModel itemToRemove = spectrumList.get(i - 1);
			timeBarRowModel.remInterval(itemToRemove);
			spectrumList.remove(itemToRemove);
		}
		double startTime = this.getStartTime() + this.getDelay();
		for (int i = 0; i < numberOfSpectrums; i++) {
			SpectrumModel spectrum = null;
			if (i < current) {
				spectrum = spectrumList.get(i);
			} else {
				spectrum = new SpectrumModel(this);
			}
			spectrum.setStartTime(startTime);
			startTime += timePerSpectrum;
			spectrum.setEndTime(startTime);
			spectrum.setName("Spectrum " + i + 1);
			if (i >= current) {
				spectrumList.add(spectrum);
				timeBarRowModel.addInterval(spectrum);
			}
		}
		TimingGroupModel.this.firePropertyChange(NO_OF_SPECTRUMS_PROP_NAME, null, spectrumList.size());
		updateMaxAccumulationForDetector();
	}

	public int getNumberOfSpectrums() {
		return spectrumList.size();
	}

	public double getIntegrationTime() {
		return integrationTime;
	}

	public void setIntegrationTime(double integrationTime) {
		this.firePropertyChange(INTEGRATION_TIME_PROP_NAME, this.integrationTime, this.integrationTime = integrationTime);
	}

	private double getAvailableTimeForSpectrum() {
		return getDuration() - getDelay();
	}

	public double getTimePerSpectrum() {
		return timePerSpectrum;
	}

	public void setTimePerSpectrum(double timePerSpectrum) {
		this.firePropertyChange(TIME_PER_SPECTRUM_PROP_NAME, this.timePerSpectrum, this.timePerSpectrum = timePerSpectrum);
		updateSpectrumsAndNoOfAccumulations();
	}

	public double getDelayBetweenSpectrum() {
		return delayBetweenSpectrum;
	}

	public void setDelayBetweenSpectrum(double value) {
		this.firePropertyChange(DELAY_BETWEEN_SPECTRUM_PROP_NAME, delayBetweenSpectrum, delayBetweenSpectrum = value);
		updateSpectrumsAndNoOfAccumulations();
	}

	public int getNoOfAccumulations() {
		return noOfAccumulations;
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

	@Override
	public void dispose() {
		for(SpectrumModel spectrum : spectrumList) {
			timeBarRowModel.remInterval(spectrum);
		}
		spectrumList.clear();
	}

	private void updateMaxAccumulationForDetector() {
		maxAccumulationforDetector = 10;
	}

	public int getMaxAccumulationforDetector() {
		return maxAccumulationforDetector;
	}

	public double getTimeResolution() {
		return delayBetweenSpectrum + timePerSpectrum;
	}
}
