/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

import static gda.jython.InterfaceProvider.getJythonServerNotifer;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.Scannable;
import gda.device.detector.ExperimentLocationUtils;
import gda.device.detector.ExperimentStatus;
import gda.device.detector.StripDetector;
import gda.device.scannable.FrameIndexer;
import gda.device.scannable.ScannableUtils;
import gda.observable.IObserver;
import gda.scan.ede.EdeScanProgressBean;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.position.EdeScanPosition;

import java.util.List;
import java.util.Vector;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

/**
 * Runs a single set of timing groups for EDE through the XSTRIP DAServer interface.
 * <p>
 * So this: moves sample to correct position, opens/closes shutter, runs the timing groups through the TFG unit and
 * writes data to given Nexus file.
 * <p>
 * Also holds data in memory for quick retrieval for online data.
 */
public class EdeScan extends ConcurrentScanChild {

	private static final Logger logger = LoggerFactory.getLogger(EdeScan.class);

	private final StripDetector theDetector;
	// also keep SDPs in memory for quick retrieval for online data reduction and storage to ASCII files.
	private final Vector<ScanDataPoint> rawData = new Vector<ScanDataPoint>();

	private EdeScanParameters scanParameters;
	private EdeScanPosition motorPositions;
	private EdeScanType scanType;
	private FrameIndexer indexer = null;
	private IObserver progressUpdater;

	/**
	 * @param scanParameters
	 *            - timing parameters of the data collection
	 * @param motorPositions
	 *            -
	 * @param scanType
	 * @param theDetector
	 * @param repetitionNumber
	 *            - if this is a negative number then frame index columns will not be added to the output. Useful for
	 *            single spectrum scans where such indexing is meaningless.
	 */
	public EdeScan(EdeScanParameters scanParameters, EdeScanPosition motorPositions, EdeScanType scanType,
			StripDetector theDetector, Integer repetitionNumber) {
		setMustBeFinal(true);
		this.scanParameters = scanParameters;
		this.motorPositions = motorPositions;
		this.scanType = scanType;
		this.theDetector = theDetector;
		allDetectors.add(theDetector);
		if (repetitionNumber >= 0) {
			// then use indexer to report progress of scan in data
			indexer = new FrameIndexer(scanType, motorPositions.getType(), repetitionNumber);
			indexer.setName(theDetector.getName() + "_progress");
			allScannables.add(indexer);
		}
		super.setUp();
	}

	@Override
	public String toString() {
		return "EDE scan - type:" + scanType.toString() + " " + motorPositions.getType().toString();
	}

	public String getHeaderDescription() {
		String desc = scanType.toString() + " " + motorPositions.getType().toString() + " scan with " + scanParameters.getGroups().size() + " timing groups";
		for (int index = 0; index < scanParameters.getGroups().size(); index++){
			TimingGroup group = scanParameters.getGroups().get(index);
			desc += "\n#Group "+ index + " "+group.getHeaderDescription();
		}
		return desc;
	}

	@Override
	public int getDimension() {
		return scanParameters.getTotalNumberOfFrames();
	}

	public int getNumberOfAvailablePoints() {
		return rawData.size();
	}

	public void setProgressUpdater(IObserver progressUpdater) {
		this.progressUpdater = progressUpdater;
	}

	public List<ScanDataPoint> getDataPoints(int firstFrame, int lastFrame) {
		if (lastFrame >= getNumberOfAvailablePoints()) {
			throw new IllegalArgumentException("Only " + getNumberOfAvailablePoints() + " are available!");
		}
		// add one as I want this methods arguments to be inclusive, but the List.subList method's second argument is
		// exclusive
		return rawData.subList(firstFrame, lastFrame + 1);
	}

	@Override
	protected ScanObject isScannableToBeMoved(Scannable scannable) {
		return null;
	}

	@Override
	public void doCollection() throws Exception {
		validate();
		theDetector.loadParameters(scanParameters);
		motorPositions.moveIntoPosition();
		checkForInterrupts();
		if (!isChild()) {
			currentPointCount = -1;
		}

		theDetector.collectData();
		// sleep for a moment to allow collection to start
		Thread.sleep(250);

		Integer nextFrameToRead = 0;
		try {
			ExperimentStatus progressData = theDetector.fetchStatus();
			Integer currentFrame = ExperimentLocationUtils.getAbsoluteFrameNumber(scanParameters, progressData.loc);
			while (!collectionFinished(progressData)) {
				// Review here we assume currentFrame - 1 is ready to read
				if (currentFrame > nextFrameToRead) {
					createDataPoints(nextFrameToRead, currentFrame - 1);
					nextFrameToRead = currentFrame;
				}
				// Why do we need to fetch status twice ?
				progressData = theDetector.fetchStatus();
				Thread.sleep(100);
				checkForInterrupts();
				progressData = theDetector.fetchStatus();
				currentFrame = ExperimentLocationUtils.getAbsoluteFrameNumber(scanParameters, progressData.loc);
			}
		} catch (Exception e) {
			// scan has been aborted, so stop the collection and let the scan write out the rest of the data point which
			// have been collected so far
			theDetector.stop();
			throw e;
		} finally {
			// have we read all the frames?
			readoutRestOfFrames(nextFrameToRead);
		}

	}

