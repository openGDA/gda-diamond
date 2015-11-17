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

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.DAServer;
import gda.device.detector.EdeDetector;
import gda.device.detector.frelon.EdeFrelon;
import gda.device.detector.frelon.FrelonCcdDetectorData;
import gda.device.lima.LimaCCD.AcqTriggerMode;
import gda.device.scannable.ScannableUtils;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.position.EdeScanPosition;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

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
			if ( numberOfFrames > 1 ) {
				( (EdeFrelon) theDetector).setDropFirstFrame( false );
			} else {
				( (EdeFrelon) theDetector).setDropFirstFrame( true );
			}

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
