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

import org.apache.commons.io.FilenameUtils;

import uk.ac.gda.beans.ObservableModel;

import com.google.gson.annotations.Expose;

public class EnergyCalibration extends ObservableModel {
	public static final String MANUAL_PROP_NAME = "manual";
	public static final String DATA_READY_PROP_NAME = "dataReady";

	private boolean dataReady;
	@Expose
	private boolean manual;

	private final CalibrationEnergyData edeData = new SampleData();
	private final CalibrationEnergyData refData = new ReferenceData();

	public static final String POLYNOMIAL_ORDER_PROP_NAME = "polynomialOrder";
	@Expose
	private int polynomialOrder = 2;

	private final CalibrationDetails calibrationDetails = new CalibrationDetails();

	public void setRefData(String referenceDataFileFullPath) throws Exception {
		refData.setDataFile(referenceDataFileFullPath);
		calibrationDetails.setReferenceDataFileName(FilenameUtils.getName(referenceDataFileFullPath));
		checkAndFireDataReady();
	}

	public void setEdeData(String sampleDataFileFullPath) throws Exception {
		edeData.setDataFile(sampleDataFileFullPath);
		calibrationDetails.setSampleDataFileName(FilenameUtils.getName(sampleDataFileFullPath));
		checkAndFireDataReady();
	}

	private void checkAndFireDataReady() {
		boolean ready = (refData.getFileName() != null && edeData.getFileName() != null);
		firePropertyChange(DATA_READY_PROP_NAME, dataReady, dataReady = ready);
	}

	public boolean getDataReady() {
		return dataReady;
	}

	public CalibrationEnergyData getRefData() {
		return refData;
	}

	public CalibrationEnergyData getEdeData() {
		return edeData;
	}

	public boolean isManual() {
		return manual;
	}

	public void setManual(boolean manual) {
		firePropertyChange(MANUAL_PROP_NAME, this.manual, this.manual = manual);
	}

	public int getPolynomialOrder() {
		return polynomialOrder;
	}

	public void setPolynomialOrder(int polynomialOrder) {
		this.firePropertyChange(POLYNOMIAL_ORDER_PROP_NAME, this.polynomialOrder, this.polynomialOrder = polynomialOrder);
	}

	public CalibrationDetails getCalibrationDetails() {
		return calibrationDetails;
	}
}