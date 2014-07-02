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
import gda.device.detector.StripDetector;
import gda.device.detector.countertimer.TfgScaler;
import gda.device.scannable.ScannableUtils;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.position.EdeScanPosition;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

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
public class EdeWithTFGScan extends EdeWithoutTriggerScan implements EnergyDispersiveExafsScan {

	private static final Logger logger = LoggerFactory.getLogger(EdeWithTFGScan.class);
	private final DAServer daserver;
	private final TfgScaler injectionCounter;

	public EdeWithTFGScan(EdeScanParameters scanParameters, EdeScanPosition motorPositions, EdeScanType scanType,
			StripDetector theDetector, Integer repetitionNumber, Scannable shutter) {
		super(scanParameters, motorPositions, scanType, theDetector, repetitionNumber, shutter, null);

		daserver = Finder.getInstance().find("daserver");
		injectionCounter = Finder.getInstance().find("injectionCounter");
	}

	@Override
	public void doCollection() throws Exception {
		// load the detector parameters
		validate();
		logger.debug(toString() + " loading detector parameters...");
		theDetector.loadParameters(scanParameters);

		// derive the eTFG parameters and load them
		prepareTFG();

		// move into the it position
		moveSampleIntoPosition();

		// start the detector running (it waits for a pulse from the eTFG)
		startTFG();

		// start the eTFG running
		logger.debug(toString() + " starting detector running...");
		InterfaceProvider.getTerminalPrinter().print(
				"Starting " + scanType.toString() + " " + motorPositions.getType().getLabel() + " scan");
		theDetector.collectData();

		// poll to get progress
		Thread.sleep(500);

		pollDetectorAndFetchData();
		logger.debug(toString() + " doCollection finished.");
	}

	private void prepareTFG() throws DeviceException {

		int numberOfRepetitions = scanParameters.getNumberOfRepetitions();
		int[] samEnvPulseWidths = deriveSamEnvPulseWidths();
		int[] samEnvDelays = deriveSamEnvDelays();
		int itDelay = deriveItDelay();
		int xchipStartPulseWidth = 50000; // 1ms pulse to start XCHIP
		int totalNumberItFramesPerRepetition = scanParameters.getTotalNumberOfFrames();

		StringBuffer sb = new StringBuffer();

		// first line, initial command and number of cycles
		sb.append("tfg setup-groups");
		if (numberOfRepetitions > 1) {
			sb.append(" cycles ");
			sb.append(numberOfRepetitions);
		}
		sb.append("\n");

		// second line, wait for top-up
		// TODO what if we are not waiting for top-up? e.g. the whole thing is << 10 mins
		sb.append("1 0.0000001 0 0 0 8 0\n"); // wait for a TTL signal on TRIG 0 (machine top-up pulse)

		// series of delays plus output to drive sample environments
		for (int samEnvIndex = 0; samEnvIndex < samEnvPulseWidths.length; samEnvIndex++) {
			sb.append("1 " + samEnvDelays[samEnvIndex] + " 0 0 0 0 0\n");// # some user defined delay
			int deadPort = 2 + samEnvIndex; // the first sample environment will be plugged into USR2
			deadPort = (int) Math.pow(2, deadPort);
			sb.append("1 " + samEnvPulseWidths[samEnvIndex] + " 0 " + deadPort + " 0 0 0\n");
			// # send pulse to USR2 (repeat this and line above up to 6 times)
		}

		// then a final delay before starting It sequence
		sb.append("1 " + itDelay + " 0 0 0 0 0\n");// # some user defined delay

		// pulse on USR1 to start the XH and on USR0 to open the photon shutter
		sb.append("1 " + xchipStartPulseWidth + " 0 3 1 0 0\n");

		// time frames to count machine injection signals, keeping photon shutter open, increment from XH
		sb.append(totalNumberItFramesPerRepetition+ " 0 0.0000001 1 1 0 9\n");

		sb.append("-1 0 0 0 0 0 0");

		// send buffer to daserver.sendCommand();
		daserver.sendCommand(sb.toString());

	}

	/*
	 * @return the delay, in TFG clock cycles,  between the last pulse to a sample environment and starting the It sequence
	 */
	private int deriveItDelay() {
		// TODO Auto-generated method stub
		return 0;
	}

	/*
	 * @return the delays, in TFG clock cycles, before each trigger signal out to the sample environments
	 */
	private int[] deriveSamEnvDelays() {
		// TODO Auto-generated method stub
		return null;
	}

	/*
	 * @return the duration, in TFG clock cycles, of each trigger signal to the sample environments
	 */
	private int[] deriveSamEnvPulseWidths() {
		// TODO Auto-generated method stub
		return null;
	}

	private void startTFG() throws DeviceException {
		daserver.sendCommand("tfg arm");
	}

	@Override
	protected void addDetectorsToScanDataPoint(int lowFrame, Object[][] detData, int thisFrame,
			ScanDataPoint thisPoint) throws DeviceException {
		thisPoint.addDetector(theDetector);
		thisPoint.addDetector(injectionCounter);
		thisPoint.addDetectorData(detData[0][thisFrame - lowFrame], ScannableUtils.getExtraNamesFormats(theDetector));
		thisPoint.addDetectorData(detData[1][thisFrame - lowFrame], ScannableUtils.getExtraNamesFormats(injectionCounter));
	}

	@Override
	protected Object[][] readDetectors(int lowFrame, int highFrame) throws Exception, DeviceException {
		Object[][] detData = new Object[2][];
		detData[0] = super.readDetectors(lowFrame, highFrame)[0];
		detData[1] = injectionCounter.readoutFrames(lowFrame, highFrame);
		return detData;
	}

	@Override
	public String toString() {
		return "EDE It scan - type:" + scanType.toString() + " " + motorPositions.getType().toString();
	}
}
