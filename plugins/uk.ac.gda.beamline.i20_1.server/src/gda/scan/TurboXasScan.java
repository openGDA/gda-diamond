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

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.dawnsci.analysis.api.io.ScanFileHolderException;
import org.eclipse.dawnsci.hdf5.nexus.NexusFileHDF5;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.dawnsci.nexus.NexusFile;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DatasetUtils;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.january.dataset.ILazyDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.data.metadata.NXMetaDataProvider;
import gda.data.nexus.extractor.NexusGroupData;
import gda.data.nexus.tree.INexusTree;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.data.scan.datawriter.NexusDataWriter;
import gda.data.scan.datawriter.XasNexusDataWriter;
import gda.data.swmr.SwmrFileReader;
import gda.device.ContinuousParameters;
import gda.device.DeviceException;
import gda.device.detector.BufferedDetector;
import gda.device.detector.DummyNXDetector;
import gda.device.detector.NXDetectorData;
import gda.device.detector.countertimer.BufferedScaler;
import gda.device.detector.countertimer.TfgScalerWithLogValues;
import gda.device.scannable.ContinuouslyScannable;
import gda.device.scannable.ScannableUtils;
import gda.device.scannable.TurboXasScannable;
import gda.device.zebra.controller.Zebra;
import gda.factory.FactoryException;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gov.aps.jca.CAException;
import uk.ac.gda.devices.detector.xspress3.TRIGGER_MODE;
import uk.ac.gda.devices.detector.xspress3.Xspress3BufferedDetector;
import uk.ac.gda.devices.detector.xspress3.Xspress3Controller;
import uk.ac.gda.devices.detector.xspress3.controllerimpl.EpicsXspress3Controller;

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
	private static final Logger logger = LoggerFactory.getLogger(TurboXasScan.class);
	private TurboXasMotorParameters turboXasMotorParams;
	private boolean useAreaDetector = false;
	private boolean doTrajectoryScan = false;
	private boolean useXspress3SwmrReadout = true;

	private Map<String, String> xspressAttributeMap = new HashMap<String, String>();
	private String pathToAttributeData = "/entry/instrument/NDAttributes/";
	private SwmrFileReader xspress3FileReader;

	private int numReadoutsPerSpectrum;
	private int numSpectraPerCycle;
	private int numReadoutsPerCycle;
	private int numCycles;
	private int maxNumScalerFramesPerCycle = 250000;

	private volatile int lastFrameRead;

	private PlotUpdater plotUpdater = new PlotUpdater();

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
	}

	@Override
	public void doCollection() throws Exception {

		XasNexusDataWriter dataWriter = new XasNexusDataWriter();
		setDataWriter(dataWriter);

		logger.info("Running scan");

		plotUpdater.setCurrentSpectrumNumber(1);
		plotUpdater.setCurrentGroupNumber(1);
		plotUpdater.setEnergyAxisName(ENERGY_COLUMN_NAME);
		plotUpdater.setPositionAxisName(POSITION_COLUMN_NAME);

		plotUpdater.clearDatanamesToIgnore();
		plotUpdater.addDatanameToIgnore(ENERGY_COLUMN_NAME);
		plotUpdater.addDatanameToIgnore(POSITION_COLUMN_NAME);
		plotUpdater.addDatanameToIgnore(TfgScalerWithLogValues.LNITIREF_LABEL);
		plotUpdater.addDatanameToIgnore("Iref");

		ContinuouslyScannable scanAxis = getScanAxis();
		if (scanAxis instanceof TurboXasScannable && turboXasMotorParams != null) {
			if (doTrajectoryScan) {
				collectMultipleSpectraTrajectoryScan();
			} else {
				collectMultipleSpectra();
			}
			addTimeAxis();
		} else {
			logger.info("Setting up scan using ContinuousParameters");
			lastFrameRead = 0;
			numReadoutsPerSpectrum = getTotalNumberOfPoints();
			prepareDetectors(numReadoutsPerSpectrum, 1);
			collectOneSpectrum(true);
		}

		logger.info("Scan finished");
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
		runnable.setDetector(getScanDetectors()[0]);
		runnable.setTimingGroups(turboXasMotorParams.getScanParameters().getTimingGroups());
		return runnable;
	}

	/**
	 * Collect multiple spectra by performing motor moves for several timing groups.
	 * @throws Exception
	 */
	private void collectMultipleSpectraTrajectoryScan() throws Exception {
		TurboXasScannable turboXasScannable = (TurboXasScannable) getScanAxis();
		logger.info("Setting up scan using TurboXasScannable ({})", turboXasScannable.getName());

		addMetaDataAtScanStart();

		// Set area detector flag (for timing, encoder position information)
		turboXasScannable.setUseAreaDetector(useAreaDetector);
		turboXasScannable.setMotorParameters(turboXasMotorParams);
		// Calculate motor parameters for first timing group (i.e. positions and num readouts for spectrum)
		turboXasMotorParams.setMotorParametersForTimingGroup(0);
		// Move motor to near scan start position to avoid following error, if motor is a long way from where it needs to be...
		// turboXasScannable.moveTo(turboXasMotorParams.getScanStartPosition());

		// Configure the zebra
		turboXasScannable.configureZebra(); // would normally get called in ContinuousScan.prepareForContinuousMove()
		// Arm zebra
		Zebra zebra = turboXasScannable.getZebraDevice();
		zebra.reset();
		zebra.pcArm();

		// Prepare detectors (BufferedScalers) for readout of all spectra
		prepareDetectors();

		// Create the trajectory scan profile
		TrajectoryScanPreparer trajScanPreparer = turboXasScannable.getTrajectoryScanPreparer();
		trajScanPreparer.setDefaults();
		trajScanPreparer.clearTrajectoryLists();
		trajScanPreparer.addPointsForTimingGroups(turboXasMotorParams);
		trajScanPreparer.sendProfileValues();
		trajScanPreparer.setBuildProfile();
		if (trajScanPreparer.getBuildProfileStatus().equals("Failure")){
			throw new Exception("Failure when building trajectory scan profile - check Epics EDM screen");
		}

		InterfaceProvider.getTerminalPrinter().print("Running TurboXas scan using trajectory scan...");

		trajScanPreparer.setExecuteProfile();
		if (trajScanPreparer.getExecuteProfileStatus().equals("Failure")){
			throw new Exception("Failure when executing trajectory scan - check Epics EDM screen.");
		}

		// Wait until some points have been captured by zebra (i.e. motor has started moving)
		while(zebra.getPCNumberOfPointsCaptured()==0) {
			logger.info("Waiting for points to be captured by Zebra before starting data collection");
			Thread.sleep(500);
		}

		// Start detector readout thread
		DetectorReadoutRunnable detectorReadoutRunnable = getDetectorReadoutRunnable();
		Thread detectorReadoutThread = new Thread(detectorReadoutRunnable);
		detectorReadoutThread.start();

		// Wait while trajectory scan runs...
		while(trajScanPreparer.getExecuteProfileState()=="Executing") {
			Thread.sleep(500);
		}

		// Output some info on trajectory scan final execution state
		logger.info("Trajectory scan finished. Execute state = {}, percent complete = {}", trajScanPreparer.getExecuteProfileState(), trajScanPreparer.getTscanPercent());


		// Wait at end for data collection thread to finish
		waitForReadoutToFinish(detectorReadoutRunnable, 600.0);

		// flags back to default values
		turboXasScannable.atScanEnd();
 	}

	/**
	 * Add time axis to Nexus file. This is the start time of each spectrum relative the first spectrum,
	 * calculated using 'time between spectra' and 'frame time'.
	 * @throws Exception
	 */
	private void addTimeAxis() throws Exception {
		NexusFile file = null;
		try {
			String filename = getDataWriter().getCurrentFileName();
			file = NexusFileHDF5.openNexusFile(filename);
			// Read 'frame_time' and 'time between spectra' datasets from Nexus file
			String detectorEntry = "/entry1/"+getScanDetectors()[0].getName()+"/";
			String frameTimeName = getFrameTimeFieldName();

			ILazyDataset times = file.getData(detectorEntry+frameTimeName).getDataset();
			ILazyDataset timeBetweenSpectra = file.getData(detectorEntry+TIME_BETWEEN_SPECTRA_COLUMN_NAME).getDataset();
			DoubleDataset timeBetweenSpectraVals = (DoubleDataset) timeBetweenSpectra.getSlice(null, null, null).squeeze();

			// Create dataset to store start time of each spectrum
			int numSpectra = times.getShape()[0];
			int numReadouts = times.getShape()[1];
			Dataset absoluteTime = DatasetFactory.zeros(DoubleDataset.class, numSpectra);
			// First spectrum starts at t=0
			double timeAtSpectrumStart = 0;
			absoluteTime.set(timeAtSpectrumStart, 0);

			// Calculate start time for each spectrum
			for (int i = 0; i < numSpectra - 1; i++) {
				// Take slice along time for current spectrum, find sum and add to time-between-spectra
				Dataset row = DatasetUtils.convertToDataset(times.getSlice(new int[] { i, 0 }, new int[] { i + 1, numReadouts }, null));
				double rowSum = ((Number) row.sum()).doubleValue();
				double timeForSpectra = rowSum + timeBetweenSpectraVals.get(i);
				timeAtSpectrumStart += timeForSpectra;
				absoluteTime.set(timeAtSpectrumStart, i + 1);
			}
			file.createData(detectorEntry, TIME_COLUMN_NAME, absoluteTime, true);
		} finally {
			if (file != null) {
				file.close();
			}
		}
	}

	@Override
	protected void endScan() throws DeviceException, InterruptedException {
		super.endScan();
		for (BufferedDetector detector : getScanDetectors()) {
			detector.stop();
		}
	}

	/**
	 * Collect multiple spectra by performing motor moves for several timing groups.
	 * @throws Exception
	 */
	private void collectMultipleSpectra() throws Exception {
		TurboXasScannable turboXasScannable = (TurboXasScannable) getScanAxis();
		logger.info("Setting up scan using TurboXasScannable ({})", turboXasScannable.getName());

		addMetaDataAtScanStart();

		// Set area detector flag (for timing, encoder position information)
		turboXasScannable.setUseAreaDetector(useAreaDetector);
		turboXasScannable.setMotorParameters(turboXasMotorParams);
		// Calculate motor parameters for first timing group
		turboXasMotorParams.setMotorParametersForTimingGroup(0);

		// Prepare detectors (BufferedScalers) for readout of all spectra
		prepareDetectors();

		// Make new instance of detector readout runnable to collect detector data.
		DetectorReadoutRunnable detectorReadoutRunnable = getDetectorReadoutRunnable();

		// Make detector readout thread (start it after first spectrum is available)
		Thread detectorReadoutThread = new Thread(detectorReadoutRunnable);

		InterfaceProvider.getTerminalPrinter().print("Running TurboXas scan...");

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
					detectorReadoutThread.start();
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

	private void waitForReadoutToFinish(DetectorReadoutRunnable detectorReadoutRunnable, double maxWaitTimeSecs) throws ScanFileHolderException, DeviceException, InterruptedException {
		long pollIntervalMillis = 1000;
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
				xspress3BufferedDetector.getController().setSavingFiles(false);
			}

			logger.info("Waiting for detector collection thread to finish...");
			while (!detectorReadoutRunnable.collectionFinished() && timeWaited<maxWaitTimeSecs) {
				Thread.sleep(pollIntervalMillis);
				timeWaited += pollIntervalMillis * 0.001;
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
				prepareXSpress3(numSpectra*numReadoutsPerSpectra);
			}
		}
	}

	private Xspress3BufferedDetector xspress3BufferedDetector;

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
	public void prepareXSpress3(int numReadouts) throws Exception{
		if (xspress3BufferedDetector != null) {
			Xspress3Controller controller = xspress3BufferedDetector.getController();

			controller.setSavingFiles(false);
			controller.doStop();
			controller.doReset();
			controller.setNumFramesToAcquire(numReadouts);
			controller.setHDFNumFramesToAcquire(numReadouts);
			controller.setTriggerMode(TRIGGER_MODE.TTl_Veto_Only);

			// controller.doReset();
			controller.setNextFileNumber(0);
			controller.setSavingFiles(true);
			controller.doStart();

			// create reader for loading data from Swmr file - only if using real hardware
			if (useXspress3SwmrReadout && controller instanceof EpicsXspress3Controller) {
				xspress3FileReader = new SwmrFileReader();
				xspress3FileReader.openFile(controller.getFullFileName());
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

	// Dataset names used in NeXus file
	private static final String MOTOR_PARAMS_COLUMN_NAME = "motor_parameters";
	private static final String TIME_COLUMN_NAME = "time";
	private static final String TIME_BETWEEN_SPECTRA_COLUMN_NAME = "time_between_spectra";
	private static final String ENERGY_COLUMN_NAME = "energy";
	private static final String POSITION_COLUMN_NAME = "position";
	private static final String FRAME_INDEX = "frame_index";
	private static final String ENERGY_UNITS = "eV";
	private static final String TIME_UNITS = "seconds";
	private static final String COUNT_UNITS = "counts";
	private static final String INDEX_UNITS = "index";
	private static final String POSITION_UNITS = "cm";
	private static final String I0_LABEL = "I0";
	private Dataset i0Data;

	private String getFrameTimeFieldName() {
		return getScanDetectors()[0].getExtraNames()[0];
	}

	private NXDetectorData createAxisData(BufferedDetector detector, int lowFrame, int highFrame) throws DeviceException {
		int numFramesRead = highFrame - lowFrame;
		if (numFramesRead<numReadoutsPerSpectrum) {
			logger.info("Expected {} frames for spectrum, {} frames available - padding with zeros...", numReadoutsPerSpectrum, numFramesRead );
		}

		// Number of frames to be stored in Nexus file
		// Don't record last frame of data (this corresponds to the long timeframe when
		// the motor moves back to start position)
		int numFramesToStore = numFramesRead-1;

		// Setup arrays of frame index and energy of each frame
		int[] frameIndex = new int[numFramesToStore];
		double[] energy = new double[numFramesToStore];
		ContinuouslyScannable scanAxis = getScanAxis();
		for(int i=0; i<numFramesToStore; i++) {
			frameIndex[i] = i;
			energy[i] = scanAxis.calculateEnergy(i);
		}

		// Add frame and energy axis data
		NXDetectorData frame = new NXDetectorData(detector);
		frame.addAxis(detector.getName(), ENERGY_COLUMN_NAME, new NexusGroupData(energy), 1, 1, ENERGY_UNITS, false);
		frame.addAxis(detector.getName(), FRAME_INDEX, new NexusGroupData(frameIndex), 2, 1, INDEX_UNITS, false);

		// Add position axis data if using TurboXasScannable
		if (scanAxis instanceof TurboXasScannable) {
			TurboXasScannable txasScannable = (TurboXasScannable)scanAxis;
			double[] position = new double[numFramesToStore];
			for(int i=0; i<numFramesToStore; i++) {
				position[i] = txasScannable.calculatePosition(i);
			}
			frame.addAxis(detector.getName(), POSITION_COLUMN_NAME, new NexusGroupData(position), 3, 1, POSITION_UNITS, false);
		}
		return frame;
	}

	public void addXspressDatasetToRecord(String label, String attribute) {
		xspressAttributeMap.put(label, attribute);
	}

	private void setupXspressAttributeMap(Xspress3BufferedDetector detector) {
		for(int channel=0; channel<detector.getNumberOfElements(); channel++) {
			xspressAttributeMap.put(String.format("FF_%d", channel+1), String.format("Chan%dSca%d", channel+1, 5));
		}
	}

	/**
	 * Create NXDetector data from XSpress3 detector; Readout of detector data occurs in two ways :
	 * <li> In the normal way. i.e. by reading arrays of scaler data from PVs.
	 * <li> By reading data from the XSpress3 hdf (SWMR) file (using {@link #xspress3FileReader}).
	 * When using this method, checks should be carried out before calling this function to ensure lowframe and highframe are within current dataset limits.
	 * e.g. by calling {@link SwmrFileReader#getNumAvailableFrames()}.
	 * @param detector
	 * @param lowFrame
	 * @param highFrame
	 * @return
	 * @throws DeviceException
	 * @throws ScanFileHolderException
	 */
	private NXDetectorData createNXDetectorData(Xspress3BufferedDetector detector, int lowFrame, int highFrame) throws DeviceException, ScanFileHolderException {

		NXDetectorData frame = createAxisData(detector, lowFrame, highFrame);

		INexusTree detTree = frame.getDetTree(detector.getName());

		Dataset ffSum = null;

		if (xspress3FileReader!=null) {
			// Add detector data from xspress3 hdf file
			int[] start = new int[] { lowFrame };
			int[] shape = new int[] { highFrame - lowFrame - 1 };
			int[] step = new int[shape.length];
			Arrays.fill(step, 1);
			try {
				logger.info("Adding data from hdf file {}", xspress3FileReader.getFilename());
				ffSum = DatasetFactory.zeros(highFrame - lowFrame -1);
				ffSum.setName("FF_sum");
				for (Dataset dataset : xspress3FileReader.readDatasets(start, shape, step)) {
					NXDetectorData.addData(detTree, dataset.getName(), NexusGroupData.createFromDataset(dataset),
							"counts", 1);
					if (dataset.getName().startsWith("FF")) {
						ffSum.iadd(dataset);
					}
				}
				NXDetectorData.addData(detTree, ffSum.getName(), NexusGroupData.createFromDataset(ffSum), "counts", 1);
			} catch (NexusException e) {
				logger.error("Problem reading data from hdf file", e);
			}
		} else {
			//Add detector data from xspress3 scaler readout
			NXDetectorData[] detData = detector.readFrames(lowFrame, highFrame-1);
			String[] names = detData[0].getExtraNames();
			int numFrames = detData.length;
			for(int i=0; i<names.length; i++) {
				Dataset dataset = DatasetFactory.zeros(DoubleDataset.class, numFrames);
				dataset.setName(names[i]);
				for(int frameIndex = 0; frameIndex<numFrames; frameIndex++) {
					double val = detData[frameIndex].getDoubleVals()[i];
					dataset.set(val, frameIndex);
				}
				NXDetectorData.addData(detTree, dataset.getName(), NexusGroupData.createFromDataset(dataset), "counts", 1);

				// last dataset from readFrames is total FF (i.e. sum over all detector elements)
				if (i==names.length-1) {
					ffSum = dataset;
				}
			}
		}

		// Add ff/I0 values
		if (ffSum!=null && i0Data!=null) {
			int numI0Values = i0Data.getShape()[0];
			Dataset ffSumSlice = ffSum.getSlice(null, new int[]{numI0Values}, null).squeeze();
			Dataset ffi0 = ffSumSlice.idivide(i0Data);
			// Use u2215 (division slash, ∕) rather than solidus (/), so ratio is displayed nicely and Nexus writer doesn't get confused
			ffi0.setName("FF_sum\u2215I0");
			NXDetectorData.addData(detTree, ffi0.getName(), NexusGroupData.createFromDataset(ffi0), "counts", 1);
		}
		return frame;
	}

	/**
	 * Create NXDetector data from BufferedScaler (from Tfg scaler)
	 * @param detector
	 * @param lowFrame
	 * @param highFrame
	 * @return
	 * @throws DeviceException
	 */
	private NXDetectorData createNXDetectorData(BufferedScaler detector, int lowFrame, int highFrame) throws DeviceException {

		int numFramesRead = highFrame - lowFrame;
		int numFrames = numReadoutsPerSpectrum;
//
//		// Number of frames to be stored in Nexus file
//		// Don't record last frame of data (this corresponds to the long timeframe when
//		// the motor moves back to start position)
		int numFramesToStore = numFramesRead-1;

		NXDetectorData frame = createAxisData(detector, lowFrame, highFrame);

		// Frame data from detector
		Object[] detectorFrameData = detector.readFrames(lowFrame, highFrame);
		double[][] frameDataArray = (double[][]) detectorFrameData;

		// Names of data fields on the detector
		String[] fieldNames = detector.getExtraNames();

		String frameTimeName = getFrameTimeFieldName();

		// Copy data for each field and add to detector data
		INexusTree detTree = frame.getDetTree(detector.getName());
		int maxField = Math.min(fieldNames.length, frameDataArray[0].length);
		i0Data = null;
		for(int fieldIndex=0; fieldIndex<maxField; fieldIndex++) {
			double[] detData = new double[numFramesToStore];
			for(int i=0; i<numFramesToStore; i++) {
				detData[i] = frameDataArray[i][fieldIndex];
			}
			String fieldName = fieldNames[fieldIndex];
			String units = fieldName.equals(frameTimeName) ? TIME_UNITS : COUNT_UNITS;
			NXDetectorData.addData(detTree, fieldName, new NexusGroupData(detData), units, 1);

			// Save the I0 dataset, so can calculate (and plot) FF/I0 after xspress3 data has been collected
			if (fieldName.equals(I0_LABEL)){
				i0Data = DatasetFactory.createFromObject(detData);
			}
		}

		// Store the length of last timeframe as separate dataset ('time between spectra')
		int timeFieldIndex = Arrays.asList(fieldNames).indexOf(frameTimeName);
		if (timeFieldIndex>-1) {
			double[] timeBetweenSpectra = new double[] {frameDataArray[numFrames-1][timeFieldIndex]};
			NXDetectorData.addData(detTree, TIME_BETWEEN_SPECTRA_COLUMN_NAME, new NexusGroupData(timeBetweenSpectra), TIME_UNITS, 1);
		}

		if (turboXasMotorParams != null) {
			NXDetectorData.addData(detTree, MOTOR_PARAMS_COLUMN_NAME, new NexusGroupData(turboXasMotorParams.toXML()), "", 1);
		}
		return frame;
	}

	public NexusTreeProvider[] readFrames(BufferedDetector detector, int lowFrame, int highFrame) throws Exception, DeviceException {
		NexusTreeProvider[] results = new NexusTreeProvider[1];
		if (detector instanceof BufferedScaler) {
			results[0] = createNXDetectorData( (BufferedScaler)detector, lowFrame, highFrame);
		} else if (detector instanceof Xspress3BufferedDetector) {
			results[0] = createNXDetectorData( (Xspress3BufferedDetector)detector, lowFrame, highFrame);
		}
		return results;
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
		logger.info("reading data from detectors from frames {} to {}", lowFrame, highFrame);

		detData[0] = readFrames(detector, lowFrame, highFrame);
		clearFrames(detector, lowFrame, highFrame-1);

		logger.info("data read successfully");
		return detData;
	}


	/**
	 * Runnable that can be used to collect detector data in a background thread.
	 * It monitors the number of frames of detector data available, and when enough frames
	 * for a new spectrum are available, it collects the spectrum data and writes it to the Nexus file
	 * using {@link #collectData(BufferedDetector[])}.
	 */
	private class DetectorReadoutRunnable implements Runnable {

		private int numFramesPerSpectrum;
		private int numSpectraCollected;
		private int pollIntervalMillis;
		private int totalNumSpectraToCollect;

		private BufferedDetector detector;
		private int currentTimingGroupIndex=0;
		private int numSpectraCollectedForGroup=0;
		private List<TurboSlitTimingGroup> timingGroups;

		private boolean runMethodFinished = false;

		public DetectorReadoutRunnable() {
			timingGroups = new ArrayList<TurboSlitTimingGroup>();
			pollIntervalMillis=500;
		}

		@Override
		public void run() {
			currentTimingGroupIndex=0;
			numSpectraCollectedForGroup=0;
			numSpectraCollected=0;

			logger.debug("ReadoutThread started");
			try {
				while (numSpectraCollected < totalNumSpectraToCollect) {
					int numAvailableFrames = getNumAvailableFrames();

					// Break out of while loop if frames get cleared (e.g. due to 'stop scan' button being pressed)
					if (numAvailableFrames==0 && !detector.isBusy()) {
						logger.debug("ReadoutThread : exiting (no frames available and detector not busy)");
						break;
					}

					// Last spectrum collected was final one in previous Tfg cycle - set last frame read to start of current cycle
					if (lastFrameRead==numReadoutsPerCycle) {
						lastFrameRead=0;
					}

					int numNewFrames = numAvailableFrames-lastFrameRead;

					// Currently in next Tfg cycle (and numNewFrames=0); need to read last spectrum of previous cycle
					if (numCycles>1 && lastFrameRead == numReadoutsPerCycle-numReadoutsPerSpectrum) {
						// logger.debug("ReadoutThread : Read last spectrum of cycle");
						numNewFrames = numFramesPerSpectrum;
					}

					logger.debug("ReadoutThread : {} frames of data available, {} new frames, last frame read = {}", numAvailableFrames, numNewFrames, lastFrameRead);

					// Last spectrum has 1 less frame than the others (due to edge counting)
					if (numSpectraCollected==totalNumSpectraToCollect-1) {
						numNewFrames++;
					}

					if (numNewFrames>=numFramesPerSpectrum) {

						// Update timing group number and spectrum number for spectrum being read out
						numSpectraCollectedForGroup++;
						if (currentTimingGroupIndex<timingGroups.size() &&
							numSpectraCollectedForGroup>timingGroups.get(currentTimingGroupIndex).getNumSpectra()) {

							currentTimingGroupIndex++;
							numSpectraCollectedForGroup=1;
						}
						plotUpdater.setCurrentGroupNumber(currentTimingGroupIndex+1);
						plotUpdater.setCurrentSpectrumNumber(numSpectraCollectedForGroup);

						String msg = "\tTiming group "+(currentTimingGroupIndex+1)+" : spectrum "+(numSpectraCollectedForGroup)+" of "+timingGroups.get(currentTimingGroupIndex).getNumSpectra();

						logger.debug("ReadoutThread : collecting data {}", msg);
						InterfaceProvider.getTerminalPrinter().print(msg);

						collectData(getScanDetectors());
						numSpectraCollected++;
					}
					Thread.currentThread().sleep(pollIntervalMillis);
				}
			} catch (Exception e) {
				logger.error("ReadoutThread encountered an error during data collection.", e);
			} finally {
				logger.debug("ReadoutThread finished.");
				runMethodFinished = true;
			}
		}

		public int getNumSpectraCollected() {
			return numSpectraCollected;
		}
		public void setTotalNumSpectraToCollect(int totalNumSpectraToCollect) {
			this.totalNumSpectraToCollect = totalNumSpectraToCollect;
		}
		public void setNumFramesPerSpectrum(int numFramesPerSpectrum) {
			this.numFramesPerSpectrum = numFramesPerSpectrum;
		}
		public boolean collectionFinished() {
			return runMethodFinished;
		}
		public void setDetector(BufferedDetector detector) {
			this.detector = detector;
		}
		public void setTimingGroups(final List<TurboSlitTimingGroup> timingGroups) {
			this.timingGroups = timingGroups;
		}
	}

	/**
	 * @return Maximum available frame that can be read from all detectors (BufferedScaler and Xspress3Detector)
	 * @throws DeviceException
	 * @throws ScanFileHolderException
	 * @throws NexusException
	 */
	private int getNumAvailableFrames() throws DeviceException, NexusException, ScanFileHolderException {
		int minNumFrames = -1;
		for(BufferedDetector detector : getScanDetectors()){
			int numFramesAvailable = detector.getNumberFrames();
			if (minNumFrames == -1) {
				minNumFrames = numFramesAvailable;
			}
			if (detector instanceof Xspress3BufferedDetector) {
				numFramesAvailable = ((Xspress3BufferedDetector) detector).getController().getTotalHDFFramesAvailable();
				if (xspress3FileReader != null) {
					numFramesAvailable = xspress3FileReader.getNumAvailableFrames();
				}
			}
			logger.debug("Number of frames of data available for {} : {}", detector.getName(), numFramesAvailable);
			minNumFrames = Math.min(minNumFrames,  numFramesAvailable);
		}
		return minNumFrames;
	}

	/**
	 * Read out frames from scalers for one spectrum of data and write the new data into the Nexus file.
	 * The new data is also send to the GUI progress updater.
	 * @param detector
	 * @throws Exception
	 */
	private void collectData(BufferedDetector[] detectors) throws Exception {

		int totalNumFramesAvailable = getNumAvailableFrames();

		int lastFrameToRead = lastFrameRead + numReadoutsPerSpectrum;
		if (lastFrameToRead > totalNumFramesAvailable) {
			logger.warn("Possible problem reading out data : Last frame of scaler data is {}, but need to read up to {}", totalNumFramesAvailable, lastFrameToRead);
		}

		// Create scan data point
		ScanDataPoint thisPoint = new ScanDataPoint();
		thisPoint.setUniqueName(getName());
		thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());
		thisPoint.setStepIds(getStepIds());
		thisPoint.setScanPlotSettings(getScanPlotSettings());

		int[] dims = getDimensions();
		thisPoint.setScanDimensions(dims);

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

	private void addMetaDataAtScanStart() {
		String metashopName = LocalProperties.get(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME,"metashop");
		NXMetaDataProvider metashop = Finder.getInstance().find(metashopName);
		if (metashop != null) {
			metashop.clear();
			metashop.add("TurboXasParameters", turboXasMotorParams.getScanParameters().toXML() );
		}
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

	/** Number of spectra per Tfg cycle (calculated by {@link #prepareDetectors(int, int)}) **/
	public int getNumSpectraPerCycle() {
		return numSpectraPerCycle;
	}

	/** Number of spectra per Tfg cycle (calculated by {@link #prepareDetectors(int, int)}) **/
	public int getNumReadoutsPerCycle() {
		return numReadoutsPerCycle;
	}
	/** Number of Tfg cycles needed to record all spectra (calculated by {@link #prepareDetectors(int, int)}) **/
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
}
