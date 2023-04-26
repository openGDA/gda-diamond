/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

package gda.device.robot;

import java.util.Collections;
import java.util.List;
import java.util.Objects;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;

public class MecaSampleHolderControl  extends SamplePlateMoverBase  {

	private static final Logger logger = LoggerFactory.getLogger(MecaSampleHolderControl.class);

	private Scannable sampleHolderNumberScannable;
	private Scannable moveToScanningAreaScannable;
	private Scannable moveToCassetteAreaScannable;

	private MecaStatusChecker statusChecker = new MecaStatusChecker();

	// Cassette area : theta1 <50, Scanning area : theta1 > 135

	// ALlowed range of sample holder numbers that can be used
	private int minAllowedSampleNumber = 1;
	private int maxAllowedSampleNumber = 43;

	@Override
	public void configure() {
		Objects.requireNonNull(sampleHolderNumberScannable, "Scannable for setting sample holder number has not been set.");
		Objects.requireNonNull(moveToCassetteAreaScannable, "Scannable for moving to cassette area not been set.");
		Objects.requireNonNull(moveToScanningAreaScannable, "Scannable for moving to scanning area not been set.");
		Objects.requireNonNull(statusChecker, "Status checker has not been set");

		setInputNames(new String[] {getName()});
		setOutputFormat(new String[] {"%.0f"});
		setConfigured(true);
	}
	/**
	 * Move specified sample holder into the scanning area. Any sample holder currently held is replaced
	 * in the cassette area first (by {@link #unloadPlate()}.
	 */
	@Override
	public void loadPlate(String samplePlateName) throws DeviceException {
		// Unload the sample holder if the number to be moved to beam is not the one currently set in Epics

		// Sample plate names are always integers
		int currentSample = parseInt(sampleHolderNumberScannable.getPosition().toString());
		int requestedSample = parseInt(samplePlateName);

		logger.info("Current sample holder in Epics : {}, sample holder to be picked up : {}", currentSample, requestedSample);

		if (!sampleNumberInRange(requestedSample)) {
			throw new DeviceException("Could not load sample plate "+requestedSample+". Value is not in range "+minAllowedSampleNumber+" ... "+maxAllowedSampleNumber);
		}
		if (currentSample != requestedSample) {
			unloadPlate();
		}

		logger.info("Setting sample holder number to : {}", samplePlateName);
		sampleHolderNumberScannable.moveTo(samplePlateName);
		statusChecker.waitForMove();
	}

	private boolean sampleNumberInRange(int num) {
		return num >= minAllowedSampleNumber && num <= maxAllowedSampleNumber;
	}

	/**
	 * Convert 'val' to an int.
	 *
	 * @param val string representation of an int or double
	 * @return integer value of val
	 */
	private int parseInt(String val) {
		return Double.valueOf(val).intValue();
	}

	/**
	 * Move to the cassette area (unload the currently held sample holder)
	 */
	@Override
	public void unloadPlate() throws DeviceException {
		String currentSampleHolderNumber = sampleHolderNumberScannable.getPosition().toString();
		logger.info("Moving to cassette area to return sample holder {}", currentSampleHolderNumber);
		moveToCassetteAreaScannable.moveTo(1);
		statusChecker.waitForMove();
		logger.info("Move to cassette area finished");
	}

	@Override
	public void moveToBeam() throws DeviceException {
		logger.info("Moving sample holder to scanning area...");
		moveToScanningAreaScannable.moveTo(1);
		statusChecker.waitForMove();
		logger.info("Move to scanning area finished");
	}

	@Override
	public List<String> getPlateNames() {
		return Collections.emptyList();
	}

	/**
	 * @return Name of the sample holder currently set in epics
	*/
	@Override
	public String getCurrentPlate() {
		try {
			return sampleHolderNumberScannable.getPosition().toString();
		} catch (DeviceException e) {
			logger.error("Problem getting current plate name from Epics",e);
			return "";
		}
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		return sampleHolderNumberScannable.getPosition();
	}

	public Scannable getSampleHolderNumberScannable() {
		return sampleHolderNumberScannable;
	}

	public void setSampleHolderNumberScannable(Scannable sampleHolderNumberScannable) {
		this.sampleHolderNumberScannable = sampleHolderNumberScannable;
	}

	public Scannable getMoveToScanningAreaScannable() {
		return moveToScanningAreaScannable;
	}

	public void setMoveToScanningAreaScannable(Scannable moveToScanningAreaScannable) {
		this.moveToScanningAreaScannable = moveToScanningAreaScannable;
	}

	public Scannable getMoveToCassetteAreaScannable() {
		return moveToCassetteAreaScannable;
	}

	public void setMoveToCassetteAreaScannable(Scannable moveToCassetteAreaScannable) {
		this.moveToCassetteAreaScannable = moveToCassetteAreaScannable;
	}

	public int getMinAllowedSampleNumber() {
		return minAllowedSampleNumber;
	}

	public void setMinAllowedSampleNumber(int minAllowedSampleNumber) {
		this.minAllowedSampleNumber = minAllowedSampleNumber;
	}

	public int getMaxAllowedSampleNumber() {
		return maxAllowedSampleNumber;
	}

	public void setMaxAllowedSampleNumber(int maxAllowedSampleNumber) {
		this.maxAllowedSampleNumber = maxAllowedSampleNumber;
	}

	public MecaStatusChecker getStatusChecker() {
		return statusChecker;
	}
	public void setStatusChecker(MecaStatusChecker statusChecker) {
		this.statusChecker = statusChecker;
	}
}
