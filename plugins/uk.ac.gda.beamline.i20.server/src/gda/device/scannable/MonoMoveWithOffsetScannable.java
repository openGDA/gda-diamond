/*-
 * Copyright © 2016 Diamond Light Source Ltd.
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

package gda.device.scannable;

import java.util.Arrays;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import uk.ac.gda.beans.exafs.XesScanParameters;

/**
 * Scannable to move bragg and also adjust bragg offset for each move.
 *
 * @since 26/8/2016
 */

public class MonoMoveWithOffsetScannable extends ScannableMotionBase {

	private static final Logger logger = LoggerFactory.getLogger(MonoMoveWithOffsetScannable.class);

	private Scannable bragg;
	private Scannable braggOffset;

	private double offsetLastMove;
	private double braggEnergyLastMove;

	private int scanType; // 0 for XAS or 1,2,3,4 for XES (i.e.	XesScanParameters.FIXED_XES_SCAN_XAS etc)
	private String loopType; // XesScanParameters.EF_OUTER_MONO_INNER, or XesScanParameters.MONO_OUTER_EF_INNER
	private int numStepsPerInnerLoop;
	private boolean scanIsOneDimensional;

	private double offsetGradient, offsetStartValue, energyOffsetStart;
	private double offsetMoveThreshold;

	private boolean adjustBraggOffset;

	public MonoMoveWithOffsetScannable(String name, Scannable bragg, Scannable braggOffset) {
		setName(name);
		this.bragg = bragg;
		this.braggOffset = braggOffset;

		setInputNames(new String[] {bragg.getName()} );
		setExtraNames(new String[] {braggOffset.getName()} );

		setOutputFormat(new String[] {bragg.getOutputFormat()[0], braggOffset.getOutputFormat()[0]} );

		offsetLastMove = 0;
		braggEnergyLastMove = 0;

		setScanType(0);

		loopType = "";
		numStepsPerInnerLoop = 0;

		offsetGradient = offsetStartValue = energyOffsetStart = 0.0;
		offsetMoveThreshold = 0;
		adjustBraggOffset = false;
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return bragg.isBusy() || braggOffset.isBusy();
	}

	@Override
	public Object getPosition() throws DeviceException {
		if  ( scanType == 0 ) {
			// XAS mode
			return new Object[] {ScannableUtils.getCurrentPositionArray(bragg)[0] , ScannableUtils.getCurrentPositionArray(braggOffset)[0]};
		}
		else
			return bragg.getPosition();
	}

	/**
	 * Calculate bragg offset for given value of bragg energy
	 */
	public double getOffsetForEnergy(double energy) {
		return offsetStartValue + (energy - energyOffsetStart)*offsetGradient;
	}

	/**
	 * Apply the offset for specified energy to offset motor.
	 * @param energy
	 * @throws DeviceException
	 */
	public void adjustBraggOffsetMotor(double energy) throws DeviceException {
		double offset = getOffsetForEnergy(energy);
		if ( Math.abs(offset - offsetLastMove) > offsetMoveThreshold ) {
			braggOffset.asynchronousMoveTo(offset);
			offsetLastMove = offset;
		}
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {

		double energy = ScannableUtils.objectToArray(position)[0];

		if (!adjustBraggOffset) {
			bragg.asynchronousMoveTo(energy);
		} else {
			// move bragg and block until finished so that offset can then be adjusted
			bragg.moveTo(energy);

			// XAS or 1d XES scan : adjust offset
			if (scanType == 0 || scanType != XesScanParameters.SCAN_XES_SCAN_MONO) {
				adjustBraggOffsetMotor(energy);
			} else if (scanType == XesScanParameters.SCAN_XES_SCAN_MONO) {
				// 2D scan,

				// Mono is inner loop, adjust offset motor as normal
				if (loopType.equals(XesScanParameters.EF_OUTER_MONO_INNER)) {
					adjustBraggOffsetMotor(energy);
				} else {
					// When XES is inner loop, each mono move corresponds to start of new line
					if (Math.abs(energy - braggEnergyLastMove) > 0) {
						//TODO adjust braggOffset to maximise signal, *without doing a scan*
						// e.g. use MonoOptimisation.goldenSectionSearch() but reset Tfg frames
						// afterwards so rest of scan proceeds correctly.
					}
				}
			}
		}

		braggEnergyLastMove = energy;
	}

	public String getLoopType() {
		return loopType;
	}

	public void setLoopType(String loopType) {
		this.loopType = loopType;
	}

	public int getNumStepsPerInnerLoop() {
		return numStepsPerInnerLoop;
	}

	public void setNumStepsPerInnerLoop(int numStepsPerInnerLoop) {
		this.numStepsPerInnerLoop = numStepsPerInnerLoop;
	}

	public int getScanType() {
		return scanType;
	}

	private int[] oneDimensionalScanTypes = {0, XesScanParameters.SCAN_XES_FIXED_MONO, XesScanParameters.FIXED_XES_SCAN_XAS,
											XesScanParameters.FIXED_XES_SCAN_XANES };

	public void setScanType(int scanType) {
		this.scanType = scanType;
		scanIsOneDimensional = Arrays.asList(oneDimensionalScanTypes).contains(scanType);
	}

	public double getOffsetLastMove() {
		return offsetLastMove;
	}

	// Offset calculation parameter getter, setters...
	public double getOffsetGradient() {
		return offsetGradient;
	}

	public void setOffsetGradient(double offsetGradient) {
		this.offsetGradient = offsetGradient;
	}

	public double getEnergyOffsetStart() {
		return energyOffsetStart;
	}

	public void setEnergyOffsetStart(double energyOffsetStart) {
		this.energyOffsetStart = energyOffsetStart;
	}

	public double getOffsetMoveThreshold() {
		return offsetMoveThreshold;
	}

	public void setOffsetMoveThreshold(double offsetMoveThreshold) {
		this.offsetMoveThreshold = offsetMoveThreshold;
	}

	public boolean getAdjustBraggOffset() {
		return adjustBraggOffset;
	}

	public void setAdjustBraggOffset(boolean adjustBraggOffset) {
		this.adjustBraggOffset = adjustBraggOffset;
	}

	public double getOffsetStartValue() {
		return offsetStartValue;
	}

	public void setOffsetStartValue(double offsetStartValue) {
		this.offsetStartValue = offsetStartValue;
	}
}
