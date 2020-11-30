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
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.SortedMap;
import java.util.TreeMap;
import java.util.concurrent.Future;
import java.util.concurrent.TimeoutException;

import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang.StringUtils;
import org.dawnsci.ede.EdeDataConstants;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.nexus.tree.NexusTreeProvider;
import gda.data.scan.datawriter.XasNexusDataWriter;
import gda.device.ContinuousParameters;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.device.detector.DummyNXDetector;
import gda.device.detector.countertimer.TfgScalerWithLogValues;
import gda.device.enumpositioner.ValvePosition;
import gda.device.scannable.ContinuouslyScannable;
import gda.device.scannable.MetashopDataScannable;
import gda.device.scannable.ScannableUtils;
import gda.device.scannable.TurboXasScannable;
import gda.device.trajectoryscancontroller.TrajectoryScanController;
import gda.device.trajectoryscancontroller.TrajectoryScanController.ExecuteState;
import gda.device.trajectoryscancontroller.TrajectoryScanController.ExecuteStatus;
import gda.factory.FactoryException;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.scan.ede.datawriters.AsciiWriter;
import gov.aps.jca.CAException;
import uk.ac.diamond.daq.concurrent.Async;
import uk.ac.gda.beans.vortex.Xspress3Parameters;
import uk.ac.gda.devices.detector.xspress3.Xspress3BufferedDetector;
import uk.ac.gda.server.exafs.epics.device.scannable.ShutterChecker;
import uk.ac.gda.util.beans.xml.XMLHelpers;

/**
 *  A TurboXasScan is a type of Continuous scan which can perform multiple sweeps of a fast slit and collect the spectra for each sweep.
 *  It is designed to used with a {@link TurboXasScannable} object which contains a full definition of the experiment
 *  in a {@link TurboXasParameters} object, including timing group information in a List of {@link TurboSlitTimingGroup}s.
 *  It can also be used with a {@link ContinuouslyScannable}, in which case the behaviour is like a regular {@link ContinuousScan}.
 *  (i.e. a single spectrum is collected).
 * 	<li>A timing group comprises one or more spectra with the same time per spectrum (i.e. motor speed used for scan)
 *  <li>Each timing group can have a different time per spectrum.
 *  <li>The pulse streams for multiple spectra used for hardware triggered data collection are produced from the Zebra.
 *  The Zebra is configured by the {@link TurboXasScannable} being used, or assumed to be already configured before the scan start.
 *  <li>Data is added to the NeXus file one spectrum at a time after the motor move for each has been completed.
 *  by using multiple gates (i.e. one gate per spectrum).
 *  <li>Spectra are sent to Ede scan plot view in the client as they are collected.
 */
public class TurboXasScan extends ContinuousScan {

	private static final long serialVersionUID = 1L;

	private static final Logger logger = LoggerFactory.getLogger(TurboXasScan.class);
	private TurboXasMotorParameters turboXasMotorParams;
	private TurboXasScannable turboSlit;

	private boolean doTrajectoryScan = false;
	private boolean useXspress3SwmrReadout = true;
	private boolean twoWayScan = false;

	private TurboXasNexusTree nexusTree = new TurboXasNexusTree();
	private PlotUpdater plotUpdater = new PlotUpdater();
	private List<Scannable> scannablesToMonitor;
	private Optional<Scannable> shutter = Optional.empty();
	private DetectorFunctions detectorFunctions = new DetectorFunctions();

	private AsciiWriter asciiWriter;
	private boolean writeAsciiDataAfterScan = false;

	private int numReadoutsPerSpectrum;
	private int numSpectraPerCycle;
	private int numReadoutsPerCycle;
	private int numCycles;
	private int maxNumScalerFramesPerCycle = 250000;
	private String dataNameToSelectInPlot = EdeDataConstants.LN_I0_IT_COLUMN_NAME;
	private volatile int lastFrameRead;
	private int pollIntervalMillis = 500;
	private List<String> datasetNamesToAverage = Collections.emptyList();
	private Optional<Scannable> scannableToMove = Optional.empty();
	private List<Object> positionsForScan = Collections.emptyList();

	private Future<?> spectrumEventProcessing = null;
	private SortedMap<Integer, List<SpectrumEvent>> spectrumEventMap = new TreeMap<>();
	private int spectrumEventTimeoutSecs = 600;

	public TurboXasScan(ContinuouslyScannable energyScannable, Double start, Double stop, Integer numberPoints,
			Double time, BufferedDetector[] detectors) {
		super(energyScannable, start, stop, numberPoints, time, detectors);
		detectorFunctions.setDetectors(detectors);
	}

	public TurboXasScan(ContinuouslyScannable energyScannable, TurboXasMotorParameters motorParams, BufferedDetector[] detectors) {
		// don't set scan time here, there may be multiple timing groups...
		super(energyScannable, motorParams.getScanStartPosition(), motorParams.getScanEndPosition(),
				motorParams.getNumReadoutsForScan(), 0.0, detectors);
		turboXasMotorParams = motorParams;
		doTrajectoryScan = turboXasMotorParams.getScanParameters().getUseTrajectoryScan();
		detectorFunctions.setDetectors(detectors);
		addMetaDataScannable();

		// Set the datawriter
		XasNexusDataWriter dataWriter = createDataWriter();
		setDataWriter(dataWriter);
	}

