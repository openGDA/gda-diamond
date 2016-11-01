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

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.ContinuousParameters;
import gda.device.DeviceException;
import gda.device.detector.ZebraAreaDetectorPreparer;
import gda.device.zebra.controller.Zebra;
import gda.scan.TurboXasMotorParameters;

/**
 * Continuous Scannable for Turbo slit position
 * @since 19/5/2016
 */
public class TurboXasScannable extends ScannableMotor implements ContinuouslyScannable {

	private static final Logger logger = LoggerFactory.getLogger(TurboXasScannable.class);

	private Zebra zebraDevice;

	private  ContinuousParameters continuousParameters;
	private TurboXasMotorParameters motorParameters;

	private int positionTriggerEncoder;
	private int positionTriggerTimeUnits;
	private double pulseWidthFraction;
	private double motorStabilisationDistance;

	private double scanStartMotorPosition, scanEndMotorPosition;
	private double motorScanSpeed, scanMotorRange;
	private double initialMotorPosition, finalMotorPosition, motorRampDistance;
	private double maxMotorSpeed = 300; // TODO : set this dynamically by looking at PV (BL20J-OP-PCHRO-01:TS:XFINE.VMAX)

	private double positionStepSize;
	private int numReadoutsForScan;
	private int ttlOutputPort;

	private enum ScanParametersType { NONE, ERROR, CONTINUOUSPARAMS, TURBOXASMOTORPARAMS };
	private ScanParametersType lastParameterSetType;

	private boolean configZebraDuringPrepare;
	private boolean armZebraAtScanStart;
	private boolean disarmZebraAtScanEnd;

	private int numZebraGates;

	public TurboXasScannable() {
		positionTriggerEncoder = Zebra.PC_ENC_ENC3;
		ttlOutputPort = 31; // set TTL output 1 to 'PC_PULSE'
		positionTriggerTimeUnits = Zebra.PC_TIMEUNIT_SEC;

		motorStabilisationDistance = 0.1;
		pulseWidthFraction = 0.98;
		lastParameterSetType = ScanParametersType.NONE;
		numZebraGates = 1;
	}

	@Override
	public void setContinuousParameters(ContinuousParameters continuousParameters) {
		this.continuousParameters = continuousParameters;
		lastParameterSetType = ScanParametersType.CONTINUOUSPARAMS;
	}

	@Override
	public ContinuousParameters getContinuousParameters() {
		return continuousParameters;
	}

	public void setTurboXasMotorParameters(TurboXasMotorParameters motorParameters) {
		this.motorParameters = motorParameters;
		lastParameterSetType = ScanParametersType.TURBOXASMOTORPARAMS;
	}

	public TurboXasMotorParameters getTurboXasMotorParameters() {
		return motorParameters;
	}

	public Zebra getZebraDevice() {
		return zebraDevice;
	}

	public void setZebraDevice(Zebra zebraDevice) {
		this.zebraDevice = zebraDevice;
	}

	public void setMotorParameters() throws DeviceException {
		switch(lastParameterSetType) {
			case TURBOXASMOTORPARAMS : setMotorParameters(motorParameters);
				break;
			case CONTINUOUSPARAMS : setMotorParameters(continuousParameters);
				break;
			default : throw new DeviceException("Scan parameters have not been set - unable to calculate motor positions for scan");
		}
	}
	/**
	 * Set motor parameters from a TurboXasMotorParameters object
	 * @param motorParameters
	 * @throws DeviceException
	 */
	public void setMotorParameters(TurboXasMotorParameters motorParameters) throws DeviceException {
		// Convert from energy to real-space motor positions
		scanStartMotorPosition = motorParameters.getScanStartPosition();
		scanEndMotorPosition = motorParameters.getScanEndPosition();

		// set real-space range and speed
		scanMotorRange = motorParameters.getScanPositionRange();
		motorScanSpeed = motorParameters.getScanMotorSpeed();

		initialMotorPosition = motorParameters.getStartPosition();
		finalMotorPosition = motorParameters.getEndPosition();

		numReadoutsForScan = motorParameters.getNumReadoutsForScan();
		positionStepSize = motorParameters.getPositionStepsize();

		this.motorParameters = motorParameters;
		lastParameterSetType = ScanParametersType.TURBOXASMOTORPARAMS;

	}

