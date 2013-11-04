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

package gda.scan;

import static org.junit.Assert.assertEquals;
import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.device.MotorException;
import gda.device.detector.DummyXStripDAServer;
import gda.device.detector.StepScanXHDetector;
import gda.device.detector.XHDetector;
import gda.device.enumpositioner.DummyPositioner;
import gda.device.monitor.DummyMonitor;
import gda.device.motor.DummyMotor;
import gda.device.scannable.ScannableMotor;
import gda.factory.FactoryException;
import gda.scan.ede.EdeLinearExperiment;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.EdeSingleExperiment;
import gda.scan.ede.position.EdePositionType;
import gda.scan.ede.position.EdeScanPosition;
import gda.scan.ede.position.ExplicitScanPositions;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.Vector;

import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
import org.junit.Test;

import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public class EdeScanTest extends EdeTestBase{

	private DummyXStripDAServer daserver;
	private XHDetector xh;
	private String testDir;
	private DummyMonitor topupMonitor;

	public void setup(String testName) throws Exception {
		/* String testFolder = */TestHelpers.setUpTest(EdeScanTest.class, testName, true);
		LocalProperties.setScanSetsScanNumber(true);
		LocalProperties.set("gda.scan.sets.scannumber", "true");
		LocalProperties.set("gda.scanbase.firstScanNumber", "-1");
		LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, "NexusDataWriter");
		LocalProperties.set("gda.nexus.createSRS", "false");
		testDir = LocalProperties.getBaseDataDir();

		// dummy daserver
		daserver = new DummyXStripDAServer();
		// detector
		xh = new XHDetector();
		xh.setDaServer(daserver);
		xh.setName("xh");
		xh.setDetectorName("xh0");
		xh.configure();
		// topup monitor
		topupMonitor = new DummyMonitor();
		topupMonitor.setName("topup");
		topupMonitor.setValue(120.0);
	}

	@Test
	public void testRunScan() throws Exception {
		setup("testRunScan");
		runTestScan(-1, 5);
	}

	@Test
	public void testRunScanOutputProgressData() throws Exception {
		setup("testRunScanOutputProgressData");
		// create the extra columns by having number of repetitions >= 0
		runTestScan(1, 10);
	}

	private void runTestScan(int repetitionNumber, int numberExpectedAsciiColumns) throws Exception {
		EdeScanParameters scanParams = new EdeScanParameters();
		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(20);
		group1.setTimePerScan(0.005);
		group1.setTimePerFrame(0.02);
		scanParams.addGroup(group1);

		ScannableMotor xScannable = createMotor("xScannable");
		ScannableMotor yScannable = createMotor("yScannable");

		LocalProperties.set("gda.nexus.createSRS", "true");
		ExplicitScanPositions inBeam = new ExplicitScanPositions(EdePositionType.INBEAM, 1d, 1d, xScannable, yScannable);
		// EdeScanPosition outBeam = new EdeScanPosition(EdePositionType.OUTBEAM,0d,0d,"xScannable","yScannable");

		EdeScan theScan = new EdeScan(scanParams, inBeam, EdeScanType.LIGHT, xh, repetitionNumber, createShutter2());
		theScan.runScan();

		List<ScanDataPoint> data = theScan.getData();

		assertEquals(20, data.size());

		// test the SRS file to see if the number of columns is correct
		FileReader asciiFile = new FileReader(testDir + File.separator + "1.dat");
		BufferedReader reader = null;
		try {
			reader = new BufferedReader(asciiFile);
			reader.readLine(); // &SRS
			reader.readLine(); // &END
			reader.readLine(); // header line
			String dataString = reader.readLine(); // first data point
			String[] dataParts = dataString.split("\t");
			assertEquals(numberExpectedAsciiColumns, dataParts.length);
		} finally {
			if (reader != null) {
				reader.close();
			}
		}
	}

	@Test
	public void testRunExperimentSameParameters() throws Exception {
		setup("testRunExperimentSameParameters");
		EdeScanParameters scanParams = new EdeScanParameters();
		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.005);
		group1.setTimePerFrame(0.02);
		scanParams.addGroup(group1);

		ScannableMotor xScannable = createMotor("xScannable");
		ScannableMotor yScannable = createMotor("yScannable");

		ExplicitScanPositions inBeam = new ExplicitScanPositions(EdePositionType.INBEAM, 1d, 1d, xScannable, yScannable);
		ExplicitScanPositions outBeam = new ExplicitScanPositions(EdePositionType.OUTBEAM, 0d, 0d, xScannable,
				yScannable);

		EdeSingleExperiment theExperiment = new EdeSingleExperiment(scanParams, outBeam, inBeam, xh, topupMonitor, createShutter2());
		String filename = theExperiment.runExperiment();

		testNumberColumnsInEDEFile(filename, 9);
	}

	@Test
	public void testRunExperimentDifferentParameters() throws Exception {
		setup("testRunExperimentDifferentParameters");
		EdeScanParameters i0Params = new EdeScanParameters();
		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.005);
		group1.setTimePerFrame(0.02);
		i0Params.addGroup(group1);

		EdeScanParameters itParams = new EdeScanParameters();
		TimingGroup group2 = new TimingGroup();
		group2.setLabel("group1");
		group2.setNumberOfFrames(1);
		group2.setTimePerScan(0.05);
		group2.setTimePerFrame(0.02);
		itParams.addGroup(group2);

		ScannableMotor xScannable = createMotor("xScannable");
		ScannableMotor yScannable = createMotor("yScannable");

		ExplicitScanPositions inBeam = new ExplicitScanPositions(EdePositionType.INBEAM, 1d, 1d, xScannable, yScannable);
		ExplicitScanPositions outBeam = new ExplicitScanPositions(EdePositionType.OUTBEAM, 0d, 0d, xScannable,
				yScannable);

		EdeSingleExperiment theExperiment = new EdeSingleExperiment(i0Params, itParams, outBeam, inBeam, xh, topupMonitor, createShutter2());
		String filename = theExperiment.runExperiment();

		testNumberColumnsInEDEFile(filename, 9);
	}

	private void testNumberColumnsInEDEFile(String filename, int numExpectedColumns) throws FileNotFoundException,
			IOException {
		List<String> lines = Files.readAllLines(Paths.get(filename), Charset.defaultCharset());
		for (String line : lines) {
			if (!line.startsWith("#")) {
				String[] dataParts = line.split("\t");
				assertEquals(numExpectedColumns, dataParts.length);
				return;
			}
		}
	}

	@Test
	public void testStepScan() throws Exception {
		setup("testExperimentUsingStepScan");
		LocalProperties.set("gda.nexus.createSRS", "true");
		ScannableMotor xScannable = createMotor("xScannable");
		StepScanXHDetector ssxh = new StepScanXHDetector();
		ssxh.setXh(xh);
		new ConcurrentScan(new Object[] { xScannable, 0., 1., 1., ssxh, 0.2 }).runScan();

		// test the SRS file to see if the number of columns is correct
		FileReader asciiFile = new FileReader(testDir + File.separator + "1.dat");
		BufferedReader reader = null;
		try {
			reader = new BufferedReader(asciiFile);
			reader.readLine(); // &SRS
			reader.readLine(); // &END
			reader.readLine(); // header line
			String dataString = reader.readLine(); // first data point
			String[] dataParts = dataString.split("\t");
			assertEquals(6, dataParts.length);
		} finally {
			if (reader != null) {
				reader.close();
			}
		}
	}

	@Test
	public void testSingleExperimentUsingEdeScanParametersStaticMethods() throws Exception {
		setup("testExperimentUsingEdeScanParametersStaticMethods");

		EdeScanParameters itparams = EdeScanParameters.createSingleFrameScan(0.2);

		ScannableMotor xScannable = createMotor("xScannable");
		ScannableMotor yScannable = createMotor("yScannable");

		ExplicitScanPositions inBeam = new ExplicitScanPositions(EdePositionType.INBEAM, 1d, 1d, xScannable, yScannable);
		ExplicitScanPositions outBeam = new ExplicitScanPositions(EdePositionType.OUTBEAM, 0d, 0d, xScannable,
				yScannable);

		EdeSingleExperiment theExperiment = new EdeSingleExperiment(itparams, outBeam, inBeam, xh, topupMonitor, createShutter2());
		String filename = theExperiment.runExperiment();

		testNumberColumnsInEDEFile(filename, 9);
	}

	@Test
	public void testSingleExperimentUsingEdeScanParametersStaticMethodsControlFilename() throws Exception {
		setup("testExperimentUsingEdeScanParametersStaticMethods");

		EdeScanParameters itparams = EdeScanParameters.createSingleFrameScan(0.2);

		ScannableMotor xScannable = createMotor("xScannable");
		ScannableMotor yScannable = createMotor("yScannable");

		ExplicitScanPositions inBeam = new ExplicitScanPositions(EdePositionType.INBEAM, 1d, 1d, xScannable, yScannable);
		ExplicitScanPositions outBeam = new ExplicitScanPositions(EdePositionType.OUTBEAM, 0d, 0d, xScannable,
				yScannable);

		EdeSingleExperiment theExperiment = new EdeSingleExperiment(itparams, outBeam, inBeam, xh, topupMonitor, createShutter2());
		theExperiment.setFilenameTemplate("mysample_%s_sample1");
		String filename = theExperiment.runExperiment();

		testNumberColumnsInEDEFile(filename, 9);
	}

	@Test
	public void testEnergyCalibrationUsingEdeScanParametersStaticMethods() throws Exception {
		setup("testEnergyCalibrationUsingEdeScanParametersStaticMethods");

		EdeScanParameters itparams = EdeScanParameters.createSingleFrameScan(0.2);

		ScannableMotor xScannable = createMotor("xScannable");
		ScannableMotor yScannable = createMotor("yScannable");

		ExplicitScanPositions inBeam = new ExplicitScanPositions(EdePositionType.INBEAM, 1d, 1d, xScannable, yScannable);
		ExplicitScanPositions outBeam = new ExplicitScanPositions(EdePositionType.OUTBEAM, 0d, 0d, xScannable,
				yScannable);

		xh.setEnergyCalibration(new PolynomialFunction(new double[] { 0., 2. }));

		EdeSingleExperiment theExperiment = new EdeSingleExperiment(itparams, outBeam, inBeam, xh, topupMonitor, createShutter2());
		String filename = theExperiment.runExperiment();

		boolean firstLine = true;
		List<String> lines = Files.readAllLines(Paths.get(filename), Charset.defaultCharset());
		for (String line : lines) {
			if (!line.startsWith("#") && firstLine) {
				String[] dataParts = line.split("\t");
				assertEquals(9, dataParts.length);
				firstLine = false;
			} else if (!line.startsWith("#") && !firstLine) {
				String[] dataParts = line.split("\t");
				assertEquals(9, dataParts.length);
				assertEquals(1., Double.parseDouble(dataParts[0]), 0.1);
				assertEquals(0.0, Double.parseDouble(dataParts[1]), 0.1);
				return;
			}
		}
	}

	@Test
	public void testSimpleLinearExperiment() throws Exception {
		setup("testSimpleLinearExperiment");

		Vector<TimingGroup> groups = new Vector<TimingGroup>();

		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(10);
		group1.setTimePerScan(0.005);
		group1.setNumberOfScansPerFrame(5);
		groups.add(group1);

		TimingGroup group2 = new TimingGroup();
		group2.setLabel("group2");
		group2.setNumberOfFrames(10);
		group2.setTimePerScan(0.05);
		group2.setNumberOfScansPerFrame(5);
		groups.add(group2);

		TimingGroup group3 = new TimingGroup();
		group3.setLabel("group3");
		group3.setNumberOfFrames(5);
		group3.setTimePerScan(0.01);
		group3.setNumberOfScansPerFrame(5);
		groups.add(group3);

		EdeScanParameters params = new EdeScanParameters();
		params.setGroups(groups);

		ScannableMotor xScannable = createMotor("xScannable");
		ScannableMotor yScannable = createMotor("yScannable");

		EdeScanPosition inBeam = new ExplicitScanPositions(EdePositionType.INBEAM, 1d, 1d, xScannable, yScannable);
		EdeScanPosition outBeam = new ExplicitScanPositions(EdePositionType.OUTBEAM, 0d, 0d, xScannable, yScannable);
		EdeScanPosition refSample = new ExplicitScanPositions(EdePositionType.REFERENCE, 0d, 0d, xScannable, yScannable);

		EdeLinearExperiment theExperiment = new EdeLinearExperiment(params, outBeam, inBeam, refSample, xh, topupMonitor, createShutter2());
		String filename = theExperiment.runExperiment();

		testNumberColumnsInEDEFile(filename, 8);
		testNumberLinesInEDEFile(filename, 1024 * 25);
		testNumberColumnsInEDEFile(theExperiment.getI0Filename(), 7);
		testNumberLinesInEDEFile(theExperiment.getI0Filename(), 1024 * 3 * 2);
		testNumberColumnsInEDEFile(theExperiment.getIRefFilename(), 4);
		testNumberLinesInEDEFile(theExperiment.getIRefFilename(), 1024 * 3);
		testNumberColumnsInEDEFile(theExperiment.getItFinalFilename(), 8);
		testNumberLinesInEDEFile(theExperiment.getItFinalFilename(), 1024 * 25);
		testNumberColumnsInEDEFile(theExperiment.getItAveragedFilename(), 8);
		testNumberLinesInEDEFile(theExperiment.getItAveragedFilename(), 1024 * 25);
	}

	private void testNumberLinesInEDEFile(String filename, int numExpectedLines) throws IOException {
		List<String> lines = Files.readAllLines(Paths.get(filename), Charset.defaultCharset());

		int numDataLines = 0;
		for (String line : lines) {
			if (!line.startsWith("#"))
				numDataLines++;
		}
		assertEquals(numExpectedLines, numDataLines);
	}

}
