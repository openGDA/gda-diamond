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

package gda.scan;

import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
import org.apache.commons.math3.analysis.solvers.LaguerreSolver;
import org.apache.commons.math3.analysis.solvers.PolynomialSolver;
import org.dawnsci.ede.herebedragons.PolynomialParser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.thoughtworks.xstream.XStream;
import com.thoughtworks.xstream.annotations.Annotations;
import com.thoughtworks.xstream.annotations.XStreamAlias;

import gda.jython.InterfaceProvider;

/**
 * This class calculates real space motor positions for a Turbo XAS scan from user specified set of parameters based on energy.
 * @since 14/7/2016
 */
@XStreamAlias("TurboXasMotorParameters")
public class TurboXasMotorParameters {

	private static final Logger logger = LoggerFactory.getLogger(TurboXasMotorParameters.class);

	@XStreamAlias("TurboXasParameters")
	private TurboXasParameters scanParameters;

	// These are all set using values from TurboXasScanParameters
	private double scanStartPosition, scanEndPosition;
	private double scanMotorSpeed;
	private double returnMotorSpeed;

	private double startPosition, endPosition, motorRampDistance;
	private int    numReadoutsForScan;
	private double positionStepsize;
	private PolynomialFunction positionToEnergyPolynomial;

	// These are parameters of the motor to be used for scan
	private double motorMaxSpeed;
	private double motorTimeToVelocity;
	private double motorHighLimit;
	private double motorLowLimit;

	// Not currently set from scanParameters, should it be?
	private double motorStabilisationDistance;

	static final double minimumAllowedMotorMoveSize = 1e-6;

	public TurboXasMotorParameters() {
		scanParameters = new TurboXasParameters();
		setDefaultMotorParams();
		setScanParameters(scanParameters);
	}

	public TurboXasMotorParameters(TurboXasParameters params) {
		scanParameters = params;
		setDefaultMotorParams();
		setScanParameters(scanParameters);
	}

	public void setDefaultMotorParams() {
		motorMaxSpeed = 300;
		returnMotorSpeed = 250;
		motorTimeToVelocity = 0.015;
		motorStabilisationDistance = 0.1;
		motorHighLimit = 10000;
		motorLowLimit = -10000;
	}

	public void setScanParameters(TurboXasParameters params) {
		scanParameters = params;
		setPositionToEnergyPolynomial(params.getEnergyCalibrationPolynomial());
	}

	public void setPositionToEnergyPolynomial(String eqnString) {
		if (eqnString != null && eqnString.length() > 0) {
			double[] polynomialCoefficients = PolynomialParser.extractCoefficientsFromString(eqnString);
			positionToEnergyPolynomial = new PolynomialFunction(polynomialCoefficients);
		} else {
			positionToEnergyPolynomial = null;
		}
	}

	public void setPositionToEnergyPolynomial(PolynomialFunction positionToEnergyPolynomial) {
		this.positionToEnergyPolynomial = positionToEnergyPolynomial;
	}

	public PolynomialFunction getPositionToEnergyPolynomial() {
		return positionToEnergyPolynomial;
	}


	public TurboXasParameters getScanParameters() {
		return scanParameters;
	}

	public void setMotorParameters() {
		setMotorParametersForTimingGroup(0);
	}

	/**
	 * Calculate motor parameters for specified timing group of a scan :
	 *    Initial, final positions including velocity ramp up/down, velocity stabilisation distance;
	 *    Motor speed is calculated from motor range for energy range of scan and time per spectrum spectrum
	 * See <a href="http://confluence.diamond.ac.uk/display/I20/Turbo+XAS+scans">Turbo XAS scans confluence page</a> for more details.
	 * @param timingGroupIndex
	 */
	public void setMotorParametersForTimingGroup(int timingGroupIndex) {
		if ( scanParameters == null ) {
			logger.warn("Scan parameters have not been set - cannot compute motor parameters");
			return;
		}

		int numTimingGroups = scanParameters.getTimingGroups().size();
		if ( timingGroupIndex > numTimingGroups-1 ) {
			logger.warn("Specified timing group index {} > number of timing groups ({})", timingGroupIndex, numTimingGroups);
			return;
		}

		setMotorParametersForTime(scanParameters.getTimingGroups().get(timingGroupIndex).getTimePerSpectrum());
		calculateSetPositionStepSize();

	}

