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

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.List;

import de.jaret.util.date.Interval;
import de.jaret.util.ui.timebars.model.DefaultRowHeader;
import de.jaret.util.ui.timebars.model.DefaultTimeBarModel;
import de.jaret.util.ui.timebars.model.DefaultTimeBarRowModel;
import de.jaret.util.ui.timebars.model.TimeBarModel;

public class CyclicExperimentModel extends TimeResolvedExperimentModel {
	private static final String CYCLIC_EXPERIMENT_MODEL_DATA_STORE_KEY = "CYCLIC_TIME_RESOLVED_EXPERIMENT_DATA";

	public static final String NO_OF_REPEATED_GROUPS_PROP_NAME = "noOfRepeatedGroups";
	private int noOfRepeatedGroups;

	public static final String CYCLES_DURATION_PROP_NAME = "cyclesDuration";
	private double cyclesDuration;

	private final DefaultTimeBarModel cyclicTimebarModel;

	private final DefaultTimeBarRowModel cyclicTimeBarRowModel;

	public CyclicExperimentModel() {
		cyclicTimebarModel = new DefaultTimeBarModel();
		DefaultRowHeader header = new DefaultRowHeader("Cycles");
		cyclicTimeBarRowModel = new DefaultTimeBarRowModel(header);
		cyclicTimebarModel.addRow(cyclicTimeBarRowModel);

		this.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if (evt.getPropertyName().equals(ExperimentTimingDataModel.DURATION_PROP_NAME)) {
					double startTime = 0.0;
					for(Interval object : cyclicTimeBarRowModel.getIntervals()) {
						ExperimentCycleModel experimentCycleModel = (ExperimentCycleModel) object;
						experimentCycleModel.setTimes(startTime, (double) evt.getNewValue());
						startTime += experimentCycleModel.getDuration();
					}
					updateTimes();
				} else if (evt.getPropertyName().equals(NO_OF_REPEATED_GROUPS_PROP_NAME)) {
					int existingCycles = cyclicTimeBarRowModel.getIntervals().size();
					for (int i=existingCycles; i < noOfRepeatedGroups; i++) {
						ExperimentCycleModel experimentCycleModel = new ExperimentCycleModel(CyclicExperimentModel.this);
						experimentCycleModel.setName("Cycle " + (i + 1));
						experimentCycleModel.setTimes(i * CyclicExperimentModel.this.getDuration(), CyclicExperimentModel.this.getDuration());
						cyclicTimeBarRowModel.addInterval(experimentCycleModel);

					}
					if (noOfRepeatedGroups < existingCycles) {
						List<Interval> rowsToRemove = new ArrayList<Interval>();
						for (int i = noOfRepeatedGroups; i < existingCycles; i++) {
							int rowIndex = i;
							rowsToRemove.add(cyclicTimeBarRowModel.getIntervals().get(rowIndex));
						}
						for (Interval cycleToRemove : rowsToRemove) {
							cyclicTimeBarRowModel.remInterval(cycleToRemove);
						}
					}
					updateTimes();
				}

			}
		});
		this.setNoOfRepeatedGroups(1);
	}

	private void updateTimes() {
		if (cyclicTimeBarRowModel.getIntervals().size() > 0) {
			ExperimentCycleModel lastCycle = ((ExperimentCycleModel) cyclicTimeBarRowModel.getIntervals().get(cyclicTimeBarRowModel.getIntervals().size() - 1));
			this.firePropertyChange(CYCLES_DURATION_PROP_NAME, cyclesDuration, cyclesDuration = lastCycle.getEndTime());
		}
	}


	public int getNoOfRepeatedGroups() {
		return noOfRepeatedGroups;
	}

	public void setNoOfRepeatedGroups(int noOfRepeatedGroups) {
		this.firePropertyChange(NO_OF_REPEATED_GROUPS_PROP_NAME, this.noOfRepeatedGroups, this.noOfRepeatedGroups = noOfRepeatedGroups);
	}

	public TimeBarModel getCyclicTimeBarModel() {
		return cyclicTimebarModel;
	}


	public double getCyclesDuration() {
		return cyclesDuration;
	}

	public double getCyclesDurationInSec() {
		return ExperimentUnit.MILLI_SEC.convertToSecond(cyclesDuration);
	}

	@Override
	protected String getDataStoreKey() {
		return CYCLIC_EXPERIMENT_MODEL_DATA_STORE_KEY;
	}
}
