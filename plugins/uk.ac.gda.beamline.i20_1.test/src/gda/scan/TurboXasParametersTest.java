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

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.CoreMatchers.notNullValue;
import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.assertTrue;

import org.dawnsci.ede.herebedragons.PolynomialParser;
import org.junit.Before;
import org.junit.Test;

public class TurboXasParametersTest {

	TurboXasParameters parameters;
	private TurboXasMotorParameters motorParameters;

	static final String testSampleName = "Test sample";
	static final double startEnergy = 1200.0;
	static final double endEnergy = 1800.0;
	static final double energyStep = 2.5;
	static double calibrationPolyMinEnergy = 1000, calibrationPolyEnergyRange = 1000;
	static final String calibrationPoly = "1000 + 1000*x + 20x^2";

	static final double calibrationMinPos = -5, calibrationMaxPos = 5;

	static final String group1Name ="first group";
	static final double group1TimePerSpectrum = 5.0, group1TimeBetweenSpectra = 10.0;
	static final int group1NumSpectra = 5;

	static final String group2Name ="2nd group";
	static final double group2TimePerSpectrum = 1.0e-3, group2TimeBetweenSpectra = 1.5e-3;
	static final int group2NumSpectra = 100;

	static final double numericalTolerance = 1e-9;

	@Before
	public void setUp() {
		parameters = new TurboXasParameters();
		parameters.setSampleName( testSampleName );
		parameters.setStartEnergy(startEnergy);
		parameters.setEndEnergy(endEnergy);
		parameters.setEnergyStep(energyStep);
		parameters.setEnergyCalibrationPolynomial( calibrationPoly );
		parameters.setEnergyCalibrationMinPosition(calibrationMinPos);
		parameters.setEnergyCalibrationMaxPosition(calibrationMaxPos);

		parameters.addTimingGroup( new TurboSlitTimingGroup(group1Name, group1TimePerSpectrum, group1TimeBetweenSpectra, group1NumSpectra) );
		parameters.addTimingGroup( new TurboSlitTimingGroup(group2Name, group2TimePerSpectrum, group2TimeBetweenSpectra, group2NumSpectra) );

		motorParameters = new TurboXasMotorParameters( parameters );
	}

	private void testDoublesEquals( double expected, double actual ) {
		assertEquals( expected, actual, numericalTolerance );
	}

	@Test
	public void serializedXmlCanBeProduced() {
		String xmlStringFromParams = parameters.toXML();
		assertThat( xmlStringFromParams, is(notNullValue()) );
		assertTrue(xmlStringFromParams.length() > 0);
	}

	@Test
	public void serializedXmlIsCorrect() {
		String xmlStringFromParams = parameters.toXML();
		String actualXmlString = getCorrectXmlString();
		assertThat( actualXmlString, is( equalTo(xmlStringFromParams) ) );
	}

	@Test
	public void parametersCopiedCorrectly() {
		assertThat( parameters.getSampleName(), is(equalTo(testSampleName)) );
		testDoublesEquals( startEnergy, parameters.getStartEnergy() );
		testDoublesEquals( endEnergy, parameters.getEndEnergy() );
		testDoublesEquals( energyStep, parameters.getEnergyStep() );
		assertThat( parameters.getEnergyCalibrationPolynomial(), is(equalTo(calibrationPoly)));
		testDoublesEquals( calibrationMinPos, parameters.getEnergyCalibrationMinPosition() );
		testDoublesEquals( calibrationMaxPos, parameters.getEnergyCalibrationMaxPosition() );

		// Test values of the timing groups ...
		assertThat( parameters.getTimingGroups().size(), is(equalTo(2)) );

		TurboSlitTimingGroup group = parameters.getTimingGroups().get(0);

		assertThat( group.getName(), is(equalTo(group1Name)) );
		testDoublesEquals( group.getTimePerSpectrum(), group1TimePerSpectrum);
		testDoublesEquals( group.getTimeBetweenSpectra(), group1TimeBetweenSpectra);
		assertThat( group.getNumSpectra(), is(equalTo(group1NumSpectra)) );

		group = parameters.getTimingGroups().get(1);

		assertThat( group.getName(), is(equalTo(group2Name)) );
		testDoublesEquals( group.getTimePerSpectrum(), group2TimePerSpectrum);
		testDoublesEquals( group.getTimeBetweenSpectra(), group2TimeBetweenSpectra);
		assertThat( group.getNumSpectra(), is(equalTo(group2NumSpectra)) );
	}

	@Test
	public void positionEnergyCalculationIsWorking() {
		// Test to make sure solver produces correct position values from energy :
		// Scan across range of polynomial, evaluate the calibration polynomial and run the solver...
		for(double frac = 0 ; frac <= 1.0; frac += 0.1 ) {

			double testPosition = calibrationMinPos + frac * ( calibrationMaxPos - calibrationMinPos );

			// straightforward evaluation of calibration of energy cal. polynomial
			double energy = motorParameters.getEnergyForPosition(testPosition);

			// solve energy polynomial to find motor position for given energy
			double calculatedPosition = motorParameters.getPositionForEnergy(energy);

			testDoublesEquals(testPosition, calculatedPosition);
		}
	}