	/**
	 * Set motor parameters (start, end, initial position etc) from ContinuousParameters object
	 * @throws DeviceException
	 */
	public void setMotorParameters(ContinuousParameters continuousParameters) throws DeviceException {
		// Convert from energy to real-space motor positions
		scanStartMotorPosition = continuousParameters.getStartPosition();
		scanEndMotorPosition = continuousParameters.getEndPosition();

		// set real-space range and speed
		scanMotorRange = scanEndMotorPosition - scanStartMotorPosition;
		motorScanSpeed = Math.abs(scanMotorRange) / continuousParameters.getTotalTime();

		// determine direction of motor move
		double scanMotorDirection = 1.0;
		if (scanMotorRange < 0 )
			scanMotorDirection = -1.0;

		// ramp up distance and initial motor position
		double timeToVelocity = this.getTimeToVelocity(); // Get current motor 'Seconds to velocity' (.ACCL)

		motorRampDistance = 0.5 * motorScanSpeed * timeToVelocity;
		initialMotorPosition = scanStartMotorPosition - scanMotorDirection * (motorRampDistance + motorStabilisationDistance);
		finalMotorPosition = scanEndMotorPosition + scanMotorDirection * (motorRampDistance + motorStabilisationDistance);

		numReadoutsForScan = continuousParameters.getNumberDataPoints();
		positionStepSize = scanMotorRange/numReadoutsForScan;

		numZebraGates = 1;

		this.continuousParameters = continuousParameters;
		lastParameterSetType = ScanParametersType.CONTINUOUSPARAMS;
	}

	/**
	 * Configure Arm, Gate, Pulse, Setup parts of Zebra ('PC' part of Zebra edm screen)
	 * @throws Exception
	 */
	public void configureZebra() throws Exception {

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
		double gateStart = scanStartMotorPosition-offset;
		double gateWidth = scanMotorRange + 2*offset;
		zebraDevice.setPCGateSource(Zebra.PC_GATE_SOURCE_POSITION);
		zebraDevice.setPCGateStart(gateStart);
		zebraDevice.setPCGateWidth(Math.abs(gateWidth));
		zebraDevice.setPCGateNumberOfGates(numZebraGates);
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

		zebraDevice.setOutTTL(1, ttlOutputPort);

		// Configure the area detector settings
		if (useAreaDetector && zebraAreaDetectorPreparer != null) {
			zebraAreaDetectorPreparer.configure(numReadoutsForScan*numZebraGates);
		}
	}

	public double getPulseWidthFraction() {
		return pulseWidthFraction;
	}

	public void setPulseWidthFraction(double pulseWidthFraction) {
		this.pulseWidthFraction = pulseWidthFraction;
	}

	public double getMotorStabilisationDistance() {
		return motorStabilisationDistance;
	}

	public void setMotorStabilisationDistance(double motorStabilisationDistance) {
		this.motorStabilisationDistance = motorStabilisationDistance;
	}

	public void setConfigZebraDuringPrepare( boolean configZebraDuringPrepare) {
		this.configZebraDuringPrepare = configZebraDuringPrepare;
	}

	public void setArmZebraAtScanStart( boolean armZebraAtScanStart ) {
		this.armZebraAtScanStart = armZebraAtScanStart;
	}

	public void setDisarmZebraAtScanEnd( boolean disarmZebraAtScanEnd ) {
		this.disarmZebraAtScanEnd = disarmZebraAtScanEnd;
	}

	public void setNumZebraGates( int numZebraGates ) {
		this.numZebraGates = numZebraGates;
	}

	public int getNumZebraGates() {
		return numZebraGates;
	}

	//  Getters only for parameters derived from scan params
	public double getScanStartMotorPosition() {
		return scanStartMotorPosition;
	}

	public double getScanEndMotorPosition() {
		return scanEndMotorPosition;
	}

	public double getMotorScanSpeed() {
		return motorScanSpeed;
	}

	public double getScanMotorRange() {
		return scanMotorRange;
	}

	public double getInitialMotorPosition() {
		return initialMotorPosition;
	}

	public double getFinalMotorPosition() {
		return finalMotorPosition;
	}

	public double getPositionStepSize() {
		return positionStepSize;
	}

	public int getNumReadoutsForScan() {
		return numReadoutsForScan;
	}

	@Override
	public void prepareForContinuousMove() {
		try {
			logger.info("Setting motor parameters ...");
			setMotorParameters();

			logger.info("Moving motor to initial run-up position ("+initialMotorPosition+")");
			this.setSpeed(maxMotorSpeed);
			asynchronousMoveTo(initialMotorPosition);
			// to help reduce 'dead time', set motor speed just before starting move to final position
			// instead of setting it here after waiting for motor to move to initial position.

			if ( configZebraDuringPrepare ) {
				logger.info("Configuring zebra gate, pulse parameters ...");
				configureZebra();
			} else
				logger.info("Skipping zebra configure");

		}
		catch(Exception e) {
			logger.warn("Exception in prepareForContinuousMove", e);
		}
	}

	/**
	 * Returns number of zebra readouts used for scan.
	 */
	@Override
	public int getNumberOfDataPoints() {
		return numReadoutsForScan;
	}


