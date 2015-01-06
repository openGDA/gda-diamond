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
import gda.device.detector.Detector;
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
			Detector theDetector, Integer repetitionNumber, Scannable shutter, boolean shouldWaitForTopup) {
		super(scanParameters, motorPositions, scanType, theDetector, repetitionNumber, shutter, null);

		this.triggeringParameters = triggeringParameters;
		this.shouldWaitForTopup = shouldWaitForTopup;
		daServerForTriggeringWithTFG = Finder.getInstance().find("daserverForTfg");
	}

	@Override
	public void doCollection() throws Exception {
		// load the detector parameters
		validate();
		logger.debug(toString() + " loading detector parameters...");
		theDetector.prepareDetectorwithScanParameters(scanParameters);
		// derive the eTFG parameters and load them
		prepareTFG(shouldWaitForTopup);
		// move into the it position
		moveSampleIntoPosition();

		// start the detector running (it waits for a pulse from the eTFG)
		logger.debug(toString() + " starting detector running...");
		InterfaceProvider.getTerminalPrinter().print(
				"Starting " + scanType.toString() + " " + motorPositions.getType().getLabel() + " scan");
		theDetector.collectData();

		// start the eTFG running
		startTFG();

		// poll to get progress
		Thread.sleep(500);

		pollDetectorAndFetchData();
		logger.debug(toString() + " doCollection finished.");
	}

	private void prepareTFG(boolean shouldStartOnTopupSignal) throws DeviceException {
		int numberOfRepetitions = scanParameters.getNumberOfRepetitions();
		triggeringParameters.getDetectorDataCollection().setNumberOfFrames(scanParameters.getTotalNumberOfFrames());
		String command = triggeringParameters.getTfgSetupGrupsCommandParameters(numberOfRepetitions, shouldStartOnTopupSignal);

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
