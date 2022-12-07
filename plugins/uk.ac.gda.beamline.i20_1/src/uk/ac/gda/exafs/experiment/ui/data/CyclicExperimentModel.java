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
import gda.scan.ede.CyclicExperiment;
import gda.scan.ede.TimeResolvedExperimentParameters;

public class CyclicExperimentModel extends TimeResolvedExperimentModel {

	private static final String CYCLIC_EXPERIMENT_MODEL_DATA_STORE_KEY = "CYCLIC_TIME_RESOLVED_EXPERIMENT_DATA";

	private static final String CYCLIC_EXPERIMENT_OBJ = "cyclicExperiment";

	public static final String NO_OF_REPEATED_GROUPS_PROP_NAME = "noOfRepeatedGroups";

	private static final int INITIAL_NO_OF_CYCLES = 2;

	public static final String TIME_BETWEEN_REPETITIONS_PROP_NAME = "timeBetweenRepetitions";

	private volatile int noOfRepeatedGroups;

	private volatile double timeBetweenRepetitions;

	public CyclicExperimentModel() {
		noOfRepeatedGroups = INITIAL_NO_OF_CYCLES;
	}

	@Override
	public void setup() {
		super.setup();
		noOfRepeatedGroups = getExperimentDataModel().getNumRepetitions();
		timeBetweenRepetitions = getExperimentDataModel().getTimeBetweenRepetitions();
	}
	@Override
	public TimeResolvedExperimentParameters getParametersBeanFromCurrentSettings() throws DeviceException {
		TimeResolvedExperimentParameters params = super.getParametersBeanFromCurrentSettings();
		params.setNumberOfRepetition(noOfRepeatedGroups);
		params.setTimeBetweenRepetitions(timeBetweenRepetitions);
		return params;
	}

	@Override
	public void setupFromParametersBean(TimeResolvedExperimentParameters params) {
		super.setupFromParametersBean(params);
		setNoOfRepeatedGroups(params.getNumberOfRepetition());
		setTimeBetweenRepetitions(params.getTimeBetweenRepetitions());
	}

	public int getNoOfRepeatedGroups() {
		return noOfRepeatedGroups;
	}

	public void setNoOfRepeatedGroups(int noOfRepeatedGroups) {
		this.firePropertyChange(NO_OF_REPEATED_GROUPS_PROP_NAME, this.noOfRepeatedGroups, this.noOfRepeatedGroups = noOfRepeatedGroups);
		getExperimentDataModel().setNumRepetitions(noOfRepeatedGroups);
	}

	public double getTimeBetweenRepetitions() {
		return timeBetweenRepetitions;
	}

	/**
	 * Set the time between repetitions/cycles
	 * @param timeBetweenRepetitions (seconds)
	 */
	public void setTimeBetweenRepetitions(double timeBetweenRepetitions) {
		this.firePropertyChange(TIME_BETWEEN_REPETITIONS_PROP_NAME, this.timeBetweenRepetitions, this.timeBetweenRepetitions = timeBetweenRepetitions);
		getExperimentDataModel().setTimeBetweenRepetitions(timeBetweenRepetitions);
	}

	@Override
	protected String getDataStoreKey() {
		return CYCLIC_EXPERIMENT_MODEL_DATA_STORE_KEY;
	}

	@Override
	protected String buildScanCommand() {
		StringBuilder scanCommand = buildScanCommand(CYCLIC_EXPERIMENT_OBJ, CyclicExperiment.class);
		scanCommand.append(String.format("%s.setRepetitions(%d);%n",CYCLIC_EXPERIMENT_OBJ, this.getNoOfRepeatedGroups()));
		scanCommand.append(String.format("%s.setTimeBetweenRepetitions(%g);%n",CYCLIC_EXPERIMENT_OBJ, this.getTimeBetweenRepetitions()));
		scanCommand.append(CYCLIC_EXPERIMENT_OBJ + ".runExperiment();");
		return scanCommand.toString();
	}

	@Override
	public void doStop() {
		stopScan(CYCLIC_EXPERIMENT_OBJ);
	}
}
