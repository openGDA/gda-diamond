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
import gda.device.scannable.ScannableUtils;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.position.EdeScanPosition;

import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.experiment.trigger.TFGTrigger;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject;
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
	private static final double DEAD_TIME_IN_SEC = 0.00001; // 10µs
	private final DAServer daserver;
	private final TFGTrigger triggeringParameters;

	public EdeScanWithTFGTrigger(EdeScanParameters scanParameters, TFGTrigger triggeringParameters, EdeScanPosition motorPositions, EdeScanType scanType,
			StripDetector theDetector, Integer repetitionNumber, Scannable shutter) {
		super(scanParameters, motorPositions, scanType, theDetector, repetitionNumber, shutter, null);

		this.triggeringParameters = triggeringParameters;

		daserver = Finder.getInstance().find("daserverForTfg");
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

	private void prepareTFG() throws DeviceException {

		int numberOfRepetitions = scanParameters.getNumberOfRepetitions();
		double[] samEnvPulseWidths = deriveSamEnvPulseWidths();
		double[] samEnvDelays = deriveSamEnvDelays();
		double photonShutterDelay = derivePSDelay();
		double itDelay = deriveItDelay();

		int totalNumberItFramesPerRepetition = scanParameters.getTotalNumberOfFrames();

		StringBuffer sb = new StringBuffer();

		//		Format of 'tfg setup-groups' as follows, 7 or 9 space-separated numbers:
		//			num_frames dead_time live_time dead_port live_port dead_pause live_pause [dead_tfinc live_tfinc]
		//			Followed by last line:
		//			-1 0 0 0 0 0 0
		//			Where num_frames       	= Number of frames in this group
		//			Dead_time, Live_time   	= time as floating point seconds
		//			Dead_port, Live_port    	= port data as integer (0<=port<=128k-1)
		//			Dead_pause, Live_pause 	= pause bit (0<=pause<=1)
		//			And For TFG2 only
		//			num_repeats sequence_name
		//			This repeats the pre-recorded sequence num_repeats times.

		// first line, initial command and number of cycles
		sb.append("tfg setup-groups");
		if (numberOfRepetitions > 1) {
			sb.append(" cycles ");
			sb.append(numberOfRepetitions);
		}
		sb.append("\n");

		// second line, wait for top-up
		// TODO what if we are not waiting for top-up? e.g. the whole thing is << 10 mins
		sb.append("1 " + DEAD_TIME_IN_SEC + " 0 0 0 8 0\n"); // wait for a TTL signal on TRIG 0 (machine top-up pulse)

		// series of delays plus output to drive sample environments
		for (int samEnvIndex = 0; samEnvIndex < samEnvPulseWidths.length; samEnvIndex++) {
			sb.append("1 " + samEnvDelays[samEnvIndex] + " 0 0 0 0 0\n");// # some user defined delay
			int deadPort = triggeringParameters.getSampleEnvironment().get(samEnvIndex).getTriggerOutputPort().getUsrPort();
			sb.append("1 " + samEnvPulseWidths[samEnvIndex] + " 0 " + deadPort + " 0 0 0\n");
			// # send pulse to USR2 (repeat this and line above up to 6 times)
		}

		// then a final delay before starting It sequence
		sb.append("1 " + photonShutterDelay + " 0 0 0 0 0\n");// # some user defined delay

		// pulse on USR1 to start the XH and on USR0 to open the photon shutter
		sb.append("1 " + triggeringParameters.getPhotonShutter().getTriggerPulseLength() + " 0 1 1 0 0\n"); 	// 3 to send on both USR 0 and USR 1 as "00000011"


		// then a final delay before starting It sequence
		sb.append("1 " + itDelay + " 0 1 1 0 0\n");// # some user defined delay

		// pulse on USR1 to start the XH and on USR0 to open the photon shutter
		sb.append("1 " + triggeringParameters.getDetector().getTriggerPulseLength() + " 0 3 1 0 0\n"); 	// 3 to send on both USR 0 and USR 1 as "00000011"

		// time frames to count machine injection signals, keeping photon shutter open, increment from XH
		sb.append(totalNumberItFramesPerRepetition+ " 0 " + DEAD_TIME_IN_SEC + " 1 1 0 9\n");

		// To stop the last frame of integration
		sb.append("1 " + DEAD_TIME_IN_SEC + " 0 0 0 0 9\n");

		sb.append("-1 0 0 0 0 0 0");

		// send buffer to daserver.sendCommand();
		daserver.sendCommand(sb.toString());


	}

	private double derivePSDelay() {
		if (triggeringParameters == null){
			return 0.0;
		}


		double sumOfSamEnvDelays = 0.0;

		List<TriggerableObject> samEnvParameters = triggeringParameters.getSampleEnvironment();
		for (TriggerableObject samEnv : samEnvParameters) {
			sumOfSamEnvDelays += samEnv.getTriggerDelay();
		}

		double psdelay = triggeringParameters.getPhotonShutter().getTriggerDelay() - sumOfSamEnvDelays;
		return psdelay;
	}

	/*
	 * @return the delay, in seconds,  between the last pulse to a sample environment and starting the It sequence
	 */
	private double deriveItDelay() {

		if (triggeringParameters == null){
			return 0.0;
		}

		double delayToDetectorTrigger = triggeringParameters.getDetector().getTriggerDelay() - derivePSDelay();
		return delayToDetectorTrigger;
	}

	/*
	 * @return the delays, in seconds, before each trigger signal out to the sample environments
	 */
	private double[] deriveSamEnvDelays() {

		if (triggeringParameters == null){
			return new double[]{};
		}

		List<TriggerableObject> samEnvParameters = triggeringParameters.getSampleEnvironment();

		double[] samEnvDelays = new double[samEnvParameters.size()];
		double sumOfSamEnvDelays = 0.0;

		for (int i = 0; i < samEnvParameters.size(); i++) {
			double thisDelay = samEnvParameters.get(i).getTriggerDelay();
			samEnvDelays[i] =  thisDelay - sumOfSamEnvDelays;
			sumOfSamEnvDelays += thisDelay;
		}
		return samEnvDelays;
	}

	/*
	 * @return the duration, in seconds, of each trigger signal to the sample environments
	 */
	private double[] deriveSamEnvPulseWidths() {

		if (triggeringParameters == null){
			return new double[]{};
		}

		List<TriggerableObject> samEnvParameters = triggeringParameters.getSampleEnvironment();

		double[] samEnvWidths = new double[samEnvParameters.size()];
		for (int i = 0; i < samEnvParameters.size(); i++) {
			samEnvWidths[i] = samEnvParameters.get(i).getTriggerPulseLength();
		}

		return samEnvWidths;
	}

	private void startTFG() throws DeviceException {
		daserver.sendCommand("tfg arm");
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