	/**
	 * Calculate motor speed required to move between start, end scan positions in given time
	 *
	 * @param timeForSpectra
	 * @return motor speed
	 */
	public double getScanSpeed(double timeForSpectra) {
		// set real-space range and speed
		return Math.abs(getScanPositionRange()) / timeForSpectra;
	}

	/**
	 * Calculate total time to move from one end of scan to the other at specified motor speed, including accel and velocity stabilisation
	 * @return total time
	 */
	public double getTotalTimeForScan(double motorSpeed) {
		double timeForScan = getScanPositionRange()/motorSpeed;
		double timeForVelocityStabilisation = motorStabilisationDistance/motorSpeed;
		return timeForScan + 2.0*(timeForVelocityStabilisation + motorTimeToVelocity);
	}

	public double getTotalTimeForScan() {
		return getTotalTimeForScan(scanMotorSpeed);
	}

	/**
	 * Calculate and set motor parameters for given time for spectrum.
	 * @param timeForSpectrum
	 */
	public void setMotorParametersForTime(double timeForSpectrum) {
		// Convert from energy to real-space motor positions
		scanStartPosition = getPositionForEnergy(scanParameters.getStartEnergy());
		scanEndPosition = getPositionForEnergy(scanParameters.getEndEnergy());

		scanMotorSpeed =  getScanSpeed(timeForSpectrum);
		// determine direction of motor move
		double scanMotorDirection = 1.0;
		if ( scanEndPosition - scanStartPosition < 0 )
			scanMotorDirection = -1.0;

		// ramp up distance and initial motor position
		double timeToVelocity = getMotorTimeToVelocity();
		motorRampDistance = 0.5 * scanMotorSpeed * timeToVelocity;
		startPosition = scanStartPosition - scanMotorDirection * (motorRampDistance + motorStabilisationDistance);
		endPosition = scanEndPosition + scanMotorDirection * (motorRampDistance + motorStabilisationDistance);
	}


	/**
	 * Calculate motor position step size and number of readouts/steps for scan from energy values.
	 * (i.e. 'Pulse step' and 'Max pulses' used for Zebra).
	 * Note that the energy-position relationship is generally non-linear, so we compute stepsize from average of step size
	 * at the start and end scan energies.
	 *
	 */
	public void calculateSetPositionStepSize() {
		// Make sure calculateMotorParameters has been called first, so that scanStartMotorPosition, and scanEndMotorPosition are up-to-date
		double energyStepSize = scanParameters.getEnergyStep();
		double startEnergy = scanParameters.getStartEnergy(), endEnergy = scanParameters.getEndEnergy();

		double stepSizeStartEnergy = getPositionForEnergy(startEnergy + energyStepSize) - scanStartPosition;
		double stepSizeEndEnergy = scanEndPosition - getPositionForEnergy(endEnergy - energyStepSize);
		positionStepsize = 0.5 * (stepSizeStartEnergy + stepSizeEndEnergy);
		double floatNumReadouts = (scanEndPosition - scanStartPosition)/positionStepsize;
		int floorNumReadouts = (int) Math.floor(floatNumReadouts);
		numReadoutsForScan = floorNumReadouts;

		// round up if very close to next whole number
		double leftOver = 1 - (floatNumReadouts - floorNumReadouts);
		if ( leftOver < minimumAllowedMotorMoveSize )
			numReadoutsForScan++;

	}

