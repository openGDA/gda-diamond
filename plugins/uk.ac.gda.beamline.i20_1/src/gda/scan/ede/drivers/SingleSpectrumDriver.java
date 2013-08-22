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

import gda.device.detector.StripDetector;
import gda.device.scannable.AlignmentStageScannable;
import gda.device.scannable.ScannableMotor;
import gda.factory.Finder;
import gda.scan.ede.EdeSingleExperiment;
import gda.scan.ede.position.AlignmentStageScanPosition;
import gda.scan.ede.position.EdePositionType;
import gda.scan.ede.position.EdeScanPosition;
import gda.scan.ede.position.ExplicitScanPositions;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;

/**
 * Convenience class which takes a series of parameters, runs the scan and then returns the name of the ascii file
 * created.
 */
public class SingleSpectrumDriver {

	private final StripDetector detector;
	private final AlignmentStageScannable alignmentstage;
	private final ScannableMotor xMotor;
	private final ScannableMotor yMotor;
	private final Double i0_scantime;
	private final Integer i0_numberscans;
	private Double it_scantime;
	private Integer it_numberscans;
	private EdeScanPosition inbeamPosition;
	private EdeScanPosition outbeamPosition;

	public SingleSpectrumDriver(String detectorName, Double i0_scantime, Integer i0_numberscans, Double it_scantime,
			Integer it_numberscans) {

		this.i0_scantime = i0_scantime;
		this.i0_numberscans = i0_numberscans;
		this.it_scantime = it_scantime;
		this.it_numberscans = it_numberscans;

		detector = Finder.getInstance().find(detectorName);
		alignmentstage = Finder.getInstance().find("alignment_stage");
		xMotor = Finder.getInstance().find("sample_x");
		yMotor = Finder.getInstance().find("sample_y");

		if (this.it_scantime == null) {
			this.it_scantime = i0_scantime;
		}
		if (this.it_numberscans == null) {
			this.it_numberscans = i0_numberscans;
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
		if (yPos == null) {
			// assume xPos is a string of an AlignmentStageScannable.Devices
			AlignmentStageScannable.Devices device = AlignmentStageScannable.Devices.getDevice(xPos.toString());
			inbeamPosition = new AlignmentStageScanPosition(EdePositionType.INBEAM, device, alignmentstage);
		} else {
			Double xPosition = Double.valueOf(xPos.toString());
			Double yPosition = Double.valueOf(yPos.toString());
			inbeamPosition = new ExplicitScanPositions(EdePositionType.INBEAM, xPosition, yPosition, xMotor, yMotor);
		}
	}

	/**
	 * Takes either the motor positions as doubles or a String and null, where the String is one of the alignment stage
	 * positions.
	 * 
	 * @param xPos
	 * @param yPos
	 */
	public void setOutBeamPosition(Object xPos, Object yPos) {
		if (yPos == null) {
			// assume xPos is a string of an AlignmentStageScannable.Devices
			AlignmentStageScannable.Devices device = AlignmentStageScannable.Devices.getDevice(xPos.toString());
			outbeamPosition = new AlignmentStageScanPosition(EdePositionType.OUTBEAM, device, alignmentstage);
		} else {
			Double xPosition = Double.valueOf(xPos.toString());
			Double yPosition = Double.valueOf(yPos.toString());
			outbeamPosition = new ExplicitScanPositions(EdePositionType.OUTBEAM, xPosition, yPosition, xMotor, yMotor);
		}
	}

	public String doCollection() throws Exception {
		EdeScanParameters i0scanparams = EdeScanParameters.createSingleFrameScan(i0_scantime, i0_numberscans);
		EdeScanParameters itscanparams = EdeScanParameters.createSingleFrameScan(it_scantime, it_numberscans);

		EdeSingleExperiment theExperiment = new EdeSingleExperiment(i0scanparams, itscanparams, inbeamPosition,
				outbeamPosition, detector);
		return theExperiment.runExperiment();
	}
}
