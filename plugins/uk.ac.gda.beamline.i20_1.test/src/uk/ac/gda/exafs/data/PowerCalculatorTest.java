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

package uk.ac.gda.exafs.data;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;

import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.january.dataset.Maths;
import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.TestHelpers;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.EdeDummyDetector;
import gda.device.enumpositioner.DummyEnumPositioner;
import gda.device.scannable.DummyScannable;
import gda.factory.Factory;
import gda.factory.FactoryException;
import gda.factory.Finder;
import gda.scan.EdeTestBase;
import uk.ac.gda.exafs.data.PowerCalulator.FilterMirrorElementType;
import uk.ac.gda.exafs.data.PowerCalulator.Mirrors;

public class PowerCalculatorTest {
	private static final Logger logger = LoggerFactory.getLogger(PowerCalculatorTest.class);

	public static final String FOLDER_PATH = "testfiles/uk/ac/gda/exafs/data/PowerCalculatorTest";
	private DummyEnumPositioner atn1;
	private Scannable atn2;
	private Scannable atn3;
	private Scannable atn4;
	private Scannable atn5;

	private Scannable me1Stripe;
	private Scannable me2Stripe;
	private PowerCalulator powerCalculator;

	@Before
	public void prepare() throws Exception {
		// Set the Realm so that Writeable lists and listeners for databinding can initialise without errors.
		// (Realm is set automatically when running the GUI)
		CurrentRealm realm = new CurrentRealm(true);
		CurrentRealm.setDefault(realm);

		atn1 = createPositioner("atn1");

		atn1.setPositions(Arrays.asList("Empty",
				getFilterPosition(FilterMirrorElementType.pC.name(),  0.8),
				getFilterPosition(FilterMirrorElementType.pC.name(), 1.2),
				getFilterPosition(FilterMirrorElementType.SiC.name(), 1.0),
				getFilterPosition(FilterMirrorElementType.SiC.name(), 0.2)
				));

		atn1.moveTo("Empty");

		atn2 = createPositioner("atn2");
		atn3 = createPositioner("atn3");

		atn4 = createPositioner("atn4");
		atn5 = createPositioner("atn5");

		me1Stripe = createPositioner("me1_stripe");
		me2Stripe = createPositioner("me2_stripe");

		Scannable detectorDistance = new DummyScannable("det_distance", 500.0);
		detectorDistance.configure();

		EdeDummyDetector detector = new EdeDummyDetector();
		detector.setName("xstrip");
		detector.setMainDetectorName("xstrip");

		final Factory factory = TestHelpers.createTestFactory();
		factory.addFindable(atn1);
		factory.addFindable(atn2);
		factory.addFindable(atn3);
		factory.addFindable(atn4);
		factory.addFindable(atn5);
		factory.addFindable(me1Stripe);
		factory.addFindable(me2Stripe);
		factory.addFindable(detector);
		factory.addFindable(detectorDistance);
		Finder.addFactory(factory);

		// Unit tests are based on attenuators 1, 2, 3.
		AlignmentParametersModel.INSTANCE.setUseAtn45(false);

		powerCalculator = new PowerCalulator();
		powerCalculator.setDataPath(FOLDER_PATH);
	}

	@AfterClass
	public static void tearDownClass() {
		// Remove factories from Finder so they do not affect other tests
		Finder.removeAllFactories();
	}

	private DummyEnumPositioner createPositioner(String name) throws FactoryException {
		DummyEnumPositioner dummyPositioner = new DummyEnumPositioner();
		dummyPositioner.setName(name);
		dummyPositioner.setPositions(Arrays.asList("Pos1", "Pos2", "Pos3"));
		dummyPositioner.configure();
		return dummyPositioner;
	}

	@Test
	public void fieldSlitGapNameTest() {
		try {
			assertEquals("1p3T", powerCalculator.getFieldName(19.0));
			assertEquals("0p33T", powerCalculator.getFieldName(50.0));
			assertEquals("1p0mrad", powerCalculator.getSlitHGapName(0.96));

			assertEquals(0.8, powerCalculator.getRoundedWigglerHGap(0.7), 1e-3);
			assertEquals(1.6, powerCalculator.getRoundedWigglerHGap(1.7), 1e-3);
		} catch (Exception e) {
			Assert.fail();
		}
	}

	@Test
	public void fieldValuesTest() throws Exception {
		assertEquals(1.3, powerCalculator.getFieldValue(18.4), 1e-6);
		assertEquals(1.3, powerCalculator.getFieldValue(18.5), 1e-6);
		assertEquals(1.3, powerCalculator.getFieldValue(19.24), 1e-6);
		assertEquals(1.2, powerCalculator.getFieldValue(19.25), 1e-6);
		assertEquals(1.2, powerCalculator.getFieldValue(20), 1e-6);
		assertEquals(1.0, powerCalculator.getFieldValue(23.9), 1e-6);
		assertEquals(0.74, powerCalculator.getFieldValue(30), 1e-6);
		assertEquals(0.74, powerCalculator.getFieldValue(34.9), 1e-6);
		assertEquals(0.48, powerCalculator.getFieldValue(35), 1e-6);
		assertEquals(0.48, powerCalculator.getFieldValue(40), 1e-6);
		assertEquals(0.33, powerCalculator.getFieldValue(50), 1e-6);
		assertEquals(0.33, powerCalculator.getFieldValue(250), 1e-6);
	}

