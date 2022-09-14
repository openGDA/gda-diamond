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

import java.io.IOException;
import java.util.List;

import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.thoughtworks.xstream.annotations.XStreamAlias;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.jython.InterfaceProvider;
import gda.scan.ede.position.EnergyPositionCalculator;

/**
 * This class calculates real space motor positions for a Turbo XAS scan from user specified set of parameters based on energy.
 * @since 14/7/2016
 */
@XStreamAlias("TurboXasMotorParameters")
public class TurboXasMotorParameters {

	private static final Logger logger = LoggerFactory.getLogger(TurboXasMotorParameters.class);

	@JsonProperty("TurboXasParameters")
	private TurboXasParameters scanParameters;
	private TurboSlitTimingGroup currentTimingGroup = null;

	// These are all set using values from TurboXasScanParameters
	private double scanStartPosition, scanEndPosition;
	private double scanMotorSpeed;
	private double returnMotorSpeed;

	private double startPosition, endPosition, motorRampDistance;
	private int    numReadoutsForScan;
	private double positionStepsize;

	// These are parameters of the motor to be used for scan
	private double motorMaxSpeed;
	private double motorTimeToVelocity;
	private double motorHighLimit;
	private double motorLowLimit;

	private EnergyPositionCalculator positionCalculator = new EnergyPositionCalculator();

