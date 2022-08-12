/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

import java.util.Map;

import org.apache.commons.math3.util.Pair;
import org.dawnsci.ede.EdeDataConstants;
import org.dawnsci.ede.EdeScanType;
import org.eclipse.dawnsci.hdf5.nexus.NexusFileHDF5;
import org.eclipse.dawnsci.nexus.NexusFile;
import org.eclipse.january.dataset.BooleanDataset;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.DeviceException;
import gda.device.Monitor;
import gda.device.Scannable;
import gda.device.detector.DAServer;
import gda.device.detector.EdeDetector;
import gda.device.detector.countertimer.TfgScaler;
import gda.device.detector.frelon.EdeFrelon;
import gda.device.detector.frelon.FrelonCcdDetectorData;
import gda.device.detector.xstrip.XhDetector;
import gda.device.enumpositioner.ValvePosition;
import gda.device.lima.LimaCCD.AcqTriggerMode;
import gda.device.scannable.ScannableUtils;
import gda.device.scannable.TopupChecker;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.scan.ede.position.EdeScanPosition;
import uk.ac.gda.exafs.experiment.trigger.TFGTrigger;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

/**
 * This is the with-beam It scan in linear and cyclic experiments.
 * <p>
 * This involves more than just the XCHIP detectors. It needs to also talk to an external TFG (eTFG) unit which will
 * fire out synchronised TTL hardware signals to the photon shutter, user sample environments as well as the XCHIP
 * detector. It will also hold a counter (scaler) of signals from Diamond's injection pulses so we can match up spectra
 * to when (if) storage ring top-ups occur.
 * <p>
 * Wiring connections are assumed to be:
 * <p>
 * TRIG0 cable from machine top-up signal
 * <p>
 * TRIG1 cable from XH, to increment frames counting machine insertion signals
 * <p>
 * USR OUT 0 cable to photon shutter
 * <p>
 * USR OUT 1 cable to XH, to start the It sequence
 * <p>
 * USR OUT 2..7 cables to sample environments
 * <p>
 * SCA 0 cable from machine insertion signal
 */
public class EdeScanWithTFGTrigger extends EdeScan implements EnergyDispersiveExafsScan {

	private static final long serialVersionUID = 1L;

	private static final Logger logger = LoggerFactory.getLogger(EdeScanWithTFGTrigger.class);
	private final DAServer daServerForTriggeringWithTFG;
	private final TFGTrigger triggeringParameters;
	private final boolean shouldWaitForTopup;
	private TfgScaler injectionCounter;

	private Dataset topupScalerValueForSpectra = null;
	private Dataset topupValueUsesScalers = null;
	private TopupChecker topupCheckerMachine;
	private double lastTimeTillTopup = 600.0;
	private double timeAtTopupStart = lastTimeTillTopup;

	public EdeScanWithTFGTrigger(EdeScanParameters scanParameters, TFGTrigger triggeringParameters,
			EdeScanPosition motorPositions, EdeScanType scanType, EdeDetector theDetector, Integer repetitionNumber,
			Scannable shutter, boolean shouldWaitForTopup) {
		super(scanParameters, motorPositions, scanType, theDetector, repetitionNumber, shutter, null);

		this.triggeringParameters = triggeringParameters;
		this.shouldWaitForTopup = shouldWaitForTopup;
		daServerForTriggeringWithTFG = Finder.find("daserverForTfg");
		injectionCounter = Finder.find("injectionCounter");
		topupCheckerMachine = (TopupChecker) Finder.find("topupChecker");
	}

