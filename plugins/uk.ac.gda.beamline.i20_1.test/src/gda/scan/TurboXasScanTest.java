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

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

import java.util.HashMap;
import java.util.Map;

import org.eclipse.dawnsci.analysis.api.tree.DataNode;
import org.eclipse.dawnsci.analysis.api.tree.GroupNode;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.january.dataset.IDataset;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.Test;

import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.device.detector.BufferedDetector;
import gda.device.detector.DummyDAServer;
import gda.device.detector.countertimer.BufferedScaler;
import gda.device.memory.Scaler;
import gda.device.motor.DummyMotor;
import gda.device.scannable.ScannableMotor;
import gda.device.scannable.TurboXasScannable;
import gda.device.timer.Etfg;
import gda.device.zebra.controller.Zebra;
import gda.device.zebra.controller.impl.ZebraDummy;
import gda.factory.Factory;
import gda.factory.FactoryException;
import gda.factory.Finder;
import gda.scan.ede.datawriters.AsciiWriterTest;
import uk.ac.gda.devices.detector.xspress3.Xspress3BufferedDetector;
import uk.ac.gda.devices.detector.xspress3.Xspress3Detector;
import uk.ac.gda.devices.detector.xspress3.controllerimpl.DummyXspress3Controller;

public class TurboXasScanTest extends EdeTestBase {

	private DummyDAServer daserver;
	private Etfg tfg;
	private Scaler memory;
	private BufferedScaler bufferedScaler;
	private TurboXasScannableForTesting turboXasScannable;
	private DummyXspress3Controller controllerForDetector;
	private Xspress3Detector xspress3detector;
	private Xspress3BufferedDetector xspress3bufferedDetector;
	private ScannableMotor testMotor;
	public static final String BUFFERED_SCALER_NAME = "bufferedScaler";
	public static final String[] BUFFERED_SCALER_FIELDS = { "frame_time", "I0", "It", "Iref" };

	public static final String BUFFERED_XSPRESS3_NAME = "xspress3bufferedDetector";
	public static final String[] BUFFERED_XSPRESS3_FIELDS = new String[] {"FF", TurboXasNexusTree.FF_SUM_IO_NAME };

	@AfterClass
	public static void tearDownClass() {
		// Remove factories from Finder so they do not affect other tests
		Finder.getInstance().removeAllFactories();
	}

	@Before
	public void setupEnvironment() throws Exception {
		LocalProperties.set(LocalProperties.GDA_VAR_DIR, "/scratch/Data");

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

		turboXasScannable = new TurboXasScannableForTesting();
		turboXasScannable.setName("turboXasScannable");
		turboXasScannable.setMotor(dummyMotor);
		turboXasScannable.setZebraDevice(dummyZebra);

		setupXSpress3();

		testMotor = createMotor("testMotor", 4.20);

		setupFinder();
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

		xspress3bufferedDetector = new Xspress3BufferedDetector();
		xspress3bufferedDetector.setName(BUFFERED_XSPRESS3_NAME);
		xspress3bufferedDetector.setXspress3Detector(xspress3detector);
		xspress3bufferedDetector.configure();
	}

