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

import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.exafs.data.ClientConfig.ScannableSetup;

public class SampleStageMotors extends ObservableModel {

	public static final SampleStageMotors INSTANCE = new SampleStageMotors();

	public static final ExperimentMotorPostion[] scannables;

	static {
		scannables = new ExperimentMotorPostion[] {
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_X_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_Y_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_TOP_X_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_TOP_Y_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_TOP_Z_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_PITCH_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_ROLL_POSITION)
		};
	}

	private SampleStageMotors() {}

	public static final String SELECTED_MOTORS = "selectedMotors";
	private ExperimentMotorPostion[] selectedMotors = new ExperimentMotorPostion[]{};

	public ExperimentMotorPostion[] getSelectedMotors() {
		return selectedMotors;
	}

	public void setSelectedMotors(ExperimentMotorPostion[] selectedMotors) {
		this.firePropertyChange(SELECTED_MOTORS, this.selectedMotors, this.selectedMotors = selectedMotors);
	}

}