	/**
	 * Create Nexus datawriter, set output template to include sample name after the scan number if it's been set.
	 * @return XasNexusDataWriter
	 */
	private XasNexusDataWriter createDataWriter() {
		XasNexusDataWriter dataWriter = new XasNexusDataWriter();
		setScanNumber(dataWriter.getCurrentScanIdentifier());
		String filenameTemplate = "nexus/%d";
		String sampleName = turboXasMotorParams.getScanParameters().getSampleName();
		if (StringUtils.isNotEmpty(sampleName)) {
			// Replace any whitespace characters with '-'s :
			String name = sampleName.trim().replaceAll("\\s+", "-");
			filenameTemplate += "_"+name;
		}
		filenameTemplate += ".nxs";
		dataWriter.setNexusFileNameTemplate(filenameTemplate);
		return dataWriter;
	}

	@Override
	public void doCollection() throws Exception {

		checkMainShutterIsOpen();

		logger.info("Running scan");

		plotUpdater.setCurrentSpectrumNumber(1);
		plotUpdater.setCurrentGroupNumber(1);

		String energyAxisName =  TurboXasNexusTree.POSITION_COLUMN_NAME;
		if (turboXasMotorParams != null && !turboXasMotorParams.getScanParameters().isUsePositionsForScan()) {
			energyAxisName = TurboXasNexusTree.ENERGY_COLUMN_NAME;
		}
		if (getScanAxis() instanceof TurboXasScannable) {
			turboSlit = (TurboXasScannable) getScanAxis();
		}
		plotUpdater.setEnergyAxisName(energyAxisName);
		plotUpdater.setPositionAxisName(TurboXasNexusTree.POSITION_COLUMN_NAME);
		plotUpdater.setDatanameToSelectInPlot(dataNameToSelectInPlot);

		plotUpdater.clearDatanamesToIgnore();
		plotUpdater.addDatanameToIgnore(TurboXasNexusTree.ENERGY_COLUMN_NAME);
		plotUpdater.addDatanameToIgnore(TurboXasNexusTree.POSITION_COLUMN_NAME);
		plotUpdater.addDatanameToIgnore(TfgScalerWithLogValues.LNITIREF_LABEL);
		plotUpdater.addDatanameToIgnore("Iref");

		if (getScanAxis() instanceof TurboXasScannable && turboXasMotorParams != null) {
			collectMultipleSpectra();
		} else {
			logger.info("Setting up scan using ContinuousParameters");
			numReadoutsPerSpectrum = getTotalNumberOfPoints();
			prepareDetectors(numReadoutsPerSpectrum, 1);
			collectOneSpectrum(true);
		}

		logger.info("Scan finished");
 	}

	private void collectMultipleSpectra() throws Exception {
		setupTurboXasScannable();

		// Prepare detectors (BufferedScalers, Xspress3) for readout of all spectra - all spectra for all positions.
		prepareDetectors();

		// loop over positions, do one collection of multiple spectra at each position ...
		if (scannableToMove.isPresent() && !positionsForScan.isEmpty()) {

			for(int positionNumber=0; positionNumber<positionsForScan.size(); positionNumber++) {
				if (checkEarlyFinish()) {
					return;
				}
				Scannable scn = scannableToMove.get();
				String message = "Moving "+scn.getName()+" to position "+positionsForScan.get(positionNumber);
				logger.info(message);

				InterfaceProvider.getTerminalPrinter().print(message);
				scn.moveTo(positionsForScan.get(positionNumber));
				logger.info("{} move finished", scn.getName());

				// Add extra label to plots with the position of the scannable
				String extraPlotLabel = String.format("%s : %s", scn.getName(), scn.getPosition().toString());
				plotUpdater.setExtraLabel(extraPlotLabel);

				collectSpectra();
			}

		} else {
			// Do one collection of multiple spectra
			collectSpectra();
		}
	}

	private boolean checkEarlyFinish() throws InterruptedException {
		checkThreadInterrupted();
		waitIfPaused();
		return isFinishEarlyRequested();
	}

	/**
	 * Move turbo slit and collect spectra for all timing groups :
	 * <li> Move turbo slit to the initial position
	 * <li> Configure and arm the zebra
	 * <li> Create and start the detector readout thread
	 * <li> Open the shutter
	 * <li> Make the motor moves using either trajectory scan or Epics motor record
	 * <li> Close the shutter
	 * <li> Wait for detector readouts to finish
	 * <li> Disarm the zebra.
	 *
	 * @throws Exception
	 */
	private void collectSpectra() throws Exception {
		TurboXasScannable turboXasScannable = (TurboXasScannable) getScanAxis();

		// Move turbo slit motor to initial position
		moveToInitialPosition(turboXasScannable);

		// Configure the zebra
		turboXasScannable.configureZebra();

		// Arm zebra
		turboXasScannable.armZebra();

		// Create and start the readout thread
		DetectorReadoutRunnable detectorReadoutRunnable = getDetectorReadoutRunnable();
		detectorReadoutRunnable.setLastFrameRead(lastFrameRead);
		Async.execute(detectorReadoutRunnable);

		startSpectrumEventsThread();

		moveShutter(ValvePosition.OPEN);

		if (doTrajectoryScan) {
			moveWithTrajectoryScan();
		} else {
			moveWithMotorRecord();
		}

		InterfaceProvider.getTerminalPrinter().print("Turbo slit moves finished");

		moveShutter(ValvePosition.CLOSE);

		detectorReadoutRunnable.waitForAllSpectra(10.0);

		turboXasScannable.atScanEnd();
	}