	@Test
	public void fileNameTest() throws Exception {
		File file = getEnergyFieldFile(19.0, 0.96);
		assertEquals("1p3T-300mA-0p12x1p0mrad.dat", file.getName());
		file = getEnergyFieldFile(45.0, 1.09);
		assertEquals("0p33T-300mA-0p12x1p1mrad.dat", file.getName());
	}

	@Test(expected = FileNotFoundException.class)
	public void fileNotFoundExceptionTest() throws FileNotFoundException {
		getEnergyFieldFile(251.0, 1.09);
	}

	@Test
	public void nameSplitTest() {
		String[] result = PowerCalulator.Mirrors.INSTANCE.getNameParts("pC 2.0mm");
		assertArrayEquals(new String[] {"pC", "2.0", "mm"}, result);

		result = PowerCalulator.Mirrors.INSTANCE.getNameParts("SiC1.5mm");
		assertArrayEquals(new String[] {"SiC", "1.5", "mm"}, result);

		result = PowerCalulator.Mirrors.INSTANCE.getNameParts("pC 0.6mm (Crkd)");
		assertArrayEquals(new String[] {"pC", "0.6", "mm"}, result);

		result = PowerCalulator.Mirrors.INSTANCE.getNameParts("Left Empty");
		assertArrayEquals(new String[] {}, result);

		result = PowerCalulator.Mirrors.INSTANCE.getNameParts("Empty 3.1mrad");
		assertArrayEquals(new String[] {}, result);

		result = PowerCalulator.Mirrors.INSTANCE.getNameParts("pC 0.1 mm 3.1 mrad");
		assertArrayEquals(new String[] {"pC",  "0.1", "mm"}, result);

		result = PowerCalulator.Mirrors.INSTANCE.getNameParts("pC 4.0mm 3.1mrad");
		assertArrayEquals(new String[] {"pC",  "4.0", "mm"}, result);
	}

	@Test
	public void testFilterFileNames() throws DeviceException {
		atn1.setPosition(atn1.getPositions()[1]);
		String name = Mirrors.INSTANCE.getDataFileName(atn1.getName(), atn1.getPosition(), 0);
		assertEquals("C-pyro-0p8mm.dat", name);

		atn1.setPosition(atn1.getPositions()[2]);
		name = Mirrors.INSTANCE.getDataFileName(atn1.getName(), atn1.getPosition(), 0);
		assertEquals("C-pyro-1p2mm.dat", name);

		atn1.setPosition(atn1.getPositions()[3]);
		name = Mirrors.INSTANCE.getDataFileName(atn1.getName(), atn1.getPosition(), 0);
		assertEquals("SiC-1p0mm.dat", name);

		atn1.setPosition(atn1.getPositions()[4]);
		name = Mirrors.INSTANCE.getDataFileName(atn1.getName(), atn1.getPosition(), 0);
		assertEquals("SiC-0p2mm.dat", name);
	}

	@Test
	public void testFluxLoadsOk() throws Exception {
		File file = getEnergyFieldFile(19.0, 0.96);
		Dataset values = powerCalculator.loadDatasetFromFile(file);
		List<String[]> dataFromFile = EdeTestBase.getDataFromAsciiFile(file.getAbsolutePath());
		assertEquals("Number of rows of data from "+file.getName()+" is not correct", dataFromFile.size(), values.getShape()[0]);
		assertEquals("Number of columns of data loaded from "+file.getName()+" is not correct", dataFromFile.get(0).length, values.getShape()[1]);

		for(int i=0; i<dataFromFile.size(); i++) {
			double expectedValue = Double.parseDouble(dataFromFile.get(i)[1]);
			assertEquals(expectedValue, values.getDouble(i, 1), 1e-6);
		}
	}

	@Test
	public void testFluxFilterWithBeAtn1Calculation() throws Exception {

		ScannableSetup.ATN1.getScannable().moveTo(atn1.getPositions()[1]);

		// Load energy flux and filter data from files
		File energyFieldFile = getEnergyFieldFile(19.0, 0.96);
		File atnFilterFile = new File(FOLDER_PATH, Mirrors.INSTANCE.getDataFileName(atn1.getName(), atn1.getPosition(), 0));

		Dataset energyField = getDatasetFromFile(energyFieldFile);
		Dataset beFilter = getBeFilterTransmission();
		Dataset atnFilter = getDatasetFromFile(atnFilterFile);

		// Multiply together to get total transmission
		Dataset trans = Maths.multiply(energyField,  beFilter);
		trans = Maths.multiply(trans, atnFilter);
		int numValues = trans.getShape()[0];

		Dataset values = powerCalculator.calculateFluxVsEnergyForAllFilters(FOLDER_PATH, 19.0, 0.96, powerCalculator.getMirrorFilterMap());

		// Compare PowerCalculator filtered flux with manually calculated result
		for(int i=0; i<numValues; i++) {
			checkFlux(trans, values, i);
		}
	}

