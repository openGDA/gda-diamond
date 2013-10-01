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

package uk.ac.gda.exafs.ui.data.detector;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.core.databinding.observable.list.ListDiffVisitor;
import org.eclipse.core.databinding.observable.list.WritableList;

import com.google.gson.annotations.Expose;

import de.jaret.util.date.IntervalImpl;
import de.jaret.util.ui.timebars.model.DefaultTimeBarRowModel;

public class TimingGroupModel extends CollectionModel {

	private final WritableList spectrumList = new WritableList(new ArrayList<SpectrumModel>(), SpectrumModel.class);
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

	public static final String MAX_ACCUMULATION_FOR_DETECTOR_PROP_NAME = "maxAccumulationforDetector";
	private int maxAccumulationforDetector;

	public static final String NO_OF_SPECTRUMS_PROP_NAME = "numberOfSpectrums";

	public List<?> getSpectrumList() {
		return spectrumList;
	}

	public TimingGroupModel(DefaultTimeBarRowModel value) {
		timeBarRowModel = value;
		spectrumList.addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						timeBarRowModel.remInterval((IntervalImpl) element);
					}
					@Override
					public void handleAdd(int index, Object element) {
						timeBarRowModel.addInterval((IntervalImpl) element);
					}
				});
				TimingGroupModel.this.firePropertyChange(NO_OF_SPECTRUMS_PROP_NAME, null, spectrumList.size());
			}
		});
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

	private void updateSpectrumsAndNoOfAccumulations() {
		if (timePerSpectrum <= 0) {
			return;
		}
		spectrumList.clear();
		int numberOfSpectrums = (int) (this.getDuration() / (timePerSpectrum + delayBetweenSpectrum));
		for (int i = 0; i < numberOfSpectrums; i++) {
			SpectrumModel spectrum = new SpectrumModel(this);
			if (spectrumList.isEmpty()) { // First entry
				spectrum.setStartTime(this.getStartTime());
			} else {
				spectrum.setStartTime(((SpectrumModel) spectrumList.get(spectrumList.size() - 1)).getEndTime() + delayBetweenSpectrum);
			}
			spectrum.setEndTime(spectrum.getStartTime() + timePerSpectrum);
			spectrum.setName("Spectrum " + (spectrumList.size() + 1));
			spectrumList.add(spectrum);
		}

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

	@Override
	public void dispose() {
		spectrumList.clear();
	}

	private void updateMaxAccumulationForDetector() {
		maxAccumulationforDetector = 10;
	}

	public int getMaxAccumulationforDetector() {
		return maxAccumulationforDetector;
	}
}