	public void showParameters() {
		String numFormat = "%.5g\n", twoNumFormat = "%.5g, %.5g\n";
		String params = String.format("Start, end positions for scan energy range : "+twoNumFormat, scanStartPosition, scanEndPosition)
		+ String.format("Scan range  : "+numFormat, getScanPositionRange())
		+ String.format("Motor speed : "+numFormat, scanMotorSpeed)
		+ String.format("Initial, final position  : "+twoNumFormat, startPosition, endPosition)
		+ String.format("Ramp distance     : "+numFormat, motorRampDistance)
		+ String.format("Velocity stabilisation distance : "+numFormat, motorStabilisationDistance)
		+ String.format("Max motor speed   : "+numFormat, motorMaxSpeed)
		+ String.format("Parameters valid ? %s", validateParameters());
		InterfaceProvider.getTerminalPrinter().print(params);
	}

	/**
	 * Validate the scan motor move range. If range is zero, it probably means that
	 * the initial, final energies are the same, or that something wrong with energy cal. polynomial.
	 * @return True if > minimum motor move size
	 */
	public boolean validMotorScanRange() {
		return Math.abs(getScanPositionRange()) > minimumAllowedMotorMoveSize;
	}

	/**
	 * Validate motor scan speed
	 * @return True if speed is < maximum speed of motor
	 */
	public boolean validMotorScanSpeed() {
		return scanMotorSpeed < motorMaxSpeed && scanMotorSpeed > 0;
	}

	/**
	 * Validate motor initial, final position
	 * @return True if motor range is within motor limits
	 */
	public boolean getMotorPositionsWithinLimits() {
		// NB final position may be < initial if scanning is in -ve direction
		double maxPos = Math.max(endPosition, startPosition);
		double minPos = Math.min(endPosition, startPosition);

		return maxPos < motorHighLimit && minPos > motorLowLimit;
	}

	public boolean validateParameters() {
		if ( !validMotorScanRange() ) {
			logger.warn("Initial and final motor positions are the same! Check scan parameters and/or energy-position calibration polynomial");
		}
		if ( !getMotorPositionsWithinLimits() ) {
			logger.warn("Initial, final motor positions for scan are outside of motor limits");
		}
		if ( !validMotorScanSpeed() ) {
			logger.warn("Calculated motor speed ("+scanMotorSpeed+") exceeds motor upper speed limit ("+motorMaxSpeed+")");
		}

		return validMotorScanRange() && getMotorPositionsWithinLimits() && validMotorScanSpeed();
	}

	/**
	 *  Convert from energy to motor position by solving energy calibration
	 *  polynomial for given value of energy.
	 * @param energy
	 * @return motor position
	 */
	public double getPositionForEnergy(double energy) {

		double position = energy;

		// Solve energy calibration polynomial for position.
		if ( positionToEnergyPolynomial != null ) {
			// Construct new polynomial function to be used in solver, using coeffs
			// of energy calibration polynomial with energy subtracted :
			double[] coeffs = positionToEnergyPolynomial.getCoefficients();
			coeffs[0] -= energy;
			PolynomialFunction tmpPoly = new PolynomialFunction(coeffs);

			// Run the solver
			PolynomialSolver solver =  new LaguerreSolver();
			double result = solver.solve(10, tmpPoly, 0.0, 1.0);

			// convert x from normalised to real position
			double lowLimit = scanParameters.getEnergyCalibrationMinPosition(), highLimit = scanParameters.getEnergyCalibrationMaxPosition();
			position = (highLimit - lowLimit)*result + lowLimit;
			logger.debug(String.format("Position to energy conversion : energy = %.5g, x = %.5g, position = %.5g", energy, result, position));
		}
		return position;
	}

	/**
	 *  Convert from motor position to energy using polynomial from calibration measurement :
	 *  	E(x) = a + b*x + c*x*x etc. where x is normalised motor position and E is energy
	 *
	 * @param position
	 * @return energy
	 */
	public double getEnergyForPosition(double position) {
		if ( positionToEnergyPolynomial != null ) {
			// energy calibration polynomial works off normalised position (0 < x < 1)
			double lowLimit = scanParameters.getEnergyCalibrationMinPosition(), highLimit = scanParameters.getEnergyCalibrationMaxPosition();
			double normalisedPosition = (position - lowLimit) / (highLimit - lowLimit);
			// show warning if position is out of range, but still calculate value.
			if ( normalisedPosition < 0 || normalisedPosition > 1 ) {
				logger.warn(String.format("Possible problem converting from position to energy : value %.5g is out of range of calibration polynomial (%.5g, %.5g)", position, lowLimit, highLimit));
			}
			return positionToEnergyPolynomial.value(normalisedPosition);
		}
		else
			return position;
	}