	/**
	 * Collect multiple spectra by performing motor moves using trajectory scan moves for all the timing groups.
	 * @throws Exception
	 */
	private void moveWithTrajectoryScan() throws Exception {
		TurboXasScannable turboXasScannable = (TurboXasScannable) getScanAxis();

		// Create the trajectory scan profile
		turboXasScannable.prepareTrajectoryScan();

		InterfaceProvider.getTerminalPrinter().print("Running TurboXas scan using trajectory scan...");

		// Adjust start time of axis to account for motor to get to start of first spectrum
		TrajectoryScanPreparer trajScanPreparer = turboXasScannable.getTrajectoryScanPreparer();
		TrajectoryScanController controller = trajScanPreparer.getTrajectoryScanController();
		double timeToInitialPosition = trajScanPreparer.getMaxTimePerStep();
		double timeToScanStart = Math.abs(turboXasMotorParams.getScanStartPosition() - turboXasMotorParams.getStartPosition())/turboXasMotorParams.getScanMotorSpeed();
		long delay = (long)(1000*(timeToInitialPosition + timeToScanStart));
		nexusTree.setStartTime(System.currentTimeMillis() + delay);

		turboXasScannable.executeTrajectoryScan();

		if (controller.getExecuteStatus() == ExecuteStatus.FAILURE){
			throw new Exception("Failure when executing trajectory scan - check Epics EDM screen.");
		}

		turboXasScannable.waitForTrajectoryScan();
 	}

	/**
	 * Collect multiple spectra by performing motor moves using Epics motor record for all the timing groups.
	 * @throws Exception
	 */
	private void moveWithMotorRecord() throws Exception {

		InterfaceProvider.getTerminalPrinter().print("Running TurboXas scan...");
		TurboXasScannable turboXasScannable = (TurboXasScannable) getScanAxis();

		// Zebra is already configured and armed, set flags so it is not repeated during {@link TurboXasScannable#performContinuousMove}
		turboXasScannable.setConfigZebraDuringPrepare(false);
		turboXasScannable.setArmZebraAtScanStart(false);
		turboXasScannable.setDisarmZebraAtScanEnd(false); // don't disarm zebra after first timing group

		// Loop over timing groups...
		List<TurboSlitTimingGroup> timingGroups = turboXasMotorParams.getScanParameters().getTimingGroups();
		for (int i = 0; i < timingGroups.size(); i++) {
			logger.info("Setting motor parameters for timing group {} of {}", i+1, timingGroups.size());

			// calculate and set the motor parameters for this timing group
			turboXasMotorParams.setMotorParametersForTimingGroup(i);

			// Loop over number of spectra (repetitions) ...
			int numRepetitions = timingGroups.get(i).getNumSpectra();
			for (int j = 0; j < numRepetitions; j++) {
				logger.info("Collecting spectrum : repetition {} of {}", j+1, numRepetitions);
				collectOneSpectrum(false);
			}
		}
 	}

	/**
	 * @return Total number of spectra across all timing groups
	 */
	private int getNumSpectra() {
		int totNumSpectra = 1;
		// Determine total number of spectra across all timing groups -
		if (turboXasMotorParams != null) {
			totNumSpectra = 0;
			for( TurboSlitTimingGroup group : turboXasMotorParams.getScanParameters().getTimingGroups() ) {
				totNumSpectra += group.getNumSpectra();
			}
		}
		return totNumSpectra;
	}

	/**
	 * Number of times the spectrum collection will be repeated.
	 * There will be one repetition per value in {@link #positionsForScan} list.
	 *
	 * @return number of repetitions
	 */
	public int getNumRepetitions() {
		if (scannableToMove.isPresent() && !positionsForScan.isEmpty()) {
			return positionsForScan.size();
		}
		return 1;
	}

	/**
	 * Create runnable object used for performing detector readout.	 *
	 * @return DetectorReadoutRunnable
	 */
	private DetectorReadoutRunnable getDetectorReadoutRunnable() {
		DetectorReadoutRunnable runnable = new DetectorReadoutRunnable();
		runnable.setNumFramesPerSpectrum(turboXasMotorParams.getNumReadoutsForScan());
		runnable.setTotalNumSpectraToCollect(getNumSpectra());
		runnable.setTimingGroups(turboXasMotorParams.getScanParameters().getTimingGroups());
		runnable.setPollIntervalMillis(pollIntervalMillis);
		return runnable;
	}

