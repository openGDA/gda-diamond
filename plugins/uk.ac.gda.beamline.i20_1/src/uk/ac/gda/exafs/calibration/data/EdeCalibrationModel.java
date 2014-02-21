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

package uk.ac.gda.exafs.calibration.data;

import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;

import uk.ac.gda.beans.ObservableModel;

public class EdeCalibrationModel extends ObservableModel {
	public static final String MANUAL_PROP_NAME = "manual";
	private boolean manual;

	public static final String DATA_READY_PROP_NAME = "dataReady";
	private boolean dataReady;

	private final CalibrationDataModel edeData = new EdeCalibrationDataModel();
	private final CalibrationDataModel refData = new RefCalibrationDataModel();

	private PolynomialFunction calibrationResult;

	public void setRefData(String refFileName) throws Exception {
		refData.setDataFile(refFileName);
		checkAndFireDataReady();
	}

	public void setEdeData(String edeSpectrumDataFileName) throws Exception {
		edeData.setDataFile(edeSpectrumDataFileName);
		checkAndFireDataReady();
	}

	private void checkAndFireDataReady() {
		boolean ready = (refData.getFileName() != null && edeData.getFileName() != null);
		firePropertyChange(DATA_READY_PROP_NAME, dataReady, dataReady = ready);
	}

	public boolean getDataReady() {
		return dataReady;
	}

	public CalibrationDataModel getRefData() {
		return refData;
	}
	public CalibrationDataModel getEdeData() {
		return edeData;
	}
	public boolean isManual() {
		return manual;
	}
	public void setManual(boolean manual) {
		firePropertyChange(MANUAL_PROP_NAME, this.manual, this.manual = manual);
	}

	public PolynomialFunction getCalibrationResult() {
		return calibrationResult;
	}

	public void setCalibrationResult(PolynomialFunction calibrationResult) {
		this.calibrationResult = calibrationResult;
	}
}

