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

	// ContinuouslyScannable qscanAxis;
	// private Double start;
	// private Double stop;
	// private Double time;
	// private Integer numberScanpoints;
	private XHDetector xhDet;

//	/**
//	 * 
//	 */
//	public SimpleContinuousScan() {
//		super();
//		setMustBeFinal(true);
//	}

	public SimpleContinuousScan(XHDetector xhDet) {
		setMustBeFinal(true);
		// allScannables.add(energyScannable);
		// double step = (stop - start) / (numberPoints - 1);
		// ImplicitScanObject firstScanObject = new ImplicitScanObject(energyScannable, start, stop, step);
		// firstScanObject.calculateScanPoints();
		// allScanObjects.add(firstScanObject);
		// qscanAxis = energyScannable;
		//
		// this.start = start;
		// this.stop = stop;
		// this.numberScanpoints = numberPoints;
		// this.time = time;

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
				Thread.sleep(1000);
				checkForInterrupts();

				// get lowest number of frames from all detectors
				int frameNumberReached = xhDet.getNumberFrames() -1;

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

	// private int getMaxFrameRead() throws DeviceException {
	// int smallestFrameLimit = Integer.MAX_VALUE;
	// for (BufferedDetector detector : qscanDetectors) {
	// int thisDetMax = detector.maximumReadFrames();
	// if (thisDetMax < smallestFrameLimit) {
	// smallestFrameLimit = thisDetMax;
	// }
	// }
	// return smallestFrameLimit;
	// }

	@Override
	protected void endScan() throws DeviceException {
		// InterfaceProvider.getTerminalPrinter().print("continuous scan end scan is called");
		// qscanAxis.continuousMoveComplete();
		// for (BufferedDetector detector : qscanDetectors) {
		// detector.setContinuousMode(false);
		// }
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
		try {
			detData = xhDet.readFrames(lowFrame, highFrame);
			// for (BufferedDetector detector : qscanDetectors) {
			// Object[] data = detector.readFrames(lowFrame, highFrame);
			// detData.put(detector.getName(), data);
			// }
		} catch (DeviceException e1) {
			throw new DeviceException("Exception while reading out frames " + lowFrame + " to " + highFrame + ": "
					+ e1.getMessage(), e1);
		}
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

			// add the scannables. For the qscanAxis scannable calculate the position.
			// double stepSize = (stop - start) / (numberScanpoints - 1);
			/*
			 * thisPoint.addScannable(qscanAxis); thisPoint.addScannablePosition(start + (thisFrame - 1) * stepSize,
			 * qscanAxis.getOutputFormat()); for (Scannable scannable : allScannables) { if
			 * (!scannable.equals(qscanAxis)) { thisPoint.addScannable(scannable);
			 * thisPoint.addScannablePosition(scannable.getPosition(), scannable.getOutputFormat()); } }
			 */
			// for (Scannable scannable : allScannables) {
			// if (scannable.equals(qscanAxis)) {
			// thisPoint.addScannable(qscanAxis);
			//
			// try {
			// thisPoint.addScannablePosition(qscanAxis.calculateEnergy(thisFrame), qscanAxis.getOutputFormat());
			// } catch (DeviceException e) {
			// thisPoint.addScannablePosition(start + (thisFrame - 1) * stepSize, qscanAxis.getOutputFormat());
			// }
			//
			// }
			// else {
			// if (scannable.getOutputFormat().length == 0) {
			// handleZeroInputExtraNameDevice(scannable);
			// } else {
			// thisPoint.addScannable(scannable);
			// thisPoint.addScannablePosition(scannable.getPosition(), scannable.getOutputFormat());
			// }
			// }

			// }
			// readout the correct frame from the detectors
			// for (BufferedDetector detector : qscanDetectors) {
			// Object data = detData.get(detector.getName())[thisFrame - lowFrame];
			// if (data != null) {
			thisPoint.addDetector(xhDet);
			thisPoint.addDetectorData(detData[thisFrame - lowFrame], ScannableUtils.getExtraNamesFormats(xhDet));
			// }
			// }

			// Set some parameters in the data point.
			// (This is implemented as setters at the moment, as I didn't want to risk changing the constructor
			// statement above and risk breaking the scanning system!)
			thisPoint.setCurrentPointNumber(this.currentPointCount);
			thisPoint.setNumberOfPoints(getTotalNumberOfPoints());
			thisPoint.setInstrument(instrument);
			thisPoint.setCommand(getCommand());
			thisPoint.setScanIdentifier(getDataWriter().getCurrentScanIdentifier());

			// then write data to data handler
			getDataWriter().addData(thisPoint);

			checkForInterrupts();

			// update the filename (if this was the first data point and so
			// filename would never be defined until first data added
			thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());

			// then notify IObservers of this scan (e.g. GUI panels)
			notifyServer(thisPoint);
			// this new command re-reads the detectors - so do not want that!!
			// scanDataPointPipeline.populatePositionsAndDataAndPublish(thisPoint);
		}
	}

}