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

import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.ContinuousParameters;
import gda.device.DeviceException;
import gda.device.zebra.controller.Zebra;

/*
 * Continuous Scannable for Turbo slit position
 * @since 19/5/2016
 */
public class TurboXasScannable extends ScannableMotor implements ContinuouslyScannable {

	private static final Logger logger = LoggerFactory.getLogger(TurboXasScannable.class);

	private Zebra zebraDevice;

	private  ContinuousParameters continuousParameters;
	private int positionTriggerEncoder;
	private int positionTriggerTimeUnits;
	private double pulseWidthFraction;
	private double motorStabilisationDistance;

	private double scanStartMotorPosition, scanEndMotorPosition;
	private double motorScanSpeed, scanMotorRange;
	private double initialMotorPosition, finalMotorPosition, motorRampDistance;
	private double maxMotorSpeed = 300; // TODO : set this dynamically by looking at PV (BL20J-OP-PCHRO-01:TS:XFINE.VMAX)

	private PolynomialFunction energyToPositionPolynomial;


	public TurboXasScannable() {
		positionTriggerEncoder = Zebra.PC_ENC_ENC3;
		motorStabilisationDistance = 0.1;
		positionTriggerTimeUnits = Zebra.PC_TIMEUNIT_SEC;
		energyToPositionPolynomial = new PolynomialFunction( new double[]{0,1} ); // coefficients of powers of x; 1st element is constant term,
		pulseWidthFraction = 0.98;
	}

	@Override
	public void setContinuousParameters(ContinuousParameters continuousParameters) {
		this.continuousParameters = continuousParameters;

	}

	@Override
	public ContinuousParameters getContinuousParameters() {
		return continuousParameters;
	}

	public Zebra getZebraDevice() {
		return zebraDevice;
	}

	public void setZebraDevice(Zebra zebraDevice) {
		this.zebraDevice = zebraDevice;
	}

	public PolynomialFunction getEnergyToPositionPolynomial() {
		return energyToPositionPolynomial;
	}

	public void setEnergyToPositionPolynomial(PolynomialFunction energyToPositionPolynomial) {
		this.energyToPositionPolynomial = energyToPositionPolynomial;
	}

	public void setEnergyToPositionPolynomial(double [] coeffArray ) {
		energyToPositionPolynomial = new PolynomialFunction( coeffArray );
	}

	/**
	 *  Convert from photon energy to motor position - use polynomial from calibration measurement :
	 *  	E(x) = a + b*x + c*x*x etc. where x is motor position and E is energy
	 * @param photon energy
	 * @return motor position
	 */
	private double getMotorPositionForEnergy( double energy ) {

		// solve for roots in specified interval - may need to do this if supplied polynomial is energy as func. of position.
		// rather than position as function of energy...

		//UnivariateRealSolver solver = new BisectionSolver();
		//result = solver.solve(f, -0.2, 0.2);

		if ( energyToPositionPolynomial != null )
			return energyToPositionPolynomial.value(energy);
		else
			return energy;
	}

	/**
	 *  Get Energy for given motor position  - do this by solving energyToPositionPolynomial ?
	 * @param motor position
	 * @return photon energy
	 */
	private double getEnergyForMotorPosition( double position ) {
		return position;
	}
	/**
	 * Set motor parameters (start, end, initial position etc) from current continuousParameters
	 * @throws DeviceException
	 */
	public void setMotorParameters() throws DeviceException {
		// Convert from energy to real-space motor positions
		scanStartMotorPosition = getMotorPositionForEnergy(continuousParameters.getStartPosition());
		scanEndMotorPosition = getMotorPositionForEnergy(continuousParameters.getEndPosition());

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
	}

