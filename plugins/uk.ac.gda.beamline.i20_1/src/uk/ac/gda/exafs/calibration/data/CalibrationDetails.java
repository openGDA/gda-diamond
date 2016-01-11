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

import java.io.Serializable;

import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
import org.apache.commons.math3.util.Precision;

import com.google.gson.Gson;
import com.google.gson.annotations.Expose;

import uk.ac.gda.beans.ObservableModel;

public class CalibrationDetails extends ObservableModel implements Serializable {

	private static final Gson gson = new Gson();

	@Expose
	private String referenceDataFileName;
	@Expose
	private String sampleDataFileName;

	public static final String CALIBRATION_RESULT_PROP_NAME = "calibrationResult";
	@Expose
	private PolynomialFunction calibrationResult = new PolynomialFunction(new double[] {0,2048});

	public static final String REFERENCE_RANGE_START_PROP_NAME = "refRanceStart";
	@Expose
	private double refRangeStart;

	public static final String REFERENCE_RANGE_END_PROP_NAME = "refRanceEnd";
	@Expose
	private double refRangeEnd;

	public static final String SAMPLE_RANGE_START_PROP_NAME = "sampleRangeStart";
	@Expose
	private double sampleRangeStart;

	public static final String SAMPLE_RANGE_END_PROP_NAME = "sampleRangeEnd";
	@Expose
	private double sampleRangeEnd;

	private static final String GOODNESS_OF_FIT_PROP_NAME = "goodnessOfFit";
	@Expose
	private double goodnessOfFit;

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

	public double getRefRangeStart() {
		return refRangeStart;
	}
	public void setRefRangeStart(double refRanceStart) {
		this.firePropertyChange(REFERENCE_RANGE_START_PROP_NAME, refRangeStart, refRangeStart = refRanceStart);
	}
	public double getRefRangeEnd() {
		return refRangeEnd;
	}
	public void setRefRangeEnd(double refRanceEnd) {
		this.firePropertyChange(REFERENCE_RANGE_END_PROP_NAME, refRangeEnd, refRangeEnd = refRanceEnd);
	}
	public double getSampleRangeStart() {
		return sampleRangeStart;
	}
	public void setSampleRangeStart(double sampleRanceStart) {
		this.firePropertyChange(SAMPLE_RANGE_START_PROP_NAME, sampleRangeStart, sampleRangeStart = sampleRanceStart);
	}
	public double getSampleRangeEnd() {
		return sampleRangeEnd;
	}
	public void setSampleRanceEnd(double sampleRanceEnd) {
		this.firePropertyChange(SAMPLE_RANGE_END_PROP_NAME, sampleRangeEnd, sampleRangeEnd = sampleRanceEnd);
	}

	public void setGoodnessOfFit(double goodnessOfFit) {
		this.firePropertyChange(GOODNESS_OF_FIT_PROP_NAME, this.goodnessOfFit, this.goodnessOfFit = goodnessOfFit);
	}

	public double getGoodnessOfFit() {
		return goodnessOfFit;
	}

	@Override
	public String toString() {
		return gson.toJson(this);
	}

	public static CalibrationDetails toObject(String str) {
		return gson.fromJson(str, CalibrationDetails.class);
	}

	public String getFormattedPolinormal() {
		double[] polynom = calibrationResult.getCoefficients();
		for (int i = 0; i < polynom.length; i++) {
			polynom[i] = Precision.round(polynom[i], 3);
		}
		return new PolynomialFunction(polynom).toString();
	}
}
