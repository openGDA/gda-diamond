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

import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.exafs.data.ScannableSetup;

public class SampleStageMotors extends ObservableModel {

	public enum ExperimentMotorPostionType {
		I0, It, IRef
	}

	public static final ExperimentMotorPostion[] scannables;

	static {
		scannables = new ExperimentMotorPostion[] {
				new ExperimentMotorPostion(ScannableSetup.ALIGNMENT_STAGE_X_POSITION),
				new ExperimentMotorPostion(ScannableSetup.ALIGNMENT_STAGE_Y_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_TABLEX_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_TABLEY_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_X_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_Y_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_Z_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_TOP_X_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_TOP_Y_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_TOP_Z_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_PITCH_POSITION),
				new ExperimentMotorPostion(ScannableSetup.SAMPLE_ROLL_POSITION),
				new ExperimentMotorPostion(ScannableSetup.USER_MOTOR1_POSITION),
				new ExperimentMotorPostion(ScannableSetup.USER_MOTOR2_POSITION)
		};
	}

	public static final SampleStageMotors INSTANCE = new SampleStageMotors();

	private SampleStageMotors() {}

	public static final String USE_IREF_PROP_NAME = "useIref";
	private boolean useIref;

	public static final String SELECTED_MOTORS_PROP_NAME = "selectedMotors";
	private ExperimentMotorPostion[] selectedMotors = new ExperimentMotorPostion[]{
			//			scannables[0], scannables[1]
	};

	public ExperimentMotorPostion[] getSelectedMotors() {
		return selectedMotors;
	}

	public void setSelectedMotors(ExperimentMotorPostion[] selectedMotors) {
		this.firePropertyChange(SELECTED_MOTORS_PROP_NAME, this.selectedMotors, this.selectedMotors = selectedMotors);
	}

	public boolean isUseIref() {
		return useIref;
	}

	public void setUseIref(boolean useIref) {
		this.firePropertyChange(USE_IREF_PROP_NAME, this.useIref, this.useIref = useIref);
	}

	public String getFormattedSelectedPositions(ExperimentMotorPostionType type) {
		StringBuilder position = new StringBuilder();
		position.append("{");
		for (int i=0; i < selectedMotors.length; i++) {
			position.append("'" +selectedMotors[i].getScannableSetup().getScannableName() + "'" + ":");
			double positionValue;
			if (type == ExperimentMotorPostionType.I0) {
				positionValue = selectedMotors[i].getTargetI0Position();
			} else if (type == ExperimentMotorPostionType.It) {
				positionValue = selectedMotors[i].getTargetItPosition();
			} else {
				positionValue = selectedMotors[i].getTargetIrefPosition();
			}
			position.append(positionValue);
			if (selectedMotors.length > 1 & i < selectedMotors.length - 1) {
				position.append(",");
			}
		}
		position.append("}");
		return position.toString();
	}
}

