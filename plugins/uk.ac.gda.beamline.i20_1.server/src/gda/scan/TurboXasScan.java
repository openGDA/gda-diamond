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
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.apache.commons.io.FilenameUtils;
import org.dawnsci.ede.EdeDataConstants;
import org.eclipse.dawnsci.analysis.api.io.ScanFileHolderException;
import org.eclipse.dawnsci.nexus.NexusException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.nexus.tree.NexusTreeProvider;
import gda.data.scan.datawriter.XasNexusDataWriter;
import gda.data.swmr.SwmrFileReader;
import gda.device.ContinuousParameters;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.device.detector.DummyNXDetector;
import gda.device.detector.countertimer.BufferedScaler;
import gda.device.detector.countertimer.TfgScalerWithLogValues;
import gda.device.enumpositioner.ValvePosition;
import gda.device.scannable.ContinuouslyScannable;
import gda.device.scannable.MetashopDataScannable;
import gda.device.scannable.ScannableUtils;
import gda.device.scannable.TurboXasScannable;
import gda.device.trajectoryscancontroller.TrajectoryScanController;
import gda.device.trajectoryscancontroller.TrajectoryScanController.ExecuteState;
import gda.device.trajectoryscancontroller.TrajectoryScanController.ExecuteStatus;
import gda.device.zebra.controller.impl.ZebraDummy;
import gda.factory.FactoryException;
import gda.jython.InterfaceProvider;
import gda.scan.ede.datawriters.AsciiWriter;
import gov.aps.jca.CAException;
import uk.ac.diamond.daq.concurrent.Async;
import uk.ac.gda.beans.vortex.Xspress3Parameters;
import uk.ac.gda.devices.detector.xspress3.TRIGGER_MODE;
import uk.ac.gda.devices.detector.xspress3.Xspress3BufferedDetector;
import uk.ac.gda.devices.detector.xspress3.Xspress3Controller;
import uk.ac.gda.devices.detector.xspress3.controllerimpl.EpicsXspress3Controller;
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

	private boolean useAreaDetector = false;
	private boolean doTrajectoryScan = false;
	private boolean useXspress3SwmrReadout = true;
	private boolean twoWayScan = false;

	private Map<String, String> xspressAttributeMap = new HashMap<String, String>();
	private String pathToAttributeData = "/entry/instrument/NDAttributes/";

	private Xspress3BufferedDetector xspress3BufferedDetector;
	private SwmrFileReader xspress3FileReader;
	private TurboXasNexusTree nexusTree = new TurboXasNexusTree();
	private PlotUpdater plotUpdater = new PlotUpdater();
	private List<Scannable> scannablesToMonitor;
	private Optional<Scannable> shutter = Optional.empty();

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

	public TurboXasScan(ContinuouslyScannable energyScannable, Double start, Double stop, Integer numberPoints,
			Double time, BufferedDetector[] detectors) {
		super(energyScannable, start, stop, numberPoints, time, detectors);
	}

	public TurboXasScan(ContinuouslyScannable energyScannable, TurboXasMotorParameters motorParams, BufferedDetector[] detectors) {
		// don't set scan time here, there may be multiple timing groups...
		super(energyScannable, motorParams.getScanStartPosition(), motorParams.getScanEndPosition(),
				motorParams.getNumReadoutsForScan(), 0.0, detectors);
		turboXasMotorParams = motorParams;
		doTrajectoryScan = turboXasMotorParams.getScanParameters().getUseTrajectoryScan();
		addMetaDataScannable();

		// Set the datawriter
		XasNexusDataWriter dataWriter = new XasNexusDataWriter();
		setDataWriter(dataWriter);
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

		ContinuouslyScannable scanAxis = getScanAxis();
		if (scanAxis instanceof TurboXasScannable && turboXasMotorParams != null) {
			if (doTrajectoryScan) {
				collectMultipleSpectraTrajectoryScan();
			} else {
				collectMultipleSpectra();
			}
		} else {
			logger.info("Setting up scan using ContinuousParameters");
			lastFrameRead = 0;
			numReadoutsPerSpectrum = getTotalNumberOfPoints();
			prepareDetectors(numReadoutsPerSpectrum, 1);
			prepareNexusTreeProvider(numReadoutsPerSpectrum);
			collectOneSpectrum(true);
		}

		logger.info("Scan finished");
 	}

	/**
	 * Collect multiple spectra by performing motor moves for several timing groups.
	 * @throws Exception
	 */
	private void collectMultipleSpectraTrajectoryScan() throws Exception {
		TurboXasScannable turboXasScannable = setupTurboXasScannable();

		moveToIntialPosition(turboXasScannable);

		// Configure the zebra
		turboXasScannable.configureZebra(); // would normally get called in ContinuousScan.prepareForContinuousMove()

		// Arm zebra
		turboXasScannable.armZebra();

		// Prepare detectors (BufferedScalers) for readout of all spectra
		prepareDetectors();

		// Create the trajectory scan profile
		TrajectoryScanPreparer trajScanPreparer = turboXasScannable.getTrajectoryScanPreparer();
		trajScanPreparer.setDefaults();
		trajScanPreparer.setTwoWayScan(twoWayScan);
		trajScanPreparer.addPointsForTimingGroups(turboXasMotorParams);

		// send profile points to Epics trajectory scan, building and appending as necessary
		TrajectoryScanController controller = trajScanPreparer.getTrajectoryScanController();
		if (controller.getExecuteState() != ExecuteState.DONE) {
			throw new Exception("Problem building trajectory scan profile - scan is already runninng!");
		}
		trajScanPreparer.sendAppendProfileValues();

		InterfaceProvider.getTerminalPrinter().print("Running TurboXas scan using trajectory scan...");

		moveShutter(ValvePosition.OPEN);

		// Adjust start time of axis to account for motor to get to start of first spectrum
		double timeToInitialPosition = trajScanPreparer.getMaxTimePerStep();
		double timeToScanStart = Math.abs(turboXasMotorParams.getScanStartPosition() - turboXasMotorParams.getStartPosition())/turboXasMotorParams.getScanMotorSpeed();
		long delay = (long)(1000*(timeToInitialPosition + timeToScanStart));
		nexusTree.setStartTime(System.currentTimeMillis() + delay);

		trajScanPreparer.setExecuteProfile();

		if (controller.getExecuteStatus() == ExecuteStatus.FAILURE){
			throw new Exception("Failure when executing trajectory scan - check Epics EDM screen.");
		}

		// Wait until some points have been captured by zebra (i.e. motor has started moving)
		while(getNumCapturedZebraPulses()==0) {
			logger.info("Waiting for points to be captured by Zebra before starting data collection");
			Thread.sleep(100);
		}

		// Start detector readout thread
		DetectorReadoutRunnable detectorReadoutRunnable = getDetectorReadoutRunnable();
		Async.execute(detectorReadoutRunnable);

		waitForTrajectoryScan(controller);

		if (controller.getExecuteStatus() == ExecuteStatus.SUCCESS) {
			// Wait at end for data collection thread to finish
			waitForReadoutToFinish(detectorReadoutRunnable, 600.0);
		}
		// flags back to default values
		turboXasScannable.atScanEnd();
 	}

	/**
	 * Collect multiple spectra by performing motor moves for several timing groups.
	 * @throws Exception
	 */
	private void collectMultipleSpectra() throws Exception {
		TurboXasScannable turboXasScannable = setupTurboXasScannable();

		moveToIntialPosition(turboXasScannable);

		// Prepare detectors (BufferedScalers) for readout of all spectra
		prepareDetectors();

		// Make new instance of detector readout runnable to collect detector data.
		// start it after first spectrum is available
		DetectorReadoutRunnable detectorReadoutRunnable = getDetectorReadoutRunnable();

		InterfaceProvider.getTerminalPrinter().print("Running TurboXas scan...");

		moveShutter(ValvePosition.OPEN);

		// Loop over timing groups...
		List<TurboSlitTimingGroup> timingGroups = turboXasMotorParams.getScanParameters().getTimingGroups();
		for (int i = 0; i < timingGroups.size(); i++) {
			turboXasScannable.setDisarmZebraAtScanEnd(false); // don't disarm zebra after first timing group

			logger.info("Setting motor parameters for timing group {} of {}", i+1, timingGroups.size());

			// calculate and set the motor parameters for this timing group
			turboXasMotorParams.setMotorParametersForTimingGroup(i);

			// Loop over number of spectra (repetitions) ...
			int numRepetitions = timingGroups.get(i).getNumSpectra();
			for (int j = 0; j < numRepetitions; j++) {
				logger.info("Collecting spectrum : repetition {} of {}", j+1, numRepetitions);

				collectOneSpectrum(false);

				// Start collection thread after first spectrum
				if (i==0 && j==0) {
					Async.execute(detectorReadoutRunnable);
				}

				// Set flags so we don't reconfigure and rearm zebra for next timing group or scan
				// (each group has same number of readouts etc., only the motor speed changes)
				turboXasScannable.setArmZebraAtScanStart(false);
				turboXasScannable.setConfigZebraDuringPrepare(false);
			}
		}
		// Wait at end for data collection thread to finish
		waitForReadoutToFinish(detectorReadoutRunnable, 600.0);

		// flags back to default values
		turboXasScannable.atScanEnd();
 	}

	/**
	 * @return Total number of spectra across all timing groups
	 */
	private int getTotalNumSpectra() {
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
	 * Create runnable object used for performing detector readout.	 *
	 * @return DetectorReadoutRunnable
	 */
	private DetectorReadoutRunnable getDetectorReadoutRunnable() {
		DetectorReadoutRunnable runnable = new DetectorReadoutRunnable();
		runnable.setNumFramesPerSpectrum(turboXasMotorParams.getNumReadoutsForScan());
		runnable.setTotalNumSpectraToCollect(getTotalNumSpectra());
		runnable.setTimingGroups(turboXasMotorParams.getScanParameters().getTimingGroups());
		runnable.setPollIntervalMillis(pollIntervalMillis);
		return runnable;
	}

	private TurboXasScannable setupTurboXasScannable() throws Exception {
		TurboXasScannable turboXasScannable = (TurboXasScannable) getScanAxis();
		logger.info("Setting up scan using TurboXasScannable ({})", turboXasScannable.getName());

		// Set area detector flag (for timing, encoder position information)
		turboXasScannable.setUseAreaDetector(useAreaDetector);
		turboXasScannable.setMotorParameters(turboXasMotorParams);
		turboXasScannable.setTwoWayScan(twoWayScan);
		// Calculate motor parameters for first timing group (i.e. positions and num readouts for spectrum)
		turboXasMotorParams.setMotorParametersForTimingGroup(0);
		return turboXasScannable;
	}

	/**
	 * Wait for trajectory scan to execute.
	 * @return false if trajectory scan failed to execute successfully (i.e. if execute status != 'success' after scan finishes)
	 * @param controller
	 * @throws IOException
	 * @throws InterruptedException
	 */
	private boolean waitForTrajectoryScan(TrajectoryScanController controller) throws IOException, InterruptedException {
		logger.debug("Waiting for trajectory scan to execute");

		// Give it at least a second (in case trajectory hasn't quite started yet)...
		Thread.sleep(1000);

		// Wait while trajectory scan runs...
		while (controller.getExecuteState() == ExecuteState.EXECUTING) {
			Thread.sleep(500);
		}

		// Output some info on trajectory scan final execution state
		logger.debug("Trajectory scan finished. Execute state = {}, percent complete = {}", controller.getExecuteState(), controller.getScanPercentComplete());

		if (controller.getScanPercentComplete()<100 && controller.getExecuteStatus() != ExecuteStatus.SUCCESS) {
			String message = "\nTrajectory scan failed to execute correctly. Check Edm screen for more information";
			logger.warn(message);
			InterfaceProvider.getTerminalPrinter().print(message);
			return false;
		}
		return true;
	}

	/**
	 * Move the motor to the initial scan position using 1-point trajectory scan.
	 * (Initial position is close to actual start position for bi-directional trajectory scan)
	 *
	 * @param turboXasScannable
	 * @throws Exception
	 */
	private void moveToIntialPosition(TurboXasScannable turboXasScannable) throws Exception {
		TrajectoryScanPreparer trajScanPreparer = turboXasScannable.getTrajectoryScanPreparer();
		TrajectoryScanController controller = trajScanPreparer.getTrajectoryScanController();
		// Move the motor to the start position before arming zebras. Initial position is close to actual start position
		// and outside of the zebra gate.
		turboXasScannable.moveWithTrajectoryScan(turboXasMotorParams.getStartPosition(), trajScanPreparer.getMaxTimePerStep());
		waitForTrajectoryScan(controller);
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

	private void waitForReadoutToFinish(DetectorReadoutRunnable detectorReadoutRunnable, double maxWaitTimeSecs) throws ScanFileHolderException, DeviceException, InterruptedException {
		try {
			// Wait while XSpress3 hdf writing is still active; then close the file so final frames are
			// flushed to disk and available for reading.
			double timeWaited = 0.0;
			if (xspress3FileReader!=null && xspress3BufferedDetector!=null) {
				logger.info("Waiting for Xspress3 hdf writer to finish...");
				int lastFrame = 0;
				int currentFrame = -1;
				while (lastFrame!=currentFrame && timeWaited<maxWaitTimeSecs) {
					Thread.sleep(pollIntervalMillis);
					lastFrame = currentFrame;
					currentFrame = xspress3BufferedDetector.getController().getTotalHDFFramesAvailable();
					timeWaited += pollIntervalMillis * 0.001;
				}
				//stop the file writer
				xspress3BufferedDetector.getController().doStopSavingFiles();
			}

			logger.info("Waiting for detector collection thread to finish...");
			int expectedTotalNumFrames = getTotalNumSpectra()*numReadoutsPerSpectrum;
			int lastFrame = detectorReadoutRunnable.getLastFrameRead();
			while (lastFrame<expectedTotalNumFrames && timeWaited<maxWaitTimeSecs) {
				logger.info("Last frame read = {}", lastFrame);
				Thread.sleep(1000);
				timeWaited += 1.0;
				lastFrame = detectorReadoutRunnable.getLastFrameRead();
			}
		} catch (InterruptedException e) {
			logger.error("Sleep interrupted while waiting for readout to finish", e);
		} finally {
			int numSpectraCollected = detectorReadoutRunnable.getNumSpectraCollected();
			if (!detectorReadoutRunnable.collectionFinished()) {
				logger.warn("Detector collection not finished after {} secs. {} spectra collected.", maxWaitTimeSecs, numSpectraCollected);
			} else {
				logger.warn("Detector collection finished. {} spectra collected.", numSpectraCollected);
			}
		}
	}

	public void setScalerMode() throws DeviceException {
		// Try to set scalert64 mode first, otherwise Scalers seem to return junk. imh 14/9/2016
		BufferedDetector det = getScanDetectors()[0];
		if ( det instanceof BufferedScaler ) {
			Object result = ((BufferedScaler)det).getDaserver().sendCommand("tfg setup-cc-mode scaler64");
			if (!result.toString().equals("0")) {
				logger.info("Problem setting Tfg to use scaler64 mode - scaler readout may not work correctly...");
			}
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
		int totNumSpectra = getTotalNumSpectra();
		lastFrameRead = 0;
		numReadoutsPerSpectrum = turboXasMotorParams.getNumReadoutsForScan();
		prepareDetectors(numReadoutsPerSpectrum, totNumSpectra); //also arms it
		prepareNexusTreeProvider(numReadoutsPerSpectrum);
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
		setScalerMode();
		int maxNumSpectraPerCycle = (int) Math.floor(maxNumScalerFramesPerCycle/numReadoutsPerSpectra);
		numSpectraPerCycle = Math.min(numSpectra,  maxNumSpectraPerCycle);
		numReadoutsPerCycle = numSpectraPerCycle*numReadoutsPerSpectra;

		// Setup scaler memory to record all frames of data for all spectra across all timing groups
		ContinuousParameters params = createContinuousParameters();
		params.setNumberDataPoints(numReadoutsPerCycle);
		numCycles = (int) Math.ceil((double)numSpectra*numReadoutsPerSpectra/numReadoutsPerCycle);

		for (BufferedDetector detector : getScanDetectors() ) {
			detector.clearMemory();
			if (detector instanceof BufferedScaler) {
				((BufferedScaler)detector).setNumCycles(numCycles);
			}
			detector.setContinuousParameters(params);
			detector.setContinuousMode(true);
			checkThreadInterrupted();
			if (detector instanceof Xspress3BufferedDetector) {
				xspress3BufferedDetector = (Xspress3BufferedDetector)detector;
				prepareXSpress3(numSpectra, numReadoutsPerSpectra);
			}
		}
	}

	public void prepareNexusTreeProvider(int numReadoutsPerSpectrum) {
		nexusTree.setFrameTimeFieldName(getFrameTimeFieldName());
		nexusTree.setScanAxis(getScanAxis());
		nexusTree.setXspress3FileReader(xspress3FileReader);
		nexusTree.setNumReadoutsPerSpectrum(numReadoutsPerSpectrum);
		nexusTree.setExtraScannables(scannablesToMonitor);
		nexusTree.setStartTime(System.currentTimeMillis());
	}

	public Xspress3BufferedDetector getXspress3Detector() {
		for (BufferedDetector detector : getScanDetectors() ) {
			if (detector instanceof Xspress3BufferedDetector) {
				return (Xspress3BufferedDetector) detector;
			}
		}
		return null;
	}

	/**
	 * Prepeare XPress3 for collection:
	 * set number of frames to collect (for both the detector and hdf plugin),
	 * set trigger mode and next file number.
	 * @param numReadouts
	 * @throws Exception
	 */
	public void prepareXSpress3(int numSpectra, int numReadoutsPerSpectrum) throws Exception{
		if (xspress3BufferedDetector != null) {
			Xspress3Controller controller = xspress3BufferedDetector.getController();

			int totNumReadouts = numSpectra*numReadoutsPerSpectrum;

			controller.doStopSavingFiles();
			controller.doStop();
			controller.doReset();
			controller.setNumFramesToAcquire(totNumReadouts);
			controller.setHDFNumFramesToAcquire(totNumReadouts);
			controller.setTriggerMode(TRIGGER_MODE.TTl_Veto_Only);

			// set the HDF writer extra dimensions, so that MCA data has outer dimensions = [numSpectra, numReadoutsPerSpectrum]
			controller.configureHDFDimensions(new int[] { numReadoutsPerSpectrum, numSpectra });

			// controller.doReset();
			controller.setNextFileNumber(0);
			controller.setSavingFiles(true);
			controller.doStart();

			// create reader for loading data from Swmr file - only if using real hardware
			if (useXspress3SwmrReadout && controller instanceof EpicsXspress3Controller) {
				xspress3FileReader = new SwmrFileReader();
				if (xspressAttributeMap.isEmpty()) {
					setupXspressAttributeMap(xspress3BufferedDetector);
				}
				xspressAttributeMap.keySet().forEach((key) -> xspress3FileReader.addDatasetToRead(key, pathToAttributeData + xspressAttributeMap.get(key)));
			}
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
		ContinuouslyScannable scanAxis = getScanAxis();
		ContinuousParameters params = scanAxis.getContinuousParameters();

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
			collectData(scanDetectors);
		}
	}

	private String getFrameTimeFieldName() {
		return getScanDetectors()[0].getExtraNames()[0];
	}

	public void addXspressDatasetToRecord(String label, String attribute) {
		xspressAttributeMap.put(label, attribute);
	}

	private void setupXspressAttributeMap(Xspress3BufferedDetector detector) {
		for(int channel=0; channel<detector.getNumberOfElements(); channel++) {
			xspressAttributeMap.put(String.format("FF_%d", channel+1), String.format("Chan%dSca%d", channel+1, 5));
		}
	}

	@Override
	public int getDimension() {
		return 1;
	}

	private void clearFrames(BufferedDetector detector, int lowFrame, int highFrame) throws DeviceException {
		// Clear scaler memory multiple cycles are being used.
		if (numCycles>1) {
			if (detector instanceof BufferedScaler) {
				logger.debug("Clearing scaler memory frames {} to {}", lowFrame, highFrame);
				((BufferedScaler)detector).clearMemoryFrames(lowFrame, highFrame);
			}
		}
	}

	protected Object[][] readDetector(BufferedDetector detector, int lowFrame, int highFrame) throws Exception, DeviceException {
		NexusTreeProvider[][] detData = new NexusTreeProvider[1][];
		int spectrumNumber = currentPointCount+1;
		boolean reverseDetectorData = twoWayScan && spectrumNumber%2 == 1;
		nexusTree.setReverseDetectorReadout(reverseDetectorData);

		logger.info("Reading data from detectors for spectrum {} (frames {} to {}, reverse readout direction = {} ", spectrumNumber, lowFrame, highFrame, nexusTree.isReverseDetectorReadout());

		detData[0] = nexusTree.readFrames(detector, lowFrame, highFrame);
		clearFrames(detector, lowFrame, highFrame-1);

		logger.info("data read successfully");
		return detData;
	}

	private class DetectorReadoutRunnable extends DetectorReadout {

		@Override
		public int getNumAvailableFrames() throws DeviceException, NexusException, ScanFileHolderException {
			return TurboXasScan.this.getNumAvailableFrames();
		}

		@Override
		public void collectData() throws Exception {
			plotUpdater.setCurrentGroupNumber(getCurrentTimingGroupIndex()+1);
			plotUpdater.setCurrentSpectrumNumber(getNumSpectraCollectedForGroup());
			TurboXasScan.this.collectData(getScanDetectors());
		}

		@Override
		public boolean detectorsAreBusy() throws DeviceException {
			return getScanDetectors()[0].isBusy();
		}
	}

	/**
	 *
	 * @return Total number of captured pulses by zebra(s) used from scan
	 * @throws DeviceException
	 */
	private int getNumCapturedZebraPulses() throws DeviceException {
		if (turboSlit != null) {
			// In dummy mode, just return total number of points that should have been captured
			if (turboSlit.getZebraDevice() instanceof ZebraDummy) {
				return numReadoutsPerCycle*numCycles;
			}

			try {
				int numPulsesZebra1 = turboSlit.getZebraDevice().getPCNumberOfPointsCaptured();
				int numPulsesZebra2 = 0;
				if (twoWayScan && turboSlit.getZebraDevice2() != null) {
					numPulsesZebra2 = turboSlit.getZebraDevice2().getPCNumberOfPointsCaptured();
				}
				logger.debug("Number of pulses captured by zebras : zebra1 = {}, zebra2 = {}", numPulsesZebra1, numPulsesZebra2);
				return numPulsesZebra1 + numPulsesZebra2;
			} catch (Exception e) {
				throw new DeviceException("Problem getting number of captured pulses from zebra(s)", e);
			}
		}
		return 0;
	}

	/**
	 *
	 * @param detector
	 * @return Number of scaler frames available on Tfg
	 * @throws DeviceException
	 */
	private int getNumTfgScalerFrames(BufferedScaler detector) throws DeviceException {
		// For Tfg scalers, convert to absolute frame number in whole experiment if using cycles.
		// (scaler readout will convert back to 'frame within cycle' as necessary)
		int numFramesAvailable = detector.getNumberFrames();
		if (detector.getNumCycles() > 1) {
			int currentCycle = detector.getCurrentCycle(); // cycle counting starts from 0
			int readoutsPerCycle = detector.getContinuousParameters().getNumberDataPoints();
			if (currentCycle > 0) {
				numFramesAvailable += readoutsPerCycle * currentCycle;
			}
		}
		return numFramesAvailable;
	}

	/**
	 *
	 * @param detector
	 * @return Number of frames of Hdf data available from Xspress3 (based on frame ounter PV, or number of frames in hdf file if xspress3FileReader is set).
	 * @throws DeviceException
	 * @throws ScanFileHolderException
	 * @throws NexusException
	 */
	private int getNumXspress3Frames(Xspress3BufferedDetector detector) throws DeviceException, ScanFileHolderException, NexusException {
		int numFramesAvailable = detector.getController().getTotalHDFFramesAvailable();
		if (xspress3FileReader != null) {
			if (xspress3FileReader.getFilename().isEmpty()) {
				String hdfFilename = detector.getController().getFullFileName();
				xspress3FileReader.openFile(hdfFilename);
			}
			numFramesAvailable = xspress3FileReader.getNumAvailableFrames();
		}
		return numFramesAvailable;
	}

	/**
	 * @return Maximum available frame that can be read from all detectors (BufferedScaler and Xspress3Detector)
	 * @throws DeviceException
	 * @throws ScanFileHolderException
	 * @throws NexusException
	 */
	private int getNumAvailableFrames() throws DeviceException, NexusException, ScanFileHolderException {
		int minNumFrames = getNumCapturedZebraPulses();
		logger.debug("Number of frames of data available on zebra(s) : {}", minNumFrames);
		for(BufferedDetector detector : getScanDetectors()){
			int numFramesAvailable = detector.getNumberFrames();
			if (detector instanceof BufferedScaler) {
				numFramesAvailable = getNumTfgScalerFrames((BufferedScaler) detector);
			} else if (detector instanceof Xspress3BufferedDetector) {
				numFramesAvailable = getNumXspress3Frames((Xspress3BufferedDetector) detector);
			}

			logger.debug("Number of frames of data available for {} : {}", detector.getName(), numFramesAvailable);
			minNumFrames = Math.min(minNumFrames,  numFramesAvailable);
		}
		logger.debug("Number of frames of data available to readout : {}", minNumFrames);
		return minNumFrames;
	}

	/**
	 * Read out frames from scalers for one spectrum of data and write the new data into the Nexus file.
	 * The new data is also send to the GUI progress updater.
	 * This function should only be called after checks to ensure the required frames of data are available.
	 * @param detector
	 * @throws Exception
	 */
	private void collectData(BufferedDetector[] detectors) throws Exception {

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
		int totalNumFramesAvailable = getNumAvailableFrames();
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

		numPoints = getTotalNumSpectra();

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
		Xspress3BufferedDetector xspress3Detector = getXspress3Detector();
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

	public void setUseAreaDetector(boolean useAreaDetector) {
		this.useAreaDetector = useAreaDetector;
	}

	public boolean getUseAreaDetector() {
		return useAreaDetector;
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

	private void moveShutter(String position) throws DeviceException {
		if (shutter.isPresent()) {
			logger.debug("Moving {} to {}", shutter.get().getName(), position);
			InterfaceProvider.getTerminalPrinter().print("Moving "+shutter.get().getName()+" to '"+position+"' position ");
			shutter.get().moveTo(position);
			logger.debug("Shutter move finished");
		}
	}
}
