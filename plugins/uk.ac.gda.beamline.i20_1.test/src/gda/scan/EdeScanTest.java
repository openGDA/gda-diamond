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
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.io.FilenameUtils;
import org.dawnsci.ede.DataFileHelper;
import org.dawnsci.ede.EdeDataConstants;
import org.dawnsci.ede.EdePositionType;
import org.dawnsci.ede.EdeScanType;
import org.dawnsci.ede.TimeResolvedDataFileHelper;
import org.eclipse.dawnsci.hdf5.nexus.NexusFileFactoryHDF5;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.dawnsci.nexus.NexusFile;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;
import org.powermock.core.classloader.annotations.PowerMockIgnore;

import gda.configuration.properties.LocalProperties;
import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import gda.device.DeviceException;
import gda.device.detector.DummyDAServer;
import gda.device.detector.EdeDummyDetector;
import gda.device.detector.StepScanEdeDetector;
import gda.device.detector.countertimer.TfgScaler;
import gda.device.detector.xstrip.DummyXStripDAServer;
import gda.device.detector.xstrip.XhDetector;
import gda.device.enumpositioner.DummyEnumPositioner;
import gda.device.memory.Scaler;
import gda.device.monitor.DummyMonitor;
import gda.device.scannable.ScannableMotor;
import gda.device.scannable.ScannableUtils;
import gda.factory.FactoryException;
import gda.factory.Finder;
import gda.factory.ObjectFactory;
import gda.jython.InterfaceProvider;
import gda.jython.scriptcontroller.ScriptControllerBase;
import gda.scan.ede.CyclicExperiment;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.SingleSpectrumScan;
import gda.scan.ede.TimeResolvedExperiment;
import gda.scan.ede.TimeResolvedExperimentParameters;
import gda.scan.ede.position.EdeScanMotorPositions;
import gda.scan.ede.position.ExplicitScanPositions;
import uk.ac.gda.exafs.experiment.trigger.TFGTrigger;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject.TriggerOutputPort;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

@PowerMockIgnore({"javax.management.*", "javax.xml.parsers.*", "com.sun.org.apache.xerces.internal.jaxp.*", "ch.qos.logback.*", "org.slf4j.*"})
public class EdeScanTest extends EdeTestBase {

	private static final int MCA_WIDTH = 1024;
	private DummyXStripDAServer daserver;
	private XhDetector xh;
	private DummyMonitor topupMonitor;
	private final DummyEnumPositioner shutter = createShutter2();
	private ScannableMotor xScannable;
	private ScannableMotor yScannable;
	private Map<String, Double> inOutBeamMotors;
	private ScriptControllerBase edeProgressUpdater;
	private AsciiDataWriterConfiguration config;
	private EdeDummyDetector dummyEdeDetector;

	private DummyDAServer daserverForTfg;
	private Scaler memory;
	private TfgScaler injectionCounter;

	@Before
	public void setupEnvironment() throws Exception {
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

		dummyEdeDetector = new EdeDummyDetector();
		dummyEdeDetector.setName("dummyEdeDetector");
		dummyEdeDetector.setMainDetectorName(xh.getName());
//		dummyEdeDetector.setLowerChannel(0);
		dummyEdeDetector.setMaxPixel(MCA_WIDTH);
		dummyEdeDetector.setUpperChannel(dummyEdeDetector.getMaxPixel());
		dummyEdeDetector.configure();

		// topup monitor
		topupMonitor = new DummyMonitor();
		topupMonitor.setName("topup");
		topupMonitor.setValue(120.0);

		xScannable = createMotor("xScannable", 7000);
		yScannable = createMotor("yScannable", 8000);

		edeProgressUpdater = new ScriptControllerBase();
		edeProgressUpdater.setName(EdeExperiment.PROGRESS_UPDATER_NAME);

		ObjectFactory factory = new ObjectFactory();
		factory.addFindable(xh);
		factory.addFindable(dummyEdeDetector);
		factory.addFindable(topupMonitor);
		factory.addFindable(shutter);
		factory.addFindable(xScannable);
		factory.addFindable(yScannable);
		factory.addFindable(edeProgressUpdater);

		createObjectsForEdeScanWithTfg();
		factory.addFindable(daserverForTfg);
		factory.addFindable(injectionCounter);

		config = new AsciiDataWriterConfiguration();
		factory.addFindable(config);

		Finder.getInstance().addFactory(factory);

		inOutBeamMotors = new HashMap<String, Double>();
		inOutBeamMotors.put(xScannable.getName(), 0.3);
		inOutBeamMotors.put(yScannable.getName(), 0.3);
	}

