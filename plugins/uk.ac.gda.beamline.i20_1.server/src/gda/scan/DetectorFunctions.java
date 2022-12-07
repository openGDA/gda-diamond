/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.TimeoutException;

import org.eclipse.dawnsci.analysis.api.io.ScanFileHolderException;
import org.eclipse.dawnsci.nexus.NexusException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.swmr.SwmrFileReader;
import gda.device.ContinuousParameters;
import gda.device.DeviceException;
import gda.device.detector.BufferedDetector;
import gda.device.detector.countertimer.BufferedScaler;
import gda.device.zebra.controller.Zebra;
import gda.device.zebra.controller.impl.ZebraDummy;
import uk.ac.gda.devices.detector.xspress3.TRIGGER_MODE;
import uk.ac.gda.devices.detector.xspress3.Xspress3BufferedDetector;
import uk.ac.gda.devices.detector.xspress3.Xspress3Controller;
import uk.ac.gda.devices.detector.xspress3.controllerimpl.EpicsXspress3Controller;

/**
 * Detector related functions refactored from {@link TurboXasScan}. Contains methods to :
 * <li> Get the highest available frame across all detectors ({@link #getNumAvailableFrames()}).
 * <li> Prepare detectors for collection at the start of a scan ({@link #prepareDetectors(ContinuousParameters, int, int, int)}).
 * <li> Wait for Xspress3 detector to finish writing it's Hdf file ({@link #waitForXspress3(double)}).
 * <li> Get the total number of pulses captured by the zebra(s) ({@link #getNumCapturedZebraPulses()});
 * The detectors being used for the scan should first be set with {@link #setDetectors(BufferedDetector[])} before using the above functions.
 *
 */
public class DetectorFunctions  {

	private static final Logger logger = LoggerFactory.getLogger(DetectorFunctions.class);

	private BufferedDetector[] detectors;
	private Zebra zebra1 = null;
	private Zebra zebra2 = null;
	private boolean useTwoZebras;

	private SwmrFileReader xspress3FileReader;
	private Xspress3BufferedDetector xspress3BufferedDetector;
	private Map<String, String> xspressAttributeMap = Collections.emptyMap();
	private String pathToAttributeData = "/entry/instrument/NDAttributes";

	private boolean useXspress3SwmrReadout = true;

	private int totalNumReadoutsForDummy = 0;


	/**
	 * @return Maximum available frame that can be read from all detectors (BufferedScaler and Xspress3Detector)
	 * @throws DeviceException
	 * @throws ScanFileHolderException
	 * @throws NexusException
	 */
	public int getNumAvailableFrames() throws Exception {
		int minNumFrames = Integer.MAX_VALUE;
		for (BufferedDetector detector : detectors) {
			int numFramesAvailable = detector.getNumberFrames();
			if (detector instanceof BufferedScaler) {
				numFramesAvailable = getNumTfgScalerFrames((BufferedScaler) detector);
			} else if (detector instanceof Xspress3BufferedDetector) {
				numFramesAvailable = getNumXspress3Frames((Xspress3BufferedDetector) detector);
			}
			logger.debug("Number of frames of data available for {} : {}", detector.getName(), numFramesAvailable);
			minNumFrames = Math.min(minNumFrames, numFramesAvailable);
		}
		logger.debug("Number of frames of data available to readout : {}", minNumFrames);
		return minNumFrames;
	}

	/**
	 *
	 * @return Total number of captured pulses by zebra(s) used from scan
	 * @throws DeviceException
	 */
	public int getNumCapturedZebraPulses() throws DeviceException {
			// In dummy mode, just return total number of points that should have been captured
		if (zebra1 instanceof ZebraDummy) {
			return totalNumReadoutsForDummy;
		}

		try {
			int numPulsesZebra1 = zebra1.getPCNumberOfPointsCaptured();
			int numPulsesZebra2 = 0;
			if (useTwoZebras && zebra2 != null) {
				numPulsesZebra2 = zebra2.getPCNumberOfPointsCaptured();
			}
			logger.debug("Number of pulses captured by zebras : zebra1 = {}, zebra2 = {}", numPulsesZebra1,	numPulsesZebra2);
			return numPulsesZebra1 + numPulsesZebra2;
		} catch (Exception e) {
			throw new DeviceException("Problem getting number of captured pulses from zebra(s)", e);
		}
	}