	public void doCollectionFrelon() throws Exception {
		// load the detector parameters
		validate();
		logger.debug(toString() + " loading detector parameters...");
		theDetector.prepareDetectorwithScanParameters(scanParameters);

		triggeringParameters.setDetector(theDetector);

		moveShutter(ValvePosition.CLOSE);

		// move into the it position
		moveSampleIntoPosition();

		waitBeforeCycle();

		moveShutter(ValvePosition.OPEN);

		// start the detector running (it waits for a pulse from the eTFG)
		logger.debug(toString() + " starting detector running...");
		InterfaceProvider.getTerminalPrinter().print("Starting " + scanType.toString() + " " + motorPositions.getType().getLabel() + " scan");

		// Store orig. trigger mode setting
		EdeFrelon detector=((EdeFrelon)theDetector);
		AcqTriggerMode acqTriggerMode = detector.getLimaCcd().getAcqTriggerMode();

		// Set external trigger mode - this object is used to set Frelon trigger mode in configureDetectorForTimingGroup
		FrelonCcdDetectorData detectorSettings = (FrelonCcdDetectorData) detector.getDetectorData();
		detectorSettings.setTriggerMode(AcqTriggerMode.EXTERNAL_TRIGGER);

		// set to true (always want to use scalers to measure topup injections for Tfg Frelon scans)
		triggeringParameters.setUseCountFrameScalers(true);

		lastTimeTillTopup = getTimeUntilTopup();

		// Multiple timing groups
		for (Integer i = 0; i < scanParameters.getGroups().size(); i++) {
			if (Thread.currentThread().isInterrupted()) {
				break;
			}
			TimingGroup currentTimingGroup = scanParameters.getGroups().get(i);

			// set scans per frame on detector so TFG scans per frame is correct...
			int scansPerFrame = currentTimingGroup.getNumberOfScansPerFrame();

			// Number of frames is now incremented in EdeFrelon.configureDetectorForTimingGroup
			// dropFirstFrame flag is set to 'true' (true by default)
			int numberOfFrames = scanParameters.getTotalNumberOfFrames();

			theDetector.setNumberScansInFrame(scansPerFrame);

			// EdeScanWithTfgTrigger is *only* used for Tfg triggered light It - *never* drop 1st frame! imh 5/5/2016
			((EdeFrelon) theDetector).setDropFirstFrame(false);

			triggeringParameters.getDetectorDataCollection().setNumberOfFrames(numberOfFrames);

			theDetector.configureDetectorForTimingGroup(currentTimingGroup);

			// theDetector.setNumberScansInFrame( detectorSettings.getNumberOfImages() );
			prepareTFG(shouldWaitForTopup);

			theDetector.collectData();

			// start the eTFG running
			startTFG();

			Thread.sleep(250);

			// poll tfg and fetch data
			pollDetectorAndFetchData();
		}
		detector.getLimaCcd().setAcqTriggerMode(acqTriggerMode);
		detectorSettings.setTriggerMode(acqTriggerMode);
	}

	/**
	 * Sum scaler counts for each time frame to get total scaler counts for each spectra.
	 * Each spectra has is made up of numAccumulationsPerSpectra frames
	 * @param scalerCountsForFrames [numSpectra*numAccumulationsPerSpectra][numScalers]
	 * @param numAccumulationsPerSpectra
	 * @param numSpectra
	 * @return scalerCountsForSpectra [numSpectra][numScalers]
	 * @throws Exception
	 * @since 6/5/2016
	 */
	private double[][] getScalerCountsForSpectra(int firstSpectrum, int lastSpectrum) throws Exception {

		logger.debug("Getting scaler counts for spectra {} to {}", firstSpectrum, lastSpectrum);

		// Lookup the range of scaler frames to be used for each spectrum :
		Map<Integer, Pair<Integer, Integer>> framesForSpectra = triggeringParameters.getFramesForSpectra();
		Pair<Integer, Integer> framesForFirstSpectrum = framesForSpectra.get(firstSpectrum);
		Pair<Integer, Integer> framesForLastSpectrum = framesForSpectra.get(lastSpectrum);
		if (framesForFirstSpectrum == null || framesForLastSpectrum == null) {
			logger.error("Scaler frame range for spectrum {}...{} has not been set - no scaler values will be present for this spectrum", firstSpectrum, lastSpectrum);
			return null;
		}

		logger.debug("Scaler frame ranges : spectrum {} = {}, spectrum {} = {}", firstSpectrum, framesForFirstSpectrum, lastSpectrum, framesForLastSpectrum);

		// Read the required scaler frame data from injectionCounter
		int firstScalerFrameToRead = framesForFirstSpectrum.getFirst();
		int lastScalerFrameToRead = framesForLastSpectrum.getSecond();
		logger.debug("Reading scaler frames {} to {}", firstScalerFrameToRead, lastScalerFrameToRead);
		Object[] detectorFrameData = injectionCounter.readoutFrames(firstScalerFrameToRead, lastScalerFrameToRead);
		double[][] scalerCountsForFrames = (double[][]) detectorFrameData;

		int numScalers = scalerCountsForFrames[0].length;
		logger.debug("Scaler data shape : {}, {}", scalerCountsForFrames.length, numScalers);

		// Array to store total scaler counts for each spectrum, for each scaler channel
		int numSpectra = lastSpectrum - firstSpectrum + 1;
		double[][] scalerCountsForSpectra = new double[numSpectra][numScalers];

		for(int spectrumIndex=0; spectrumIndex<numSpectra; spectrumIndex++) {
			int spectrumNumber = firstSpectrum + spectrumIndex;
			Pair<Integer, Integer> frames = framesForSpectra.get(spectrumNumber);
			if (frames == null) {
				logger.warn("Scaler frame range for spectrum {} has not been set - no scaler values will be present for this spectrum", spectrumNumber);
				continue;
			}

			// Convert absolute frame number to frame indices in scalerCountsForFrames :
			int firstFrameIndex = frames.getFirst()-firstScalerFrameToRead;
			int lastFrameIndex = frames.getSecond()-firstScalerFrameToRead;
			logger.debug("Adding scaler counts for spectrum {} (frames = {}, indices = [{}, {}])", spectrumNumber, frames, firstFrameIndex, lastFrameIndex);

			// Scaler values for spectrum is the sum of scaler counts over range of frames :
			for(int scalerFrameIndex=firstFrameIndex; scalerFrameIndex<lastFrameIndex; scalerFrameIndex++) {
				// Add counts for each scaler channel to the sum for the spectrum
				for(int scalerChannelIndex = 0; scalerChannelIndex<numScalers; scalerChannelIndex++) {
					scalerCountsForSpectra[spectrumIndex][scalerChannelIndex] += scalerCountsForFrames[scalerFrameIndex][scalerChannelIndex];
				}
			}
		}

		return scalerCountsForSpectra;
	}

