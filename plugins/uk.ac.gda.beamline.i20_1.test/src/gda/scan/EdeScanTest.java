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

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.dawnsci.analysis.api.tree.DataNode;
import org.eclipse.dawnsci.analysis.api.tree.GroupNode;
import org.eclipse.dawnsci.hdf5.nexus.NexusFileHDF5;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.dawnsci.nexus.NexusFile;
import org.junit.Ignore;
import org.junit.Test;
import org.powermock.core.classloader.annotations.PowerMockIgnore;

import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.device.detector.xstrip.DummyXStripDAServer;
import gda.device.detector.xstrip.StepScanXHDetector;
import gda.device.detector.xstrip.XhDetector;
import gda.device.enumpositioner.DummyPositioner;
import gda.device.monitor.DummyMonitor;
import gda.device.scannable.ScannableMotor;
import gda.factory.Findable;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.SingleSpectrumScan;
import gda.scan.ede.datawriters.EdeTimeResolvedExperimentDataWriter;
import gda.scan.ede.position.EdePositionType;
import gda.scan.ede.position.ExplicitScanPositions;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

@Ignore("2015/09/29 All tests in the class are currently ignored, so just ignore the entire class")
@PowerMockIgnore({"javax.management.*", "javax.xml.parsers.*", "com.sun.org.apache.xerces.internal.jaxp.*", "ch.qos.logback.*", "org.slf4j.*"})
public class EdeScanTest extends EdeTestBase {

	private static final int MCA_WIDTH = 1024;
	private DummyXStripDAServer daserver;
	private XhDetector xh;
	private String testDir;
	private DummyMonitor topupMonitor;
	private final DummyPositioner shutter = createShutter2();
	private ScannableMotor xScannable;
	private ScannableMotor yScannable;
	private Map<String, Double> inOutBeamMotors;

	private void setup(String testName) throws Exception {
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
		xh = new XhDetector();
		xh.setDaServer(daserver);
		xh.setName("xh");
		xh.setDetectorName("xh0");
		File file = new File(LocalProperties.getVarDir(), "/templates/EdeScan_Parameters.xml");
		xh.setTemplateFileName(file.getAbsolutePath());
		xh.configure();
		// topup monitor
		topupMonitor = new DummyMonitor();
		topupMonitor.setName("topup");
		topupMonitor.setValue(120.0);

		xScannable = createMotor("xScannable");
		yScannable = createMotor("yScannable");

		Map<String, Findable> mockScannble = new HashMap<String, Findable>();
		mockScannble.put("xh", xh);
		mockScannble.put("topup", topupMonitor);
		mockScannble.put(shutter.getName(), shutter);
		mockScannble.put(EdeExperiment.PROGRESS_UPDATER_NAME, null);
		mockScannble.put("xScannable", xScannable);
		mockScannble.put("yScannable", yScannable);
		setupMockForFinder(mockScannble);

		inOutBeamMotors = new HashMap<String, Double>();
		inOutBeamMotors.put("xScannable", 0.3);
		inOutBeamMotors.put("yScannable", 0.3);
	}

	// FIXME Rewrite the tests
	@Test()
	@Ignore
	public void testRunExperimentSameParameters() throws Exception {
		setup("testRunExperimentSameParameters");

		SingleSpectrumScan theExperiment = new SingleSpectrumScan(0.001, 0.005, 1, inOutBeamMotors, inOutBeamMotors,
				"xh", "topup", shutter.getName());
		String filename = theExperiment.runExperiment();

		testNumberColumnsInEDEFile(filename, 9);
	}

	// FIXME Rewrite the tests
	@Test
	@Ignore
	public void testRunScan() throws Exception {
		setup("testRunScan");
		runTestScan(-1, 1);
	}

	// FIXME Rewrite the tests
	@Test
	@Ignore
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

		EdeScan theScan = new EdeScan(scanParams, inBeam, EdeScanType.LIGHT, xh, repetitionNumber, createShutter2(),null);
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