	@Override
	public void performContinuousMove() throws DeviceException {
		try {
			if ( armZebraAtScanStart ) {
				logger.info("Arming Zebra");
				zebraDevice.reset();
				zebraDevice.pcArm(); // should wait until armed, but seems to wait for ever

				// Arm the area detector
				if (useAreaDetector && zebraAreaDetectorPreparer != null) {
					zebraAreaDetectorPreparer.arm();
				}

			} else
				logger.info("Skipping arm at scan start");

			while (isBusy()) {
				logger.info("Waiting for turbo slit to finish moving to runup position");
				Thread.sleep(20);
			}

			logger.info("Turbo slit move started (final position = "+finalMotorPosition+")");
			this.setSpeed(motorScanSpeed);
			asynchronousMoveTo(finalMotorPosition );

		} catch (Exception e) {
			logger.error("Exception in performContinuousMove", e);
			throw new DeviceException(e.getMessage(), e);
		}
	}

	@Override
	public void continuousMoveComplete() throws DeviceException {
		// Use rough estimate of how long motor takes for move for max wait time
		double maxWaitTime = 2.0*scanMotorRange/motorScanSpeed;
		try {
			logger.info("Waiting for Turbo slit to finish move at end of scan");
			waitWhileBusy(maxWaitTime);
		} catch (DeviceException e) {
			// Timeout
			logger.error("DeviceException while waiting for Turbo slit to finish moving at end of scan "+e+"\n --- Stopping motor" );
			stop();
		} catch (InterruptedException e) {
			// Scan is aborted for some other reason - rethrow as DeviceException
			logger.error("InterruptedException while waiting for Turbo slit to finish moving at end of scan ", e);
			throw new DeviceException(e.getMessage(), e);
		}

		if ( disarmZebraAtScanEnd ) {
			try {
				logger.info("Disarming Zebra at end of scan");
				zebraDevice.pcDisarm();
			} catch (Exception e) {
				logger.error("Exception while trying to disarm Zebra at end of scan", e);
				throw new DeviceException(e.getMessage(), e);
			}
		}else {
			logger.info("Skipping disarm at scan end");
		}
	}

	@Override
	public double calculateEnergy(int frameIndex) throws DeviceException {
		double deltaPositionPerFrame = scanMotorRange/numReadoutsForScan;
		double motorPosition = scanStartMotorPosition + frameIndex*deltaPositionPerFrame;
		if (lastParameterSetType == ScanParametersType.TURBOXASMOTORPARAMS)
			return motorParameters.getEnergyForPosition(motorPosition);
		else
			return motorPosition;
	}

	public int getTtlOutputPort() {
		return ttlOutputPort;
	}

	public void setTtlOutputPort(int ttlOutputPort) {
		this.ttlOutputPort = ttlOutputPort;
	}

	/**
	 *  Reset Zebra arm, disarm and configure parameters to default values (i.e. all true)
	 */
	public void resetZebraArmConfigFlags() {
		armZebraAtScanStart = true;
		disarmZebraAtScanEnd = true;
		configZebraDuringPrepare = true;
	}

	@Override
	public void atScanStart() {
		resetZebraArmConfigFlags();
	}

	@Override
	public void atScanEnd() {
		resetZebraArmConfigFlags();
	}

	private boolean useAreaDetector = false;
	private ZebraAreaDetectorPreparer zebraAreaDetectorPreparer;

	public void setUseAreaDetector(boolean useAreaDetector) throws Exception {
		this.useAreaDetector = useAreaDetector;
		if (useAreaDetector) {
			zebraAreaDetectorPreparer = makeZebraAreaDetectorPreparer();
		} else
			zebraAreaDetectorPreparer = null;
	}

	public void setAreaDetectorPreparer(ZebraAreaDetectorPreparer preparer) {
		zebraAreaDetectorPreparer = preparer;
		if (preparer != null) {
			useAreaDetector = true;
		} else {
			useAreaDetector = false;
		}
	}

	public ZebraAreaDetectorPreparer getAreaDetectorPreparer() {
		return zebraAreaDetectorPreparer;
	}

	/** Make default area detector preparer for i20-1 zebra
	 * This is is for testing purposes only, so set hdf file path to the tmp directory.
	 * To change how it's set up (e.g. in script), just make
	 * a new ZebraAreaDector object and pass it in via. {@link #setAreaDetectorPreparer(ZebraAreaDetectorPreparer)}.
	 */
	private ZebraAreaDetectorPreparer makeZebraAreaDetectorPreparer() throws Exception {
		String zebraPv = zebraDevice.getZebraPrefix();
		String dataDir = "/dls/i20-1/data/2016/cm14479-4/tmp/";
		String fileName = "test";
		ZebraAreaDetectorPreparer preparer = new ZebraAreaDetectorPreparer(zebraPv);
		preparer.setFileDirectory(dataDir);
		preparer.setFilename(fileName);
		preparer.setCamPvSuffix(""); // Normal area detectors use "CAM:"
		preparer.setHdfPvSuffix("HDF:"); // NB Normal area detectors use "HDF5:"
		preparer.setFilenameTemplate("%s%s%d.hdf");
		return preparer;
	}
}
