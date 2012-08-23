/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i13i;

import gda.device.Scannable;

public class StageCompositeDefinition {
	Scannable scannable;
	int decimalPlaces = 3;
	double stepSize=1.;
	double smallStep=1.;
	double bigStep=10.;
	/**
	 * 0 - RotationView - SWT_NONE
	 * 1 - RotationView - SWT_SINGLE
	 */
	int controlType=1;
	public Scannable getScannable() {
		return scannable;
	}
	public void setScannable(Scannable scannable) {
		this.scannable = scannable;
	}
	public int getDecimalPlaces() {
		return decimalPlaces;
	}
	public void setDecimalPlaces(int decimalPlaces) {
		this.decimalPlaces = decimalPlaces;
	}
	public double getStepSize() {
		return stepSize;
	}
	public void setStepSize(double stepSize) {
		this.stepSize = stepSize;
	}
	public int getControlType() {
		return controlType;
	}
	public void setControlType(int controlType) {
		this.controlType = controlType;
	}
	public double getSmallStep() {
		return smallStep;
	}
	public void setSmallStep(double smallStep) {
		this.smallStep = smallStep;
	}
	public double getBigStep() {
		return bigStep;
	}
	public void setBigStep(double bigStep) {
		this.bigStep = bigStep;
	}
	

}