	// Motor related parameters - ideally set these using values from the motor to be used for scan
	public double getMotorMaxSpeed() {
		return motorMaxSpeed;
	}
	public void setMotorMaxSpeed(double maxMotorSpeed) {
		this.motorMaxSpeed = maxMotorSpeed;
	}

	public double getMotorTimeToVelocity() {
		return motorTimeToVelocity;
	}
	public void setMotorTimeToVelocity(double motorTimeToVelocity) {
		this.motorTimeToVelocity = motorTimeToVelocity;
	}

	public double getMotorHighLimit() {
		return motorHighLimit;
	}
	public void setMotorHighLimit(double motorHighLimit) {
		this.motorHighLimit = motorHighLimit;
	}

	public double getMotorLowLimit() {
		return motorLowLimit;
	}
	public void setMotorLowLimit(double motorLowLimit) {
		this.motorLowLimit = motorLowLimit;
	}

	// User specified param
	public double getMotorStabilisationDistance() {
		return motorStabilisationDistance;
	}
	public void setMotorStabilisationDistance(double motorStabilisationDistance) {
		this.motorStabilisationDistance = motorStabilisationDistance;
	}

	// Only have 'Getters' for the computed parameters
	/**
	 *
	 * @return Start scan position of motor (from user specified start energy)
	 */
	public double getScanStartPosition() {
		return scanStartPosition;
	}

	/**
	 *
	 * @return End scan position of motor (from user specified end energy)
	 */
	public double getScanEndPosition() {
		return scanEndPosition;
	}

	/**
	 *
	 * @return Start position for motor (including ramp and stabilisation distance)
	 */
	public double getStartPosition() {
		return startPosition;
	}

	/**
	 *
	 * @return End position for motor (including ramp and stabilisation distance)
	 */
	public double getEndPosition() {
		return endPosition;
	}

	/**
	 *
	 * @return Motor speed to be used during scan during data collection
	 */
	public double getScanMotorSpeed() {
		return scanMotorSpeed;
	}

	public double getReturnMotorSpeed() {
		return returnMotorSpeed;
	}

	public void setReturnMotorSpeed(double returnMotorSpeed) {
		this.returnMotorSpeed = returnMotorSpeed;
	}

	public double getScanPositionRange() {
		return scanEndPosition - scanStartPosition;
	}

	public double getMotorRampDistance() {
		return motorRampDistance;
	}

	public int getNumReadoutsForScan() {
		return numReadoutsForScan;
	}

	public double getPositionStepsize() {
		return positionStepsize;
	}

	/**
	 * Return new XStream object that can serialize/deserialize {@link TurboXasMotorParameters} objects to/from XML
	 * @return XStream
	 */
	static public XStream getXStream() {
		XStream xstream = TurboXasParameters.getXStream();
		Annotations.configureAliases(xstream,  TurboXasMotorParameters.class);
		xstream.omitField(TurboXasMotorParameters.class , "positionToEnergyPolynomial");
		return xstream;
	}

	/**
	 * Serialize {@link TurboXasMotorParameters} object to XML.
	 * @return String with XML serialized object
	 */
	public String toXML() {
		XStream xstream = TurboXasMotorParameters.getXStream();
		return xstream.toXML(this);
	}

	/**
	 * Create new {@link TurboXasMotorParameters} object deserialized from supplied XML string.
	 * @param xmlString
	 * @return TurboXasMotorParameters object
	 */
	static public TurboXasMotorParameters fromXML(String xmlString) {
		XStream xstream = TurboXasMotorParameters.getXStream();
		return (TurboXasMotorParameters) xstream.fromXML(xmlString);
	}

}