	private Boolean collectionFinished(ExperimentStatus progressData) {
		// TODO test this actually works with hardware!!!
		return progressData.toString().contains("Idle");
	}

	@Override
	public String getCommand() {
		return theDetector.getName();
	}

	@Override
	public int getTotalNumberOfPoints() {
		if (!isChild()) {
			return scanParameters.getTotalNumberOfFrames();
		}
		return getParent().getTotalNumberOfPoints();
	}

	private void validate() throws IllegalArgumentException {
		if (motorPositions == null) {
			throw new IllegalArgumentException("Cannot run EdeScan as sample motor positions have not been supplied");
		}
		if (scanParameters == null) {
			throw new IllegalArgumentException("Cannot run EdeScan as scan parameters have not been supplied");
		}
	}

	private void readoutRestOfFrames(Integer nextFrameToRead) throws Exception {
		int absLowFrame = nextFrameToRead;
		if (absLowFrame == getDimension()) {
			return;
		}
		int absHighFrame = getDimension() - 1;
		createDataPoints(absLowFrame, absHighFrame);
	}

	/**
	 * @param lowFrame
	 *            - where 0 is the first frame
	 * @param highFrame
	 *            - where number scan points -1 is the last frame
	 * @throws Exception
	 */
	private void createDataPoints(int lowFrame, int highFrame) throws Exception {
		// readout the correct frame from the detectors
		NexusTreeProvider[] detData;
		logger.info("reading data from detectors from frames " + lowFrame + " to " + highFrame);
		detData = theDetector.readFrames(lowFrame, highFrame);
		logger.info("data read successfully");

		for (int thisFrame = lowFrame; thisFrame <= highFrame; thisFrame++) {
			checkForInterrupts();
			currentPointCount++;
			stepId = new ScanStepId(theDetector.getName(), currentPointCount);

			ScanDataPoint thisPoint = new ScanDataPoint();
			thisPoint.setUniqueName(name);
			thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());
			thisPoint.setStepIds(getStepIds());
			thisPoint.setScanPlotSettings(getScanPlotSettings());
			thisPoint.setScanDimensions(getDimensions());
			if (indexer != null) {
				indexer.setGroup(ExperimentLocationUtils.getGroupNum(scanParameters, thisFrame));
				indexer.setFrame(ExperimentLocationUtils.getFrameNum(scanParameters, thisFrame));
				thisPoint.addScannable(indexer);
				thisPoint.addScannablePosition(indexer.getPosition(), indexer.getOutputFormat());
			}
			thisPoint.addDetector(theDetector);
			thisPoint.addDetectorData(detData[thisFrame - lowFrame], ScannableUtils.getExtraNamesFormats(theDetector));
			thisPoint.setCurrentPointNumber(currentPointCount);
			thisPoint.setNumberOfPoints(getTotalNumberOfPoints());
			thisPoint.setInstrument(instrument);
			thisPoint.setCommand(getCommand());
			thisPoint.setScanIdentifier(getDataWriter().getCurrentScanIdentifier());

			// then write data to data handler
			storeAndBroadcastSDP(thisFrame, thisPoint);
			getDataWriter().addData(thisPoint);

			checkForInterrupts();

			// update the filename (if this was the first data point and so filename would never be defined until first
			// data added
			thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());

			// then notify IObservers of this scan (e.g. GUI panels)
			getJythonServerNotifer().notifyServer(this, thisPoint);
		}
	}

	private void storeAndBroadcastSDP(int absoulteFrameNumber, ScanDataPoint thisPoint) {

		if (progressUpdater != null) {
			int groupNumOfThisSDP = ExperimentLocationUtils.getGroupNum(scanParameters, absoulteFrameNumber);
			int frameNumOfThisSDP = ExperimentLocationUtils.getFrameNum(scanParameters, absoulteFrameNumber);
			EdeScanProgressBean progress = new EdeScanProgressBean(groupNumOfThisSDP, frameNumOfThisSDP, scanType,
					motorPositions.getType(), thisPoint);
			progressUpdater.update(this, progress);
		}
		rawData.add(thisPoint);
	}

	public List<ScanDataPoint> getData() {
		return getDataPoints(0, getNumberOfAvailablePoints() - 1);
	}

	public EdeScanParameters getScanParameters() {
		return scanParameters;
	}

	public void setScanParameters(EdeScanParameters scanParameters) {
		this.scanParameters = scanParameters;
	}

	public EdeScanPosition getMotorPositions() {
		return motorPositions;
	}

	public void setMotorPositions(EdeScanPosition motorPositions) {
		this.motorPositions = motorPositions;
	}

	public EdeScanType getScanType() {
		return scanType;
	}

	public void setScanType(EdeScanType scanType) {
		this.scanType = scanType;
	}
}
