/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.XHDetector;
import gda.device.scannable.ScannableUtils;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Bespoke scan for I20 based on the ContinuousScan. Operates the XH detector and nothing else but utilises the GDA
 * infrastructure for writing files & making data available for display by the UI.
 * <p>
 * In principal this could work within multi-dimensional scans...
 */
public class SimpleContinuousScan extends ConcurrentScanChild {

	private static final Logger logger = LoggerFactory.getLogger(SimpleContinuousScan.class);
	private XHDetector xhDet;

	public SimpleContinuousScan(XHDetector xhDet) {
		setMustBeFinal(true);

		this.xhDet = xhDet;
		allDetectors.add(xhDet);

		super.setUp();
	}

	@Override
	public int getDimension() {
		return xhDet.getTotalNumberOfFrames();
	}

	/**
	 * returns null as nothing is moved
	 */
	@Override
	protected ScanObject isScannableToBeMoved(Scannable scannable) {
		return null;
	}

	@Override
	public void doCollection() throws Exception {

		// for performance, see how many frames to read at any one time
		int maxFrameRead = xhDet.maximumReadFrames();

		checkForInterrupts();
		if (!isChild()) {
			currentPointCount = -1;
		}

		xhDet.collectData();

		int highestFrameNumberRead = -1;

		int numberOfFramesInExperiment = xhDet.getTotalNumberOfFrames();

		try {
			while (highestFrameNumberRead < numberOfFramesInExperiment - 1) {
				// sleep for a second
				Thread.sleep(100);
				checkForInterrupts();

				// get lowest number of frames from all detectors
				int frameNumberReached = xhDet.getNumberFrames();

				// do not collect more than 20 frames at any one time
				if (frameNumberReached - highestFrameNumberRead > maxFrameRead) {
					frameNumberReached = highestFrameNumberRead + maxFrameRead;
				}

				// get data from detectors for that frame and create an sdp and send it out
				if (frameNumberReached > -1 && frameNumberReached > highestFrameNumberRead) {
					createDataPoints(highestFrameNumberRead + 1, frameNumberReached);
				}
				highestFrameNumberRead = frameNumberReached;
				logger.info("number of frames completed:" + new Integer(frameNumberReached + 1));
			}
		} catch (InterruptedException e) {
			// scan has been aborted, so stop the collection and let the scan write out the rest of the data point which
			// have been collected so far
			xhDet.stop();
		}

		// have we read all the frames?
		if (highestFrameNumberRead == xhDet.getTotalNumberOfFrames() - 1) {
			return;
		}

		// collect the rest of the frames and send the resulting sdp's out
		while (highestFrameNumberRead < xhDet.getTotalNumberOfFrames() - 1) {
			int nextFramesetEnd = highestFrameNumberRead + maxFrameRead;
			if (nextFramesetEnd > xhDet.getTotalNumberOfFrames() - 1) {
				nextFramesetEnd = xhDet.getTotalNumberOfFrames() - 1;
			}
			createDataPoints(highestFrameNumberRead + 1, nextFramesetEnd);
			highestFrameNumberRead = nextFramesetEnd;
		}
	}

	@Override
	protected void endScan() throws DeviceException {
		super.endScan();
	}

	@Override
	public String getCommand() {
		return xhDet.getName();
	}

	@Override
	public int getTotalNumberOfPoints() {
		if (!isChild()) {
			return xhDet.getTotalNumberOfFrames();
		}
		return getParent().getTotalNumberOfPoints();
	}

	/**
	 * @param lowFrame
	 *            - where 0 is the first frame
	 * @param highFrame
	 *            - where number scan points -1 is the last frame
	 * @throws Exception
	 */
	@SuppressWarnings("deprecation")
	private void createDataPoints(int lowFrame, int highFrame) throws Exception {

		// readout the correct frame from the detectors
		NexusTreeProvider[] detData;
		logger.info("reading data from detectors from frames " + lowFrame + " to " + highFrame);
		detData = xhDet.readFrames(lowFrame, highFrame);
		logger.info("data read successfully");

		for (int thisFrame = lowFrame; thisFrame <= highFrame; thisFrame++) {
			checkForInterrupts();
			currentPointCount++;
			this.stepId = new ScanStepId(xhDet.getName(), currentPointCount);
			ScanDataPoint thisPoint = new ScanDataPoint();
			thisPoint.setUniqueName(name);
			thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());
			thisPoint.setStepIds(getStepIds());
			thisPoint.setScanPlotSettings(getScanPlotSettings());
			thisPoint.setScanDimensions(getDimensions());
			thisPoint.addDetector(xhDet);
			thisPoint.addDetectorData(detData[thisFrame - lowFrame], ScannableUtils.getExtraNamesFormats(xhDet));
			thisPoint.setCurrentPointNumber(this.currentPointCount);
			thisPoint.setNumberOfPoints(getTotalNumberOfPoints());
			thisPoint.setInstrument(instrument);
			thisPoint.setCommand(getCommand());
			thisPoint.setScanIdentifier(getDataWriter().getCurrentScanIdentifier());

			// then write data to data handler
			getDataWriter().addData(thisPoint);

			checkForInterrupts();

			// update the filename (if this was the first data point and so filename would never be defined until first
			// data added
			thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());

			// then notify IObservers of this scan (e.g. GUI panels)
			notifyServer(thisPoint);
		}
	}

}