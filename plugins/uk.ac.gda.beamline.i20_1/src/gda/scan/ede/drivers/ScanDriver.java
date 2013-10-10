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

import gda.device.scannable.AlignmentStageScannable;
import gda.device.scannable.ScannableMotor;
import gda.factory.Finder;
import gda.scan.ede.position.AlignmentStageScanPosition;
import gda.scan.ede.position.EdePositionType;
import gda.scan.ede.position.EdeScanPosition;
import gda.scan.ede.position.ExplicitScanPositions;

public abstract class ScanDriver {

	private final AlignmentStageScannable alignmentstage;
	private final ScannableMotor xMotor;
	private final ScannableMotor yMotor;

	protected EdeScanPosition inbeamPosition;
	protected EdeScanPosition outbeamPosition;
	protected EdeScanPosition referencePosition;
	protected String fileTemplate;

	public ScanDriver() {
		alignmentstage = Finder.getInstance().find("alignment_stage");
		xMotor = Finder.getInstance().find("sample_x");
		yMotor = Finder.getInstance().find("sample_y");
	}

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
	 * 
	 * @param xPos
	 * @param yPos
	 */
	public void setInBeamPosition(Object xPos, Object yPos) {
		inbeamPosition = setPosition(EdePositionType.INBEAM, xPos, yPos);
	}

	/**
	 * Takes either the motor positions as doubles or a String and null, where the String is one of the alignment stage
	 * positions.
	 * 
	 * @param xPos
	 * @param yPos
	 */
	public void setOutBeamPosition(Object xPos, Object yPos) {
		outbeamPosition = setPosition(EdePositionType.OUTBEAM, xPos, yPos);
	}

	/**
	 * Takes either the motor positions as doubles or a String and null, where the String is one of the alignment stage
	 * positions.
	 * 
	 * @param xPos
	 * @param yPos
	 */
	public void setReferencePosition(Object xPos, Object yPos) {
		referencePosition = setPosition(EdePositionType.REFERENCE, xPos, yPos);
	}

	private EdeScanPosition setPosition(EdePositionType type, Object xPos, Object yPos) {
		EdeScanPosition position;
		if (yPos == null) {
			// assume xPos is a string of an AlignmentStageScannable.Devices
			AlignmentStageScannable.AlignmentStageDevice device = AlignmentStageScannable.AlignmentStageDevice
					.valueOf(xPos.toString());
			position = new AlignmentStageScanPosition(type, device, alignmentstage);
		} else {
			Double xPosition = Double.valueOf(xPos.toString());
			Double yPosition = Double.valueOf(yPos.toString());
			position = new ExplicitScanPositions(type, xPosition, yPosition, xMotor, yMotor);
		}
		return position;
	}
}