	public void createObjectsForEdeScanWithTfg() throws FactoryException, DeviceException {
		daserverForTfg = new DummyDAServer();
		daserverForTfg.setName("daserverForTfg");
		daserverForTfg.configure();

		memory = new Scaler();
		memory.setDaServer(daserverForTfg);
		memory.setHeight(1);
		memory.setWidth(4);
		memory.setOpenCommand("tfg open-cc");
		memory.configure();

		injectionCounter = new TfgScaler();
		injectionCounter.setScaler(memory);
		injectionCounter.setName("injectionCounter");
		injectionCounter.setNumChannelsToRead(3);
		injectionCounter.setTimeChannelRequired(false);
		injectionCounter.setOutputFormat(new String[] { "%6.4g", "%6.4g", "%6.4g", "%6.4g" });
	}

	@Test()
	public void testSingleSpectrumScan() throws Exception {
		setup(EdeScanTest.class, "testSingleSpectrumScan");

		SingleSpectrumScan theExperiment = new SingleSpectrumScan(0.001, 1, 0.005, 1, inOutBeamMotors, inOutBeamMotors,
				"xh", "topup", shutter.getName());

		String sampleDetails = "Sample details - single spectrum scan";
		theExperiment.setSampleDetails(sampleDetails);

		String filename = theExperiment.runExperiment();
		testNumberColumnsInEDEFile(filename, 9);
		testNexusStructure(theExperiment.getNexusFilename(), 1, 0);

		// Check the sample details are set correctly in Nexus file
		testSampleDetails(theExperiment.getNexusFilename(), sampleDetails);
	}

	@Test
	public void testRunScan() throws Exception {
		setup(EdeScanTest.class, "testRunScan");
		runEdeScan(-1, 1);
	}

	@Test
	public void testRunScanOutputProgressData() throws Exception {
		setup(EdeScanTest.class, "testRunScanOutputProgressData");
		// create the extra columns by having number of repetitions >= 0
		runEdeScan(10, 1);
	}