	private TurboXasScannable setupTurboXasScannable() throws Exception {
		TurboXasScannable turboXasScannable = (TurboXasScannable) getScanAxis();
		logger.info("Setting up scan using TurboXasScannable ({})", turboXasScannable.getName());

		// Set area detector flag (for timing, encoder position information)
		turboXasScannable.setMotorParameters(turboXasMotorParams);
		turboXasScannable.setTwoWayScan(twoWayScan);
		// Calculate motor parameters for first timing group (i.e. positions and num readouts for spectrum)
		turboXasMotorParams.setMotorParametersForTimingGroup(0);
		return turboXasScannable;
	}

	/**
	 * Move the motor to the initial scan position using 1-point trajectory scan.
	 * (Initial position is close to actual start position for bi-directional trajectory scan)
	 * If the trajectory fails to execute, try to move the motor instead with the Epics motor record.
	 *
	 * @param turboXasScannable
	 * @throws Exception
	 */
	private void moveToInitialPosition(TurboXasScannable turboXasScannable) throws DeviceException {
		double startPosition = turboXasMotorParams.getStartPosition();
		if (!doTrajectoryScan) {
			logger.info("Moving turbo slit to {} at start of scan", startPosition);
			turboXasScannable.moveTo(startPosition);
		} else {
			try {
				logger.info("Moving turbo slit to {} at start of scan using Trajectory scan", startPosition);
				TrajectoryScanPreparer trajScanPreparer = turboXasScannable.getTrajectoryScanPreparer();
				// Move the motor to the start position before arming zebras. Initial position is close to actual start position
				// and outside of the zebra gate.
				turboXasScannable.moveWithTrajectoryScan(startPosition, trajScanPreparer.getMaxTimePerStep());
				turboXasScannable.waitForTrajectoryScan();
			} catch(Exception e) {
				logger.warn("Problem moving turbo slit to {} at start of scan using trajectory scan.", startPosition, e);
				logger.info("Trying to move motor using Epics motor record instead");
				turboXasScannable.moveTo(startPosition);
			}
		}
	}

	@Override
	protected void endScan() throws DeviceException, InterruptedException {

		// Catch exceptions from super.endScan, so the rest of this function can complete correctly.
		try {
			super.endScan();
		} catch(DeviceException de) {
			logger.warn("DeviceException at end of scan when trying to stop scannables.", de);
		}

		// Stop the trajectory scan if it's still running by using 'Abort' button in Epics controller
		if (doTrajectoryScan) {
			TurboXasScannable turboXasScannable = (TurboXasScannable) getScanAxis();
			TrajectoryScanPreparer trajScanPreparer = turboXasScannable.getTrajectoryScanPreparer();
			try {
				if (trajScanPreparer.getTrajectoryScanController().getExecuteState() != ExecuteState.DONE) {
					trajScanPreparer.setAbortProfile();
				}
			} catch (Exception e) {
				logger.warn("Problem stopping Epics Trajectory scan for Turbo Slit at end of scan", e);
			}
		}

		for (BufferedDetector detector : getScanDetectors()) {
			try {
				detector.stop();
			}catch(DeviceException de) {
				logger.warn("Problem stopping detector {} at end of scan", detector.getName(), de);
			}
		}

		// Close shutter after motion and detectors have been stopped
		moveShutter(ValvePosition.CLOSE);

		try {
			nexusTree.addDataAtEndOfScan(getDataWriter().getCurrentFileName(), getScanDetectors());
		} catch (Exception e) {
			logger.warn("Problem adding time axis data at end of scan", e);
		}

		if (spectrumEventProcessing != null && !spectrumEventProcessing.isDone()) {
			logger.warn("Spectrum event processing has not finished yet - stopping it now");
			spectrumEventProcessing.cancel(true);
		}

		try {
			writeAsciiData();
		} catch (Exception e) {
			logger.error("Problem writing ascii file at end of scan : {}", e.getMessage(), e);
		}
	}

	private void writeAsciiData() throws Exception {
		if (writeAsciiDataAfterScan) {
			if (asciiWriter == null) {
				asciiWriter = new AsciiWriter();
			}
			String nexusPath = Paths.get(getDataWriter().getCurrentFileName()).toAbsolutePath().toString();
			asciiWriter.setNexusFilename(nexusPath);

			String asciiName = FilenameUtils.getBaseName(nexusPath)+"_ascii.dat";
			Path asciiDir = Paths.get(FilenameUtils.getFullPath(nexusPath)).getParent().resolve("ascii");
			if (!asciiDir.toFile().exists()) {
				asciiDir = Paths.get(FilenameUtils.getFullPath(nexusPath));
			}
			asciiWriter.setAsciiFilename(asciiDir.resolve(asciiName).toAbsolutePath().toString());

			// Set the detector names on AsciiWriter so the correct data is read from Nexus file. 20/9/2018
			String[] detectorNames = Arrays.stream(getScanDetectors()).map(BufferedDetector::getName).toArray(String[]::new);
			asciiWriter.setDetectorNames(detectorNames);

			logger.info("Writing ascii data to {} at end of scan", asciiWriter.getAsciiFilename());
			asciiWriter.writeAsciiFile();
		}
	}

