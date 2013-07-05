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
import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.ExperimentLocation;
import gda.device.detector.ExperimentLocationUtils;
import gda.device.detector.ExperimentStatus;
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
		return xhDet.getLoadedParameters().getTotalNumberOfFrames();
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

		checkForInterrupts();
		if (!isChild()) {
			currentPointCount = -1;
		}

		xhDet.collectData();
		// sleep for a moment to allow collection to start
		Thread.sleep(250);

		ExperimentLocation lastReadLoc = new ExperimentLocation(0, 0, 0);
		try {
			// ExperimentLocation finalFrame = getFinalFrameLoc();
			ExperimentStatus progressData = xhDet.fetchStatus();
			while (!collectionFinished(progressData)) {
				if (canReadoutMoreFrames(progressData, lastReadLoc)) {
					createDataPoints(progressData, lastReadLoc);
					lastReadLoc = progressData.loc;
				}
				progressData = xhDet.fetchStatus();
				Thread.sleep(100);
				checkForInterrupts();
			}
		} catch (Exception e) {
			// scan has been aborted, so stop the collection and let the scan write out the rest of the data point which
			// have been collected so far
			xhDet.stop();
			if (!(e instanceof InterruptedException)) {
				throw e;
			}
		}

		// have we read all the frames?
		readoutRestOfFrames(lastReadLoc);
	}

	private Boolean collectionFinished(ExperimentStatus progressData) {
		//FIXME this will fail when collection having a delay as this returns idle,0,0,0!!
		return progressData.detectorStatus == Detector.IDLE && progressData.loc.groupNum <= 0
				&& progressData.loc.frameNum <= 0 && progressData.loc.scanNum <= 0;
	}

	private Boolean canReadoutMoreFrames(ExperimentStatus progressData, ExperimentLocation lastReadLoc) {

		if (progressData.loc.groupNum > lastReadLoc.groupNum) {
			return true;
		} else if (progressData.loc.groupNum == lastReadLoc.groupNum
				&& progressData.loc.frameNum > lastReadLoc.frameNum) {
			return true;
		}
		return false;
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
			return xhDet.getLoadedParameters().getTotalNumberOfFrames();
		}
		return getParent().getTotalNumberOfPoints();
	}

	private void readoutRestOfFrames(ExperimentLocation lastReadLoc) throws Exception {
		int absLowFrame = ExperimentLocationUtils.getAbsoluteFrameNumber(xhDet.getLoadedParameters(), lastReadLoc);
		if (absLowFrame == getTotalNumberOfPoints()) {
			return;
		}
//		absLowFrame++;
		int absHighFrame = getTotalNumberOfPoints() - 1;
		createDataPoints(absLowFrame, absHighFrame);
	}

	private void createDataPoints(ExperimentStatus progressData, ExperimentLocation lastReadLoc) throws Exception {
		
		
		int absLowFrame = ExperimentLocationUtils.getAbsoluteFrameNumber(xhDet.getLoadedParameters(), lastReadLoc);
//		absLowFrame++;
		int absHighFrame = ExperimentLocationUtils
				.getAbsoluteFrameNumber(xhDet.getLoadedParameters(), progressData.loc);
		// something wrong with the logic here!
//		if (progressData.detectorStatus != Detector.IDLE)
			absHighFrame--;
		createDataPoints(absLowFrame, absHighFrame);
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