	private void runEdeScan(int repetitionNumber, int numberExpectedAsciiColumns) throws Exception {
		EdeScanParameters scanParams = new EdeScanParameters();
		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(20);
		group1.setTimePerScan(0.005);
		group1.setTimePerFrame(0.02);
		scanParams.addGroup(group1);

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

	@Test
	public void testStepScan() throws Exception {
		setup(EdeScanTest.class, "testStepScan");
		LocalProperties.set("gda.nexus.createSRS", "true");
		ScannableMotor xScannable = createMotor("xScannable");
		StepScanEdeDetector ssxh = new StepScanEdeDetector();
		ssxh.setDetector(xh);

		int numExpectedColumns = 6;
		int numExpectedDataRows = 11;

		Scan scan = new ConcurrentScan(new Object[] { xScannable, 0., 10., 1., ssxh, 0.2 });
		scan.runScan();
		String nxsFilename = InterfaceProvider.getCurrentScanInformationHolder().getCurrentScanInformation().getFilename();
		String asciiFilename = nxsFilename.replace(".nxs", ".dat");

		// Test dimensions of scan data in Nexus file
		checkDetectorData(nxsFilename, xh.getName(), numExpectedDataRows);
		assertDimensions(nxsFilename, xh.getName(), xScannable.getName(), new int[] {numExpectedDataRows});

		// test the SRS file to see if the number of columns and rows are correct
		FileReader asciiFile = new FileReader(asciiFilename);
		BufferedReader reader = null;
		try {
			reader = new BufferedReader(asciiFile);
			// Skip header parts
			String dataString = "";
			while( !dataString.startsWith(xScannable.getName()) ) {
				dataString=reader.readLine();
			}
			// Read first row of data
			dataString=reader.readLine();

			// Read and count rows of data, make sure each is correct length
			int numDataRows = 0;
			while(dataString!=null && dataString.length()>0) {
				String[] dataParts = dataString.split("\t");
				assertEquals(numExpectedColumns, dataParts.length);
				dataString=reader.readLine();
				numDataRows++;
			}

			// Check number of rows of data is
			assertEquals(numExpectedDataRows, numDataRows);

		} finally {
			if (reader != null) {
				reader.close();
			}
		}
	}

	private int getNumSpectra(List<TimingGroup> groups) {
		int totalNumSpectra = 0;
		for(TimingGroup group : groups) {
			totalNumSpectra += group.getNumberOfFrames();
		}
		return totalNumSpectra;
	}

	@Test
	public void testSimpleLinearExperimentWithMotorMove() throws Exception {
		setup(EdeScanTest.class, "testSimpleLinearExperimentWithMotorMove");

		List<TimingGroup> groups = new ArrayList<TimingGroup>();

		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(10);
		group1.setTimePerScan(0.005);
		group1.setNumberOfScansPerFrame(5);
		groups.add(group1);

		TimeResolvedExperiment theExperiment = new TimeResolvedExperiment(0.1, groups, inOutBeamMotors, inOutBeamMotors,
				xh.getName(), topupMonitor.getName(), shutter.getName());

		String sampleDetails = "Sample details - linear experiment with motor move";
		theExperiment.setSampleDetails(sampleDetails);

		EdeScanMotorPositions itPos = theExperiment.getItScanPositions();
		itPos.setScannableToMoveDuringScan(xScannable);
		itPos.setMotorPositionsDuringScan(1, 5, 5);

		// Check values of motor positions are correct
		List<Double> scanPositions = itPos.getMotorPositionsDuringScan();
		double[] expectedPositions = new double[]{1, 2, 3, 4, 5};
		for(int i=0; i<scanPositions.size(); i++) {
			assertEquals(scanPositions.get(i), expectedPositions[i], 1e-5);
		}

		theExperiment.runExperiment();
		int numberExpectedSpectra = getNumSpectra(groups)*scanPositions.size();
		testNexusStructure(theExperiment.getNexusFilename(), numberExpectedSpectra, 1);

		int numRawSpectra = numberExpectedSpectra+4; // lightIt + (darkI0, darkIt, lightI0, lightI0 after scan)
		checkDetectorData(theExperiment.getNexusFilename(), xh.getName(), numRawSpectra);
		checkDetectorTimeframeData(theExperiment.getNexusFilename(), xh.getName(), numRawSpectra);

		// check correct number of motor position values have been written
		assertDimensions(theExperiment.getNexusFilename(), xh.getName(), xScannable.getName(), new int[] {numRawSpectra});

		// Check the sample details are set correctly in Nexus file
		testSampleDetails(theExperiment.getNexusFilename(), sampleDetails);
	}

	private void checkDetectorData(String nexusFilename, String detectorName, int numSpectra) throws NexusException {
		// Check that raw data has correct dimensions and all non-negative values (i.e. counts)
		assertDimensions(nexusFilename, detectorName, EdeDataConstants.DATA_COLUMN_NAME, new int[]{numSpectra, MCA_WIDTH});
		checkDataValidRange(nexusFilename, detectorName, EdeDataConstants.DATA_COLUMN_NAME, new RangeValidator(0, 0, true, false));

		// Check that pixel data has correct dimensions and ranges from 0... MCA_WIDTH
		assertDimensions(nexusFilename, detectorName, EdeDataConstants.PIXEL_COLUMN_NAME, new int[]{MCA_WIDTH});
		checkDataValidRange(nexusFilename, detectorName, EdeDataConstants.PIXEL_COLUMN_NAME, new RangeValidator(0, MCA_WIDTH, true, true));

		assertDimensions(nexusFilename, detectorName, EdeDataConstants.ENERGY_COLUMN_NAME, new int[]{MCA_WIDTH});
	}

	public void checkDetectorTimeframeData(String nexusFilename, String detectorName, int numSpectra) throws NexusException {

		String[] specInfoColumns = new String[]{ EdeDataConstants.CYCLE_COLUMN_NAME, EdeDataConstants.FRAME_COLUMN_NAME,
												 EdeDataConstants.TIMINGGROUP_COLUMN_NAME, EdeDataConstants.IT_COLUMN_NAME,
												 EdeDataConstants.BEAM_IN_OUT_COLUMN_NAME };

		for(String columnName : specInfoColumns) {
			assertDimensions(nexusFilename, detectorName, columnName, new int[]{numSpectra});
		}

	}

	@Test
	public void testSimpleLinearExperiment() throws Exception {
		setup(EdeScanTest.class, "testSimpleLinearExperiment");

		List<TimingGroup> groups = new ArrayList<TimingGroup>();

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

		TimeResolvedExperiment theExperiment = new TimeResolvedExperiment(0.1, groups, inOutBeamMotors, inOutBeamMotors,
				xh.getName(), topupMonitor.getName(), shutter.getName());
		theExperiment.setIRefParameters(inOutBeamMotors, inOutBeamMotors, 0.1, 1, 0.1, 1);
		theExperiment.runExperiment();

		int numberExpectedSpectra = getNumSpectra(groups);

		testNexusStructure(theExperiment.getNexusFilename(), numberExpectedSpectra, 1);
		checkDetectorData(theExperiment.getNexusFilename(), xh.getName(), numberExpectedSpectra+16);
		checkDetectorTimeframeData(theExperiment.getNexusFilename(), xh.getName(), numberExpectedSpectra+16);
		testEdeAsciiFiles(theExperiment.getNexusFilename(), numberExpectedSpectra, groups.size(), true);
	}

	@Test
	public void testLinearExperimentMonitorScannables() throws Exception {
		setup(EdeScanTest.class, "testLinearExperimentMonitorScannables");

		List<TimingGroup> groups = new ArrayList<TimingGroup>();

		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(10);
		group1.setTimePerScan(0.005);
		group1.setNumberOfScansPerFrame(5);
		groups.add(group1);

		double xposition = ScannableUtils.getCurrentPositionArray(xScannable)[0];
		double yposition = ScannableUtils.getCurrentPositionArray(yScannable)[0];

		TimeResolvedExperiment theExperiment = new TimeResolvedExperiment(0.1, groups, inOutBeamMotors, inOutBeamMotors,
				xh.getName(), topupMonitor.getName(), shutter.getName());
		theExperiment.addScannableToMonitorDuringScan(xScannable);
		theExperiment.addScannableToMonitorDuringScan(yScannable.getName()); // use finder to locate scannable
		theExperiment.runExperiment();
		String nexusFilename = theExperiment.getNexusFilename();
		int numberExpectedSpectra = getNumSpectra(groups) + 4;

		// Check dataset for scannable positions have correct dimensions and content
		assertDimensions(nexusFilename, xh.getName(), xScannable.getName(), new int[]{numberExpectedSpectra});
		checkDataValidRange(nexusFilename, xh.getName(), xScannable.getName(), new RangeValidator(xposition, xposition, true, true));

		assertDimensions(nexusFilename, xh.getName(), yScannable.getName(), new int[]{numberExpectedSpectra});
		checkDataValidRange(nexusFilename, xh.getName(), yScannable.getName(), new RangeValidator(yposition, yposition, true, true));
	}

	private void testNexusStructure(String nexusFilename, int numberExpectedSpectra, int numberRepetitions) throws Exception {
		boolean checkForCycles = numberRepetitions>1;
		if (numberRepetitions > 0){
			// Scans with I0 measured before and after It
			numberExpectedSpectra *= numberRepetitions;
			assertLinearData(nexusFilename, EdeDataConstants.LN_I0_IT_COLUMN_NAME,numberExpectedSpectra, checkForCycles);
			assertLinearData(nexusFilename, EdeDataConstants.LN_I0_IT_AVG_I0S_COLUMN_NAME,numberExpectedSpectra, checkForCycles);
			assertLinearData(nexusFilename, EdeDataConstants.LN_I0_IT_FINAL_I0_COLUMN_NAME,numberExpectedSpectra, checkForCycles);
		} else {
			// numberRepetitions = 0 -> single spectrum scan (no final I0 measurement)
			assertLinearData(nexusFilename, EdeDataConstants.LN_I0_IT_COLUMN_NAME,numberExpectedSpectra, checkForCycles);
		}
	}

	private void assertLinearData(String nexusFilename, String groupName, int numberSpectra, boolean testForCycles) throws NexusException{
		assertDimensions(nexusFilename, groupName, EdeDataConstants.DATA_COLUMN_NAME, new int[] { numberSpectra, MCA_WIDTH });
		assertDimensions(nexusFilename, groupName, EdeDataConstants.ENERGY_COLUMN_NAME, new int[] { MCA_WIDTH });
		assertDimensions(nexusFilename, groupName, EdeDataConstants.TIMINGGROUP_COLUMN_NAME, new int[] { numberSpectra });
		assertDimensions(nexusFilename, groupName, EdeDataConstants.TIME_COLUMN_NAME, new int[] { numberSpectra });
		assertDimensions(nexusFilename, groupName, EdeDataConstants.PIXEL_COLUMN_NAME, new int[] { MCA_WIDTH });

		if (testForCycles){
			assertDimensions(nexusFilename, groupName, EdeDataConstants.CYCLE_COLUMN_NAME, new int[] { numberSpectra });
		}
	}

	@Test
	@Ignore
	public void testSimpleCyclicExperiment() throws Exception {
		setup(EdeScanTest.class, "testSimpleCyclicExperiment");

		List<TimingGroup> groups = new ArrayList<TimingGroup>();

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

		final int numCycles = 3;
		final int numberExpectedSpectra = getNumSpectra(groups);

		CyclicExperiment theExperiment = new CyclicExperiment(0.1, groups, inOutBeamMotors, inOutBeamMotors,
				"xh", "topup", shutter.getName(), numCycles);
		theExperiment.setIRefParameters(inOutBeamMotors, inOutBeamMotors, 0.1, 1, 0.1, 1);
		String filename = theExperiment.runExperiment();

		testEdeAsciiFiles(theExperiment.getNexusFilename(), numberExpectedSpectra, 3, false);

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


		testNexusStructure(theExperiment.getNexusFilename(), numberExpectedSpectra, numCycles);
	}

	private String getAsciiName(String nexusFilename, String filenameExt) {
		String asciiFolder = DataFileHelper.convertFromNexusToAsciiFolder(nexusFilename);
		String filenameNoPrefix = FilenameUtils.getName(nexusFilename);
		return asciiFolder + FilenameUtils.removeExtension(filenameNoPrefix) + "_" + filenameExt + "." +  EdeDataConstants.ASCII_FILE_EXTENSION;
	}

	private void testEdeAsciiFiles(String nexusFilename, int numberExpectedSpectra, int numTimingGroups, boolean testIref) throws IOException {
		testEdeAsciiFile(getAsciiName(nexusFilename, EdeDataConstants.IT_COLUMN_NAME), 3, MCA_WIDTH*numberExpectedSpectra);
		testEdeAsciiFile(getAsciiName(nexusFilename, EdeDataConstants.LN_I0_IT_AVG_I0S_COLUMN_NAME), 3, MCA_WIDTH*numberExpectedSpectra);
		testEdeAsciiFile(getAsciiName(nexusFilename, EdeDataConstants.LN_I0_IT_FINAL_I0_COLUMN_NAME), 3, MCA_WIDTH*numberExpectedSpectra);
		testEdeAsciiFile(getAsciiName(nexusFilename, EdeDataConstants.IT_RAW_COLUMN_NAME), 7, MCA_WIDTH*numberExpectedSpectra);
		testEdeAsciiFile(getAsciiName(nexusFilename, EdeDataConstants.I0_RAW_COLUMN_NAME), 6, MCA_WIDTH*numTimingGroups*2);
		if (testIref) {
			testEdeAsciiFile(getAsciiName(nexusFilename, EdeDataConstants.IREF_RAW_DATA_NAME), 7, MCA_WIDTH);
			testEdeAsciiFile(getAsciiName(nexusFilename, EdeDataConstants.IREF_DATA_NAME), 3, MCA_WIDTH);
			testEdeAsciiFile(getAsciiName(nexusFilename, EdeDataConstants.IREF_FINAL_DATA_NAME), 3, MCA_WIDTH);
		}
	}

	private void testEdeAsciiFile(String path, int numColumns, int numRows) throws IOException {
		testNumberColumnsInEDEFile(path, numColumns);
		testNumberLinesInEDEFile(path, numRows);
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

	private void testSampleDetails(String nexusFilename, String expectedSampleDetails) throws Exception {
		try (NexusFile file = new NexusFileFactoryHDF5().newNexusFile(nexusFilename)) {
			file.openToWrite(false);
			String sampleDetailsFromAttribute = file.getAttributeValue("/entry1/metaData@" + EdeDataConstants.SAMPLE_DETAILS_NAME);
			assertEquals(expectedSampleDetails,  sampleDetailsFromAttribute);
		}
	}

	private TFGTrigger getTfgTrigger() {
		TFGTrigger triggerParams = new TFGTrigger();
		// triggerParams.setDetector(xh);
		triggerParams.getDetectorDataCollection().setTriggerDelay(0.1); // start time
		triggerParams.getDetectorDataCollection().setTriggerPulseLength(0.001);
		triggerParams.getDetectorDataCollection().setNumberOfFrames(5);
		triggerParams.getDetectorDataCollection().setCollectionDuration(0.50688);
		return triggerParams;
	}

	private TimeResolvedExperimentParameters getTimeResolvedExperimentParameters() throws DeviceException {
		EdeScanParameters scanParams = new EdeScanParameters();
		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(20);
		group1.setTimePerScan(0.005);
		group1.setTimePerFrame(0.02);
		scanParams.addGroup(group1);

		TFGTrigger tfgTrigger = getTfgTrigger();
		TriggerableObject trigger1= tfgTrigger.createNewSampleEnvEntry( 0.0995, 2*1e-3, TriggerOutputPort.USR_OUT_2 );
		tfgTrigger.getSampleEnvironment().add(trigger1);

		LocalProperties.set("gda.nexus.createSRS", "true");

		Map<String, Double> itPositionsMap = new HashMap<String, Double>();
		itPositionsMap.put(xScannable.getName(), 10.12);
		itPositionsMap.put(yScannable.getName(), 11.14);

		Map<String, Double> i0PositionsMap = new HashMap<String, Double>();
		i0PositionsMap.put(xScannable.getName(), 10.144);

		EdeScanMotorPositions scanMotorPositions=new EdeScanMotorPositions(EdePositionType.INBEAM, itPositionsMap);
		scanMotorPositions.setScannableToMoveDuringScan(yScannable);
		scanMotorPositions.setMotorPositionsDuringScan(0,  10,  11);

		TimeResolvedExperimentParameters allParams = new TimeResolvedExperimentParameters();
		allParams.setFileNamePrefix("filename_prefix");
		allParams.setSampleDetails("sample_details");
		allParams.setI0AccumulationTime(1.11);
		allParams.setI0NumAccumulations(17);
		allParams.setItTimingGroups(scanParams.getGroups());
		allParams.setItTriggerOptions(tfgTrigger);
		allParams.setI0MotorPositions(i0PositionsMap);
		allParams.setItMotorPositions(itPositionsMap);
		allParams.setDetectorName(xh.getName());
		allParams.setTopupMonitorName("topup");
		allParams.setBeamShutterScannableName(shutter.getName());
		allParams.setHideLemoFields(true);
		allParams.setGenerateAsciiData(true);
		return allParams;
	}

	@Test
	public void testEdeScanIsSetCorrectlyFromParameters() throws Exception {
		setup(EdeScanTest.class, "testEdeScanIsSetCorrectlyFromParameters");

		TimeResolvedExperimentParameters allParams = getTimeResolvedExperimentParameters();

		TimeResolvedExperiment tre = allParams.createTimeResolvedExperiment();

		// Basic checks to make sure TimeResolvedExperiment has correct settings
		assertEquals(tre.getI0ScanPositions().getPositionMap(), allParams.getI0MotorPositions() );
		assertEquals(tre.getItScanPositions().getPositionMap(), allParams.getItMotorPositions() );
		assertEquals(tre.getSampleDetails(), allParams.getSampleDetails());
		assertEquals(tre.getFileNamePrefix(), allParams.getFileNamePrefix());
		assertEquals(tre.getUseFastShutter(), allParams.getUseFastShutter());
		assertEquals(tre.getFastShutterName(), allParams.getFastShutterName());

		// Check the timing group
		EdeScanParameters itScanParameters = tre.getItScanParameters();
		assertEquals(itScanParameters.getGroups(), allParams.getItTimingGroups());
		assertEquals(itScanParameters.getTotalNumberOfFrames(), allParams.getItTimingGroups().get(0).getNumberOfFrames());
		assertEquals(tre.getItTriggerOptions(), allParams.getItTriggerOptions());
	}

	@Test
	public void testTimeResolvedExperimentParametersSerializeOk() throws Exception {
		setup(EdeScanTest.class, "testTimeResolvedExperimentParametersSerializeOk");
		TimeResolvedExperimentParameters allParams = getTimeResolvedExperimentParameters();

		// Add names of some scannables to monitor
		Map<String, String> scannablesToMonitorDuringScan = new HashMap<String,String>();
		scannablesToMonitorDuringScan.put("scannable1", "");
		scannablesToMonitorDuringScan.put("scannable2", "pvForScannable2");
		allParams.setScannablesToMonitorDuringScan(scannablesToMonitorDuringScan);

		String origXmlString = allParams.toXML();

		// Try to serialize and save to text file
		String fname = "testTimeResolvedParameters.xml";
		String dir = new File(testDir).getParent().toString();
		String fullPathToFile = dir+"/"+fname;
		allParams.saveToFile(fullPathToFile);

		// Create new bean from xml file, compare with original
		TimeResolvedExperimentParameters savedParams = TimeResolvedExperimentParameters.loadFromFile(fullPathToFile);
		assertEquals(origXmlString, savedParams.toXML());
	}

	@Test
	public void testEdeScanRunsFromParameters() throws Exception {
		setup(EdeScanTest.class, "testEdeScanRunsFromParameters");
		TimeResolvedExperimentParameters allParams = getTimeResolvedExperimentParameters();
		TimeResolvedExperiment theExperiment = allParams.createTimeResolvedExperiment();
		theExperiment.runExperiment();

		int numberExpectedSpectra = getNumSpectra(allParams.getItTimingGroups());

		testNexusStructure(theExperiment.getNexusFilename(), numberExpectedSpectra, 1);
		checkDetectorData(theExperiment.getNexusFilename(), xh.getName(), numberExpectedSpectra+4);
		checkDetectorTimeframeData(theExperiment.getNexusFilename(), xh.getName(), numberExpectedSpectra+4);
		testEdeAsciiFiles(theExperiment.getNexusFilename(), numberExpectedSpectra, allParams.getItTimingGroups().size(), false);
	}

	@Test
	public void testEdeScanRunsFromParametersNoAscii() throws Exception {
		setup(EdeScanTest.class, "testEdeScanRunsFromParametersNoAscii");
		TimeResolvedExperimentParameters allParams = getTimeResolvedExperimentParameters();
		allParams.setGenerateAsciiData(false); // don't generate ascii files after the scan
		TimeResolvedExperiment theExperiment = allParams.createTimeResolvedExperiment();
		theExperiment.runExperiment();

		int numberExpectedSpectra = getNumSpectra(allParams.getItTimingGroups());
		testNexusStructure(theExperiment.getNexusFilename(), numberExpectedSpectra, 1);
		checkDetectorData(theExperiment.getNexusFilename(), xh.getName(), numberExpectedSpectra+4);
		checkDetectorTimeframeData(theExperiment.getNexusFilename(), xh.getName(), numberExpectedSpectra+4);

		// Check that no post-scan Ascii files were written ...
		String[] fileExt = {EdeDataConstants.IT_COLUMN_NAME,
				EdeDataConstants.LN_I0_IT_AVG_I0S_COLUMN_NAME, EdeDataConstants.LN_I0_IT_FINAL_I0_COLUMN_NAME,
				EdeDataConstants.IT_RAW_COLUMN_NAME, EdeDataConstants.I0_RAW_COLUMN_NAME};

		for( String ext : fileExt) {
			String fname = getAsciiName(theExperiment.getNexusFilename(), ext);
			File f = new File(fname);
			assertFalse("File "+fname+" should not have been written!", f.exists());
		}
	}

	@Test
	public void testEdeScanWithTfg() throws Exception {
		setup(EdeScanTest.class, "testEdeScanWithTfg");
		LocalProperties.set(LocalProperties.GDA_DUMMY_MODE_ENABLED, "True");
		TimeResolvedExperimentParameters allParams = getTimeResolvedExperimentParameters();
		allParams.getItTimingGroups().get(0).setGroupTrig(true);
		TimeResolvedExperiment theExperiment = allParams.createTimeResolvedExperiment();
		theExperiment.runExperiment();

		int numberExpectedSpectra = getNumSpectra(allParams.getItTimingGroups());

		// Check the topup scaler datasets have been written correctly :
		assertDimensions(theExperiment.getNexusFilename(), xh.getName(), EdeDataConstants.SCALER_FRAME_COUNTS, new int[] { numberExpectedSpectra, injectionCounter.getNumChannelsToRead() });
		// all values should be >= 0
		checkDataValidRange(theExperiment.getNexusFilename(), xh.getName(), EdeDataConstants.SCALER_FRAME_COUNTS, new RangeValidator(0, 1, true, false));

		assertDimensions(theExperiment.getNexusFilename(), xh.getName(), "is_topup_measured_from_scaler", new int[] { numberExpectedSpectra });
		// All values should be = 1
		checkDataValidRange(theExperiment.getNexusFilename(), xh.getName(), "is_topup_measured_from_scaler", new RangeValidator(1, 1, true, true));

		testNexusStructure(theExperiment.getNexusFilename(), numberExpectedSpectra, 1);
		checkDetectorData(theExperiment.getNexusFilename(), xh.getName(), numberExpectedSpectra+4);
		checkDetectorTimeframeData(theExperiment.getNexusFilename(), xh.getName(), numberExpectedSpectra+4);
		testEdeAsciiFiles(theExperiment.getNexusFilename(), numberExpectedSpectra, allParams.getItTimingGroups().size(), false);
	}

	// Setup dummy detector with some data and set scan object to use it for specified position and type part of scan
	private void setDummyDetectorForScanPart(EdeExperiment edeExperiment, EdePositionType positionType, EdeScanType scanType) {
		// Setup dummy detector with some data
		Dataset detData = DatasetFactory.createLinearSpace(DoubleDataset.class, 0.0, 1000.0, MCA_WIDTH/2);
		dummyEdeDetector.setDetectorData(detData);
		edeExperiment.setDetectorForScanPart(positionType, scanType, dummyEdeDetector);
	}

	@Test
	public void testEdeScanRunsWithDummyDetector() throws Exception {
		setup(EdeScanTest.class, "testEdeScanRunsWithDummyDetector");

		// TODO Should also make a test that loads data from NExus file. e,g,
		//dummyEdeDetector.loadDetectorDataFromNexusFile(nexusFileName, "/entry1/xh/data", -1);

		TimeResolvedExperimentParameters allParams = getTimeResolvedExperimentParameters();
		TimeResolvedExperiment theExperiment = allParams.createTimeResolvedExperiment();

		setDummyDetectorForScanPart(theExperiment, EdePositionType.OUTBEAM, EdeScanType.LIGHT);

		// use dummy detector for light I0 part of the scan
		setDummyDetectorForScanPart(theExperiment, EdePositionType.OUTBEAM, EdeScanType.LIGHT);
		theExperiment.runExperiment();

		int numberExpectedSpectra = getNumSpectra(allParams.getItTimingGroups());

		testNexusStructure(theExperiment.getNexusFilename(), numberExpectedSpectra, 1);
		checkDetectorData(theExperiment.getNexusFilename(), xh.getName(), numberExpectedSpectra+4);
		checkDetectorTimeframeData(theExperiment.getNexusFilename(), xh.getName(), numberExpectedSpectra+4);
	}

	@Test
	public void testAsciiFilesCanBeCreatedFromNexusAfterScan() throws Exception {
		setup(EdeScanTest.class, "testAsciiFilesCanBeCreatedFromNexusAfterScan");
		TimeResolvedExperimentParameters allParams = getTimeResolvedExperimentParameters();
		TimeResolvedExperiment theExperiment = allParams.createTimeResolvedExperiment();
		theExperiment.setWriteAsciiData(false); // don't generate ascii files after scan
		theExperiment.runExperiment();

		int numberExpectedSpectra = getNumSpectra(allParams.getItTimingGroups());

		// First check to make sure ascii files were *not* generated
		boolean filesNotFound = false;
		try {
			testEdeAsciiFiles(theExperiment.getNexusFilename(), numberExpectedSpectra, allParams.getItTimingGroups().size(), false);
		} catch(NoSuchFileException fnf) {
			filesNotFound = true;
		}
		assertTrue(filesNotFound);

		// Create the ascii files
		TimeResolvedDataFileHelper.createAsciiFiles(theExperiment.getNexusFilename());
		testEdeAsciiFiles(theExperiment.getNexusFilename(), numberExpectedSpectra, allParams.getItTimingGroups().size(), false);
	}
}
