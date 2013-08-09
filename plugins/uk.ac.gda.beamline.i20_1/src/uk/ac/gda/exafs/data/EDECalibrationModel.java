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

public class EDECalibrationModel extends ObservableModel {
	public static final EDECalibrationModel INSTANCE = new EDECalibrationModel();

	public static final String I0_X_POSITION_PROP_NAME = "i0xPosition";
	private double i0xPosition;

	public static final String I0_Y_POSITION_PROP_NAME = "i0yPosition";
	private double i0yPosition;

	public static final String I0_INTEGRATION_TIME_PROP_NAME = "i0IntegrationTime";
	private double i0IntegrationTime;

	public static final String I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME = "i0NumberOfAccumulations";
	private int i0NumberOfAccumulations;

	public static final String IT_INTEGRATION_TIME_PROP_NAME = "itIntegrationTime";
	private double itIntegrationTime;

	public static final String IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME = "itNumberOfAccumulations";
	private int itNumberOfAccumulations;

	public double getI0xPosition() {
		return i0xPosition;
	}

	public void setI0xPosition(double value) {
		firePropertyChange(I0_X_POSITION_PROP_NAME, i0xPosition, i0xPosition = value);
	}

	public double getI0yPosition() {
		return i0yPosition;
	}

	public void setI0yPosition(double value) {
		firePropertyChange(I0_Y_POSITION_PROP_NAME, i0yPosition, i0yPosition = value);
	}

	public double getI0IntegrationTime() {
		return i0IntegrationTime;
	}
	public void setI0IntegrationTime(double value) {
		firePropertyChange(I0_INTEGRATION_TIME_PROP_NAME, i0IntegrationTime, i0IntegrationTime = value);
	}
	public double getI0NumberOfAccumulations() {
		return i0NumberOfAccumulations;
	}
	public void setI0NumberOfAccumulations(int value) {
		firePropertyChange(I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME, i0NumberOfAccumulations, i0NumberOfAccumulations = value);
	}
	public double getItIntegrationTime() {
		return itIntegrationTime;
	}
	public void setItIntegrationTime(double value) {
		firePropertyChange(IT_INTEGRATION_TIME_PROP_NAME, itIntegrationTime, itIntegrationTime = value);
	}
	public int getItNumberOfAccumulations() {
		return itNumberOfAccumulations;
	}
	public void setITNumberOfAccumulations(int value) {
		firePropertyChange(IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME, itNumberOfAccumulations, itNumberOfAccumulations = value);
	}
}
