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
import java.util.Map.Entry;

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
import gda.device.Scannable;
import gda.device.detector.DAServer;
import gda.device.detector.EdeDetector;
import gda.device.detector.countertimer.TfgScaler;
import gda.device.detector.frelon.EdeFrelon;
import gda.device.detector.frelon.FrelonCcdDetectorData;
import gda.device.lima.LimaCCD.AcqTriggerMode;
import gda.device.scannable.ScannableUtils;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.datawriters.EdeDataConstants;
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


	public EdeScanWithTFGTrigger(EdeScanParameters scanParameters, TFGTrigger triggeringParameters, EdeScanPosition motorPositions, EdeScanType scanType,
			EdeDetector theDetector, Integer repetitionNumber, Scannable shutter, boolean shouldWaitForTopup) {
		super(scanParameters, motorPositions, scanType, theDetector, repetitionNumber, shutter, null);

		this.triggeringParameters = triggeringParameters;
		this.shouldWaitForTopup = shouldWaitForTopup;
		daServerForTriggeringWithTFG = Finder.getInstance().find("daserverForTfg");
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
		InterfaceProvider.getTerminalPrinter().print(
				"Starting " + scanType.toString() + " " + motorPositions.getType().getLabel() + " scan");

		// Store orig. trigger mode setting
		EdeFrelon detector=((EdeFrelon)theDetector);
		AcqTriggerMode acqTriggerMode = detector.getLimaCcd().getAcqTriggerMode();

		// Set external trigger mode - this object is used to set Frelon trigger mode in configureDetectorForTimingGroup
		FrelonCcdDetectorData detectorSettings = (FrelonCcdDetectorData) detector.getDetectorData();
		detectorSettings.setTriggerMode(AcqTriggerMode.EXTERNAL_TRIGGER);

		// set to true (always want to use scalers to measure topup injections for Tfg Frelon scans)
		triggeringParameters.setUseCountFrameScalers(true);

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

			theDetector.setNumberScansInFrame( scansPerFrame );

			// i.e. Only drop first frame for non It collection (helps with TFG timing calculations).
//			if ( numberOfFrames > 1 ) {
//				( (EdeFrelon) theDetector).setDropFirstFrame( false );
//			} else {
//				( (EdeFrelon) theDetector).setDropFirstFrame( true );
//			}
			// EdeScanWithTfgTrigger is *only* used for Tfg triggered light It - *never* drop 1st frame! imh 5/5/2016
			( (EdeFrelon) theDetector).setDropFirstFrame( false );

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

			addScalerFrameCounts( scansPerFrame, numberOfFrames );
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
	private double [][] getScalerCountsForSpectra( double [][] scalerCountsForFrames, int numAccumulationsPerSpectra, int numSpectra ) throws Exception {
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
	 * Scaler count>0 for spectra indicates that topup injection was taking place at same time as spectrum was measured.
	 * @param numAccumulationsPerSpectra
	 * @param numSpectra
	 * @throws Exception
	 * @since 6/5/2016
	 */
	private void addScalerFrameCounts(int numAccumulationsPerSpectra, int numSpectra ) throws Exception {
		final TfgScaler injectionCounter = Finder.getInstance().find("injectionCounter");
		if ( injectionCounter != null ) {
			// Read scaler data : one value for each accumulation
			int totNumFrames =  numAccumulationsPerSpectra * numSpectra;
			double [][]scalerCounts = injectionCounter.readoutFrames(0,  totNumFrames );

			// Convert to scaler counts for each spectra (i.e. sum over accumulations for each spectra)
			double [][]scalerCountsForSpectra = getScalerCountsForSpectra(scalerCounts, numAccumulationsPerSpectra, numSpectra );

			if ( scalerCountsForSpectra == null )
				return;

			Dataset scalerDataset = DatasetFactory.createFromObject( scalerCountsForSpectra );

			String fname = getDataWriter().getCurrentFileName();
			IHierarchicalDataFile file = HierarchicalDataFactory.getWriter( fname );

			String targetPath = HierarchicalDataFileUtils.createParentEntry(file, "/entry1/" + theDetector.getName(), Nexus.DATA);

			addDatasetToNexus( file, EdeDataConstants.SCALER_FRAME_COUNTS, targetPath, scalerDataset, null );
			file.close();
		}
	}

	private void addDatasetToNexus(IHierarchicalDataFile file, String dataName, String fullPath, Dataset data, Map<String, String> attributes) throws Exception {
		long[] shape = H5Utils.getLong(data.getShape());
		String insertedData = file.replaceDataset(dataName, Dataset.FLOAT64, shape, data.getBuffer(), fullPath);
		if (attributes == null) {
			return;
		}
		for (Entry<String, String> entry : attributes.entrySet()) {
			file.setAttribute(insertedData, entry.getKey(), entry.getValue());
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
		thisPoint.addDetector(theDetector);
		//thisPoint.addDetector(injectionCounter);
		thisPoint.addDetectorData(detData[0][thisFrame - lowFrame], ScannableUtils.getExtraNamesFormats(theDetector));
		//thisPoint.addDetectorData(detData[1][thisFrame - lowFrame], ScannableUtils.getExtraNamesFormats(injectionCounter));
	}

	@Override
	protected Object[][] readDetectors(int lowFrame, int highFrame) throws Exception, DeviceException {
		Object[][] detData = new Object[1][];
		detData[0] = super.readDetectors(lowFrame, highFrame)[0];
		//detData[1] = injectionCounter.readoutFrames(lowFrame, highFrame);
		return detData;
	}

	@Override
	public String toString() {
		return "EDE It scan - type:" + scanType.toString() + " " + motorPositions.getType().toString();
	}
}