	/**
	 * Wait for a zebra to capture at least the specified number of points
	 * @param zebra
	 * @param numPoints
	 * @param timeOut
	 * @throws IllegalStateException
	 * @throws TimeoutException
	 * @throws IOException
	 * @throws InterruptedException
	 */
	private void waitForZebra(Zebra zebra, int numPoints, int timeOut) throws TimeoutException, IOException, InterruptedException {
		logger.debug("Waiting up to {} secs for zebra to capture >= {} points...", timeOut, numPoints);
		zebra.getNumberOfPointsCapturedPV().waitForValue(numCaptured -> numCaptured >= numPoints, timeOut);
		logger.debug("Captured >= {} points", numPoints);
	}

	/**
	 * Wait for zebra(s) to capture number of points each corresponding to a number of spectra
	 * @param numSpectra
	 * @param numPointsPerSpectrum
	 * @param timeOutSeconds
	 * @throws IllegalStateException
	 * @throws TimeoutException
	 * @throws IOException
	 * @throws InterruptedException
	 */
	public void waitForCapturedZebraPulses(int numSpectra, int numPointsPerSpectrum, int timeOutSeconds) throws TimeoutException, IOException, InterruptedException {
		if (!useTwoZebras) {
			int capturedPoints = numSpectra * numPointsPerSpectrum;
			logger.debug("Waiting for zebra1 to capture points for {} spectra", numSpectra);
			waitForZebra(zebra1, capturedPoints, timeOutSeconds);
			return;
		}

		int numSpectraZebra1 = numSpectra/2 + numSpectra%2;
		int numSpectraZebra2 = numSpectra - numSpectraZebra1;
		logger.debug("Waiting for (zebra1, zebra2) to capture points for ({}, {}) spectra...", numSpectraZebra1, numSpectraZebra2);
		waitForZebra(zebra1, numSpectraZebra1*numPointsPerSpectrum, timeOutSeconds);
		logger.debug("Zebra1 finished, now waiting for zebra2...");
		waitForZebra(zebra2, numSpectraZebra2*numPointsPerSpectrum, timeOutSeconds);
	}

