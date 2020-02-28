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
import gda.scan.ede.TimeResolvedExperimentParameters;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.experiment.ui.data.SampleStageMotors.ExperimentMotorPostionType;

public class CyclicExperimentModel extends TimeResolvedExperimentModel {

	private static final String CYCLIC_EXPERIMENT_MODEL_DATA_STORE_KEY = "CYCLIC_TIME_RESOLVED_EXPERIMENT_DATA";

	private static final String CYCLIC_EXPERIMENT_OBJ = "cyclicExperiment";

	public static final String NO_OF_REPEATED_GROUPS_PROP_NAME = "noOfRepeatedGroups";

	private static final int INITIAL_NO_OF_CYCLES = 2;

	private int noOfRepeatedGroups;

	private double cyclesDuration;

	public CyclicExperimentModel() {
		this.setNoOfRepeatedGroups(INITIAL_NO_OF_CYCLES);
	}

	@Override
	public TimeResolvedExperimentParameters getParametersBeanFromCurrentSettings() throws DeviceException {
		TimeResolvedExperimentParameters params = super.getParametersBeanFromCurrentSettings();
		params.setNumberOfRepetition(noOfRepeatedGroups);
		return params;
	}

	@Override
	public void setupFromParametersBean(TimeResolvedExperimentParameters params) {
		setNoOfRepeatedGroups(params.getNumberOfRepetition());
	}

	public int getNoOfRepeatedGroups() {
		return noOfRepeatedGroups;
	}

	public void setNoOfRepeatedGroups(int noOfRepeatedGroups) {
		this.firePropertyChange(NO_OF_REPEATED_GROUPS_PROP_NAME, this.noOfRepeatedGroups, this.noOfRepeatedGroups = noOfRepeatedGroups);
	}

	public double getCyclesDuration() {
		return cyclesDuration;
	}

	public double getCyclesDurationInSec() {
		return ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertTo(cyclesDuration, ExperimentUnit.SEC);
	}

	@Override
	protected String getDataStoreKey() {
		return CYCLIC_EXPERIMENT_MODEL_DATA_STORE_KEY;
	}

	@Override
	protected String buildScanCommand() {
		StringBuilder builder = new StringBuilder("from gda.scan.ede import CyclicExperiment;");
		builder.append(String.format(CYCLIC_EXPERIMENT_OBJ + " = CyclicExperiment(%f",
				ExperimentUnit.DEFAULT_EXPERIMENT_UNIT_FOR_I0_IREF.convertTo(this.getExperimentDataModel().getI0IntegrationTime(), ExperimentUnit.SEC)));

		builder.append(String.format(", %s, mapToJava(%s), mapToJava(%s), \"%s\", \"%s\", \"%s\", %d );\n",
				TIMING_GROUPS_OBJ_NAME,
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.I0),
				SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.It),
				DetectorModel.INSTANCE.getCurrentDetector().getName(),
				DetectorModel.TOPUP_CHECKER,
				DetectorModel.SHUTTER_NAME,
				this.getNoOfRepeatedGroups()));

		builder.append(String.format(CYCLIC_EXPERIMENT_OBJ + ".setNoOfSecPerSpectrumToPublish(%f);\n", this.getNoOfSecPerSpectrumToPublish()));
		builder.append(String.format(CYCLIC_EXPERIMENT_OBJ + ".setFileNameSuffix(\"%s\");\n", this.getExperimentDataModel().getFileNameSuffix()));
		builder.append(String.format(CYCLIC_EXPERIMENT_OBJ + ".setSampleDetails(\"%s\");\n", this.getExperimentDataModel().getSampleDetails()));

		// Add timing groups
		addTimingGroupsMethodCallToCommand(CYCLIC_EXPERIMENT_OBJ, builder);

		// Add number of I0 accumulations
		addI0AccumulationMethodCallToCommand(CYCLIC_EXPERIMENT_OBJ, builder);

		// Add external Tfg command
		addItTriggerMethodCallToCommand(CYCLIC_EXPERIMENT_OBJ, builder);

		// Add Iref commands
		addIRefMethodCallStrToCommand(CYCLIC_EXPERIMENT_OBJ, builder);

		builder.append(CYCLIC_EXPERIMENT_OBJ + ".runExperiment();");
		return builder.toString();
	}
}
