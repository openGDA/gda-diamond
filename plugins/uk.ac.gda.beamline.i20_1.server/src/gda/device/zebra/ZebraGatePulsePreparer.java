/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

package gda.device.zebra;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.ContinuousParameters;
import gda.device.DeviceException;
import gda.device.zebra.controller.Zebra;
import gda.factory.FindableBase;
import gda.scan.TurboXasMotorParameters;



public class ZebraGatePulsePreparer extends FindableBase {
	private static final Logger logger = LoggerFactory.getLogger(ZebraGatePulsePreparer.class);
	private Zebra zebraDevice;

	private double scanStartMotorPosition;
	private double scanMotorRange;
	private int numReadoutsForScan;
	private double positionStepSize;
	private int numGates;
	private double motorStabilisationDistance;
	private int ttlOutputPort;
	private int positionTriggerEncoder;
	private int positionTriggerTimeUnits;
	private double pulseWidthFraction;

	public ZebraGatePulsePreparer() {
		zebraDevice = null;
		setDefaults();
	}

	public ZebraGatePulsePreparer(Zebra zebraDevice) {
		this.zebraDevice = zebraDevice;
		setDefaults();
	}

	public void setDefaults() {
		motorStabilisationDistance = 0.1;
		positionTriggerEncoder = Zebra.PC_ENC_ENC3;
		ttlOutputPort = 31; // set TTL output 1 to 'PC_PULSE'
		positionTriggerTimeUnits = Zebra.PC_TIMEUNIT_SEC;
		pulseWidthFraction = 0.5; // width of each pulse as fraction of pulse step
	}

	public void setFromParameters(ContinuousParameters continuousParameters) throws DeviceException {
		scanStartMotorPosition = continuousParameters.getStartPosition();
		double scanEndMotorPosition = continuousParameters.getEndPosition();
		scanMotorRange = scanEndMotorPosition - scanStartMotorPosition;
		numReadoutsForScan = continuousParameters.getNumberDataPoints();
		positionStepSize = scanMotorRange/numReadoutsForScan;
		numGates = 1;
	}

	public void setFromParameters(TurboXasMotorParameters motorParameters) throws DeviceException {
		scanStartMotorPosition = motorParameters.getScanStartPosition();
		scanMotorRange = motorParameters.getScanPositionRange();
		numReadoutsForScan = motorParameters.getNumReadoutsForScan();
		positionStepSize = motorParameters.getPositionStepsize();
		motorStabilisationDistance = motorParameters.getMotorStabilisationDistance();

		numGates = motorParameters.getScanParameters().getTotalNumSpectra();
	}

	public void configureZebra() throws Exception {

		if (zebraDevice==null) {
			logger.warn("Cannot configure - zebraDevice has not been set");
			return;
		}

		// each of these calls to zebra waits for callback before continuing. Overhead ?
		zebraDevice.reset(); // sometimes gate download gets 'stuck' (esp. for large number of fast pulses), need to reset before gate can be reconfigured. imh 12/8/2016

		// 'arm' settings
		zebraDevice.pcDisarm(); // disarm before trying to configure
		zebraDevice.setPCArmSource(Zebra.PC_ARM_SOURCE_SOFT); // soft trigger

		// 'setup' settings
		int dirEnumValue = scanMotorRange > 0 ? Zebra.PC_DIR_POSITIVE : Zebra.PC_DIR_NEGATIVE;
		zebraDevice.setPCDir(dirEnumValue);
		zebraDevice.setPCEnc(positionTriggerEncoder);
		zebraDevice.setPCTimeUnit(positionTriggerTimeUnits);

		// 'gate' settings
		// Pulse start needs to be slightly after gate start (to avoid triggering issues)
		// -> adjust gate start position by small 'offset' so that pulse start is at correct position :
		double offset = motorStabilisationDistance*0.5;
		double gateStart = scanStartMotorPosition;
		gateStart += scanMotorRange > 0 ? -offset : offset;
		double gateWidth = Math.abs(scanMotorRange) + 2*offset;
		zebraDevice.setPCGateSource(Zebra.PC_GATE_SOURCE_POSITION);
		zebraDevice.setPCGateStart(gateStart);
		zebraDevice.setPCGateWidth(Math.abs(gateWidth));
		zebraDevice.setPCGateNumberOfGates(numGates);
		zebraDevice.setPCGateStep(0);

		// 'pulse' settings
		double pulseStart = offset;
		double pulseStep = positionStepSize;
		double pulseWidth = pulseStep * pulseWidthFraction;

		zebraDevice.setPCPulseSource(Zebra.PC_PULSE_SOURCE_POSITION);
		zebraDevice.setPCPulseStart(pulseStart);
		zebraDevice.setPCPulseWidth(pulseWidth);
		zebraDevice.setPCPulseStep(pulseStep);
		zebraDevice.setPCPulseMax(numReadoutsForScan);
		zebraDevice.setPCNumberOfPointsCaptured(0);

		zebraDevice.setOutTTL(1, ttlOutputPort);
	}

	public double getMotorStabilisationDistance() {
		return motorStabilisationDistance;
	}

	public void setMotorStabilisationDistance(double motorStabilisationDistance) {
		this.motorStabilisationDistance = motorStabilisationDistance;
	}

	public int getPositionTriggerTimeUnits() {
		return positionTriggerTimeUnits;
	}

	public void setPositionTriggerTimeUnits(int positionTriggerTimeUnits) {
		this.positionTriggerTimeUnits = positionTriggerTimeUnits;
	}

	public int getPositionTriggerEncoder() {
		return positionTriggerEncoder;
	}

	public void setPositionTriggerEncoder(int positionTriggerEncoder) {
		this.positionTriggerEncoder = positionTriggerEncoder;
	}

	public int getTtlOutputPort() {
		return ttlOutputPort;
	}

	public void setTtlOutputPort(int ttlOutputPort) {
		this.ttlOutputPort = ttlOutputPort;
	}

	public double getPulseWidthFraction() {
		return pulseWidthFraction;
	}

	public void setPulseWidthFraction(double pulseWidthFraction) {
		this.pulseWidthFraction = pulseWidthFraction;
	}

	public int getNumGates() {
		return numGates;
	}

	public void setNumGates(int numGates) {
		this.numGates = numGates;
	}

	public int getNumReadoutsForScan() {
		return numReadoutsForScan;
	}

	public void setNumReadoutsForScan(int numReadoutsForScan) {
		this.numReadoutsForScan = numReadoutsForScan;
	}

	public double getScanStartMotorPosition() {
		return scanStartMotorPosition;
	}

	public void setScanStartMotorPosition(double scanStartMotorPosition) {
		this.scanStartMotorPosition = scanStartMotorPosition;
	}

	public void setScanMotorRange(double scanMotorRange) {
		this.scanMotorRange = scanMotorRange;
	}

	public double getScanMotorRange() {
		return scanMotorRange;
	}

	public void setZebraDevice(Zebra zebraDevice) {
		this.zebraDevice = zebraDevice;
	}

	public Zebra getZebraDevice() {
		return this.zebraDevice;
	}
}
