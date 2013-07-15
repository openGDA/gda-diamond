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

package gda.scan;

import gda.data.scan.datawriter.DataWriter;
import gda.device.detector.StripDetector;

import java.util.List;

import uk.ac.gda.exafs.ui.data.EdeScanParameters;

/**
 * Runs a single shot scan for EDE.
 * <p>
 * So this: moves sample to correct position, opens/closes shutter, runs a SimpleContinuousScan and writes data to given Nexus file.
 * <p>
 * Also holds data in memory for quick retrieval for online data. 
 */
public class EdeScan {

	EdeScanParameters scanParameters;
	EdeScanPosition motorPositions;
	EdeScanType scanType;
	DataWriter fileWriter;
	private StripDetector theDetector;
	private SimpleContinuousScan theScan;
	
	public EdeScan(EdeScanParameters scanParameters, EdeScanPosition motorPositions, EdeScanType scanType, DataWriter fileWriter, StripDetector theDetector) {
		super();
		this.scanParameters = scanParameters;
		this.motorPositions = motorPositions;
		this.scanType = scanType;
		this.fileWriter = fileWriter;
		this.theDetector = theDetector;
	}
	
	public void runScan() throws Exception {
		validate();
		theDetector.loadParameters(scanParameters);
		motorPositions.moveIntoPosition();
		theScan = new SimpleContinuousScan(theDetector);
		theScan.setDataWriter(fileWriter);
		theScan.runScan();
	}
	
	private void validate() throws IllegalArgumentException {
		if (motorPositions == null){
			throw new IllegalArgumentException("Cannot run EdeScan as sample motor positions have not been supplied");
		}
		if (scanParameters == null){
			throw new IllegalArgumentException("Cannot run EdeScan as scan parameters have not been supplied");
		}
	}
	
	public List<ScanDataPoint> getData() {
		return theScan.getDataPoints(0, theScan.getNumberOfAvailablePoints() - 1);
	}

	public EdeScanParameters getScanParameters() {
		return scanParameters;
	}

	public void setScanParameters(EdeScanParameters scanParameters) {
		this.scanParameters = scanParameters;
	}

	public EdeScanPosition getMotorPositions() {
		return motorPositions;
	}
	public void setMotorPositions(EdeScanPosition motorPositions) {
		this.motorPositions = motorPositions;
	}
	public EdeScanType getScanType() {
		return scanType;
	}
	public void setScanType(EdeScanType scanType) {
		this.scanType = scanType;
	}
	public DataWriter getFileWriter() {
		return fileWriter;
	}
	public void setFileWriter(DataWriter fileWriter) {
		this.fileWriter = fileWriter;
	}
}
