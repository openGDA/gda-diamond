/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.b16.experimentdefinition;

import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;

/**
 * A bean which holds the top level parameter files used in the
 * checking algorithm.
 */
public class ExafsValidatorBean /*extends AbstractValidator*/ {
    private IScanParameters   scanParams;
	private ISampleParameters    sampleParams;
    private IDetectorParameters  detectorParams;
    private IOutputParameters    outputParams;
    
    private String outputParamsName, detectorParamsName, sampleParamsName, scanParamsName;
    
    
	/**
	 * @return Returns the scanParams.
	 */
	public IScanParameters getScanParams() {
		return scanParams;
	}
	/**
	 * @param scanParams The scanParams to set.
	 */
	public void setScanParams(IScanParameters scanParams) {
		this.scanParams = scanParams;
	}

	/**
	 * @return Returns the sampleParams.
	 */
	public ISampleParameters getSampleParams() {
		return sampleParams;
	}
	/**
	 * @param sampleParams The sampleParams to set.
	 */
	public void setSampleParams(ISampleParameters sampleParams) {
		this.sampleParams = sampleParams;
	}
	/**
	 * @return Returns the detectorParams.
	 */
	public IDetectorParameters getDetectorParams() {
		return detectorParams;
	}
	/**
	 * @param detectorParams The detectorParams to set.
	 */
	public void setDetectorParams(IDetectorParameters detectorParams) {
		this.detectorParams = detectorParams;
	}
	/**
	 * @return Returns the outputParams.
	 */
	public IOutputParameters getOutputParams() {
		return outputParams;
	}
	/**
	 * @param outputParams The outputParams to set.
	 */
	public void setOutputParams(IOutputParameters outputParams) {
		this.outputParams = outputParams;
	}
	/**
	 * @return Returns the outputParamsName.
	 */
	public String getOutputParamsName() {
		return outputParamsName;
	}
	/**
	 * @param outputParamsName The outputParamsName to set.
	 */
	public void setOutputParamsName(String outputParamsName) {
		this.outputParamsName = outputParamsName;
	}
	/**
	 * @return Returns the detectorParamsName.
	 */
	public String getDetectorParamsName() {
		return detectorParamsName;
	}
	/**
	 * @param detectorParamsName The detectorParamsName to set.
	 */
	public void setDetectorParamsName(String detectorParamsName) {
		this.detectorParamsName = detectorParamsName;
	}
	/**
	 * @return Returns the sampleParamsName.
	 */
	public String getSampleParamsName() {
		return sampleParamsName;
	}
	/**
	 * @param sampleParamsName The sampleParamsName to set.
	 */
	public void setSampleParamsName(String sampleParamsName) {
		this.sampleParamsName = sampleParamsName;
	}
	/**
	 * @return Returns the scanParamsName.
	 */
	public String getScanParamsName() {
		return scanParamsName;
	}
	/**
	 * @param scanParamsName The scanParamsName to set.
	 */
	public void setScanParamsName(String scanParamsName) {
		this.scanParamsName = scanParamsName;
	}
}
