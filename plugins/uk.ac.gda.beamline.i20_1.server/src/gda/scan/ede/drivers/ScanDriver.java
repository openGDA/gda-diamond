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

package gda.scan.ede.drivers;

import java.util.Map;

import org.dawnsci.ede.EdePositionType;

import gda.device.DeviceException;
import gda.scan.ede.position.EdeScanMotorPositions;
import gda.scan.ede.position.EdeScanPosition;

public abstract class ScanDriver {

	protected EdeScanPosition inbeamPosition;
	protected EdeScanPosition outbeamPosition;
	protected EdeScanPosition referencePosition;
	protected String fileTemplate;

	/**
	 * @return the full path of the name of the summary ASCII format file
	 * @throws Exception
	 */
	public abstract String doCollection() throws Exception;

	protected void validate() throws Exception {
		if (inbeamPosition == null) {
			throw new Exception("In beam (It) position has not been set!");
		}
		if (outbeamPosition == null) {
			throw new Exception("Out of beam (I0) position has not been set!");
		}

	}

	/**
	 * Takes either the motor positions as doubles or a String and null, where the String is one of the alignment stage
	 * positions.
	 * @throws DeviceException
	 *
	 */
	public void setInBeamPosition(Map<String, Double> scanableMotorPositions) throws DeviceException {
		inbeamPosition = setPosition(EdePositionType.INBEAM, scanableMotorPositions);
	}

	/**
	 * Takes either the motor positions as doubles or a String and null, where the String is one of the alignment stage
	 * positions.
	 * @throws DeviceException
	 *
	 */
	public void setOutBeamPosition(Map<String, Double> scanableMotorPositions) throws DeviceException {
		outbeamPosition = setPosition(EdePositionType.OUTBEAM, scanableMotorPositions);
	}

	/**
	 * Takes either the motor positions as doubles or a String and null, where the String is one of the alignment stage
	 * positions.
	 * @throws DeviceException
	 *
	 */
	public void setReferencePosition(Map<String, Double> scanableMotorPositions) throws DeviceException {
		referencePosition = setPosition(EdePositionType.REFERENCE, scanableMotorPositions);
	}

	private EdeScanPosition setPosition(EdePositionType type, Map<String, Double> scanableMotorPositions) throws DeviceException {
		// FIXME Replacing with alignment stage motors is removed until the requirement spec is cleared
		return new EdeScanMotorPositions(type, scanableMotorPositions);
	}
}