	private void setupFinder() {
		final Factory factory = TestHelpers.createTestFactory("test");
		factory.addFindable(turboXasScannable);
		factory.addFindable(bufferedScaler);
		factory.addFindable(xspress3bufferedDetector);
		factory.addFindable(testMotor);
		factory.addFindable(xspress3detector);
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
		double timeForScan = 1;

		TurboXasScan scan = new TurboXasScan( turboXasScannable, startPos, endPos, numReadouts, timeForScan, new BufferedDetector[] {bufferedScaler} );
		scan.runScan();

		String nxsFile = scan.getDataWriter().getCurrentFileName();
		int numPointsPerSpectrum = numReadouts-1;
		int[] expectedDims = new int[]{1, numPointsPerSpectrum};
		for(String name : bufferedScaler.getExtraNames()) {
			assertDimensions(nxsFile, bufferedScaler.getName(), name, expectedDims);
			checkDataValidRange(nxsFile, bufferedScaler.getName(), name, new RangeValidator(0, 1, true, false) );
		}
		assertDimensions(nxsFile, bufferedScaler.getName(), TurboXasNexusTree.FRAME_INDEX, new int[]{numPointsPerSpectrum});
		assertDimensions(nxsFile, bufferedScaler.getName(), TurboXasNexusTree.ENERGY_COLUMN_NAME, new int[]{numPointsPerSpectrum});
		assertDimensions(nxsFile, bufferedScaler.getName(), TurboXasNexusTree.POSITION_COLUMN_NAME, new int[]{numPointsPerSpectrum});
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

	/**
	 * @param params
	 * @return Total number of spectra across all timing groups
	 */
	public int getNumSpectra(TurboXasParameters params) {
		return params.getTimingGroups().stream().mapToInt(TurboSlitTimingGroup::getNumSpectra).sum();
	}

	public int getNumPointsPerSpectrum(TurboXasParameters params) {
		return (int) ((params.getEndPosition()-params.getStartPosition())/params.getPositionStepSize()) - 1;
	}


	@Test
	public void testTurboXasScanMultipleSpectra() throws InterruptedException, Exception {
		setup(TurboXasScan.class, "testTurboXasScanMultipleSpectra");
		TurboXasParameters parameters = getTurboXasParameters();
		parameters.addTimingGroup(new TurboSlitTimingGroup("group1", 0.10, 0.0, 5));
		parameters.addTimingGroup(new TurboSlitTimingGroup("group2", 0.10, 0.0, 7));

		int numPointsPerSpectrum = getNumPointsPerSpectrum(parameters);
		int numSpectra = getNumSpectra(parameters);

		TurboXasMotorParameters motorParameters = parameters.getMotorParameters();
		motorParameters.setMotorParametersForTimingGroup(0);
		turboXasScannable.setMotorParameters(motorParameters);
		TurboXasScan scan = new TurboXasScan(turboXasScannable, motorParameters, new BufferedDetector[]{bufferedScaler});
		scan.runScan();

		String nexusFilename = scan.getDataWriter().getCurrentFileName();
		checkScalerNexusData(nexusFilename, numSpectra, numPointsPerSpectrum);
		checkNXDataGroups(nexusFilename, numSpectra, numPointsPerSpectrum);

	}

	@Test
	public void testTurboXasScanMultipleSpectraFinishEarly() throws InterruptedException, Exception {
		setup(TurboXasScan.class, "testTurboXasScanMultipleSpectraFinishEarly");
		TurboXasParameters parameters = getTurboXasParameters();
		parameters.addTimingGroup(new TurboSlitTimingGroup("group1", 0.10, 0.0, 10));
		parameters.addTimingGroup(new TurboSlitTimingGroup("group2", 0.10, 0.0, 12));

		// Run the scan in a background thread
		final TurboXasScan scan = new TurboXasScan(turboXasScannable, parameters.getMotorParameters(), new BufferedDetector[]{bufferedScaler});
		Thread runScanThread = new Thread( () -> {
			try {
				scan.runScan();
			} catch (Exception e) {
				System.out.print("Exception caught during scan : " + e);
		}});
		runScanThread.start();

		// Wait for a few spectra to be collected, then make the scan exit early by throwing InterruptedException
		int pointCount = 0;
		while (runScanThread.isAlive()) {
			Thread.sleep(500);
			pointCount = scan.getCurrentPointCount();
			System.out.println("Waiting for scan to complete, current point = " + pointCount);
			if (pointCount > 5) {
				turboXasScannable.setThrowException(true);
			}
		}
		int numPointsPerSpectrum = getNumPointsPerSpectrum(parameters);
		IDataset frameTimes = getDataset(scan.getDataWriter().getCurrentFileName(), bufferedScaler.getName(), "frame_time");
		int numSpectra = frameTimes.getShape()[0];
		checkScalerNexusData(scan.getDataWriter().getCurrentFileName(), numSpectra, numPointsPerSpectrum);
	}

	@Test
	public void testTurboXasScanMultipleSpectraXspress3() throws InterruptedException, Exception {
		setup(TurboXasScan.class, "testTurboXasScanMultipleSpectraXspress3");
		TurboXasParameters parameters = getTurboXasParameters();
		parameters.addTimingGroup(new TurboSlitTimingGroup("group1", 0.10, 0.0, 5));
		parameters.addTimingGroup(new TurboSlitTimingGroup("group2", 0.10, 0.0, 7));

		int numPointsPerSpectrum = getNumPointsPerSpectrum(parameters);
		int numSpectra = getNumSpectra(parameters);

		TurboXasMotorParameters motorParameters = parameters.getMotorParameters();
		motorParameters.setMotorParametersForTimingGroup(0);
		turboXasScannable.setMotorParameters(motorParameters);
		TurboXasScan scan = new TurboXasScan(turboXasScannable, motorParameters, new BufferedDetector[]{bufferedScaler, xspress3bufferedDetector});
		scan.runScan();

		String nexusFilename = scan.getDataWriter().getCurrentFileName();
		checkScalerNexusData(nexusFilename, numSpectra, numPointsPerSpectrum);
		checkDetectorNexusData(nexusFilename, xspress3bufferedDetector.getName(), numSpectra, numPointsPerSpectrum);
	}

	@Test
	public void testTurboXasParametersCreatesScan() throws InterruptedException, Exception {
		setup(TurboXasScan.class, "testTurboXasParametersCreatesScan");
		TurboXasParameters parameters = getTurboXasParameters();
		parameters.addTimingGroup(new TurboSlitTimingGroup("group1", 0.10, 0.0, 10));

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
		parameters.addTimingGroup(new TurboSlitTimingGroup("group1", 0.10, 0.0, 10));
		int numPointsPerSpectrum = getNumPointsPerSpectrum(parameters);
		int numSpectra = 10;

		TurboXasScan scan = parameters.createScan();
		scan.runScan();
		String nexusFilename = scan.getDataWriter().getCurrentFileName();

		checkScalerNexusData(nexusFilename, numSpectra, numPointsPerSpectrum);
		checkDetectorNexusData(nexusFilename, xspress3bufferedDetector.getName(), numSpectra, numPointsPerSpectrum);
		checkNXDataGroups(nexusFilename, numSpectra, numPointsPerSpectrum);

		// Check data for the scannable being monitored is present and has correct dimensions (1 value per spectrum)
		assertDimensions(nexusFilename, bufferedScaler.getName(), testMotor.getName(), new int[]{numSpectra});
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
		parameters.addTimingGroup(new TurboSlitTimingGroup("group1", 0.10, 0.0, 10));
		TurboXasScan scan = parameters.createScan();
		scan.setWriteAsciiDataAfterScan(true);
		scan.runScan();

		int numEnergies = getNumPointsPerSpectrum(parameters);
		int numSpectra = parameters.getTotalNumSpectra();
		int numFields = bufferedScaler.getExtraNames().length + 2; // 2 fields for Xspress3 - FF and FF_sum/I0
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
		checkDataValidRange(nexusFilename, detectorGroup, name, new RangeValidator(0, 1, true, false) );
	}

	private void checkScalerNexusData(String nexusFilename, int numSpectra, int numPointsPerSpectrum) throws NexusException {
		// Check shape and content of scaler output (should be all >0 when not also producing lnI0It values)
		checkDetectorNexusData(nexusFilename, bufferedScaler.getName(), numSpectra, numPointsPerSpectrum);

		// Check the extra datasets written at end of scan to show spectrum index and group for each spectra, time between spectra etc.
		assertDimensions(nexusFilename, bufferedScaler.getName(), "frame_time", new int[]{numSpectra, numPointsPerSpectrum});
		assertDimensions(nexusFilename, bufferedScaler.getName(), TurboXasNexusTree.TIME_BETWEEN_SPECTRA_COLUMN_NAME, new int[]{numSpectra});
		assertDimensions(nexusFilename, bufferedScaler.getName(), TurboXasNexusTree.TIME_COLUMN_NAME, new int[]{numSpectra});
		assertDimensions(nexusFilename, bufferedScaler.getName(), TurboXasNexusTree.SPECTRUM_INDEX, new int[]{numSpectra});
		assertDimensions(nexusFilename, bufferedScaler.getName(), TurboXasNexusTree.SPECTRUM_GROUP, new int[]{numSpectra});
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
		for(String name : bufferedScaler.getExtraNames()) {
			String groupName = bufferedScaler.getName()+"_"+name;
			assertDimensions(filename, groupName, name, new int[] {numSpectra, numPointsPerSpectrum});
			assertDimensions(filename, groupName, TurboXasNexusTree.ENERGY_COLUMN_NAME, new int[] {numPointsPerSpectrum});
			assertDimensions(filename, groupName, TurboXasNexusTree.POSITION_COLUMN_NAME, new int[] {numPointsPerSpectrum});
			assertDimensions(filename, groupName, TurboXasNexusTree.SPECTRUM_INDEX, new int[] {numSpectra});
			assertDimensions(filename, groupName, TurboXasNexusTree.TIME_COLUMN_NAME, new int[] {numSpectra});
		}
	}
}
