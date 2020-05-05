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

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.stream.Collectors;

import org.apache.commons.io.FilenameUtils;
import org.eclipse.dawnsci.analysis.api.tree.Attribute;
import org.eclipse.dawnsci.analysis.api.tree.DataNode;
import org.eclipse.dawnsci.analysis.api.tree.GroupNode;
import org.eclipse.dawnsci.nexus.NexusConstants;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.dawnsci.nexus.template.impl.NexusTemplateServiceImpl;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.IDataset;
import org.eclipse.january.dataset.IntegerDataset;
import org.eclipse.january.dataset.StringDataset;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.data.ServiceHolder;
import gda.data.metadata.NXMetaDataProvider;
import gda.device.DeviceException;
import gda.device.detector.BufferedDetector;
import gda.device.detector.DummyDAServer;
import gda.device.detector.countertimer.BufferedScaler;
import gda.device.memory.Scaler;
import gda.device.motor.DummyMotor;
import gda.device.scannable.ScannableMotor;
import gda.device.scannable.TurboXasScannable;
import gda.device.timer.Etfg;
import gda.device.trajectoryscancontroller.DummyTrajectoryScanController;
import gda.device.trajectoryscancontroller.TrajectoryScanController.ExecuteStatus;
import gda.device.zebra.controller.Zebra;
import gda.device.zebra.controller.impl.ZebraDummy;
import gda.factory.Factory;
import gda.factory.FactoryException;
import gda.factory.Finder;
import gda.scan.ede.datawriters.AsciiWriterTest;
import uk.ac.gda.beans.vortex.Xspress3Parameters;
import uk.ac.gda.devices.detector.xspress3.Xspress3BufferedDetector;
import uk.ac.gda.devices.detector.xspress3.Xspress3Detector;
import uk.ac.gda.devices.detector.xspress3.controllerimpl.DummyXspress3Controller;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class TurboXasScanTest extends EdeTestBase {

	private static final Logger logger = LoggerFactory.getLogger(TurboXasScanTest.class);
	private DummyDAServer daserver;
	private Etfg tfg;
	private Scaler memory;
	private BufferedScaler bufferedScaler;
	private TurboXasScannableForTesting turboXasScannable;
	private DummyXspress3Controller controllerForDetector;
	private Xspress3Detector xspress3detector;
	private Xspress3BufferedDetector xspress3bufferedDetector;
	private ScannableMotor testMotor;
	private boolean twoWayScan;
	private final double timePerSpectrum = 0.01;
	private ScannableMotor dummyScannableMotor;

	public static final String BUFFERED_SCALER_NAME = "bufferedScaler";
	public static final String[] BUFFERED_SCALER_FIELDS = { "frame_time", "I0", "It", "Iref" };

	public static final String BUFFERED_XSPRESS3_NAME = "xspress3bufferedDetector";
	public static final String[] BUFFERED_XSPRESS3_FIELDS = new String[] {"Chan0", "FF", TurboXasNexusTree.FF_SUM_IO_NAME };

	private static final String XSPRESS3_METADATA_NAME = "Xspress3";
	private static final String TURBOXAS_METADATA_NAME = "TurboXasParameters";

	@AfterClass
	public static void tearDownClass() {
		// Remove factories from Finder so they do not affect other tests
		Finder.getInstance().removeAllFactories();
	}

	@Before
	public void setupEnvironment() throws Exception {
		Path tempDataDir = Files.createTempDirectory(TurboXasScanTest.class.getName());
		LocalProperties.set(LocalProperties.GDA_VAR_DIR, tempDataDir.toString());
		new ServiceHolder().setNexusTemplateService(new NexusTemplateServiceImpl());

		daserver = new DummyDAServer();
		daserver.configure();

		tfg = new Etfg();
		tfg.setDaServer(daserver);
		tfg.configure();

		memory = new Scaler();
		memory.setDaServer(daserver);
		memory.setHeight(1);
		memory.setWidth(4);
		memory.setOpenCommand("tfg open-cc");
		memory.configure();

		bufferedScaler = new BufferedScaler();
		bufferedScaler.setName(BUFFERED_SCALER_NAME);
		bufferedScaler.setScaler(memory);
		bufferedScaler.setTimer(tfg);
		bufferedScaler.setDaserver(daserver);
		bufferedScaler.setTFGv2(true);
		bufferedScaler.setOutputLogValues(false);
		bufferedScaler.setTimeChannelRequired(true);
		bufferedScaler.setExtraNames(BUFFERED_SCALER_FIELDS);
		bufferedScaler.setFirstDataChannel(0);
		bufferedScaler.setNumChannelsToRead(3);
		bufferedScaler.setOutputFormat(new String[] { "%.5g", "%.5g", "%.5g", "%.5g", "%.5g" });
		bufferedScaler.configure();

		Zebra dummyZebra = new ZebraDummy();
		DummyMotor dummyMotor = new DummyMotor();
		dummyMotor.setName("dummyMotor");
		dummyMotor.setMinPosition(-10000);
		dummyMotor.setMaxPosition(10000);
		dummyMotor.setPosition(0);
		dummyMotor.configure();

		TrajectoryScanPreparer trajectoryScanPreparer = new TrajectoryPreparerForTest();
		trajectoryScanPreparer.setTrajectoryScanController(new DummyTrajectoryScanController());

		turboXasScannable = new TurboXasScannableForTesting();
		turboXasScannable.setName("turboXasScannable");
		turboXasScannable.setMotor(dummyMotor);
		turboXasScannable.setZebraDevice(dummyZebra);
		turboXasScannable.setTrajectoryScanPreparer(trajectoryScanPreparer);
		turboXasScannable.setTrajectoryScanInitialWaitTimeMs(0);

		setupXSpress3();

		testMotor = createMotor("testMotor", 4.20);

		dummyScannableMotor = createScannableMotor("dummyScannableMotor");
		dummyScannableMotor.setName("dummyScannableMotor");

		setupFinder();
	}

	/**
	 * Version of trajectory preparer that doesn't run the scan (dummy controller setExecuteProfile always takes 5 seconds to run),
	 * and just sets the execute status to 'SUCCESS'.
	 */
	private class TrajectoryPreparerForTest extends TrajectoryScanPreparer{
		@Override
		public void setExecuteProfile() {
			DummyTrajectoryScanController controller = (DummyTrajectoryScanController) getTrajectoryScanController();
			controller.setExecuteStatus(ExecuteStatus.SUCCESS);
		}
	}

	public void setupXSpress3() throws FactoryException {
		controllerForDetector = new DummyXspress3Controller(tfg, daserver);
		controllerForDetector.setName("controllerForDetector");
		controllerForDetector.setNumFramesToAcquire(1);
		controllerForDetector.setNumberOfChannels(2048); //number of detector elements
		controllerForDetector.configure();
		controllerForDetector.setSimulationFileName("/scratch/testfile");
		controllerForDetector.configure();

		xspress3detector = new Xspress3Detector();
		xspress3detector.setName("xspress3detector");
		xspress3detector.setController(controllerForDetector);
		xspress3detector.configure();
		xspress3detector.setWriteHDF5Files(true);

		xspress3bufferedDetector = new Xspress3BufferedDetector();
		xspress3bufferedDetector.setName(BUFFERED_XSPRESS3_NAME);
		xspress3bufferedDetector.setXspress3Detector(xspress3detector);
		xspress3bufferedDetector.configure();
	}

	private void setupFinder() {
		final Factory factory = TestHelpers.createTestFactory();
		factory.addFindable(turboXasScannable);
		factory.addFindable(bufferedScaler);
		factory.addFindable(xspress3bufferedDetector);
		factory.addFindable(testMotor);
		factory.addFindable(xspress3detector);
		factory.addFindable(dummyScannableMotor);
		Finder.getInstance().addFactory(factory);
		addMetashopToFinder();
	}

	/**
	 * This is used to throw an exception in the middle of a scan, to check that the 'after scan' Nexus data is written correctly.
	 */
	private class TurboXasScannableForTesting extends TurboXasScannable {
		public boolean throwException = false;

		public void setThrowException(boolean throwException) {
			this.throwException = throwException;
		}

		@Override
		public void waitWhileBusy() throws InterruptedException, DeviceException {
			if (throwException) {
				throw new InterruptedException("Interrupted exception thrown by TurboXasScannableForTesting");
			} else {
				super.waitWhileBusy();
			}
		}
	}

	@Test
	public void testScalerReadoutLength() throws DeviceException, InterruptedException {
		bufferedScaler.setCollectionTime(1.0);
		bufferedScaler.collectData();
		bufferedScaler.waitWhileBusy();
		double[] readoutValues = bufferedScaler.readout();
		int numChannels = bufferedScaler.getNumChannelsToRead();
		numChannels += bufferedScaler.isTimeChannelRequired() ? 1 : 0;
		assertEquals(readoutValues.length, numChannels);
	}

	@Test
	public void testTurboXasSingleSpectraContinuousScan() throws InterruptedException, Exception {
		setup(TurboXasScan.class, "testTurboXasSingleSpectraContinuousScan");

		double startPos = 0;
		double endPos = 10;
		int numReadouts = 20;
		double timeForScan = 0.001;

		TurboXasScan scan = new TurboXasScan( turboXasScannable, startPos, endPos, numReadouts, timeForScan, new BufferedDetector[] {bufferedScaler} );
		runScan(scan);

		String nxsFile = scan.getDataWriter().getCurrentFileName();
		checkDetectorNexusData(nxsFile, bufferedScaler.getName(), 1, numReadouts);
	}

	private TurboXasParameters getTurboXasParameters() {
		TurboXasParameters parameters = new TurboXasParameters();
		parameters.setSampleName( "sample name" );
		parameters.setStartPosition(0);
		parameters.setEndPosition(10);
		parameters.setPositionStepSize(0.01);

		// Set names of motors to be moved, detectors used etc.
		// These are used in {@link TurboXasParameters#createScan} method to create and
		// setup the TurboXasScan object
		parameters.setMotorToMove(turboXasScannable.getName());
		parameters.setDetectors(new String[] {bufferedScaler.getName(), xspress3bufferedDetector.getName()});
		// Set scannable to monitor during scan
		Map<String, String> scnToMonitor = new HashMap<>();
		scnToMonitor.put(testMotor.getName(), "");
		parameters.setScannablesToMonitorDuringScan(scnToMonitor);
		return parameters;
	}

	private void addTimingGroups(TurboXasParameters parameters) {
		parameters.addTimingGroup(new TurboSlitTimingGroup("group1", timePerSpectrum, 0.0, 3));
		parameters.addTimingGroup(new TurboSlitTimingGroup("group2", timePerSpectrum, 0.0, 5));
	}

	private void addTimingGroup(TurboXasParameters parameters) {
		parameters.addTimingGroup(new TurboSlitTimingGroup("group1", timePerSpectrum, 0.0, 3));
	}

	/** Run TurboXasScan, first setting poll interval to small value so tests run quicker */
	private void runScan(TurboXasScan scan) throws InterruptedException, Exception {
		scan.setPollIntervalMillis(0);
		twoWayScan = scan.isTwoWayScan();
		scan.runScan();
	}

	/**
	 * @param params
	 * @return Total number of spectra across all timing groups
	 */
	public int getNumSpectra(TurboXasParameters params) {
		return params.getTimingGroups().stream().mapToInt(TurboSlitTimingGroup::getNumSpectra).sum();
	}

	public int getNumPointsPerSpectrum(TurboXasParameters params) {
		return (int) ((params.getEndPosition()-params.getStartPosition())/params.getPositionStepSize());
	}


	@Test
	public void testTurboXasScanMultipleSpectra() throws InterruptedException, Exception {
		setup(TurboXasScan.class, "testTurboXasScanMultipleSpectra");
		TurboXasParameters parameters = getTurboXasParameters();
		addTimingGroups(parameters);
		parameters.setTwoWayScan(true);

		int numPointsPerSpectrum = getNumPointsPerSpectrum(parameters);
		int numSpectra = getNumSpectra(parameters);

		TurboXasMotorParameters motorParameters = parameters.getMotorParameters();
		motorParameters.setMotorParametersForTimingGroup(0);
		turboXasScannable.setMotorParameters(motorParameters);
		TurboXasScan scan = new TurboXasScan(turboXasScannable, motorParameters, new BufferedDetector[]{bufferedScaler});
		runScan(scan);

		String nexusFilename = scan.getDataWriter().getCurrentFileName();
		checkScalerNexusData(nexusFilename, numSpectra, numPointsPerSpectrum);
		checkNXDataGroups(nexusFilename, numSpectra, numPointsPerSpectrum);

	}

	@Test
	public void testTurboXasScanMultipleSpectraFinishEarly() throws InterruptedException, Exception {
		setup(TurboXasScan.class, "testTurboXasScanMultipleSpectraFinishEarly");
		TurboXasParameters parameters = getTurboXasParameters();
		addTimingGroups(parameters);

		// Run the scan in a background thread
		final TurboXasScan scan = new TurboXasScan(turboXasScannable, parameters.getMotorParameters(), new BufferedDetector[]{bufferedScaler});
		Thread runScanThread = new Thread( () -> {
			try {
				runScan(scan);
			} catch (Exception e) {
				System.out.print("Exception caught during scan : " + e);
		}});
		runScanThread.start();

		// Wait for a few spectra to be collected, then make the scan exit early by throwing InterruptedException
		int pointCount = 0;
		while (runScanThread.isAlive()) {
			Thread.sleep(500);
			pointCount = scan.getCurrentPointCount();
			logger.info("Waiting for scan to complete, current point = {}", pointCount);
			if (pointCount > 5) {
				turboXasScannable.setThrowException(true);
			}
		}
		int numPointsPerSpectrum = getNumPointsPerSpectrum(parameters);
		IDataset frameTimes = getDataset(scan.getDataWriter().getCurrentFileName(), bufferedScaler.getName(), BUFFERED_SCALER_FIELDS[0]);
		int numSpectra = frameTimes.getShape()[0];
		checkScalerNexusData(scan.getDataWriter().getCurrentFileName(), numSpectra, numPointsPerSpectrum);
	}

	@Test
	public void testTurboXasScanMultipleSpectraXspress3() throws InterruptedException, Exception {
		setup(TurboXasScan.class, "testTurboXasScanMultipleSpectraXspress3");
		TurboXasParameters parameters = getTurboXasParameters();
		addTimingGroups(parameters);

		int numPointsPerSpectrum = getNumPointsPerSpectrum(parameters);
		int numSpectra = getNumSpectra(parameters);

		TurboXasMotorParameters motorParameters = parameters.getMotorParameters();
		motorParameters.setMotorParametersForTimingGroup(0);
		turboXasScannable.setMotorParameters(motorParameters);
		TurboXasScan scan = new TurboXasScan(turboXasScannable, motorParameters, new BufferedDetector[]{bufferedScaler, xspress3bufferedDetector});
		runScan(scan);

		String nexusFilename = scan.getDataWriter().getCurrentFileName();
		checkScalerNexusData(nexusFilename, numSpectra, numPointsPerSpectrum);
		checkDetectorNexusData(nexusFilename, xspress3bufferedDetector.getName(), numSpectra, numPointsPerSpectrum);

		// Check FF sums have been added to Nexus file
		assertDimensions(nexusFilename, xspress3bufferedDetector.getName(), TurboXasNexusTree.FF_SUM_NAME, new int[]{numSpectra, numPointsPerSpectrum});
		assertDimensions(nexusFilename, xspress3bufferedDetector.getName(), TurboXasNexusTree.FF_SUM_IO_NAME, new int[]{numSpectra, numPointsPerSpectrum});
		Dataset i0Data = (Dataset) getDataset(nexusFilename, bufferedScaler.getName(), TurboXasNexusTree.I0_LABEL);
		Dataset ffSumData = (Dataset) getDataset(nexusFilename, xspress3bufferedDetector.getName(), TurboXasNexusTree.FF_SUM_NAME);
		Dataset ffSumI0Data = (Dataset) getDataset(nexusFilename, xspress3bufferedDetector.getName(), TurboXasNexusTree.FF_SUM_IO_NAME);
		for(int i=0; i<numSpectra; i++) {
			for(int j=0; j<numPointsPerSpectrum; j++) {
				assertEquals(ffSumData.getDouble(i,j)/i0Data.getDouble(i,j), ffSumI0Data.getDouble(i,j), 1e-6);
			}
		}
		checkMetaData(nexusFilename, parameters);
	}

	@Test
	public void testTurboXasParametersCreatesScan() throws InterruptedException, Exception {
		setup(TurboXasScan.class, "testTurboXasParametersCreatesScan");
		TurboXasParameters parameters = getTurboXasParameters();
		addTimingGroup(parameters);

		TurboXasScan scan = parameters.createScan();

		// Check that detector have been located and set correctly
		BufferedDetector[] detectors = scan.getScanDetectors();
		assertNotNull(detectors);
		assertEquals(detectors.length, 2);
		assertEquals(detectors[0].getName(), bufferedScaler.getName());
		assertEquals(detectors[1].getName(), xspress3bufferedDetector.getName());

		// Check that any scannables to be monitored have been set correctly
		assertNotNull(scan.getScannablesToMonitor());
		assertEquals(scan.getScannablesToMonitor().get(0).getName(), testMotor.getName());
	}

	@Test
	public void testTurboXasParameterCreatedScanRuns() throws InterruptedException, Exception {
		setup(TurboXasScan.class, "testTurboXasParameterCreatedScanRuns");
		TurboXasParameters parameters = getTurboXasParameters();
		addTimingGroup(parameters);
		int numPointsPerSpectrum = getNumPointsPerSpectrum(parameters);
		int numSpectra = parameters.getTimingGroups().get(0).getNumSpectra();

		TurboXasScan scan = parameters.createScan();
		runScan(scan);
		String nexusFilename = scan.getDataWriter().getCurrentFileName();

		checkScalerNexusData(nexusFilename, numSpectra, numPointsPerSpectrum);
		checkDetectorNexusData(nexusFilename, xspress3bufferedDetector.getName(), numSpectra, numPointsPerSpectrum);
		checkNXDataGroups(nexusFilename, numSpectra, numPointsPerSpectrum);

		// Check data for the scannable being monitored is present and has correct dimensions (1 value per spectrum)
		assertDimensions(nexusFilename, bufferedScaler.getName(), testMotor.getName(), new int[]{numSpectra});
		checkMetaData(nexusFilename, parameters);
	}

	/**
	 * Do basic check that TurboXasScan runs and produces Ascii file at end with correct number of rows and columns
	 * of data. More extensive checks of content are done in {@link AsciiWriterTest}.
	 * @throws InterruptedException
	 * @throws Exception
	 */
	@Test
	public void testAsciiWriterProcessesNexusFile() throws InterruptedException, Exception {
		setup(TurboXasScan.class, "testAsciiWriterProcessesNexusFile");
		TurboXasParameters parameters = getTurboXasParameters();
		addTimingGroup(parameters);
		TurboXasScan scan = parameters.createScan();
		scan.setWriteAsciiDataAfterScan(true);
		runScan(scan);

		// Reduce the number of expected spectrum points to account for NaNs removed when writing to Ascii.
		int numEnergies = getNumPointsPerSpectrum(parameters)-1;
		if (parameters.isTwoWayScan()) {
			numEnergies--;
		}

		int numSpectra = parameters.getTotalNumSpectra();
		int numFields = bufferedScaler.getExtraNames().length + xspress3bufferedDetector.getExtraNames().length + 2; // Xspress3 has 2 extra values : FF_sum, FF_sum/I0
		int numAxisColumns = 3; // index, position, energy

		String asciiFileName = scan.getAsciiDataWriter().getAsciiFilename();

		// Check ascii file has correct number of line and columns of data
		testNumberLinesInFile(asciiFileName, numEnergies);
		testNumberColumnsInFile(asciiFileName, numAxisColumns + numFields * numSpectra);
	}

	/**
	 * Check the axis data and all 2d datasets in a detector group. 2d datasets should have shape [numSpectra, numPointsPerSpectrum],
	 * axis data should have shape [numPointsPerSpectrum].
	 * @param nexusFilename name of nexus file containing data
	 * @param detectorNode name of group node with detector data (i.e. name of detector)
	 * @param numSpectra
	 * @param numPointsPerSpectrum
	 * @throws NexusException
	 */
	private void checkDetectorNexusData(String nexusFilename,  String detectorNode, int numSpectra, int numPointsPerSpectrum) throws NexusException {
		// Check shapes of axis datasets: should all be [numPointsPerSpectrum]
		checkAxisData(nexusFilename, detectorNode, numPointsPerSpectrum);

		// Check shape and content of all other datasets in group : if 2d, they should all be [numSpectra, numPointsPerSpectrum], with numbers >=0
		int[] expectedDims = new int[]{numSpectra, numPointsPerSpectrum};
		GroupNode groupNode = getGroupNode(nexusFilename, detectorNode);
		for(DataNode node : groupNode.getDataNodes()) {
			if (node.getDataset().getShape().length == expectedDims.length) {
				checkScanData(nexusFilename, detectorNode, node.getDataset().getName(), expectedDims);
			}
		}
	}

	private void checkAxisData(String nexusFilename, String detectorGroup, int numPointsPerSpectrum) throws NexusException {
		// Test frame index and energy datasets
		assertDimensions(nexusFilename, detectorGroup, TurboXasNexusTree.ENERGY_COLUMN_NAME, new int[]{numPointsPerSpectrum});
		assertDimensions(nexusFilename, detectorGroup, TurboXasNexusTree.POSITION_COLUMN_NAME, new int[]{numPointsPerSpectrum});
		assertDimensions(nexusFilename, detectorGroup, TurboXasNexusTree.FRAME_INDEX, new int[]{numPointsPerSpectrum});
	}

	private void checkScanData(String nexusFilename, String detectorGroup, String name, int[] expectedDims) throws NexusException {
		assertDimensions(nexusFilename, detectorGroup, name, expectedDims);
		RangeValidator rangeValidator = new RangeValidator(0, 1, true, false);

		// Check all values in a Dataset to make sure they are all within expected range
		Dataset dataset = (Dataset) getDataset(nexusFilename, detectorGroup, name);
		for(int i=0; i<expectedDims[0]; i++) {
			// Set index in row where NaN is expected (last value for single directional scans)
			int nanIndex = expectedDims[1]-1;
			// Two way scan alternates NaN values at start/end of the row
			if (twoWayScan && i%2==1) {
				nanIndex=0;
			}
			for(int j=0; j<expectedDims[1]; j++) {
				Double datasetVal = dataset.getDouble(i, j);
				if (j==nanIndex) {
					assertTrue("Value "+datasetVal+" at index "+nanIndex+" is not NaN", datasetVal.isNaN());
				} else {
					assertTrue("Value "+datasetVal+" is not >=0 ", rangeValidator.valueOk(datasetVal));
				}
			}
		}
		logger.info("Data in {}/{} is ok", detectorGroup, name);
	}

	private void checkScalerNexusData(String nexusFilename, int numSpectra, int numPointsPerSpectrum) throws NexusException {
		// Check scaler datasets are present and have correct shape
		for(String scalerField : BUFFERED_SCALER_FIELDS) {
			assertDimensions(nexusFilename, bufferedScaler.getName(), scalerField, new int[]{numSpectra, numPointsPerSpectrum});
		}

		// Check shape and content of scaler output (should be all >0 when not also producing lnI0It values)
		checkDetectorNexusData(nexusFilename, bufferedScaler.getName(), numSpectra, numPointsPerSpectrum);

		// Check the extra datasets written at end of scan to show spectrum index and group for each spectra, time between spectra etc.
		assertDimensions(nexusFilename, bufferedScaler.getName(), TurboXasNexusTree.TIME_BETWEEN_SPECTRA_COLUMN_NAME, new int[]{numSpectra});
		assertDimensions(nexusFilename, bufferedScaler.getName(), TurboXasNexusTree.TIME_COLUMN_NAME, new int[]{numSpectra});
		assertDimensions(nexusFilename, bufferedScaler.getName(), TurboXasNexusTree.SPECTRUM_INDEX, new int[]{numSpectra});
		assertDimensions(nexusFilename, bufferedScaler.getName(), TurboXasNexusTree.SPECTRUM_GROUP, new int[]{numSpectra});
		checkTimeData(nexusFilename);
	}

	/**
	 * Check spectrum start times are calculated correctly correctly and have consistent shapes.
	 * @param nexusFilename
	 * @throws NexusException
	 */
	private void checkTimeData(String nexusFilename) throws NexusException {
		IDataset timeBetweenSpectra = getDataset(nexusFilename, bufferedScaler.getName(), TurboXasNexusTree.TIME_BETWEEN_SPECTRA_COLUMN_NAME);
		IDataset startTimes = getDataset(nexusFilename, bufferedScaler.getName(), TurboXasNexusTree.TIME_COLUMN_NAME);
		IDataset frameTime = getDataset(nexusFilename, bufferedScaler.getName(), BUFFERED_SCALER_FIELDS[0]);
		IDataset startTimesUtc = getDataset(nexusFilename, bufferedScaler.getName(), TurboXasNexusTree.TIME_UTC_COLUMN_NAME);

		int numSpectra = frameTime.getShape()[0];
		int numPoints= frameTime.getShape()[1];
		assertDimensions(startTimes, new int[] {numSpectra});
		assertDimensions(startTimesUtc, new int[] {numSpectra});
		assertDimensions(timeBetweenSpectra, new int[] {numSpectra});

		double startTime = 0;
		long startTimeUtc = startTimesUtc.getLong(0);

		for(int i=0; i<numSpectra; i++) {
			assertEquals("Start time data for spectrum "+i+" is not currect", startTime, startTimes.getDouble(i), 1e-6);
			assertEquals("UTC start time data for spectrum "+i+" is not currect", startTimeUtc, startTimesUtc.getLong(i));
			Dataset dat = (Dataset) frameTime.getSlice(new int[] { i, 0 }, new int[] { i + 1, numPoints }, null).squeeze();
			double timeForSpectrum = ((Number) dat.sum(true)).doubleValue();
			double timeBetweenSpectrumStart = timeForSpectrum + timeBetweenSpectra.getDouble(i);
			startTime += timeBetweenSpectrumStart;
			startTimeUtc = (long) (startTime * 1000) + startTimesUtc.getLong(0);
		}
	}

	/**
	 * Check that NXData group has been created for each set of data produced by buffered scaler;
	 * Checks dimensions of each dataset in the group (which are really just links back to original datasets in detector group).
	 *
	 * @param filename
	 * @param numSpectra
	 * @param numPointsPerSpectrum
	 * @throws NexusException
	 */
	private void checkNXDataGroups(String filename, int numSpectra, int numPointsPerSpectrum) throws NexusException {

		// Check default attribute has been set on /entry1/ node
		GroupNode groupNode = getGroupNode(filename, "");
		Attribute entry1Attributes = groupNode.getAttribute(NexusConstants.DEFAULT);
		assertNotNull("/entry1/ attributes have not been set", entry1Attributes);

		String expectedSignalName = bufferedScaler.getName() + "_" + bufferedScaler.getExtraNames()[2];
		assertEquals("Signal attribute on /entry1/ has not been set correctly",
				((StringDataset)entry1Attributes.getValue()).getString(),
				expectedSignalName);

		checkAttributes(filename, bufferedScaler.getName(), bufferedScaler.getExtraNames()[2]);

		for(String name : bufferedScaler.getExtraNames()) {
			String groupName = bufferedScaler.getName()+"_"+name;
			checkAttributes(filename, groupName, name);
			assertDimensions(filename, groupName, name, new int[] {numSpectra, numPointsPerSpectrum});
			assertDimensions(filename, groupName, TurboXasNexusTree.ENERGY_COLUMN_NAME, new int[] {numPointsPerSpectrum});
			assertDimensions(filename, groupName, TurboXasNexusTree.POSITION_COLUMN_NAME, new int[] {numPointsPerSpectrum});
			assertDimensions(filename, groupName, TurboXasNexusTree.SPECTRUM_INDEX, new int[] {numSpectra});
			assertDimensions(filename, groupName, TurboXasNexusTree.TIME_COLUMN_NAME, new int[] {numSpectra});
		}
	}

	/**
	 * Check attributes have been set correctly on a NXData group
	 * @param filename
	 * @param groupName
	 * @param signalName
	 * @throws NexusException
	 */
	private void checkAttributes(String filename, String groupName, String signalName) throws NexusException {
		GroupNode groupNode = getGroupNode(filename,  groupName);
		assertEquals("Wrong number of attributes for /entry1/"+groupName, 7, groupNode.getNumberOfAttributes());

		// Check axis names have been set
		assertEquals(TurboXasNexusTree.TIME_COLUMN_NAME, groupNode.getAttribute(NexusConstants.DATA_AXES).getValue().getString(0));
		assertEquals(TurboXasNexusTree.ENERGY_COLUMN_NAME, groupNode.getAttribute(NexusConstants.DATA_AXES).getValue().getString(1));

		// signal attribute is set to name of scaler dataset
		assertEquals(((StringDataset)groupNode.getAttribute(NexusConstants.DATA_SIGNAL).getValue()).getString(), signalName);

		// Check that the _indices attributes have been set (energy_indices, frame_indices, position_indices, time_indices)
		for (Entry<String, Integer> attrib : TurboXasNexusTree.getAttributeDataNames().entrySet()) {
			String attributeName = attrib.getKey() + NexusConstants.DATA_INDICES_SUFFIX;
			IDataset dataset = groupNode.getAttribute(attributeName).getValue();
			assertEquals(attrib.getValue().intValue(), ((IntegerDataset) dataset).get());
		}
	}

	@Test
	public void checkMetaDataAddedRemovedFromMetaShop() throws Exception {
		setup(TurboXasScan.class, "checkMetaDataAddedRemovedFromMetaShop");

		TurboXasParameters parameters = getTurboXasParameters();
		addTimingGroup(parameters);

		TurboXasScan scan = parameters.createScan();

		// At scan start should add turboxas and xspress parameter metadata to metashop
		NXMetaDataProvider metaShop = Finder.getInstance().find("metaShop");
		scan.callScannablesAtScanStart();
		assertEquals(TURBOXAS_METADATA_NAME+" in metashop does not match expected value", parameters.toXML(), metaShop.get(TURBOXAS_METADATA_NAME));
		assertEquals(XSPRESS3_METADATA_NAME+" parameters in metashop does not match expected value", getXspress3ConfigParmeters(), metaShop.get(XSPRESS3_METADATA_NAME));


		// At scan end should remove the metadata from metashop
		scan.callScannablesAtScanEnd();
		assertNull(TURBOXAS_METADATA_NAME+" parameters not removed from metashop", metaShop.get(TURBOXAS_METADATA_NAME));
		assertNull(XSPRESS3_METADATA_NAME+" parameters not removed from metashop", metaShop.get(XSPRESS3_METADATA_NAME));
	}

	@Test
	public void testWithAverages() throws Exception {
		setup(TurboXasScan.class, "testWithAverages");
		TurboXasParameters parameters = getTurboXasParameters();
		addTimingGroup(parameters);

		TurboXasScan scan = parameters.createScan();

		// Set the names of the datasets to compute comulative averages
		List<String> names = Arrays.asList(bufferedScaler.getName()+"/"+bufferedScaler.getExtraNames()[1],
							bufferedScaler.getName()+"/"+bufferedScaler.getExtraNames()[2]);
		scan.setDatasetNamesToAverage(names);

		runScan(scan);

		// Check averages have been written to Nexus file and that values are correct.
		String nexusFilename = scan.getDataWriter().getCurrentFileName();
		for(String name : names) {
			// Load the averaged and  non-averaged datasets from Nexus file
			String datasetName = FilenameUtils.getName(name);
			IDataset originalData = getDataset(nexusFilename, bufferedScaler.getName(), datasetName);
			IDataset averagedData = getDataset(nexusFilename, bufferedScaler.getName(), datasetName+"_avg");

			// shape of averaged and non-averaged data should be the same
			assertArrayEquals(originalData.getShape(), averagedData.getShape());

			// Calculate cumulative average for each row using the original data and
			// check the average values in Nexus file written during the scan are correct
			int numRows = originalData.getShape()[0];
			int numColumns = originalData.getShape()[1];
			for(int i=0; i<numColumns; i++) {
				IDataset data = originalData.getSlice(new int[] {0, i}, new int[] {numRows, i+1}, null ).squeeze();
				IDataset avgComputed = computeCumulativeAverage(data);
				IDataset avgFromScan = averagedData.getSlice(new int[] {0, i}, new int[] {numRows, i+1}, null ).squeeze();
				assertDatasetsMatch(avgComputed, avgFromScan, 1e-6);
			}
		}
	}

	@Test
	public void testWithMotorMove() throws Exception {
		setup(TurboXasScan.class, "testWithMotorMove");
		TurboXasParameters parameters = getTurboXasParameters();
		addTimingGroups(parameters);
		TurboXasScan scan = parameters.createScan();
		scan.setScannableToMove(dummyScannableMotor);
		scan.addScannableToMonitor(dummyScannableMotor);
		List<Object> positionsForScan = Arrays.asList(1.0, 2.0, 3.0, 4.0, 5.0);
		scan.setPositionsForScan(positionsForScan);

		scan.runScan();

		List<Double> dblList = positionsForScan.stream().map(val -> (Double) val).collect(Collectors.toList());
		testMotorMoveResults(scan.getDataWriter().getCurrentFileName(), parameters, dblList);
	}

	@Test
	public void testWithMotorMoveUsingParameters() throws Exception {
		setup(TurboXasScan.class, "testWithMotorMoveUsingParameters");
		TurboXasParameters parameters = getTurboXasParameters();
		addTimingGroups(parameters);
		parameters.setRunMappingScan(true);
		parameters.setScannableToMove(dummyScannableMotor.getName());
		parameters.setScannablePositions(Arrays.asList(Arrays.asList(1.0, 2.0, 3.0, 4.0, 5.0)));
		TurboXasScan scan = parameters.createScan();
		scan.runScan();

		testMotorMoveResults(scan.getDataWriter().getCurrentFileName(), parameters, parameters.getScannablePositions().get(0));
	}

	private void testMotorMoveResults(String nexusFilename, TurboXasParameters parameters, List<Double> positionsForScan) throws Exception {
		int numPointsPerSpectrum = getNumPointsPerSpectrum(parameters);
		int numSpectraPerPosition = getNumSpectra(parameters);
		int numSpectra = numSpectraPerPosition * positionsForScan.size();

		checkScalerNexusData(nexusFilename, numSpectra, numPointsPerSpectrum);
		checkDetectorNexusData(nexusFilename, xspress3bufferedDetector.getName(), numSpectra, numPointsPerSpectrum);
		checkNXDataGroups(nexusFilename, numSpectra, numPointsPerSpectrum);

		// Check data for the scannable being moved is present and has correct dimensionss
		assertDimensions(nexusFilename, bufferedScaler.getName(), dummyScannableMotor.getName(), new int[]{numSpectra});
		IDataset dataset = getDataset(nexusFilename, bufferedScaler.getName(), dummyScannableMotor.getName());
		assertArrayEquals(dataset.getShape(), new int[] {numSpectra});
		// Check there are correct number of values (numSpectraPerPosition) at each position.
		for(int i=0; i<numSpectra; i++) {
			int posIndex = i/numSpectraPerPosition;
			double expectedVal = Double.parseDouble(positionsForScan.get(posIndex).toString());
			assertEquals(expectedVal, dataset.getDouble(i), 1e-5);
		}
		checkMetaData(nexusFilename, parameters);
	}

	@Test
	public void testSpectrumEventMap() throws Exception {
		setup(TurboXasScan.class, "testSpectrumEventMap");

		TurboXasScan scan = new TurboXasScan(turboXasScannable, 0.0, 10.0, 1000, 1.0, new BufferedDetector[] {bufferedScaler});

		assertEquals(0, scan.getSpectrumEvents().size());

		// add some events to the map (order should not matter)
		scan.addSpectrumEvent(20, testMotor, 3);
		scan.addSpectrumEvent( 5, testMotor, 1);
		scan.addSpectrumEvent(10, testMotor, 10);
		scan.addSpectrumEvent(10, dummyScannableMotor, 50);

		// Keys should be automatically sorted into ascending order
		Map<Integer, List<SpectrumEvent>> events = scan.getSpectrumEvents();
		assertArrayEquals(new Integer[] {5, 10, 20}, events.keySet().toArray(new Integer[] {}));

		// Check scannables and positions are correct for each time
		int spectrumNumber = 5;
		assertEquals(1, events.get(spectrumNumber).size());
		assertEquals(events.get(spectrumNumber).get(0), new SpectrumEvent(spectrumNumber, testMotor, 1));

		spectrumNumber = 10;
		assertEquals(2, events.get(spectrumNumber).size());
		assertEquals(new SpectrumEvent(spectrumNumber, testMotor, 10), events.get(spectrumNumber).get(0));
		assertEquals(new SpectrumEvent(spectrumNumber, dummyScannableMotor, 50), events.get(spectrumNumber).get(1));

		spectrumNumber = 20;
		assertEquals(1, events.get(spectrumNumber).size());
		assertEquals(new SpectrumEvent(spectrumNumber, testMotor, 3), events.get(spectrumNumber).get(0));
	}

	/**
	 * Compute cumulative ('running') average for a 1-d dataset.
	 * @param vals
	 * @return
	 */
	private IDataset computeCumulativeAverage(IDataset vals) {
		Dataset newValues = DatasetFactory.zeros(vals.getSize());
		int count=2;
		newValues.set(vals.getDouble(0), 0);
		for(int i=1; i<vals.getSize(); i++) {
			double newValue = vals.getDouble(i)/count + newValues.getDouble(i-1)*(count-1)/count;
			newValues.set(newValue, i);
			count++;
		}
		return newValues;
	}

	/**
	 * Check metadata added to before_scan section of Nexus file is correct.
	 * i.e. TurboXasParameter and Xspress3 parameter XML strings match expected values.
	 * @param filename
	 * @param parameters
	 * @throws Exception
	 */
	private void checkMetaData(String filename, TurboXasParameters parameters) throws Exception {
		// check the TurboXas parameters
		IDataset metadata = getDataset(filename, "before_scan", TURBOXAS_METADATA_NAME);
		assertNotNull(metadata);
		assertEquals(TURBOXAS_METADATA_NAME+" metadata does not match expected value", parameters.toXML(), metadata.getString(0));
		logger.info("{} metadata is ok", TURBOXAS_METADATA_NAME);

		// Check xspress3 parameters if that detector was included in the scan
		String scanCommand = getDataset(filename, "", "scan_command").getString();
		if (scanCommand.contains(xspress3bufferedDetector.getName())) {
			metadata = getDataset(filename, "before_scan", XSPRESS3_METADATA_NAME);
			assertNotNull(metadata);
			assertEquals(XSPRESS3_METADATA_NAME+" parameter metadata does not match expected value", getXspress3ConfigParmeters(), metadata.getString(0));
			logger.info("{} metadata is ok", XSPRESS3_METADATA_NAME);
		}
	}

	private String getXspress3ConfigParmeters() throws Exception {
		return XMLHelpers.toXMLString(Xspress3Parameters.mappingURL, xspress3bufferedDetector.getConfigurationParameters());
	}
}