	@Test
	public void testFluxFilterWithBeCalculation() throws Exception {

		// Load energy flux and Be filter data from file
		File energyFieldFile = getEnergyFieldFile(19.0, 0.96);

		Dataset energyField = getDatasetFromFile(energyFieldFile);
		Dataset beFilter = getBeFilterTransmission();
		int numValues = beFilter.getShape()[0];
		Dataset trans = Maths.multiply(energyField,  beFilter);

		// Make sure ATN1 scannable is set to empty
		ScannableSetup.ATN1.getScannable().moveTo("Empty");
		System.out.println("testFluxFilterWithBeCalculation, atn1 = "+ atn1.getPosition());
		Dataset totalFlux = powerCalculator.calculateFluxVsEnergyForAllFilters(FOLDER_PATH, 19.0, 0.96, powerCalculator.getMirrorFilterMap());

		// Compare PowerCalculator filtered flux with manually calculated result
		for(int i=0; i<numValues; i++) {
			checkFlux(trans, totalFlux, i);
		}
	}

	@Test
	public void testFindNearest() {
		assertEquals(3.0, PowerCalulator.Mirrors.INSTANCE.findNearest(3.124), Double.MIN_VALUE);
		assertEquals(3.25, PowerCalulator.Mirrors.INSTANCE.findNearest(3.13), Double.MIN_VALUE);
	}

	@Test
	public void testPower() throws Exception {
		ScannableSetup.ATN1.getScannable().moveTo(atn1.getPositions()[0]);
		powerCalculator.setRingCurrent(300);
		double power = powerCalculator.getPower(19.0, 0.96);
		double expected = 238.87603840327034;
		assertEquals(expected, power, 1e-4);

		powerCalculator.setRingCurrent(150);
		power = powerCalculator.getPower(19.0, 0.96);
		assertEquals(expected*0.5, power, 1e-4);

		ScannableSetup.ATN1.getScannable().moveTo(atn1.getPositions()[1]);
		powerCalculator.setRingCurrent(300);
		power = powerCalculator.getPower(19.0, 0.96);
		expected = 158.43633630769472;
		assertEquals(expected, power, 1e-4);
	}

	/**
	 * Read table of numbers from Ascii file store in a dataset. Skips over lines beginning with '#'
	 * @param file
	 * @return Dataset of numbers shape = (numRows, numColumns);
	 * @throws IOException
	 */
	private Dataset getDatasetFromFile(File file) throws IOException {
		logger.info("Loading dataset from file {}", file.getName());
		List<String[]> valuesFromFile = EdeTestBase.getDataFromAsciiFile(file.getAbsolutePath());
		int numRows = valuesFromFile.size();
		int numCols = valuesFromFile.get(0).length; // assume same number of values in each row

		Dataset dataset = DatasetFactory.zeros(DoubleDataset.class, numRows, numCols);
		for(int i=0; i<numRows; i++) {
			String[] values = valuesFromFile.get(i);
			for(int j=0; j<numCols; j++) {
				dataset.set(Double.parseDouble(values[j]), i, j);
			}
		}
		return dataset;
	}

	private String getFilterPosition(String name, double thickness) {
		return String.format("%s %.1fmm", name, thickness);
	}

	private void adjustTransmission(Dataset transmission, double power) {
		for(int i=0; i<transmission.getShape()[0]; i++) {
			double trans = Math.pow(transmission.getDouble(i, 1), power);
			transmission.set(trans, i, 1);
		}
	}

	private Dataset getBeFilterTransmission() throws IOException {
		File beFilterFile = new File(FOLDER_PATH, PowerCalulator.BE_FILTER_FILE_NAME);
		Dataset beFilter = getDatasetFromFile(beFilterFile);
		adjustTransmission(beFilter, PowerCalulator.BE_FILTER_THICKNESS_MM/0.3);
		return beFilter;
	}

	private void checkFlux(Dataset expectedData, Dataset actualData, int index) {
		double expected = expectedData.getDouble(index,1);
		double actual = actualData.getDouble(index,1);
		double diff = Math.abs(expected-actual);
		double fracDiff = actual > 1e-10 ? diff/actual : diff;
		assertTrue("Flux value "+index+" was not correct. Expected = "+expected+", actual = "+actual, fracDiff < 1e-4);
	}

	private File getEnergyFieldFile(double wigglerGap, double s1HGap) throws FileNotFoundException, IllegalArgumentException {
		return powerCalculator.getEnergyFieldFile(FOLDER_PATH, wigglerGap, s1HGap);
	}
}