	/**
	 * Configure Arm, Gate, Pulse, Setup parts of Zebra ('PC' part of Zebra edm screen)
	 * @throws Exception
	 */
	public void configureZebra() throws Exception {

		// each of these calls to zebra waits for callback before continuing. Overhead ?

		// 'arm' settings
		zebraDevice.pcDisarm(); // disarm before trying to configure
		zebraDevice.setPCArmSource(Zebra.PC_ARM_SOURCE_SOFT); // soft trigger

		// 'setup' settings
		int dirEnumValue = scanMotorRange > 0 ? Zebra.PC_DIR_POSITIVE : Zebra.PC_DIR_NEGATIVE;
		zebraDevice.setPCDir(dirEnumValue);
		zebraDevice.setPCEnc(positionTriggerEncoder);
		zebraDevice.setPCTimeUnit(positionTriggerTimeUnits);

		// 'gate' settings
		zebraDevice.setPCGateSource(Zebra.PC_GATE_SOURCE_POSITION);
		zebraDevice.setPCGateStart(scanStartMotorPosition);
		zebraDevice.setPCGateWidth(Math.abs(scanMotorRange));
		zebraDevice.setPCGateNumberOfGates(1);
		zebraDevice.setPCGateStep(0);

		// 'pulse' settings

		// separation between start of each pulse
		double pulseStart = 0;
		double pulseStep = scanMotorRange / continuousParameters.getNumberDataPoints();
		double pulseWidth = pulseStep * pulseWidthFraction;

		zebraDevice.setPCPulseSource(Zebra.PC_PULSE_SOURCE_POSITION);
		zebraDevice.setPCPulseStart(pulseStart);
		zebraDevice.setPCPulseWidth(pulseWidth);
		zebraDevice.setPCPulseStep(pulseStep);
		zebraDevice.setPCPulseMax(continuousParameters.getNumberDataPoints());

		zebraDevice.setOutTTL(1, 31); // set TTL output 1 to 'PC_PULSE'
	}

	public double getPulseWidthFraction() {
		return pulseWidthFraction;
	}

	public void setPulseWidthFraction( double pulseWidthFraction ) {
		this.pulseWidthFraction = pulseWidthFraction;
	}

	public double getMotorStabilisationDistance() {
		return motorStabilisationDistance;
	}

	public void setMotorStabilisationDistance(double motorStabilisationDistance) {
		this.motorStabilisationDistance = motorStabilisationDistance;
	}

	@Override
	public void prepareForContinuousMove() {
		try {
			logger.info("Setting motor parameters ...");
			setMotorParameters();

			logger.info("Moving motor to initial run-up position ("+initialMotorPosition+")");
			this.setSpeed(maxMotorSpeed);
			moveTo(initialMotorPosition);
			this.setSpeed(motorScanSpeed);

			logger.info("Configuring zebra gate, pulse parameters ...");
			configureZebra();
		}
		catch( Exception e ) {
			logger.warn("Exception in prepareForContinuousMove", e);
		}
	}

	@Override
	public int getNumberOfDataPoints() {
		return continuousParameters.getNumberDataPoints();
	}

	@Override
	public void performContinuousMove() throws DeviceException {
		try {

			logger.info("Arming Zebra");
			zebraDevice.reset();
			zebraDevice.pcArm(); // should wait until armed, but seems to wait for ever

			while (isBusy()) {
				logger.info("Waiting for turbo slit to finish moving to runup position");
				Thread.sleep(100);
			}

			logger.info("Turbo slit move started (final position = "+finalMotorPosition+")");
			asynchronousMoveTo(finalMotorPosition );

		} catch (Exception e) {
			logger.error("Exception in performContinuousMove", e);
			throw new DeviceException(e.getMessage(), e);
		}
	}

	@Override
	public void continuousMoveComplete() throws DeviceException {
		double maxWaitTime = continuousParameters.getTotalTime()*2;
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

		try {
			logger.info("Disarming Zebra at end of scan");
			zebraDevice.pcDisarm();
		} catch (Exception e) {
			logger.error("Exception while trying to disarm Zebra at end of scan", e);
			throw new DeviceException(e.getMessage(), e);
		}
	}

	@Override
	public double calculateEnergy(int frameIndex) throws DeviceException {
		double deltaPositionPerFrame = scanMotorRange/(continuousParameters.getNumberDataPoints()-1);
		double motorPosition = scanStartMotorPosition + frameIndex*deltaPositionPerFrame;
		return getEnergyForMotorPosition( motorPosition );
	}

}
