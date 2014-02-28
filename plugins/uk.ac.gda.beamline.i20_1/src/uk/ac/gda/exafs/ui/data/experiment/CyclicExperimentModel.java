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

import uk.ac.gda.beamline.i20_1.utils.ExperimentTimeHelper;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.ui.data.experiment.SampleStageMotors.ExperimentMotorPostionType;
import de.jaret.util.date.Interval;
import de.jaret.util.ui.timebars.model.DefaultRowHeader;
import de.jaret.util.ui.timebars.model.DefaultTimeBarModel;
import de.jaret.util.ui.timebars.model.DefaultTimeBarRowModel;
import de.jaret.util.ui.timebars.model.TimeBarModel;

public class CyclicExperimentModel extends TimeResolvedExperimentModel {

	private static final String CYCLIC_EXPERIMENT_MODEL_DATA_STORE_KEY = "CYCLIC_TIME_RESOLVED_EXPERIMENT_DATA";

	private static final String CYCLIC_EXPERIMENT_OBJ = "cyclicExperiment";

	public static final String NO_OF_REPEATED_GROUPS_PROP_NAME = "noOfRepeatedGroups";
	private int noOfRepeatedGroups;
	private static final int INITIAL_NO_OF_CYCLES = 2;

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
						CyclicExperimentDataModel experimentCycleModel = (CyclicExperimentDataModel) object;
						experimentCycleModel.setTimes(startTime, (double) evt.getNewValue());
						startTime += experimentCycleModel.getDuration();
					}
					updateTimes();
				} else if (evt.getPropertyName().equals(NO_OF_REPEATED_GROUPS_PROP_NAME)) {
					int existingCycles = cyclicTimeBarRowModel.getIntervals().size();
					for (int i=existingCycles; i < noOfRepeatedGroups; i++) {
						CyclicExperimentDataModel experimentCycleModel = new CyclicExperimentDataModel(CyclicExperimentModel.this);
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
		this.setNoOfRepeatedGroups(INITIAL_NO_OF_CYCLES);
	}

	private void updateTimes() {
		if (cyclicTimeBarRowModel.getIntervals().size() > 0) {
			CyclicExperimentDataModel lastCycle = ((CyclicExperimentDataModel) cyclicTimeBarRowModel.getIntervals().get(cyclicTimeBarRowModel.getIntervals().size() - 1));
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

	@Override
	protected String buildScanCommand() {
		StringBuilder builder = new StringBuilder("from gda.scan.ede import EdeLinearExperiment;");
		if (this.getExperimentDataModel().isUseNoOfAccumulationsForI0()) {
			builder.append(String.format(CYCLIC_EXPERIMENT_OBJ + " = EdeCyclicExperiment(%f, %d",
					ExperimentTimeHelper.fromMilliToSec(this.getExperimentDataModel().getI0IntegrationTime()),
					this.getExperimentDataModel().getI0NumberOfAccumulations()));
		} else {
			builder.append(String.format(CYCLIC_EXPERIMENT_OBJ + " = EdeCyclicExperiment(%f",
					ExperimentTimeHelper.fromMilliToSec(this.getExperimentDataModel().getI0IntegrationTime())));
		}
		builder.append(String.format(", %s, mapToJava(%s), mapToJava(%s), \"%s\", \"%s\", \"%s\", %d);",
				TIMING_GROUPS_OBJ_NAME,
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.I0),
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.It),
				DetectorModel.INSTANCE.getCurrentDetector().getName(),
				DetectorModel.TOPUP_CHECKER,
				DetectorModel.SHUTTER_NAME,
				this.getNoOfRepeatedGroups()));
		builder.append(String.format(CYCLIC_EXPERIMENT_OBJ + ".setNoOfSecPerSpectrumToPublish(%d);", this.getNoOfSecPerSpectrumToPublish()));
		if (SampleStageMotors.INSTANCE.isUseIref()) {
			builder.append(String.format(CYCLIC_EXPERIMENT_OBJ + ".setIRefParameters(mapToJava(%s), %f, %d);",
					SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.IRef),
					ExperimentTimeHelper.fromMilliToSec(this.getExperimentDataModel().getIrefIntegrationTime()), this.getExperimentDataModel().getIrefNoOfAccumulations()));
		}
		builder.append(CYCLIC_EXPERIMENT_OBJ + ".runExperiment();");
		return builder.toString();
	}
}