	@Test
	public void motorCalculationsAreCorrect() {
		// set calibration poly to be linear so that position stepsize for energy step is constant across scan range
		motorParameters.setPositionToEnergyPolynomial("1000 + 1000*x");

		motorParameters.setMotorParametersForTimingGroup(0);

		// Motor positions for start and end of energy scan range
		double startPos = motorParameters.getPositionForEnergy( startEnergy );
		double endPos = motorParameters.getPositionForEnergy( endEnergy );
		testDoublesEquals( startPos, motorParameters.getScanStartPosition() );
		testDoublesEquals( endPos, motorParameters.getScanEndPosition() );

		// Motor positions for start and end of scan, including ramp up/down distance
		double rampDist = motorParameters.getMotorRampDistance() + motorParameters.getMotorStabilisationDistance();
		testDoublesEquals( endPos + rampDist, motorParameters.getEndPosition() );
		testDoublesEquals( startPos - rampDist, motorParameters.getStartPosition() );

		// Motor speed
		double scanSpeed = (endPos - startPos)/parameters.getTimingGroups().get(0).getTimePerSpectrum();
		testDoublesEquals( scanSpeed, motorParameters.getScanMotorSpeed() );

		assertThat( motorParameters.validateParameters(), is(equalTo(true)) );

		// Number of steps is correct (determined from position stepsize via calibration polynomial).
		int expectedNumReadouts =  (int)( (endEnergy - startEnergy)/energyStep );
		assertThat( motorParameters.getNumReadoutsForScan(), is( equalTo(expectedNumReadouts)) );
	}

	@Test
	public void motorPositionValidationDetectsBadParameters() {

		// Check that scan with zero range is detected
		parameters.setEndEnergy( startEnergy );
		motorParameters.setMotorParametersForTimingGroup(0);

		assertThat( motorParameters.validMotorScanRange(), is(equalTo(false)) );
		assertThat( motorParameters.validMotorScanSpeed(), is(equalTo(false)) );
		assertThat( motorParameters.getMotorPositionsWithinLimits(), is(equalTo(true)) );

		// Back to proper values again
		parameters.setEndEnergy( endEnergy );
		motorParameters.setMotorParametersForTimingGroup(0);
		assertThat( motorParameters.validateParameters(), is(equalTo(true)) );

		// Check that out of range motor positions are detected correctly
		double aSmallAmount = 1e-3;
		motorParameters.setMotorHighLimit( motorParameters.getEndPosition() - aSmallAmount );
		assertThat( motorParameters.getMotorPositionsWithinLimits(), is(equalTo(false)) );
		motorParameters.setDefaultMotorParams();

		motorParameters.setMotorLowLimit( motorParameters.getStartPosition() + aSmallAmount );
		assertThat( motorParameters.getMotorPositionsWithinLimits(), is(equalTo(false)) );
	}

	@Test
	public void polynomialCoeffsAreExtractedFromStringCorrectly() {
		// test polynomial parsing :
		//		correct parsing of coefficient and x separator
		// 		correct identification of terms without x and with implied coeff of 1
		//		correct summation of coefficient due to more than 1 term.
		String polyString = "1 + 2*x + 4x^3 + 5 x^5 + x + 9 + x^4";
		double [] correctCoeffs = {10, 3, 0, 4, 1, 5};

		double [] extractedCoeffs = PolynomialParser.extractCoefficientsFromString(polyString);
		assertArrayEquals( correctCoeffs, extractedCoeffs, numericalTolerance);
	}

	/**
	 * Return string with serialized version of TurboXasParameters test object
	 * @return
	 */
	private String getCorrectXmlString() {
		String serializedXmlString =
						"<TurboXasParameters>\n" +
						"  <sampleName>"+testSampleName+"</sampleName>\n" +
						"  <startEnergy>"+TurboXasParameters.doubleToString(startEnergy)+"</startEnergy>\n" +
						"  <endEnergy>"+TurboXasParameters.doubleToString(endEnergy)+"</endEnergy>\n" +
						"  <energyStep>"+TurboXasParameters.doubleToString(energyStep)+"</energyStep>\n" +
						"  <energyCalibrationPolynomial>"+calibrationPoly+"</energyCalibrationPolynomial>\n" +
						"  <energyCalibrationMinPosition>"+TurboXasParameters.doubleToString(calibrationMinPos)+"</energyCalibrationMinPosition>\n" +
						"  <energyCalibrationMaxPosition>"+TurboXasParameters.doubleToString(calibrationMaxPos)+"</energyCalibrationMaxPosition>\n" +
						"  <TimingGroup>\n" +
						"    <name>"+group1Name+"</name>\n" +
						"    <timePerSpectrum>"+TurboXasParameters.doubleToString(group1TimePerSpectrum)+"</timePerSpectrum>\n" +
						"    <timeBetweenSpectra>"+TurboXasParameters.doubleToString(group1TimeBetweenSpectra)+"</timeBetweenSpectra>\n" +
						"    <numSpectra>"+group1NumSpectra+"</numSpectra>\n" +
						"  </TimingGroup>\n" +
						"  <TimingGroup>\n" +
						"    <name>"+group2Name+"</name>\n" +
						"    <timePerSpectrum>"+TurboXasParameters.doubleToString(group2TimePerSpectrum)+"</timePerSpectrum>\n" +
						"    <timeBetweenSpectra>"+TurboXasParameters.doubleToString(group2TimeBetweenSpectra)+"</timeBetweenSpectra>\n" +
						"    <numSpectra>"+group2NumSpectra+"</numSpectra>\n" +
						"  </TimingGroup>\n" +
						"</TurboXasParameters>";
		return serializedXmlString;
	}
}