	 /** Write dataset of topup scaler counts for each spectra to NeXus file.
	  * Data is appended if a dataset to be written already exists in the file.
	 *
	 * @throws Exception
	 */
	private void addScalerFrameCountsToNexus() throws Exception {
		if (topupScalerValueForSpectra == null || topupValueUsesScalers == null) {
			return;
		}
		String fname = getDataWriter().getCurrentFileName();
		try (NexusFile file = NexusFileHDF5.openNexusFile(fname)) {
			String detectorEntry = "/entry1/" + theDetector.getName() + "/";
			file.createData(detectorEntry, EdeDataConstants.SCALER_FRAME_COUNTS, topupScalerValueForSpectra,  true);
			file.createData(detectorEntry, "is_topup_measured_from_scaler", topupValueUsesScalers,  true);
		} catch (Exception e) {
			logger.error("Problem when writing topup scaler information to Nexus file", e);
		}
	}

	@Override
	public void doCollection() throws Exception {
		if (smartStopDetected()) {
			return;
		}

		if (theDetector.getName().equalsIgnoreCase("frelon")) {
			doCollectionFrelon();
		}
		else {
			doCollectionOld();
		}
		fastShutterMoveTo(ValvePosition.CLOSE);
		addScalerFrameCountsToNexus();

		waitAfterCollection();
	}

	//	@Override
	public void doCollectionOld() throws Exception {
		// load the detector parameters
		int numberOfRepititionsDone=0;
		validate();
		logger.debug(toString() + " loading detector parameters...");
		theDetector.prepareDetectorwithScanParameters(scanParameters);
		// derive the eTFG parameters and load them

		triggeringParameters.setDetector(theDetector);
		triggeringParameters.getDetectorDataCollection().setNumberOfFrames(scanParameters.getTotalNumberOfFrames());

		boolean triggerOnRisingEdge = true;
		if (theDetector instanceof XhDetector) {
			// try to get trigger rise/fall value from timing group parameters (false by default, if not set explicitly)
			if (scanParameters.getGroups().size()>0) {
				triggerOnRisingEdge = scanParameters.getGroups().get(0).isGroupTrigRisingEdge();
			} else {
				triggerOnRisingEdge = false;
			}
		}
		triggeringParameters.setTriggerOnRisingEdge(triggerOnRisingEdge);

		prepareTFG(shouldWaitForTopup);
		moveShutter(ValvePosition.CLOSE);

		// move into the it position
		moveSampleIntoPosition();

		moveShutter(ValvePosition.OPEN);

		// start the detector running (it waits for a pulse from the eTFG)
		logger.debug(toString() + " starting detector running...");
		InterfaceProvider.getTerminalPrinter().print(
				"Starting " + scanType.toString() + " " + motorPositions.getType().getLabel() + " scan");
		if (theDetector.getName().equalsIgnoreCase("frelon")) {

			EdeFrelon detector=((EdeFrelon)theDetector);

			AcqTriggerMode acqTriggerMode = detector.getLimaCcd().getAcqTriggerMode();
			detector.getLimaCcd().setAcqTriggerMode(AcqTriggerMode.EXTERNAL_TRIGGER);
			while (numberOfRepititionsDone<scanParameters.getNumberOfRepetitions()) {
				theDetector.collectData();

				// start the eTFG running
				startTFG();

				// poll to get progress
				Thread.sleep(500);

				pollDetectorAndFetchData();
				numberOfRepititionsDone++;
			}
			detector.getLimaCcd().setAcqTriggerMode(acqTriggerMode);

		} else {
			// Always enable topup scalers for dummy mode to help with unit tests
			if (LocalProperties.isDummyModeEnabled()) {
				triggeringParameters.setUseCountFrameScalers(true);
			}
			theDetector.collectData();

			// start the eTFG running
			startTFG();

			// poll to get progress
			Thread.sleep(500);

			pollDetectorAndFetchData();
		}
		logger.debug(toString() + " doCollection finished.");
	}