	// Resolution limit of position stepsize [mm] - should be set to match encoder resolution.
	private double stepsizeResolution;

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
		stepsizeResolution = 1e-4;
	}

	/**
	 * Get motor limits from scannableMotor
	 * @param scannableMotor
	 */
	public void setMotorLimits(Scannable scannableMotor) {

		if (scannableMotor==null) {
			return;
		}
		try {
			double lowerMotorLimit = (double) scannableMotor.getAttribute("lowerMotorLimit");
			double upperMotorLimit = (double) scannableMotor.getAttribute("upperMotorLimit");

			// If limits from upper/lowerMotorLimit are very big, server is probably running in dummy mode
			// and should instead try to use gda limits.
			final double numberTooBig = 1e100;
			if (Math.abs(lowerMotorLimit) > numberTooBig || Math.abs(upperMotorLimit) > numberTooBig ) {
				// gdaLimits returns Double[] as an Object
				Double[] val = (Double[])scannableMotor.getAttribute("lowerGdaLimits");
				if (val!=null) {
					lowerMotorLimit = (double) val[0];
				}
				val = (Double[])scannableMotor.getAttribute("upperGdaLimits");
				if (val!=null) {
					upperMotorLimit = (double) val[0];
				}
			}
			motorLowLimit = lowerMotorLimit;
			motorHighLimit = upperMotorLimit;

//			unitString = (String) scannableMotor.getAttribute(ScannableMotionUnits.USERUNITS);

		} catch (DeviceException| NullPointerException e) {
			logger.warn("Problem setting motor limits from scannable {}. Using currently set values {} and {}", motorLowLimit, motorHighLimit, e);
		}
	}

	public void setScanParameters(TurboXasParameters params) {
		scanParameters = params;
		positionCalculator = params.getEnergyPositionCalculator();
	}

	public void setPositionToEnergyPolynomial(String eqnString) {
		positionCalculator.setPolynomial(eqnString);
	}

	@JsonIgnore
	public PolynomialFunction getPositionToEnergyPolynomial() {
		return positionCalculator.getPolynomial();
	}

	public TurboXasParameters getScanParameters() {
		return scanParameters;
	}

	/**
	 *
	 * @return timing group last used to set motor parameters by call to {@link #setMotorParametersForTimingGroup(int)}
	 */
	@JsonIgnore
	public TurboSlitTimingGroup getCurrentTimingGroup() {
		return currentTimingGroup;
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
		currentTimingGroup = scanParameters.getTimingGroups().get(timingGroupIndex);
		setMotorParametersForTimingGroup(scanParameters.getTimingGroups().get(timingGroupIndex));
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

	public void setMotorParametersForTimingGroup(TurboSlitTimingGroup timingGroup) {
		setMotorParametersForTime(timingGroup.getTimePerSpectrum());
		returnMotorSpeed = getScanSpeed(timingGroup.getTimeBetweenSpectra());
	}

	/**
	 * Calculate and set motor parameters for given time for spectrum.
	 * @param timeForSpectrum
	 */
	public void setMotorParametersForTime(double timeForSpectrum) {
		if (scanParameters.isUsePositionsForScan()) {
			// User specified positions for start, end points
			scanStartPosition = scanParameters.getStartPosition();
			scanEndPosition = scanParameters.getEndPosition();
		} else {
			// Convert from energy to real-space motor positions
			scanStartPosition = getPositionForEnergy(scanParameters.getStartEnergy());
			scanEndPosition = getPositionForEnergy(scanParameters.getEndEnergy());
		}

		calculateSetPositionStepSize();

		double scanMotorDirection = 1.0;
		if ( scanEndPosition - scanStartPosition < 0 )
			scanMotorDirection = -1.0;

		// update end position so it can accommodate a whole number of steps
		scanEndPosition = scanStartPosition + scanMotorDirection*numReadoutsForScan*positionStepsize;

		scanMotorSpeed =  getScanSpeed(timeForSpectrum);
		// determine direction of motor move

		// ramp up distance and initial motor position
		double timeToVelocity = getMotorTimeToVelocity();
		motorRampDistance = 0.5 * scanMotorSpeed * timeToVelocity;
		startPosition = scanStartPosition - scanMotorDirection * (motorRampDistance + motorStabilisationDistance);
		endPosition = scanEndPosition + scanMotorDirection * (motorRampDistance + motorStabilisationDistance);
	}

	/**
	 * Calculate motor position step size and number of readouts/steps to use for scan from energy values.
	 * (i.e. 'Pulse step' and 'Max pulses' used for Zebra).
	 * Stepsize is encoder resolution limited to avoid rounding errors that can lead to difference between expected number
	 * of pulses and number produced by zebra from encoder readout - see {@link#getResolutionLimitedStepSize()}.
	 *
	 */
	public void calculateSetPositionStepSize() {
		// Make sure calculateMotorParameters has been called first, so that scanStartMotorPosition, and scanEndMotorPosition are up-to-date
		if (scanParameters.isUsePositionsForScan()) {
			positionStepsize = scanParameters.getPositionStepSize();
		} else {
			positionStepsize = getResolutionLimitedStepSize();
		}
		if (Math.abs(positionStepsize) < stepsizeResolution) {
			numReadoutsForScan = 0;
		} else {
			numReadoutsForScan = Math.abs((int) Math.floor(getScanPositionRange()/positionStepsize));
		}
	}

	/**
	 * Calculate resolution limited position step size corresponding to currently set energy.
	 * Step size is rounded down to nearest {@link#stepsizeResolution} mm.
	 * @return Resolution limited step size
	 */
	public double getResolutionLimitedStepSize() {
		double numStepsFromEnergy = Math.floor(scanParameters.getEndEnergy() - scanParameters.getStartEnergy())/scanParameters.getEnergyStep();
		if (numStepsFromEnergy==0) {
			return 0;
		}
		double nonRoundedPositionStepsize = getScanPositionRange()/numStepsFromEnergy;
		return Math.floor(nonRoundedPositionStepsize/stepsizeResolution)*stepsizeResolution;
	}

	public double getStepsizeResolution() {
		return stepsizeResolution;
	}

	public void setStepsizeResolution(double stepsizeResolution) {
		this.stepsizeResolution = stepsizeResolution;
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
	 * Validate currently set motor scan speed
	 * @return True if speed is < maximum speed of motor
	 */
	public boolean validMotorScanSpeed() {
		return scanMotorSpeed < motorMaxSpeed && scanMotorSpeed > 0;
	}

	public boolean validMotorReturnSpeed() {
		return returnMotorSpeed < motorMaxSpeed && returnMotorSpeed > 0;
	}
	/**
	 * Validate motor scan speed for all timing groups
	 * @return True if speeds for all groups are < maximum speed of motor
	 */
	public boolean validMotorScanSpeeds() {
		List<TurboSlitTimingGroup> timingGroups = scanParameters.getTimingGroups();

		for(int i=0; i<timingGroups.size(); i++) {
			double scanSpeed = getScanSpeed(timingGroups.get(i).getTimePerSpectrum());
			if (scanSpeed>motorMaxSpeed) {
				logger.warn("Calculated motor speed for timing group {} ({}) exceeds motor upper speed limit ({})",
						i, scanSpeed, motorMaxSpeed);
				return false;
			}
			double returnSpeed = getScanSpeed(timingGroups.get(i).getTimeBetweenSpectra());
			if (returnSpeed>motorMaxSpeed) {
				logger.warn("Calculated motor return speed for timing group {} ({}) exceeds motor upper speed limit ({})",
						i, returnSpeed, motorMaxSpeed);
				return false;
			}
		}
		return true;
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

	/**
	 * Validate motor parameters
	 * @return True if motor positions, speed
	 */
	public boolean validateParameters() {
		if ( !validMotorScanRange() ) {
			logger.warn("Initial and final motor positions are the same! Check scan parameters and/or energy-position calibration polynomial");
		}
		if ( !getMotorPositionsWithinLimits() ) {
			logger.warn("Initial, final motor positions for scan are outside of motor limits");
		}

		return validMotorScanRange() && getMotorPositionsWithinLimits() && validMotorScanSpeeds();
	}


	public double getPositionForEnergy(double energy) {
		return positionCalculator.getPositionForEnergy(energy);
	}

	public double getEnergyForPosition(double position) {
		return positionCalculator.getEnergyForPosition(position);
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
	 * @return Energy stepsize corresponding to currently set number of readouts.
	 * (Number of readouts is set using a resolution limited position stepsize)
	 */
	public double getEnergyStepSize() {
		return Math.floor(scanParameters.getEndEnergy() - scanParameters.getStartEnergy())/numReadoutsForScan;
	}

	/**
	 * Serialize {@link TurboXasMotorParameters} object to XML.
	 * @return String with XML serialized object
	 * @throws JsonProcessingException
	 */
	public String toXML() throws IOException {
		try {
			return XmlSerializationMappers.getXmlMapper().writeValueAsString(this);
		} catch (JsonProcessingException e) {
			throw new IOException("Problem converting TuboXasMotorParameters to XML", e);
		}
	}

	/**
	 * Create new {@link TurboXasMotorParameters} object deserialized from supplied XML string.
	 * @param xmlString
	 * @return TurboXasMotorParameters object
	 * @throws JsonProcessingException
	 * @throws JsonMappingException
	 */
	public static TurboXasMotorParameters fromXML(String xmlString) throws JsonMappingException, JsonProcessingException {
		return XmlSerializationMappers.getXmlMapper().readValue(xmlString, TurboXasMotorParameters.class);
	}

}
