/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

import com.google.gson.Gson;
import com.google.gson.annotations.Expose;

public class CalibrationDetails extends ObservableModel {

	private static final Gson gson = new Gson();

	@Expose
	private String referenceDataFileName;
	@Expose
	private String sampleDataFileName;

	public static final String CALIBRATION_RESULT_PROP_NAME = "calibrationResult";
	@Expose
	private PolynomialFunction calibrationResult;

	public String getReferenceDataFileName() {
		return referenceDataFileName;
	}
	public void setReferenceDataFileName(String referenceDataFileName) {
		this.referenceDataFileName = referenceDataFileName;
	}
	public String getSampleDataFileName() {
		return sampleDataFileName;
	}
	public void setSampleDataFileName(String sampleDataFileName) {
		this.sampleDataFileName = sampleDataFileName;
	}
	public PolynomialFunction getCalibrationResult() {
		return calibrationResult;
	}
	public void setCalibrationResult(PolynomialFunction calibrationResult) {
		this.firePropertyChange(CALIBRATION_RESULT_PROP_NAME, this.calibrationResult, this.calibrationResult = calibrationResult);
	}

	@Override
	public String toString() {
		return gson.toJson(this);
	}

	public static CalibrationDetails toObject(String str) {
		return gson.fromJson(str, CalibrationDetails.class);
	}
}