	// FIXME Rewrite the tests
	@Test
	@Ignore
	public void testStepScan() throws Exception {
		setup("testStepScan");
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
	@Ignore
	public void testSimpleLinearExperiment() throws Exception {
//		setup("testSimpleLinearExperiment");
//
//		List<TimingGroup> groups = new ArrayList<TimingGroup>();
//
//		TimingGroup group1 = new TimingGroup();
//		group1.setLabel("group1");
//		group1.setNumberOfFrames(10);
//		group1.setTimePerScan(0.005);
//		group1.setNumberOfScansPerFrame(5);
//		groups.add(group1);
//
//		TimingGroup group2 = new TimingGroup();
//		group2.setLabel("group2");
//		group2.setNumberOfFrames(10);
//		group2.setTimePerScan(0.05);
//		group2.setNumberOfScansPerFrame(5);
//		groups.add(group2);
//
//		TimingGroup group3 = new TimingGroup();
//		group3.setLabel("group3");
//		group3.setNumberOfFrames(5);
//		group3.setTimePerScan(0.01);
//		group3.setNumberOfScansPerFrame(5);
//		groups.add(group3);
//
//		TimeResolvedExperiment theExperiment = new TimeResolvedExperiment(0.1, groups, inOutBeamMotors, inOutBeamMotors,
//				"xh", "topup", shutter.getName());
//		theExperiment.setIRefParameters(inOutBeamMotors, inOutBeamMotors, 0.1, 1, 0.1, 1);
//		String filename = theExperiment.runExperiment();
//
//		int numberExpectedSpectra = 25;
//
//		testNumberColumnsInEDEFile(filename, 9);
//		testNumberLinesInEDEFile(filename, MCA_WIDTH * numberExpectedSpectra);
//		testNumberColumnsInEDEFile(theExperiment.getI0Filename(), 7);
//		testNumberLinesInEDEFile(theExperiment.getI0Filename(), MCA_WIDTH * 3 * 2);
//		testNumberColumnsInEDEFile(theExperiment.getIRefFilename(), 4);
//		testNumberLinesInEDEFile(theExperiment.getIRefFilename(), MCA_WIDTH * 2);
//		testNumberColumnsInEDEFile(theExperiment.getItFinalFilename(), 9);
//		testNumberLinesInEDEFile(theExperiment.getItFinalFilename(), MCA_WIDTH * numberExpectedSpectra);
//		testNumberColumnsInEDEFile(theExperiment.getItAveragedFilename(), 9);
//		testNumberLinesInEDEFile(theExperiment.getItAveragedFilename(), MCA_WIDTH * numberExpectedSpectra);
//
//		testNexusStructure(theExperiment.getNexusFilename(), numberExpectedSpectra, 1);
	}

	private void testNexusStructure(String  nexusFilename, int numberExpectedSpectra, int numberRepetitions) throws Exception {
		NexusFile file = NexusFileHDF5.openNexusFileReadOnly(nexusFilename);
		GroupNode g = file.getGroup("/entry1", false);

		// cyclic?
		if (numberRepetitions > 1){
			assertLinearData(file, g, EdeTimeResolvedExperimentDataWriter.NXDATA_LN_I0_IT+"_averaged",numberExpectedSpectra, false);
			assertLinearData(file, g, EdeTimeResolvedExperimentDataWriter.NXDATA_LN_I0_IT_WITH_FINAL_I0+"_averaged",numberExpectedSpectra, false);
			assertLinearData(file, g, EdeTimeResolvedExperimentDataWriter.NXDATA_LN_I0_IT_WITH_AVERAGED_I0+"_averaged",numberExpectedSpectra, false);
			numberExpectedSpectra *= numberRepetitions;
			assertLinearData(file, g, EdeTimeResolvedExperimentDataWriter.NXDATA_LN_I0_IT,numberExpectedSpectra, true);
			assertLinearData(file, g, EdeTimeResolvedExperimentDataWriter.NXDATA_LN_I0_IT_WITH_FINAL_I0,numberExpectedSpectra, true);
			assertLinearData(file, g, EdeTimeResolvedExperimentDataWriter.NXDATA_LN_I0_IT_WITH_AVERAGED_I0,numberExpectedSpectra, true);
		} else {
			assertLinearData(file, g, EdeTimeResolvedExperimentDataWriter.NXDATA_LN_I0_IT,numberExpectedSpectra, false);
			assertLinearData(file, g, EdeTimeResolvedExperimentDataWriter.NXDATA_LN_I0_IT_WITH_FINAL_I0,numberExpectedSpectra, false);
			assertLinearData(file, g, EdeTimeResolvedExperimentDataWriter.NXDATA_LN_I0_IT_WITH_AVERAGED_I0,numberExpectedSpectra, false);
		}
		file.close();
	}

	private void assertLinearData(NexusFile file, GroupNode g, String dataName, int numberSpectra, boolean testForCycles) throws NexusException{
		GroupNode gd = file.getGroup(g, dataName, null, false);
		assertDimensions(file, gd, "data", new int[] { numberSpectra, MCA_WIDTH });
		assertDimensions(file, gd, "energy", new int[] { MCA_WIDTH });
		assertDimensions(file, gd, "group", new int[] { numberSpectra,4 });
		assertDimensions(file, gd, "time", new int[] { numberSpectra });
		if (testForCycles){
			assertDimensions(file, gd, "cycle", new int[] { numberSpectra });
		}
	}

	private void assertDimensions(NexusFile file, GroupNode gd, String dataName, int[] expectedDims) throws NexusException {
		DataNode d = file.getData(gd, dataName);
		int[] shape = d.getDataset().getShape();
		for (int i = 0; i < expectedDims.length; i++) {
			assertEquals(expectedDims[i], shape[i]);
		}
	}

	@Test
	@Ignore
	public void testSimpleCyclicExperiment() throws Exception {
//		setup("testSimpleCyclicExperiment");
//
//		List<TimingGroup> groups = new ArrayList<TimingGroup>();
//
//		TimingGroup group1 = new TimingGroup();
//		group1.setLabel("group1");
//		group1.setNumberOfFrames(10);
//		group1.setTimePerScan(0.005);
//		group1.setNumberOfScansPerFrame(5);
//		groups.add(group1);
//
//		TimingGroup group2 = new TimingGroup();
//		group2.setLabel("group2");
//		group2.setNumberOfFrames(10);
//		group2.setTimePerScan(0.05);
//		group2.setNumberOfScansPerFrame(5);
//		groups.add(group2);
//
//		TimingGroup group3 = new TimingGroup();
//		group3.setLabel("group3");
//		group3.setNumberOfFrames(5);
//		group3.setTimePerScan(0.01);
//		group3.setNumberOfScansPerFrame(5);
//		groups.add(group3);
//
//		CyclicExperiment theExperiment = new CyclicExperiment(0.1, groups, inOutBeamMotors, inOutBeamMotors,
//				"xh", "topup", shutter.getName(), 3);
//		theExperiment.setIRefParameters(inOutBeamMotors, inOutBeamMotors, 0.1, 1, 0.1, 1);
//		String filename = theExperiment.runExperiment();
//
//		testNumberColumnsInEDEFile(filename, 10);
//		testNumberLinesInEDEFile(filename, (1024 * 25 * 3));
//
//		testNumberColumnsInEDEFile(theExperiment.getI0Filename(), 7);
//		testNumberLinesInEDEFile(theExperiment.getI0Filename(), 1024 * 3 * 2);
//
//		testNumberColumnsInEDEFile(theExperiment.getIRefFilename(), 4);
//		testNumberLinesInEDEFile(theExperiment.getIRefFilename(), 1024 * 2);
//
//		testNumberColumnsInEDEFile(theExperiment.getItFilename(), 10);
//		testNumberLinesInEDEFile(theExperiment.getItFilename(), (1024 * 25 * 3));
//
//		testNumberColumnsInEDEFile(theExperiment.getItFinalFilename(), 10);
//		testNumberLinesInEDEFile(theExperiment.getItFinalFilename(), (1024 * 25 * 3));
//
//		testNumberColumnsInEDEFile(theExperiment.getItAveragedFilename(), 10);
//		testNumberLinesInEDEFile(theExperiment.getItAveragedFilename(), (1024 * 25 * 3));

//		testNexusStructure(theExperiment.getNexusFilename(), 25, 3);
	}

	private void testNumberLinesInEDEFile(String filename, int numExpectedLines) throws IOException {
		List<String> lines = Files.readAllLines(Paths.get(filename), Charset.defaultCharset());

		int numDataLines = 0;
		for (String line : lines) {
			if (!line.startsWith("#")) {
				numDataLines++;
			}
		}
		assertEquals(numExpectedLines, numDataLines);
	}

}