	/**
	 *
	 * @param detector
	 * @return Number of scaler frames available on Tfg
	 * @throws DeviceException
	 */
	private int getNumTfgScalerFrames(BufferedScaler detector) throws DeviceException {
		// For Tfg scalers, convert to absolute frame number in whole experiment
		// if using cycles.
		// (scaler readout will convert back to 'frame within cycle' as
		// necessary)
		int numFramesAvailable = detector.getNumberFrames();
		if (detector.getNumCycles() > 1) {
			int currentCycle = detector.getCurrentCycle(); // cycle counting
															// starts from 0
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
	 * @return Number of frames of Hdf data available from Xspress3 (based on
	 * frame ounter PV, or number of frames in hdf file if xspress3FileReader is
	 * set).
	 * @throws DeviceException
	 * @throws ScanFileHolderException
	 * @throws NexusException
	 */
	private int getNumXspress3Frames(Xspress3BufferedDetector detector)
			throws DeviceException, ScanFileHolderException, NexusException {
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
	 * Wait for Xspress detector to finish writing hdf file to disk.
	 * @param maxWaitTimeSecs
	 * @return
	 * @throws InterruptedException
	 * @throws DeviceException
	 */
	public double waitForXspress3(double maxWaitTimeSecs) throws InterruptedException, DeviceException {
		double timeWaited = 0;
		long pollIntervalMillis = 500;

		if (xspress3BufferedDetector != null) {
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
		return timeWaited;
	}

	/**
	 * Prepare detectors for a turboXAS scan (i.e. clear the memory, set the number of frames to collect, and arm)
	 * @param params
	 * @param numSpectra
	 * @param numCycles
	 * @param numReadoutsPerSpectra
	 * @throws Exception
	 */
	public void prepareDetectors(ContinuousParameters params, int numSpectra, int numCycles, int numReadoutsPerSpectra) throws Exception {
		totalNumReadoutsForDummy = numSpectra * numReadoutsPerSpectra;
		for (BufferedDetector detector : detectors) {
			detector.clearMemory();
			if (detector instanceof BufferedScaler) {
				setScalerMode((BufferedScaler)detector);
				((BufferedScaler)detector).setNumCycles(numCycles);
			}
			detector.setContinuousParameters(params);
			detector.setContinuousMode(true);
			if (detector instanceof Xspress3BufferedDetector) {
				xspress3BufferedDetector = (Xspress3BufferedDetector)detector;
				prepareXSpress3(numSpectra, numReadoutsPerSpectra);
			}
		}
	}

	public boolean isTfgArmed() throws DeviceException {
		Optional<BufferedScaler> scaler = Arrays.stream(detectors).
				filter(d -> d instanceof BufferedScaler).
				map(d -> (BufferedScaler)d).
				findFirst();
		return scaler.isPresent() && scaler.get().isWaitingForTrigger();
	}

	public Xspress3BufferedDetector getXspress3Detector() {
		for (BufferedDetector detector : detectors) {
			if (detector instanceof Xspress3BufferedDetector) {
				return (Xspress3BufferedDetector) detector;
			}
		}
		return null;
	}

	private void setScalerMode(BufferedScaler detector) throws DeviceException {
		// Try to set scalert64 mode first, otherwise Scalers seem to return junk. imh 14/9/2016
		Object result = detector.getDaserver().sendCommand("tfg setup-cc-mode scaler64");
		if (!result.toString().equals("0")) {
			logger.info("Problem setting Tfg to use scaler64 mode - scaler readout may not work correctly...");
		}
	}

	/**
	 * Prepeare XPress3 for collection:
	 * set number of frames to collect (for both the detector and hdf plugin),
	 * set trigger mode and next file number.
	 * @param numReadouts
	 * @throws Exception
	 */
	private void prepareXSpress3(int numSpectra, int numReadoutsPerSpectrum) throws Exception{
		if (xspress3BufferedDetector != null) {
			Xspress3Controller controller = xspress3BufferedDetector.getController();

			// Last frame is missing (no rising edge after final captured pulse to end collection of final Xspress3 frame).
			int totNumReadouts = numSpectra*numReadoutsPerSpectrum - 1;

			controller.doStopSavingFiles();
			controller.doStop();
			controller.doReset();

			// set the HDF writer extra dimensions, so that MCA data has outer dimensions = [numSpectra, numReadoutsPerSpectrum]
			controller.configureHDFDimensions(new int[] { numReadoutsPerSpectrum, numSpectra });

			controller.setNumFramesToAcquire(totNumReadouts);
			controller.setHDFNumFramesToAcquire(totNumReadouts);
			controller.setTriggerMode(TRIGGER_MODE.TTl_Veto_Only);


			// controller.doReset();
			controller.setNextFileNumber(0);
			controller.setSavingFiles(true);
			controller.doStart();

			// create reader for loading data from Swmr file - only if using real hardware
			if (useXspress3SwmrReadout && controller instanceof EpicsXspress3Controller) {
				xspress3FileReader = new SwmrFileReader();
				if (xspressAttributeMap.isEmpty()) {
					xspressAttributeMap = createXspressAttributeMap(xspress3BufferedDetector);
				}
				xspressAttributeMap.entrySet().forEach( entry -> xspress3FileReader.addDatasetToRead(entry.getKey(), entry.getValue()));
			}
		}
	}

	private Map<String, String> createXspressAttributeMap(Xspress3BufferedDetector detector) {
		Map<String, String> map = new HashMap<>();
		for(int channel=0; channel<detector.getNumberOfElements(); channel++) {
			map.put(String.format("FF_%d", channel+1), String.format("%s/Chan%dSca%d", pathToAttributeData, channel+1, 5));
		}
		return map;
	}

	public void setZebra1(Zebra zebra1) {
		this.zebra1 = zebra1;
	}

	public void setZebra2(Zebra zebra2) {
		this.zebra2 = zebra2;
	}

	public boolean isUseTwoZebras() {
		return useTwoZebras;
	}

	public void setUseTwoZebras(boolean useTwoZebras) {
		this.useTwoZebras = useTwoZebras;
	}

	public SwmrFileReader getXspress3FileReader() {
		return xspress3FileReader;
	}

	public void setDetectors(BufferedDetector[] detectors) {
		this.detectors = detectors;
	}

	public boolean isUseXspress3SwmrReadout() {
		return useXspress3SwmrReadout;
	}

	public void setUseXspress3SwmrReadout(boolean useXspress3SwmrReadout) {
		this.useXspress3SwmrReadout = useXspress3SwmrReadout;
	}

}