	/**
	 * Prepare detectors (BufferedScalers) for readout of all spectra
	 * Do this once at beginning to avoid overhead of clearing out scaler memory etc for each spectra.
	 *
	 * @throws DeviceException
	 * @throws InterruptedException
	 */
	public void prepareDetectors() throws Exception {
		int totNumSpectra = getNumSpectra()*getNumRepetitions();
		numReadoutsPerSpectrum = turboXasMotorParams.getNumReadoutsForScan();
		prepareDetectors(numReadoutsPerSpectrum, totNumSpectra); //also arms it
	}

	/**
	 * Prepare detectors for collection. The Tfg frames will be configured to use multiple cycles if
	 * the total number of time frames required exceeds the number set by {@link #setMaxNumScalerFramesPerCycle(int)}.
	 * This allows scaler memory to be cleared in after frames have been read and written to file, so they can be reused on next cycle.
	 * (i.e. circular buffer)
	 * @param numReadoutsPerSpectra
	 * @param numSpectra
	 * @throws DeviceException
	 * @throws InterruptedException
	 * @throws FactoryException
	 * @throws CAException
	 */
	public void prepareDetectors(int numReadoutsPerSpectra, int numSpectra) throws Exception {
		lastFrameRead = 0;
		int maxNumSpectraPerCycle = (int) Math.floor(maxNumScalerFramesPerCycle/numReadoutsPerSpectra);
		numSpectraPerCycle = Math.min(numSpectra,  maxNumSpectraPerCycle);
		numReadoutsPerCycle = numSpectraPerCycle*numReadoutsPerSpectra;

		ContinuousParameters params = createContinuousParameters();
		params.setNumberDataPoints(numReadoutsPerCycle);
		numCycles = (int) Math.ceil((double)numSpectra*numReadoutsPerSpectra/numReadoutsPerCycle);

		detectorFunctions.setUseTwoZebras(twoWayScan);
		detectorFunctions.setZebra1(turboSlit.getZebraDevice());
		detectorFunctions.setZebra2(turboSlit.getZebraDevice2());
		detectorFunctions.prepareDetectors(params, numSpectra, maxNumSpectraPerCycle, numReadoutsPerSpectra);
		prepareNexusTreeProvider(numReadoutsPerSpectrum);
	}

	public void prepareNexusTreeProvider(int numReadoutsPerSpectrum) {
		nexusTree.setFrameTimeFieldName(getFrameTimeFieldName());
		nexusTree.setScanAxis(getScanAxis());
		nexusTree.setXspress3FileReader(detectorFunctions.getXspress3FileReader());
		nexusTree.setNumReadoutsPerSpectrum(numReadoutsPerSpectrum);
		nexusTree.setExtraScannables(scannablesToMonitor);
		nexusTree.setStartTime(System.currentTimeMillis());
		nexusTree.setDatasetsToAverage(datasetNamesToAverage);
		nexusTree.clearRunningAverages();
	}

	public void setAddNxDataEntries(boolean tf) {
		nexusTree.setAddNxDataEntries(tf);
	}

	public boolean isAddNxDataEntries() {
		return nexusTree.isAddNxDataEntries();
	}

	private String getFrameTimeFieldName() {
		return getScanDetectors()[0].getExtraNames()[0];
	}

	/**
	 * Perform motor move and collect data for a single spectrum
	 *
	 * @param collectData run data collection after motor move has finished. If set to false, this generally means data collection
	 * should be happening in a separate thread.
	 * @throws Exception
	 */
	public void collectOneSpectrum(boolean collectData) throws Exception {
		checkThreadInterrupted();

		// Still need to create ContinuousParameters even if scan is setup using TurboXasMotorParams -
		// - it is passed to BufferedDetector so it can set the number of data points...
		prepareScanAxis();
		ContinuousParameters params = createContinuousParameters();
		ContinuouslyScannable scanAxis = getScanAxis();

		// Get motor parameters, return motor to initial run-up position, arm the zebra with gate and pulse parameters (if 'arm at scan start' = true)
		scanAxis.waitWhileBusy(); // to make sure motor is not still moving from last repetition/scan
		scanAxis.prepareForContinuousMove();

		final int numberScanpoints = Math.abs(scanAxis.getNumberOfDataPoints());
		params.setNumberDataPoints(numberScanpoints);
		super.setTotalNumberOfPoints(numberScanpoints);

		scanAxis.performContinuousMove();

		scanAxis.waitWhileBusy();
		// Wait for scan to finish, then readout all frames at end into single ScanDataPoint object

		// return if data collection is being done in background thread
		if (!collectData){
			return;
		}

		BufferedDetector[] scanDetectors = getScanDetectors();
		if (scanDetectors.length > 0) {
			readoutData(scanDetectors);
		}
	}

	/**
	 * Set the ContinuousParameters (and TurboXasMotorParameters) to be used on the scan axis.
	 */
	private void prepareScanAxis() {
		ContinuousParameters params = createContinuousParameters();
		ContinuouslyScannable scanAxis = getScanAxis();
		scanAxis.setContinuousParameters(params);

		// TurboXasScannable is configured using TurboXasMotorParameters rather than ContinuousParameters.
		// However, still need to store continuousParameters as well, since they are used to configure BufferedDetectors
		if (scanAxis instanceof TurboXasScannable && turboXasMotorParams != null) {
			((TurboXasScannable) scanAxis).setMotorParameters(turboXasMotorParams);
			// total time is set by createContinuousParameters() but doesn't seem to be used -
			// adjust the value to calculated scan time based on motor moves just in case... :-/
			params.setTotalTime( turboXasMotorParams.getTotalTimeForScan() );
		}
	}

