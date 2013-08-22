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

import gda.device.Scannable;
import gda.device.scannable.AlignmentStage;
import gda.device.scannable.AlignmentStageScannable;
import gda.device.scannable.AlignmentStageScannable.AlignmentStageDevice;
import gda.factory.Finder;
import gda.scan.ede.drivers.SingleSpectrumDriver;

public class EDECalibrationModel extends ObservableModel {
	public static final EDECalibrationModel INSTANCE = new EDECalibrationModel();

	public static final String I0_X_POSITION_PROP_NAME = "i0xPosition";
	private double i0xPosition;

	public static final String I0_Y_POSITION_PROP_NAME = "i0yPosition";
	private double i0yPosition;

	public static final String IT_X_POSITION_PROP_NAME = "iTxPosition";
	private double iTxPosition;

	public static final String IT_Y_POSITION_PROP_NAME = "iTyPosition";
	private double iTyPosition;

	public static final String I0_INTEGRATION_TIME_PROP_NAME = "i0IntegrationTime";
	private double i0IntegrationTime;

	public static final String I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME = "i0NumberOfAccumulations";
	private int i0NumberOfAccumulations;

	public static final String IT_INTEGRATION_TIME_PROP_NAME = "itIntegrationTime";
	private double itIntegrationTime;

	public static final String IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME = "itNumberOfAccumulations";
	private int itNumberOfAccumulations;

	public static final String FILE_NAME_PROP_NAME = "fileName";
	private String fileName;

	protected EDECalibrationModel() {
		Scannable scannable = Finder.getInstance().find("alignment_stage");
		if (scannable != null && scannable instanceof AlignmentStage) {
			AlignmentStage alignmentStageScannable = (AlignmentStage) scannable;
			AlignmentStageDevice hole = alignmentStageScannable.getAlignmentStageDevice(AlignmentStageScannable.AlignmentStageDevice.hole.name());
			this.setI0xPosition(hole.getLocation().getxPosition());
			this.setI0yPosition(hole.getLocation().getyPosition());

			AlignmentStageDevice foil = alignmentStageScannable.getAlignmentStageDevice(AlignmentStageScannable.AlignmentStageDevice.hole.name());
			this.setiTxPosition(foil.getLocation().getxPosition());
			this.setiTyPosition(foil.getLocation().getyPosition());
		}
	}

	public void doScan() throws Exception {
		SingleSpectrumDriver singleSpectrumDriver = new SingleSpectrumDriver(
				DetectorConfig.INSTANCE.getCurrentDetector().getName(),
				i0IntegrationTime,
				i0NumberOfAccumulations,
				itIntegrationTime,
				itNumberOfAccumulations);
		singleSpectrumDriver.setInBeamPosition(i0xPosition, i0yPosition);
		singleSpectrumDriver.setInBeamPosition(iTxPosition, iTyPosition);
		this.setFileName(singleSpectrumDriver.doCollection());
	}

	public void setFileName(String value) {
		firePropertyChange(I0_X_POSITION_PROP_NAME, fileName, fileName = value);
	}

	public String getFileName() {
		return fileName;
	}

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

	public int getI0NumberOfAccumulations() {
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

	public void setItNumberOfAccumulations(int value) {
		firePropertyChange(IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME, itNumberOfAccumulations, itNumberOfAccumulations = value);
	}

	public double getiTxPosition() {
		return iTxPosition;
	}

	public void setiTxPosition(double value) {
		firePropertyChange(IT_X_POSITION_PROP_NAME, iTxPosition, iTxPosition = value);
	}

	public double getiTyPosition() {
		return iTyPosition;
	}

	public void setiTyPosition(double value) {
		firePropertyChange(IT_Y_POSITION_PROP_NAME, iTyPosition, iTyPosition = value);
	}
}
