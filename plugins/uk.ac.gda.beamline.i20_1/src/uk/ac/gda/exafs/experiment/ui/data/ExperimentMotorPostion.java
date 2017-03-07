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

public class ExperimentMotorPostion extends ObservableModel {

	public static final String TARGET_I0_POSITION = "targetI0Position";
	private double targetI0Position;

	public static final String TARGET_IT_POSITION = "targetItPosition";
	private double targetItPosition;

	public static final String TARGET_IREF_POSITION = "targetIrefPosition";
	private double targetIrefPosition;

	private final ScannableSetup scannableSetup;

	public ExperimentMotorPostion(ScannableSetup scannableSetup) {
		this.scannableSetup = scannableSetup;
	}

	public ScannableSetup getScannableSetup() {
		return scannableSetup;
	}

	public double getTargetI0Position() {
		return targetI0Position;
	}

	public void setTargetI0Position(double targetI0Position) {
		this.firePropertyChange(TARGET_I0_POSITION, this.targetI0Position, this.targetI0Position = targetI0Position);
	}

	public double getTargetItPosition() {
		return targetItPosition;
	}

	public void setTargetItPosition(double targetItPosition) {
		this.firePropertyChange(TARGET_IT_POSITION, this.targetItPosition, this.targetItPosition = targetItPosition);
	}

	public double getTargetIrefPosition() {
		return targetIrefPosition;
	}

	public void setTargetIrefPosition(double targetIrefPosition) {
		this.firePropertyChange(TARGET_IREF_POSITION, this.targetIrefPosition, this.targetIrefPosition = targetIrefPosition);
	}
}