	@Override
	public int getDimension() {
		return 1;
	}

	protected Object[][] readDetector(BufferedDetector detector, int lowFrame, int highFrame) throws Exception, DeviceException {
		NexusTreeProvider[][] detData = new NexusTreeProvider[1][];
		int spectrumNumber = currentPointCount+1;
		boolean reverseDetectorData = twoWayScan && spectrumNumber%2 == 1;
		nexusTree.setReverseDetectorReadout(reverseDetectorData);

		logger.info("Reading data from detectors for spectrum {} (frames {} to {}, reverse readout direction = {} ", spectrumNumber, lowFrame, highFrame, nexusTree.isReverseDetectorReadout());
		detData[0] = nexusTree.readFrames(detector, lowFrame, highFrame);
		// ScalerFrames are already cleared in nexusTree.readFrames by createNXDetectorData
		// detectorFunctions.clearScalerFrames(detector, lowFrame, highFrame-1);

		logger.info("data read successfully");
		return detData;
	}

	private class DetectorReadoutRunnable extends DetectorReadout {

		@Override
		public int getNumAvailableFrames() throws Exception {
			return detectorFunctions.getNumAvailableFrames();
		}

		@Override
		public void collectData() throws Exception {
			plotUpdater.setCurrentGroupNumber(getCurrentTimingGroupIndex()+1);
			plotUpdater.setCurrentSpectrumNumber(getNumSpectraCollectedForGroup());

			nexusTree.setGroupSpectrumNumber(getCurrentTimingGroupIndex()+1, getNumSpectraCollectedForGroup());
			TurboXasScan.this.readoutData(getScanDetectors());
		}

		@Override
		public boolean detectorsAreBusy() throws DeviceException {
			logger.debug("Checking if detectors are busy... ");
			if (detectorFunctions.isTfgArmed()) {
				logger.debug("Tfg is armed and waiting for an external trigger");
				return true;
			}
			boolean isBusy = getScanDetectors()[0].isBusy();
			logger.debug("Number of captured Zebra pulses = {}", detectorFunctions.getNumCapturedZebraPulses());
			logger.debug("Scalers are busy ? {}", isBusy);
			return isBusy;
		}
	}

	/**
	 * Read out frames from scalers for one spectrum of data and write the new data into the Nexus file.
	 * The new data is also send to the GUI progress updater.
	 * This function should only be called after checks to ensure the required frames of data are available.
	 * @param detector
	 * @throws Exception
	 */
	private void readoutData(BufferedDetector[] detectors) throws Exception {

		// Create scan data point
		ScanDataPoint thisPoint = new ScanDataPoint();
		thisPoint.setUniqueName(getName());
		thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());
		thisPoint.setStepIds(getStepIds());
		thisPoint.setScanPlotSettings(getScanPlotSettings());

		int[] dims = getDimensions();
		thisPoint.setScanDimensions(dims);

		// Add positions of any scannables being monitored
		if (scannablesToMonitor != null) {
			for(Scannable scannable : scannablesToMonitor ) {
				thisPoint.addScannable(scannable);
				thisPoint.addScannablePosition(scannable.getPosition(), scannable.getOutputFormat());
			}
		}

		int lastFrameToRead = lastFrameRead + numReadoutsPerSpectrum;
		int totalNumFramesAvailable = detectorFunctions.getNumAvailableFrames();
		if (lastFrameToRead > totalNumFramesAvailable) {
			logger.warn("Possible problem reading out data : Last frame of scaler data is {}, but need to read up to {}", totalNumFramesAvailable, lastFrameToRead);
		}

		// Add the detector data
		for(BufferedDetector detector : detectors) {
			Object[][] nxFrameData = readDetector(detector, lastFrameRead, lastFrameToRead);

			// NeXus writing works using NXDetector, so put scaler data in dummy NX detector...
			DummyNXDetector testDet = new DummyNXDetector(detector.getName(), 1);
			thisPoint.addDetector(testDet);
			thisPoint.addDetectorData(nxFrameData[0][0], ScannableUtils.getExtraNamesFormats(detector));
		}
		lastFrameRead += numReadoutsPerSpectrum;

		// If nested scan, determine number of times this scan will be repeated.
		int numPoints = 1;
		if (isChild())
			numPoints = getParent().getDimension();

		numPoints = getNumSpectra()*getNumRepetitions();

		thisPoint.setNumberOfPoints(numPoints);
		currentPointCount++;
		thisPoint.setCurrentPointNumber(currentPointCount);

		thisPoint.setInstrument(instrument);
		thisPoint.setCommand(getCommand());
		thisPoint.setScanIdentifier(getScanNumber());
		setScanIdentifierInScanDataPoint(thisPoint);

