/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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
import java.util.List;
import java.util.function.Supplier;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jython.InterfaceProvider;

/**
 * Runnable that can be used to collect detector data in a background thread.
 * It monitors the number of frames of detector data available using {@link#getNumAvailableFrames()}, and when enough frames
 * for a new spectrum are available, it collects the spectrum data and writes it to the Nexus file
 * using {@link #collectData()}.
 * Refactored from inner class in {@link TurboXasScan}.
*/
public abstract class DetectorReadout implements Runnable {
	private static final Logger logger = LoggerFactory.getLogger(DetectorReadout.class);

	private int numFramesPerSpectrum;
	private int numSpectraCollected;
	private int totalNumSpectraToCollect;

	private int currentTimingGroupIndex=0;
	private int numSpectraCollectedForGroup=0;
	private int lastFrameRead;
	private boolean runMethodFinished = false;

	private int pollIntervalMillis;

	private List<TurboSlitTimingGroup> timingGroups;

	public DetectorReadout() {
		timingGroups = new ArrayList<TurboSlitTimingGroup>();
		pollIntervalMillis=500;
	}

	/** Return the highest frame number common to all detectors to be read out */
	public abstract int getNumAvailableFrames() throws Exception;

	/** Collect data from all the detectors to be read out */
	public abstract void collectData() throws Exception;

	public abstract boolean detectorsAreBusy() throws Exception;

	@Override
	public void run() {

		currentTimingGroupIndex=0;
		numSpectraCollectedForGroup=0;
		numSpectraCollected=0;

		logger.debug("Readout loop started");
		try {
			while (numSpectraCollected < totalNumSpectraToCollect) {

				int numAvailableFrames = getNumAvailableFrames();

				int numNewFrames = numAvailableFrames-lastFrameRead;

				logger.debug("{} frames of data available, {} new frames, last frame read = {}", numAvailableFrames, numNewFrames, lastFrameRead);

				// Break out of while loop if frames get cleared (e.g. due to 'stop scan' button being pressed)
				if (numAvailableFrames==0 && !detectorsAreBusy()) {
					logger.debug("Exiting readout loop - no frames of data available and detectors are not busy.");
					break;
				}

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

					logger.debug("Collecting data : timing group {}, spectrum {} of {}",
							currentTimingGroupIndex, numSpectraCollectedForGroup, timingGroups.get(currentTimingGroupIndex).getNumSpectra());

					String msg = "\tTiming group "+(currentTimingGroupIndex+1)+" : spectrum "+(numSpectraCollectedForGroup)+
							" of "+timingGroups.get(currentTimingGroupIndex).getNumSpectra();
					InterfaceProvider.getTerminalPrinter().print(msg);

					collectData();

					numSpectraCollected++;
					lastFrameRead += numFramesPerSpectrum;
				}

				// Wait a short time for more frames of data to become available before looping again
				if ( (numAvailableFrames - lastFrameRead) < numFramesPerSpectrum ) {
					Thread.sleep(pollIntervalMillis);
				}
			}
		} catch (Exception e) {
			logger.error("ReadoutThread encountered an error during data collection.", e);
		} finally {
			logger.debug("ReadoutThread finished.");
			runMethodFinished = true;
		}
	}

	/**
	 * Wait up to maxWaitTime seconds for frameNumber frames of data to be collected.
	 * @param frameNumber
	 * @param maxWaitTime
	 * @throws InterruptedException
	 */
	public void waitForFrame(int frameNumber, double maxWaitTimeSecs) throws InterruptedException {
		logger.info("Waiting up to {} seconds for {} frames to be collected", maxWaitTimeSecs, frameNumber);
		waitWhileConditionIsTrue(() -> {return lastFrameRead < frameNumber;}, maxWaitTimeSecs);
	}

	/**
	 * Wait until all spectra have been collected.
	 * @throws InterruptedException
	 */
	public void waitForAllSpectra(double maxWaitTimeSecs) throws InterruptedException {
		logger.info("Waiting up to {} seconds for all {} spectra to be collected", maxWaitTimeSecs, totalNumSpectraToCollect);
		waitWhileConditionIsTrue( () -> {return !runMethodFinished;}, maxWaitTimeSecs);
	}

	/**
	 * Wait in a loop while the condition returns true. Waiting will continue up to maximum time of maxWaitTime (seconds);
	 * Time interval between loop repetitions is {@link #pollIntervalMillis}.
	 *
	 * @param condition - Supplier with condition to be evaluated
	 * @param maxWaitTimeSecs
	 * @throws InterruptedException
	 */
	private void waitWhileConditionIsTrue(Supplier<Boolean> condition, double maxWaitTimeSecs) throws InterruptedException {
		int timeWaited = 0;
		while(condition.get() && timeWaited<maxWaitTimeSecs*1000) {
			Thread.sleep(pollIntervalMillis);
			timeWaited += pollIntervalMillis;
		}
	}

	public int getCurrentTimingGroupIndex() {
		return currentTimingGroupIndex;
	}

	public int getNumSpectraCollectedForGroup() {
		return numSpectraCollectedForGroup;
	}

	public int getNumSpectraCollected() {
		return numSpectraCollected;
	}

	public int getLastFrameRead() {
		return lastFrameRead;
	}

	public void setLastFrameRead(int lastFrameRead) {
		this.lastFrameRead = lastFrameRead;
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

	public void setTimingGroups(final List<TurboSlitTimingGroup> timingGroups) {
		this.timingGroups = timingGroups;
	}

	public int getPollIntervalMillis() {
		return pollIntervalMillis;
	}

	public void setPollIntervalMillis(int pollIntervalMillis) {
		this.pollIntervalMillis = pollIntervalMillis;
	}
}
