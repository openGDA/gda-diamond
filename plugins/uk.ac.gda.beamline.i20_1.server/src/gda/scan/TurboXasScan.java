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
import java.util.List;

import org.eclipse.dawnsci.hdf.object.H5Utils;
import org.eclipse.dawnsci.hdf.object.IHierarchicalDataFile;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.data.metadata.NXMetaDataProvider;
import gda.data.nexus.extractor.NexusExtractor;
import gda.data.nexus.extractor.NexusGroupData;
import gda.data.nexus.tree.INexusTree;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.data.scan.datawriter.NexusDataWriter;
import gda.device.ContinuousParameters;
import gda.device.DeviceException;
import gda.device.detector.BufferedDetector;
import gda.device.detector.DummyNXDetector;
import gda.device.detector.NXDetectorData;
import gda.device.detector.countertimer.BufferedScaler;
import gda.device.scannable.ContinuouslyScannable;
import gda.device.scannable.ScannableUtils;
import gda.device.scannable.TurboXasScannable;
import gda.device.zebra.controller.Zebra;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.scriptcontroller.ScriptControllerBase;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.EdeExperimentProgressBean;
import gda.scan.ede.EdeExperimentProgressBean.ExperimentCollectionType;
import gda.scan.ede.EdeScanProgressBean;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.position.EdePositionType;

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
	private int numReadoutsPerSpectrum;

	public TurboXasScan(ContinuouslyScannable energyScannable, Double start, Double stop, Integer numberPoints,
			Double time, BufferedDetector[] detectors) {
		super(energyScannable, start, stop, numberPoints, time, detectors);
	}

	public TurboXasScan(ContinuouslyScannable energyScannable, TurboXasMotorParameters motorParams, BufferedDetector[] detectors) {
		// don't set scan time here, there may be multiple timing groups...
		super(energyScannable, motorParams.getScanStartPosition(), motorParams.getScanEndPosition(),
				motorParams.getNumReadoutsForScan(), 0.0, detectors);
		turboXasMotorParams = motorParams;
	}

	@Override
	public void doCollection() throws Exception {
		logger.info("Running scan");

		plotUpdater.setCurrentSpectrumNumber(1);
		plotUpdater.setCurrentGroupNumber(1);
		plotUpdater.setEnergyAxisName(ENERGY_COLUMN_NAME);
		detectorReadoutRunnable = null;

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
			collectOneSpectrum();
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
		// Move motor to scan start position to avoid following error, if motor is a long way from where it needs to be...
		turboXasScannable.moveTo(turboXasMotorParams.getScanStartPosition());

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
		trajScanPreparer.setExecuteProfile();

		// Wait until some points have been captured by zebra (i.e. motor has started moving)
		while(zebra.getPCNumberOfPointsCaptured()==0) {
			logger.info("Waiting for points to be captured by Zebra before starting data collection");
			Thread.sleep(500);
		}

		// Start detector readout thread
		detectorReadoutRunnable = getDetectorReadoutRunnable();
		Thread detectorReadoutThread = new Thread(detectorReadoutRunnable);
		detectorReadoutThread.start();

		InterfaceProvider.getTerminalPrinter().print("Running TurboXas scan using trajectory scan...");

		// Wait at end for data collection thread to finish
		int maxTimeoutMillis=5000;
		while (!detectorReadoutRunnable.collectionFinished()) {
			logger.info("Waiting {} ms for detector collection thread to finish...", maxTimeoutMillis);
			Thread.sleep(maxTimeoutMillis);
		}
		// flags back to default values
		turboXasScannable.atScanEnd();
 	}

	/**
	 * Add time axis to Nexus file. This is the start time of each spectrum relative the first spectrum,
	 * calculated using 'time between spectra' and 'frame time'.
	 * @throws Exception
	 */
	private void addTimeAxis() throws Exception {
		IHierarchicalDataFile file = null;
		try {
			file = org.eclipse.dawnsci.hdf.object.HierarchicalDataFactory.getWriter(getDataWriter().getCurrentFileName());

			// Read 'frame_time' and 'time between spectra' datasets from Nexus file
			String detectorEntry = "/entry1/"+getScanDetectors()[0].getName()+"/";
			String frameTimeName = getFrameTimeFieldName();
			Dataset times = H5Utils.getSet(file, detectorEntry + frameTimeName);
			Dataset timeBetweenSpectra = H5Utils.getSet(file, detectorEntry + TIME_BETWEEN_SPECTRA_COLUMN_NAME);

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
				Dataset row = times.getSlice(new int[] { i, 0 }, new int[] { i + 1, numReadouts }, null);
				double rowSum = new Double((Double) row.sum());
				double timeForSpectra = rowSum + timeBetweenSpectra.getDouble(i);
				timeAtSpectrumStart += timeForSpectra;
				absoluteTime.set(timeAtSpectrumStart, i + 1);
			}
			file.createDataset(TIME_COLUMN_NAME, absoluteTime, detectorEntry);
		} finally {
			file.close();
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
		detectorReadoutRunnable = getDetectorReadoutRunnable();

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

				collectOneSpectrum();

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
		int maxTimeoutMillis=5000;
		while (!detectorReadoutRunnable.collectionFinished()) {
			logger.info("Waiting {} ms for detector collection thread to finish...", maxTimeoutMillis);
			Thread.sleep(maxTimeoutMillis);
		}
		// flags back to default values
		turboXasScannable.atScanEnd();
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

	private int numSpectraPerCycle;
	private int numReadoutsPerCycle;
	private int numCycles;
	private int maxNumScalerFramesPerCycle = 250000;

	/**
	 * Prepare detectors (BufferedScalers) for readout of all spectra
	 * Do this once at beginning to avoid overhead of clearing out scaler memory etc for each spectra.
	 *
	 * @throws DeviceException
	 * @throws InterruptedException
	 */
	public void prepareDetectors() throws DeviceException, InterruptedException {
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
	 */
	public void prepareDetectors(int numReadoutsPerSpectra, int numSpectra) throws DeviceException, InterruptedException {
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
	 * @throws Exception
	 */
	public void collectOneSpectrum() throws Exception {
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
		if (detectorReadoutRunnable!=null){
			return;
		}

		BufferedDetector[] scanDetectors = getScanDetectors();
		if (scanDetectors.length > 0) {
			collectData(scanDetectors[0]);
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


	private String getFrameTimeFieldName() {
		return getScanDetectors()[0].getExtraNames()[0];
	}

	private NXDetectorData createNXDetectorData(BufferedDetector detector, int lowFrame, int highFrame) throws DeviceException {

		int numFramesRead = highFrame - lowFrame;
		if (numFramesRead<numReadoutsPerSpectrum) {
			logger.info("Expected {} frames for spectrum, {} frames available - padding with zeros...", numReadoutsPerSpectrum, numFramesRead );
		}

		int numFrames = numReadoutsPerSpectrum;

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

		// Frame data from detector
		Object[] detectorFrameData = detector.readFrames(lowFrame, highFrame);
		double[][] frameDataArray = (double[][]) detectorFrameData;

		// Names of data fields on the detector
		String[] fieldNames = detector.getExtraNames();

		String frameTimeName = getFrameTimeFieldName();

		// Copy data for each field and add to detector data
		INexusTree detTree = frame.getDetTree(detector.getName());
		int maxField = Math.min(fieldNames.length, frameDataArray[0].length);
		for(int fieldIndex=0; fieldIndex<maxField; fieldIndex++) {
			double[] detData = new double[numFramesToStore];
			for(int i=0; i<numFramesToStore; i++) {
				detData[i] = frameDataArray[i][fieldIndex];
			}
			String fieldName = fieldNames[fieldIndex];
			String units = fieldName.equals(frameTimeName) ? TIME_UNITS : COUNT_UNITS;
			NXDetectorData.addData(detTree, fieldName, new NexusGroupData(detData), units, 1);
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
		results[0] = createNXDetectorData(detector, lowFrame, highFrame);
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

	private PlotUpdater plotUpdater = new PlotUpdater();
	private volatile  int lastFrameRead;

	private DetectorReadoutRunnable detectorReadoutRunnable;

	/**
	 * Runnable that can be used to collect detector data in a background thread.
	 * It monitors the number of frames of detector data available, and when enough frames
	 * for a new spectrum are available, it collects the spectrum data and writes it to the Nexus file
	 * using {@link #collectData(BufferedDetector)}
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
					int numAvailableFrames = detector.getNumberFrames();

					// Break out of while loop if frames get cleared (e.g. due to 'stop scan' button being pressed)
					if (numAvailableFrames==0 && !detector.isBusy()) {
						logger.debug("ReadoutThread : exiting (no frames left and detector not busy)");
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

						collectData(detector);
						numSpectraCollected++;
					}
					Thread.currentThread().sleep(pollIntervalMillis);
				}
			} catch (Exception e) {
				logger.error("ReadoutThread encountered an error during data collection.", e);
			} finally {
				logger.debug("ReadoutThread finished.");
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
			return numSpectraCollected == totalNumSpectraToCollect;
		}
		public void setDetector(BufferedDetector detector) {
			this.detector = detector;
		}
		public void setTimingGroups(final List<TurboSlitTimingGroup> timingGroups) {
			this.timingGroups = timingGroups;
		}
	}

	/**
	 * Read out frames from scalers for one spectrum of data and write the new data into the Nexus file.
	 * The new data is also send to the GUI progress updater.
	 * @param detector
	 * @throws Exception
	 */
	private void collectData(BufferedDetector detector) throws Exception {

		// each frame is set of scaler values, corresponding to values for single photon energy/zebra pulse/motor position
		// Readout frames from Scaler memory corresponding to latest spectra.
		int totalNumFramesAvailable = detector.getNumberFrames();

		int lastFrameToRead = lastFrameRead + numReadoutsPerSpectrum;
		if (lastFrameToRead > totalNumFramesAvailable) {
			logger.warn("Possible problem reading out data : Last frame of scaler data is {}, but need to read up to {}", totalNumFramesAvailable, lastFrameToRead);
		}

		Object[][]nxFrameData = readDetector(detector, lastFrameRead, lastFrameToRead);
		lastFrameRead += numReadoutsPerSpectrum;

		// Create scan data point and add detector data.
		ScanDataPoint thisPoint = new ScanDataPoint();
		thisPoint.setUniqueName(getName());
		thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());
		thisPoint.setStepIds(getStepIds());
		thisPoint.setScanPlotSettings(getScanPlotSettings());

		int[] dims = getDimensions();
		thisPoint.setScanDimensions(dims);

		// NeXus writing works using NXDetector, so put scaler data in dummy NX detector...
		DummyNXDetector testDet = new DummyNXDetector(detector.getName(), 1);
		thisPoint.addDetector(testDet);
		thisPoint.addDetectorData(nxFrameData[0][0], ScannableUtils.getExtraNamesFormats(detector));

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

		getDataWriter().addData(thisPoint);
		thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());

		//InterfaceProvider.getJythonServerNotifer().notifyServer(this, thisPoint); // for the CommandQueue

		plotUpdater.updateShowAll(thisPoint);

	}

	private void addMetaDataAtScanStart() {
		String metashopName = LocalProperties.get(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME,"metashop");
		NXMetaDataProvider metashop = Finder.getInstance().find(metashopName);
		if (metashop != null) {
			metashop.clear();
			metashop.add("TurboXasParameters", turboXasMotorParams.getScanParameters().toXML() );
		}
	}

	private static class PlotUpdater {

		private int currentGroupNumber;
		private int currentSpectrumNumber;
		private String energyAxisName;

		public void setCurrentGroupNumber(int currentGroupNumber) {
			this.currentGroupNumber = currentGroupNumber;
		}

		public void incrementCurrentSpectrumNumber() {
			currentSpectrumNumber++;
		}

		public void setCurrentSpectrumNumber(int currentSpectrumNumber) {
			this.currentSpectrumNumber = currentSpectrumNumber;
		}

		public void setEnergyAxisName(String energyAxisName) {
			this.energyAxisName = energyAxisName;
		}

		DoubleDataset extractDoubleDatset(NexusGroupData groupData) {
			if (groupData!=null && groupData.getBuffer() instanceof double[]) {
				double[] originalData = (double[]) groupData.getBuffer();
				return (DoubleDataset) DatasetFactory.createFromObject(Arrays.copyOf(originalData, originalData.length), originalData.length);
			} else
				return null;
		}

		/**
		 * Extract detector data from scan data point and send spectra of I0, It, time etc to the progress updater.
		 * Only data from the first detector is extracted.
		 * @param scanDataPoint
		 */
		public void updateShowAll(ScanDataPoint scanDataPoint) {
			ScriptControllerBase controller = Finder.getInstance().find(EdeExperiment.PROGRESS_UPDATER_NAME);
			if ( controller != null ) {
				logger.info("PlotUpdater.updateShowAll() called");
				NXDetectorData data = (NXDetectorData) scanDataPoint.getDetectorData().get(0);

				// Extract numerical (floating point) detector data from Nexus data in scan data point
				List<String> dataNames = new ArrayList<String>();
				List<DoubleDataset> dataSets = new ArrayList<DoubleDataset>();
				INexusTree nexusDetData = data.getNexusTree().getChildNode(0);
				String detectorName = data.getNexusTree().getChildNode(0).getName();

				for(int i = 0; i<nexusDetData.getNumberOfChildNodes(); i++) {
					String dataName = nexusDetData.getChildNode(i).getName();
					NexusGroupData groupData = data.getData(detectorName, dataName, NexusExtractor.SDSClassName);
					DoubleDataset dataset = extractDoubleDatset(groupData);
					if (dataset!=null) {
						dataNames.add(dataName);
						dataSets.add(dataset);
					}
				}

				// Determine index of dataset to use for energy axis
				int energyAxisIndex = dataNames.indexOf(energyAxisName);
				if (energyAxisIndex==-1) {
					logger.info("PlotUpdater could not find energy axis data (axis name = {})",energyAxisName);
					return;
				}

				// Create progress beans and notify plot controller
				EdeScanProgressBean scanProgressBean = new EdeScanProgressBean(currentGroupNumber, currentSpectrumNumber, EdeScanType.LIGHT,
						EdePositionType.INBEAM, scanDataPoint);
				for(int i = 0; i<dataNames.size(); i++) {
					// Don't plot position column or energy datasets
					String dataName=dataNames.get(i);
					if (!dataName.equals(ENERGY_COLUMN_NAME) && !dataName.equals(POSITION_COLUMN_NAME)) {
						controller.update(null, new EdeExperimentProgressBean(ExperimentCollectionType.MULTI, scanProgressBean,
											dataNames.get(i), dataSets.get(i), dataSets.get(energyAxisIndex)));
					}
				}
			}
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