		try {
			if (getStatus().isAborting()) {
				logger.warn("Scan status = {}. Not adding data for spectrum {} to Nexus file.", getStatus(), currentPointCount+1);
				return;
			}
			getDataWriter().addData(thisPoint);
		}catch(Exception ie) {
			logger.warn("Problem adding datapoint to ascii file", ie);
		}
		thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());

		plotUpdater.setFilename(thisPoint.getCurrentFilename());
		plotUpdater.clearDatasets();
		plotUpdater.addDatasetsFromScanDataPoint(thisPoint);
		plotUpdater.sendDataToController();
	}

	private void addMetaDataScannable() {
		MetashopDataScannable scannableToManageMetadata = new MetashopDataScannable();

		scannableToManageMetadata.addData("TurboXasParameters", turboXasMotorParams.getScanParameters().toXML());
		Xspress3BufferedDetector xspress3Detector = detectorFunctions.getXspress3Detector();
		if (xspress3Detector != null) {
			try {
				scannableToManageMetadata.addData("Xspress3", XMLHelpers.toXMLString(Xspress3Parameters.mappingURL, xspress3Detector.getConfigurationParameters()));
			} catch (Exception e) {
				logger.warn("Problem getting Xspress3 parameter meta data", e);
			}
		}

		scannableToManageMetadata.atScanStart(); // add data to metashop *before* creating datawriter
		allScannables.add(scannableToManageMetadata);
	}

	public TurboXasMotorParameters getTurboXasMotorParams() {
		return turboXasMotorParams;
	}

	public boolean getDoTrajectoryScan() {
		return doTrajectoryScan;
	}

	public void setDoTrajectoryScan(boolean doTrajectoryScan) {
		this.doTrajectoryScan = doTrajectoryScan;
	}

	public boolean getUseXspress3SwmrReadout() {
		return useXspress3SwmrReadout;
	}

	public void setUseXspress3SwmrReadout(boolean useXspress3SwmrReadout) {
		this.useXspress3SwmrReadout = useXspress3SwmrReadout;
	}

	/** Number of spectra per Tfg cycle (calculated by {@link #prepareDetectors()}) **/
	public int getNumSpectraPerCycle() {
		return numSpectraPerCycle;
	}

	/** Number of spectra per Tfg cycle (calculated by {@link #prepareDetectors()}) **/
	public int getNumReadoutsPerCycle() {
		return numReadoutsPerCycle;
	}
	/** Number of Tfg cycles needed to record all spectra (calculated by {@link #prepareDetectors()}) **/
	public int getNumCycles() {
		return numCycles;
	}

	/** Get Maximum number of scaler frames of data that can be stored by Tfg **/
	public int getMaxNumScalerFramesPerCycle() {
		return maxNumScalerFramesPerCycle;
	}

	/** Set maximum number of scaler frames of data that can be stored by Tfg in single cycle
	 * (should be less than total than can be stored by tfg, typically <1million **/
	public void setMaxNumScalerFramesPerCycle(int maxNumScalerFramesPerCycle) {
		this.maxNumScalerFramesPerCycle = maxNumScalerFramesPerCycle;
	}

	public int getCurrentPointCount() {
		return currentPointCount;
	}

	public List<Scannable> getScannablesToMonitor() {
		return scannablesToMonitor;
	}

	public void setScannablesToMonitor(List<Scannable> scannablesToMonitor) {
		this.scannablesToMonitor = scannablesToMonitor;
	}

	public void addScannableToMonitor(Scannable scannable) {
		if (scannablesToMonitor==null) {
			scannablesToMonitor = new ArrayList<>();
		}
		scannablesToMonitor.add(scannable);
	}

	public boolean getWriteAsciiDataAfterScan() {
		return writeAsciiDataAfterScan;
	}

	public void setWriteAsciiDataAfterScan(boolean writeAsciiDataAfterScan) {
		this.writeAsciiDataAfterScan = writeAsciiDataAfterScan;
	}

	public AsciiWriter getAsciiDataWriter() {
		return asciiWriter;
	}

	public void setDataWriter(AsciiWriter asciiWriter) {
		this.asciiWriter = asciiWriter;
	}

	public String getDataNameToSelectInPlot() {
		return dataNameToSelectInPlot;
	}

	public void setDataNameToSelectInPlot(String dataNameToSelectInPlot) {
		this.dataNameToSelectInPlot = dataNameToSelectInPlot;
	}

	public int getPollIntervalMillis() {
		return pollIntervalMillis;
	}

	/**
	 * Poll time interval to use when waiting for new data to become available on detector(s)
	 * @param pollIntervalMillis
	 */
	public void setPollIntervalMillis(int pollIntervalMillis) {
		this.pollIntervalMillis = pollIntervalMillis;
	}

	public boolean isTwoWayScan() {
		return twoWayScan;
	}

	public void setTwoWayScan(boolean twoWayScan) {
		this.twoWayScan = twoWayScan;
	}

	/**
	 * Try to get shutter checker from list of all scannables; if present use it to check main shutter
	 * is open by calling {@link ShutterChecker#atPointStart()} (i.e. wait until main shutter is open).
	 * @throws DeviceException
	 */
	private void checkMainShutterIsOpen() throws DeviceException {
		Optional<ShutterChecker> shutterChecker = allScannables.stream()
				.filter(scn -> scn instanceof ShutterChecker)
				.map(scn -> (ShutterChecker) scn)
				.findFirst();

		if (shutterChecker.isPresent()) {
			logger.debug("Checking main shutter is open at start of scan using shutter checker", shutterChecker.get().getName());
			shutterChecker.get().atPointStart();
		}
	}

	/**
	 *
	 * @return Shutter scannable opened and closed at start and end of scan.
	 */
	public Scannable getShutter() {
		return shutter.orElse(null);
	}

	/**
	 * Set the shutter scannable to be opened and closed at start and end of the scan.
	 * @param shutter
	 */
	public void setShutter(Scannable shutter) {
		this.shutter = Optional.ofNullable(shutter);
	}

	private void moveShutter(String position) throws DeviceException, InterruptedException {
		if (shutter.isPresent()) {
			Scannable shutterScn = shutter.get();
			logger.debug("Moving {} to {}", shutterScn.getName(), position);
			if (shutterScn.getPosition().equals(position)) {
				logger.debug("{} is already in position", shutterScn.getName(), position);
				return;
			}
			InterfaceProvider.getTerminalPrinter().print("Moving "+shutterScn.getName()+" to '"+position+"' position ");
			shutterScn.moveTo(position);
			// Make sure shutter really is in the demand position...
			if (!shutterScn.getPosition().toString().equals(position)) {
				logger.debug("Waiting for shutter to move to {} (currently {})", position, shutterScn.getPosition());
				Thread.sleep(pollIntervalMillis);
			}
			logger.debug("Shutter move finished");
		}
	}

	public List<String> getDatasetNamesToAverage() {
		return datasetNamesToAverage;
	}

	public void setDatasetNamesToAverage(List<String> datasetNamesToAverage) {
		this.datasetNamesToAverage = datasetNamesToAverage;
	}

	public Scannable getScannableToMove() {
		return scannableToMove.orElse(null);
	}

	public void setScannableToMove(Scannable scannableToMove) {
		this.scannableToMove = Optional.ofNullable(scannableToMove);
	}

	public List<Object> getPositionsForScan() {
		return positionsForScan;
	}

	public void setPositionsForScan(List<Object> positionsForScan) {
		this.positionsForScan = positionsForScan;
	}

	public Map<Integer, List<SpectrumEvent>> getSpectrumEvents() {
		return spectrumEventMap;
	}

	public void addSpectrumEvent(int spectrumNumber, Scannable scannable, Object position) {
		if (!spectrumEventMap.containsKey(spectrumNumber)) {
			spectrumEventMap.put(spectrumNumber, new ArrayList<>());
		}
		spectrumEventMap.get(spectrumNumber).add(new SpectrumEvent(spectrumNumber, scannable, position));
	}

	public void addSpectrumEvent(int spectrumNumber, String scannableName, Object position) {
		Optional<Scannable> scannable = Finder.findOptional(scannableName);
		if (!scannable.isPresent()) {
			logger.warn("Can't add spectrum event for {} - scannable called {} was not found!");
			return;
		}
		addSpectrumEvent(spectrumNumber, scannable.get(), position);
	}

	private void startSpectrumEventsThread() {
		spectrumEventProcessing = Async.submit(this::processSpectrumEvents);
	}

	private void processSpectrumEvents() {
		if (spectrumEventMap.isEmpty()) {
			return; // nothing to do
		}

		logger.info("Starting the spectrum events loop...");
		for (Entry<Integer, List<SpectrumEvent>> entry : spectrumEventMap.entrySet()) {
			int numSpectra = entry.getKey();
			try {
				logger.info("Waiting for {} spectra to be captured by zebra(s)...", numSpectra);
				detectorFunctions.waitForCapturedZebraPulses(numSpectra, numReadoutsPerSpectrum, spectrumEventTimeoutSecs);

				// Process the events : move each scannable to the specified position, catch any exception to avoid exiting too early.
				for (SpectrumEvent event : entry.getValue()) {
					Scannable scn = event.getScannable();
					Object position = event.getPosition();
					logger.info("Moving {} to position {}", scn.getName(), position);
					try {
						if (scn.isBusy()) {
							logger.warn("Cannot move {} - it is already busy moving!", scn.getName());
						} else {
							scn.asynchronousMoveTo(position);
						}
					} catch (DeviceException e) {
						logger.error("Problem moving {}", scn.getName(), e);
					}
				}
			} catch (IllegalStateException | IOException | TimeoutException e) {
				logger.error("Problem waiting for {} spectra to be captured by zebra(s)", numSpectra, e);
			} catch (InterruptedException e) {
				// Deal with interrupted exception thrown when future.cancel(true) is called on the thread
				logger.error("Interrupted waiting for {} spectra to be captured by zebra(s). Exiting the spectrum event loop early", numSpectra, e);
				Thread.currentThread().interrupt();
				break;
			}
		}
		logger.info("Finished spectrum events loop.");
	}

	public int getSpectrumEventTimeoutSecs() {
		return spectrumEventTimeoutSecs;
	}

	public void setSpectrumEventTimeoutSecs(int spectrumEventTimeoutSecs) {
		this.spectrumEventTimeoutSecs = spectrumEventTimeoutSecs;
	}
}
