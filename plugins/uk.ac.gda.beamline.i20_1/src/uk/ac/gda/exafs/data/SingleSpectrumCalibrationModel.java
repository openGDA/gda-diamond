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

package uk.ac.gda.exafs.data;

public class SingleSpectrumCalibrationModel extends ObservableModel {
	private static SingleSpectrumCalibrationModel INSTANCE;

	public static final String I0_POSITION_PROP_NAME = "i0Position";
	private double i0Position;

	public static SingleSpectrumCalibrationModel getInstance() {
		if (INSTANCE == null) {
			INSTANCE = new SingleSpectrumCalibrationModel();
		}
		return INSTANCE;
	}

	public double getI0Position() {
		return i0Position;
	}

	public void setI0Position(double i0Position) {
		firePropertyChange(I0_POSITION_PROP_NAME, this.i0Position, this.i0Position = i0Position);
	}

}
