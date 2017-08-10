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

import org.dawnsci.ede.herebedragons.EdeDataConstants;
import org.dawnsci.ede.herebedragons.EdeScanType;
import org.eclipse.dawnsci.hdf.object.H5Utils;
import org.eclipse.dawnsci.hdf.object.HierarchicalDataFactory;
import org.eclipse.dawnsci.hdf.object.HierarchicalDataFileUtils;
import org.eclipse.dawnsci.hdf.object.IHierarchicalDataFile;
import org.eclipse.dawnsci.hdf.object.Nexus;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Monitor;
import gda.device.Scannable;
import gda.device.detector.DAServer;
import gda.device.detector.EdeDetector;
import gda.device.detector.countertimer.TfgScaler;
import gda.device.detector.frelon.EdeFrelon;
import gda.device.detector.frelon.FrelonCcdDetectorData;
import gda.device.lima.LimaCCD.AcqTriggerMode;
import gda.device.scannable.ScannableUtils;
import gda.device.scannable.TopupChecker;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.scan.ede.position.EdeScanPosition;
import uk.ac.gda.exafs.experiment.trigger.TFGTrigger;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;

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
		daServerForTriggeringWithTFG = Finder.getInstance().find("daserverForTfg");
		injectionCounter = Finder.getInstance().find("injectionCounter");
		topupCheckerMachine = (TopupChecker) Finder.getInstance().find("topupChecker");
	}

	public void doCollectionFrelon() throws Exception {
		// load the detector parameters
		validate();
		logger.debug(toString() + " loading detector parameters...");
		theDetector.prepareDetectorwithScanParameters(scanParameters);

		triggeringParameters.setDetector(theDetector);
		// prepareTFG(shouldWaitForTopup);
		// move into the it position
		moveSampleIntoPosition();

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
			currentTimingGroup=scanParameters.getGroups().get(i);

			// set scans per frame on detector so TFG scans per frame is correct...
			int scansPerFrame = currentTimingGroup.getNumberOfScansPerFrame();
			// int numberOfFrames = scanParameters.getTotalNumberOfFrames()+1;

			// Number of frames is now incremented in EdeFrelon.configureDetectorForTimingGroup
			// dropFirstFrame flag is set to 'true' (true by default)
			int numberOfFrames = scanParameters.getTotalNumberOfFrames();

			theDetector.setNumberScansInFrame(scansPerFrame);

			// i.e. Only drop first frame for non It collection (helps with TFG timing calculations).
//			if ( numberOfFrames > 1 ) {
//				( (EdeFrelon) theDetector).setDropFirstFrame( false );
//			} else {
//				( (EdeFrelon) theDetector).setDropFirstFrame( true );
//			}
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
	private double[][] getScalerCountsForSpectra(double[][] scalerCountsForFrames, int numAccumulationsPerSpectra, int numSpectra) throws Exception {
		int numScalers = scalerCountsForFrames[0].length;
		int numFrames = scalerCountsForFrames.length;

		if ( numSpectra * numAccumulationsPerSpectra > numFrames ) {
			// Don't throw an exception, since even if scaler values can't be converted, still want rest of
			// processed data to be written at end of scan.
			logger.error( "Problem converting scaler values : total number of frames != accumulations per spectra * number of spectra");
			return null;
		}

		double [][]scalerCountsForSpectra = new double[numSpectra][numScalers];
		int specCount = 0;
		for(int i = 0; i<numFrames; i++) {

			// add to scaler values for current spectra
			for(int j = 0; j<numScalers; j++)
				scalerCountsForSpectra[specCount][j] += scalerCountsForFrames[i][j];

			// increment counter for next spectra
			if ( i%numAccumulationsPerSpectra == 0 && i>0 )
				specCount++;
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
		IHierarchicalDataFile file = null;
		try {
			file = HierarchicalDataFactory.getWriter(fname);
			String targetPath = HierarchicalDataFileUtils.createParentEntry(file, "/entry1/" + theDetector.getName(), Nexus.DATA);
			appendDataToNexus(file, EdeDataConstants.SCALER_FRAME_COUNTS, targetPath, DatasetFactory.createFromObject(topupScalerValueForSpectra));
			appendDataToNexus(file, "is_topup_measured_from_scaler", targetPath, DatasetFactory.createFromObject(topupValueUsesScalers));
			file.close();
		} catch (Exception e) {
			logger.error("Prolbem when writing topup scaler information to Nexus file", e);
		}
		if (file!=null) {
			file.close();
		}
	}

	/**
	 * Append values to a dataset in Nexus file, one row of values at a time (1, 2-dimensional Datasets)
	 * @param file
	 * @param dataName
	 * @param fullPath
	 * @param data
	 * @throws Exception
	 */
	private void appendDataToNexus(IHierarchicalDataFile file, String dataName, String fullPath, Dataset data) throws Exception {
		long[] shape = H5Utils.getLong(data.getShape());
		int numValues = (int) (shape.length == 2 ? shape[1]:1);
		int numRows = (int) shape[0];
		long[] rowShape = new long[]{numValues};
		for(int i=0; i<numRows; i++) {
			double[] values = new double[numValues];
			if(numValues==1) {
				values[0] = data.getDouble(i);
			}else{
				for(int j=0; j<numValues; j++) {
					values[j] = data.getDouble(i,j);
				}
			}
			String insertedData = file.appendDataset(dataName, Dataset.FLOAT64, rowShape, values, fullPath);
		}
	}

	@Override
	public void doCollection() throws Exception {
		if (theDetector.getName().equalsIgnoreCase("frelon")) {
			doCollectionFrelon();
		}
		else {
			doCollectionOld();
		}
		addScalerFrameCountsToNexus();
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
		prepareTFG(shouldWaitForTopup);
		// move into the it position
		moveSampleIntoPosition();

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

		// send buffer to daserver
		daServerForTriggeringWithTFG.sendCommand(command);

	}

	private void startTFG() throws DeviceException {
		daServerForTriggeringWithTFG.sendCommand("tfg start");
	}

	@Override
	protected void addDetectorsToScanDataPoint(int lowFrame, Object[][] detData, int thisFrame,
			ScanDataPoint thisPoint) throws DeviceException {

		super.addDetectorsToScanDataPoint(lowFrame, detData, thisFrame, thisPoint);
	}

	@Override
	protected Object[][] readDetectors(int lowFrame, int highFrame) throws Exception, DeviceException {
		Object[][] detData = new Object[1][];
		detData[0] = super.readDetectors(lowFrame, highFrame)[0];
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
		int numAccumulationsPerSpectrum = currentTimingGroup == null ? 1 : currentTimingGroup.getNumberOfScansPerFrame();
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
		topupScalerValueForSpectra = DatasetFactory.zeros(new int[] {totalNumSpectra, numScalers}, Dataset.FLOAT64);
		topupValueUsesScalers = DatasetFactory.zeros(new int[] {totalNumSpectra}, Dataset.BOOL);
	}

	/**
	 * Determine whether to read topup value from scalers.
	 *
	 * @return true if topup is happening or within a few seconds either side of it, false otherwise.
	 * @throws DeviceException
	 */
	private boolean readTopupFromScalers() throws DeviceException {
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
		if (injectionCounter == null || topupCheckerMachine == null) {
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
				int firstScalerFrameToRead = lowFrame * numAccumulationsPerSpectra;
				int lastScalerFrameToRead = (highFrame + 1) * numAccumulationsPerSpectra;
				logger.debug("Reading scaler frames {} to {}", firstScalerFrameToRead, lastScalerFrameToRead);

				// Get scaler frame data from injectionCounter
				Object[] detectorFrameData = injectionCounter.readoutFrames(firstScalerFrameToRead, lastScalerFrameToRead);
				double[][] frameDataArray = (double[][]) detectorFrameData;
				logger.debug("Frame data array {}", frameDataArray[0][0]);
				// Sum over number of accumulations to find total counts for each spectrum
				double[][] countsForSpectra= getScalerCountsForSpectra(frameDataArray, numAccumulationsPerSpectra, totNumSpectra);
				logger.debug("Counts for spectra {}", countsForSpectra[0][0]);
				return countsForSpectra;
			}
		} catch (Exception e) {
			logger.error("Problem collecting topup signal data ", e);
		}
		return null;
	}
}
