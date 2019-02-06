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
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.assertTrue;

import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.dawnsci.ede.PolynomialParser;
import org.junit.Before;
import org.junit.Test;

import com.thoughtworks.xstream.XStream;

public class TurboXasParametersTest {

	TurboXasParameters parameters;
	private TurboXasMotorParameters motorParameters;

	static final String testSampleName = "Test sample";
	static final double startEnergy = 1200.0;
	static final double endEnergy = 1800.0;
	static final double energyStep = 2.5;

	static final double startPosition = 0.0;
	static final double endPosition = 10.0;
	static final double positionStep = 0.1;
	static final boolean usePositionsForScan = true;

	static double calibrationPolyMinEnergy = 1000, calibrationPolyEnergyRange = 1000;
	static final String calibrationPoly = calibrationPolyMinEnergy+" + 1000*x + 20x^2";

	static final double calibrationMinPos = -5, calibrationMaxPos = 5;
	static final String calibrationRefFilename = "reference_file.txt";
	static final String calibrationSampleFilename = "sample_file.txt";

	static final String group1Name ="first group";
	static final double group1TimePerSpectrum = 5.0, group1TimeBetweenSpectra = 10.0;
	static final int group1NumSpectra = 5;

	static final String group2Name ="2nd group";
	static final double group2TimePerSpectrum = 1.0e-3, group2TimeBetweenSpectra = 1.5e-3;
	static final int group2NumSpectra = 100;

	static final double numericalTolerance = 1e-9;

	private static final String defaultMotorToMove = "turbo_xas_slit";
	private static final String defaultDetector = "scaler_for_zebra";
	private static final boolean defaultUseTrajectoryScan = false;

	private static final List<String> extraScannablesList = Arrays.asList("scannable1", "scannable2");

	private Map<String,String> scannablesToMonitor = null;
	private boolean writeAsciiData = false;