	private void prepareTFG(boolean shouldStartOnTopupSignal) throws DeviceException {
		int numberOfRepetitions = scanParameters.getNumberOfRepetitions();
		// triggeringParameters.getDetectorDataCollection().setNumberOfFrames(scanParameters.getTotalNumberOfFrames());
		String command = triggeringParameters.getTfgSetupGroupCommandParameters(numberOfRepetitions, shouldStartOnTopupSignal);
		logger.info("Preparing external TFG using command :\n{}", command);
		// send buffer to daserver
		daServerForTriggeringWithTFG.sendCommand(command);

	}

	private void startTFG() throws DeviceException {
		daServerForTriggeringWithTFG.sendCommand("tfg start");
	}

	@Override
	protected void addDetectorsToScanDataPoint(int lowFrame, Object[] detData, int thisFrame,
			ScanDataPoint thisPoint) throws DeviceException {

		super.addDetectorsToScanDataPoint(lowFrame, detData, thisFrame, thisPoint);
	}

	@Override
	protected NexusTreeProvider[] readDetectors(int lowFrame, int highFrame) throws Exception, DeviceException {
		NexusTreeProvider[] detData = super.readDetectors(lowFrame, highFrame);
		//detData[1] = injectionCounter.readoutFrames(lowFrame, highFrame);

		// Get the topup signal value for each spectrum, do in try-catch so
		// that if anything goes wrong the spectra can still be collected as normal.
		if (triggeringParameters.getUseCountFrameScalers()) {
			try {
				storeTopupValueForSpectra(lowFrame, highFrame);
			} catch (Exception e) {
				logger.warn("Problem getting topup signal data", e);
			}
		}
		return detData;
	}

	@Override
	public String toString() {
		return "EDE It scan - type:" + scanType.toString() + " " + motorPositions.getType().toString();
	}

	/**
	 * Store topup value for specified range of spectra.
	 * Topup value is read from hardware (scalers) if topup is occuring or close to it; zeros are used otherwise.
	 * This helps reduce overhead in the scan of repeated reading from scalers if topup is not actually happening.<p>
	 * Values are stored in a dataset in memory and written to nexus file at the end of the scan by the
	 * {@link #addScalerFrameCountsToNexus()} function called at the end of {@link #doCollection()}.
	 *
	 * @param lowFrame
	 * @param highFrame
	 * @throws DeviceException
	 */
	private void storeTopupValueForSpectra(int lowFrame, int highFrame) throws DeviceException {

		if (topupScalerValueForSpectra == null || topupValueUsesScalers == null) {
			prepareTopupDatasets();
		}

		boolean readFromScalers = readTopupFromScalers();
		int numAccumulationsPerSpectrum = 1;
		if (theDetector instanceof EdeFrelon) {
			numAccumulationsPerSpectrum = ((EdeFrelon)theDetector).getCurrentTimingGroup().getNumberOfScansPerFrame();
		}
		double[][] topupValuePerSpectra = getTopupValuesForSpectra(lowFrame, highFrame, numAccumulationsPerSpectrum, readFromScalers);
		if (topupValuePerSpectra != null) {
			if (topupValuePerSpectra.length!=highFrame-lowFrame+1) {
				logger.debug("Number of frames of processed scaler values ({}) does not match number of spectra ({})", topupValuePerSpectra.length, highFrame-lowFrame+1);
			}
			int numValues = topupValuePerSpectra[0].length;
			logger.debug("Storing scaler counts for spectra {} to {}", lowFrame, lowFrame+topupValuePerSpectra.length);
			for (int i = 0; i < topupValuePerSpectra.length; i++) {
				for (int j = 0; j < numValues; j++) {
					topupScalerValueForSpectra.set(topupValuePerSpectra[i][j], lowFrame + i, j);
				}
				topupValueUsesScalers.set(readFromScalers, lowFrame + i);
			}
		}
	}