	@Before
	public void setUp() {
		parameters = new TurboXasParameters();
		parameters.setSampleName( testSampleName );
		parameters.setStartEnergy(startEnergy);
		parameters.setEndEnergy(endEnergy);
		parameters.setEnergyStep(energyStep);
		parameters.setUsePositionsForScan(true);
		parameters.setEnergyCalibrationPolynomial( calibrationPoly );
		parameters.setEnergyCalibrationMinPosition(calibrationMinPos);
		parameters.setEnergyCalibrationMaxPosition(calibrationMaxPos);
		parameters.setEnergyCalibrationFile(calibrationSampleFilename);
		parameters.setEnergyCalibrationReferenceFile(calibrationRefFilename);

		parameters.addTimingGroup( new TurboSlitTimingGroup(group1Name, group1TimePerSpectrum, group1TimeBetweenSpectra, group1NumSpectra) );
		parameters.addTimingGroup( new TurboSlitTimingGroup(group2Name, group2TimePerSpectrum, group2TimeBetweenSpectra, group2NumSpectra) );

		parameters.setDetectors(new String[] { defaultDetector });
		parameters.setExtraScannables(extraScannablesList);
		motorParameters = parameters.getMotorParameters();
		motorParameters.setMotorMaxSpeed(10000);
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
		String actualXmlString = getCorrectXmlString(parameters);
		assertThat(xmlStringFromParams , is( equalTo(actualXmlString) ) );
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

		assertEquals( defaultDetector,  parameters.getDetectors()[0]);

		assertEquals( extraScannablesList, parameters.getExtraScannables());

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
		parameters.setUsePositionsForScan(false);
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
		parameters.setUsePositionsForScan(false);
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
		parameters.setUsePositionsForScan(false);
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

	public String getExpectedMapXmlString(Map<String, String> map) {
		return getExpectedMapXmlString(map, "");
	}

	public String getExpectedMapXmlString(Map<String, String> map, String prefix) {
		String xmlString = prefix+"<scannablesToMonitorDuringScan>\n";
		String keyName = TurboXasParameters.MapConverter.keyNodeName;
		String valueName = TurboXasParameters.MapConverter.valueNodeName;

		for(Entry item : map.entrySet()) {
			xmlString += String.format("%s  <%s>%s</%s>\n", prefix, keyName, item.getKey(), keyName);
			xmlString += String.format("%s  <%s>%s</%s>\n", prefix, valueName, item.getValue(), valueName);
		}
		xmlString += prefix+"</scannablesToMonitorDuringScan>";
		return xmlString;
	}

	@Test
	public void testMapSerializesOk() {
		Map<String, String> map = getScannableMap();
		String expectedMapString = getExpectedMapXmlString(map);

		XStream xstream = TurboXasParameters.getXStream();
		String serializedMapString = xstream.toXML(map);

		assertNotNull(serializedMapString);
		assertEquals("Serialized map string does not match expected value", expectedMapString, serializedMapString);
	}

	@Test
	public void testMapDeserializesOk() {
		Map<String, String> map = getScannableMap();
		String expectedMapString = getExpectedMapXmlString(map);

		XStream xstream = TurboXasParameters.getXStream();
		Map<String,String> deserializedMap = (Map<String,String>)xstream.fromXML(expectedMapString);
		assertEquals("Deserialized map object not match expected value", map, deserializedMap);
	}

	private Map<String, String> getScannableMap() {
		Map<String, String> map = new LinkedHashMap<>();
		map.put("scannable1", "");
		map.put("scannable2", "pv:for:scannable2");
		return map;
	}

	@Test
	public void testExtraScannablesSerialize() {
		scannablesToMonitor = getScannableMap();
		parameters.setScannablesToMonitorDuringScan(scannablesToMonitor);
		String xmlStringFromParams = parameters.toXML();
		String expectedXmlString = getCorrectXmlString(parameters);
		assertThat(xmlStringFromParams , is( equalTo(expectedXmlString) ) );
	}


	@Test(expected = IllegalArgumentException.class)
	public void testGetPositionThrowsExceptionForTooLowEnergy() {
		motorParameters.getPositionForEnergy(calibrationPolyMinEnergy*0.5);
	}

	/**
	 * Return string with serialized version of TurboXasParameters test object
	 * @return
	 */
	private String getCorrectXmlString(TurboXasParameters parameters) {
		StringBuilder serializedXmlString = new StringBuilder();

		serializedXmlString.append(
			"<TurboXasParameters>\n" +
			"  <sampleName>"+parameters.getSampleName()+"</sampleName>\n" +
			"  <startEnergy>"+TurboXasParameters.doubleToString(parameters.getStartEnergy())+"</startEnergy>\n" +
			"  <endEnergy>"+TurboXasParameters.doubleToString(parameters.getEndEnergy())+"</endEnergy>\n" +
			"  <energyStep>"+TurboXasParameters.doubleToString(parameters.getEnergyStep())+"</energyStep>\n" +
			"  <startPosition>"+TurboXasParameters.doubleToString(parameters.getStartPosition())+"</startPosition>\n" +
			"  <endPosition>"+TurboXasParameters.doubleToString(parameters.getEndPosition())+"</endPosition>\n" +
			"  <positionStepSize>"+TurboXasParameters.doubleToString(parameters.getPositionStepSize())+"</positionStepSize>\n" +
			"  <usePositionsForScan>"+parameters.isUsePositionsForScan()+"</usePositionsForScan>\n" +
			"  <energyCalibrationPolynomial>"+parameters.getEnergyCalibrationPolynomial()+"</energyCalibrationPolynomial>\n" +
			"  <energyCalibrationMinPosition>"+TurboXasParameters.doubleToString(parameters.getEnergyCalibrationMinPosition())+"</energyCalibrationMinPosition>\n" +
			"  <energyCalibrationMaxPosition>"+TurboXasParameters.doubleToString(parameters.getEnergyCalibrationMaxPosition())+"</energyCalibrationMaxPosition>\n" +
			"  <energyCalibrationReferenceFile>"+parameters.getEnergyCalibrationReferenceFile()+"</energyCalibrationReferenceFile>\n" +
			"  <energyCalibrationFile>"+parameters.getEnergyCalibrationFile()+"</energyCalibrationFile>\n" +
			"  <motorToMove>"+parameters.getMotorToMove()+"</motorToMove>\n");

		// Add the detector(s)
		serializedXmlString.append("  <detectors>\n");
		for(String detectorName : parameters.getDetectors()) {
			serializedXmlString.append("    <string>"+detectorName+"</string>\n");
		}
		serializedXmlString.append("  </detectors>\n");

		serializedXmlString.append("  <useTrajectoryScan>"+parameters.getUseTrajectoryScan()+"</useTrajectoryScan>\n");

		if (parameters.getTimingGroups() != null) {
			parameters.getTimingGroups().forEach( timingGroup -> {
				serializedXmlString.append(
				"  <TimingGroup>\n" +
				"    <name>"+timingGroup.getName()+"</name>\n" +
				"    <timePerSpectrum>"+TurboXasParameters.doubleToString(timingGroup.getTimePerSpectrum())+"</timePerSpectrum>\n" +
				"    <timeBetweenSpectra>"+TurboXasParameters.doubleToString(timingGroup.getTimeBetweenSpectra())+"</timeBetweenSpectra>\n" +
				"    <numSpectra>"+timingGroup.getNumSpectra()+"</numSpectra>\n" +
				"  </TimingGroup>\n");
				}
			);
		}

		if (parameters.getScannablesToMonitorDuringScan() != null) {
			serializedXmlString.append(getExpectedMapXmlString(parameters.getScannablesToMonitorDuringScan(), "  ")+"\n");
		}

		if (parameters.getExtraScannables() != null) {
			serializedXmlString.append("  <extraScannables>\n");
			parameters.getExtraScannables().forEach((name) -> serializedXmlString.append("    <string>"+name+"</string>\n") );
			serializedXmlString.append("  </extraScannables>\n");
		}
		serializedXmlString.append("  <writeAsciiData>"+parameters.getWriteAsciiData()+"</writeAsciiData>\n");
		serializedXmlString.append("  <fastShutterName>"+parameters.getFastShutterName()+"</fastShutterName>\n");
		serializedXmlString.append("</TurboXasParameters>");

		return serializedXmlString.toString();
	}
}