	private void prepareTopupDatasets() {
		if (injectionCounter == null) {
			logger.info("InjectionCounter not set - not storing topup spectra markers.");
			return;
		}
		int totalNumSpectra = scanParameters.getTotalNumberOfFrames();
		int numScalers = injectionCounter.getNumChannelsToRead();
		topupScalerValueForSpectra = DatasetFactory.zeros(DoubleDataset.class, totalNumSpectra, numScalers);
		topupValueUsesScalers = DatasetFactory.zeros(BooleanDataset.class, totalNumSpectra);
	}

	/**
	 * Determine whether to read topup value from scalers.
	 *
	 * @return true if topup is happening or within a few seconds either side of it, false otherwise.
	 * @throws DeviceException
	 */
	private boolean readTopupFromScalers() throws DeviceException {
		if (topupCheckerMachine==null) {
			return true;
		}

		final double waitTimeEitherSideOfTopup = topupCheckerMachine.getWaittime();

		Double timeToTopup = getTimeUntilTopup();
		if (timeToTopup > lastTimeTillTopup) {
			timeAtTopupStart = timeToTopup;
		}

		lastTimeTillTopup = timeToTopup;
		if (timeToTopup < waitTimeEitherSideOfTopup || timeToTopup > timeAtTopupStart - waitTimeEitherSideOfTopup) {
			return true;
		} else {
			return false;
		}
	}

	/**
	 * @return Number of seconds until the next topup begins.
	 * @throws DeviceException
	 */
	double getTimeUntilTopup() throws DeviceException {
		if (topupCheckerMachine==null) {
			return 0.0;
		}

		Monitor monitoredScannable = topupCheckerMachine.getScannableToBeMonitored();
		if (monitoredScannable != null) {
			return ScannableUtils.getCurrentPositionArray(monitoredScannable)[0];
		} else {
			return 0.0;
		}
	}

	/**
	 * Get topup counts for specified range of spectra by reading scaler data from {@link #injectionCounter}.<p>
	 * Each spectrum has {@code numAccumulationsPerSpectra} frames of scaler data;
	 * Scaler values from {@link #injectionCounter} for each spectrum are summed together and returned as double array.
	 * Reading from scalers only takes place if {@code readFromScalers}=true; otherwise the topupCounts array is filled with zeros..
	 *
	 * @param lowFrame
	 * @param highFrame
	 * @param numAccumulationsPerSpectra
	 * @param readFromScalers if true read from hardware, if false return empty array of same size initialised with zeros
	 * @return topupCounts
	 */
	private double[][] getTopupValuesForSpectra(int lowFrame, int highFrame, int numAccumulationsPerSpectra, boolean readFromScalers) {
		if (injectionCounter == null) {
			return null;
		}

		int totNumSpectra = highFrame - lowFrame + 1;
		if (totNumSpectra == 0) {
			return null;
		}

		try {
			logger.debug("Getting topup counts for spectra {} to {}. Time to topup = {} secs, {} accumulations per spectrum",
					lowFrame, highFrame, getTimeUntilTopup(), numAccumulationsPerSpectra);

			if (!readFromScalers) {
				logger.debug("Using dummy data (zeros)");
				int numChannels = injectionCounter.getNumChannelsToRead();
				return new double[totNumSpectra][numChannels];

			} else {
				// Sum over number of accumulations to find total counts for each spectrum
				double[][] countsForSpectra= getScalerCountsForSpectra(lowFrame, highFrame);
				return countsForSpectra;
			}
		} catch (Exception e) {
			logger.error("Problem collecting topup signal data ", e);
		}
		return null;
	}
}
