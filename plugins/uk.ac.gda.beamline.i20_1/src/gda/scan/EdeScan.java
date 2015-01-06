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

import static gda.jython.InterfaceProvider.getJythonServerNotifer;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.Detector;
import gda.device.detector.DetectorStatus;
import gda.device.detector.xstrip.DetectorScanDataUtils;
import gda.device.scannable.FrameIndexer;
import gda.device.scannable.ScannableUtils;
import gda.device.scannable.TopupChecker;
import gda.jython.ITerminalPrinter;
import gda.jython.InterfaceProvider;
import gda.observable.IObserver;
import gda.scan.ede.EdeScanProgressBean;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.datawriters.ScanDataHelper;
import gda.scan.ede.position.EdeScanPosition;

import java.util.List;
import java.util.Vector;

import org.eclipse.dawnsci.analysis.dataset.impl.DoubleDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

/**
 * Runs a single set of timing groups for EDE through the XSTRIP DAServer interface.
 * <p>
 * So this: moves sample to correct position, waits for top-up to pass (if required), opens/closes shutter, runs the timing groups through the TFG unit and
 * writes data to given Nexus file.
 * <p>
 * Also holds data in memory for quick retrieval for online data.
 * <p>
 * This starts immediately and does not take sample environment triggering
 */
public class EdeScan extends ConcurrentScanChild implements EnergyDispersiveExafsScan {

	private static final Logger logger = LoggerFactory.getLogger(EdeScan.class);

	protected final Detector theDetector;
	// also keep SDPs in memory for quick retrieval for online data reduction and storage to ASCII files.
	protected final Vector<ScanDataPoint> rawData = new Vector<ScanDataPoint>();

	protected EdeScanParameters scanParameters;
	protected EdeScanPosition motorPositions;
	protected EdeScanType scanType;
	private FrameIndexer indexer = null;
	private IObserver progressUpdater;
	private final Scannable shutter;
	protected final TopupChecker topupChecker;

	//protected final TfgScaler injectionCounter;

	protected boolean isSimulated = false;

	private final ITerminalPrinter terminalPrinter;

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
	 * @param shutter
	 */
	public EdeScan(EdeScanParameters scanParameters, EdeScanPosition motorPositions, EdeScanType scanType,
			Detector theDetector, Integer repetitionNumber, Scannable shutter, TopupChecker topupChecker) {
		setMustBeFinal(true);
		this.scanParameters = scanParameters;
		this.motorPositions = motorPositions;
		this.scanType = scanType;
		this.theDetector = theDetector;
		this.shutter = shutter;
		this.topupChecker = topupChecker;
		allDetectors.add(theDetector);
		if (repetitionNumber >= 0) {
			// then use indexer to report progress of scan in data
			indexer = new FrameIndexer(scanType, motorPositions.getType(), repetitionNumber);
			indexer.setName(theDetector.getName() + "_progress");
			allScannables.add(indexer);
		}
		super.setUp();
		updateSimulated();

		//injectionCounter = Finder.getInstance().find("injectionCounter");

		terminalPrinter = InterfaceProvider.getTerminalPrinter();
	}

	private void updateSimulated() {
		if (SimulatedData.isLoaded()) {
			isSimulated = true;
		}
	}

	@Override
	public String toString() {
		return "EDE scan - type:" + scanType.toString() + " " + motorPositions.getType().toString();
	}

	@Override
	public String getHeaderDescription() {
		String desc = scanType.toString() + " " + motorPositions.getType().toString() + " scan with " + scanParameters.getGroups().size() + " timing groups";
		for (int index = 0; index < scanParameters.getGroups().size(); index++){
			TimingGroup group = scanParameters.getGroups().get(index);
			desc += "\n#Group "+ index + " " + group.getHeaderDescription();
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

	@Override
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
		// FIXME This is temporary solution as real data in unavailable
		// SimulatedData.reset();
		validate();
		if (topupChecker != null) {
			topupChecker.atScanStart();
		}
		logger.debug(toString() + " loading detector parameters...");
		theDetector.prepareDetectorwithScanParameters(scanParameters);
		shutter.moveTo("Reset");
		if (scanType == EdeScanType.DARK) {
			// close the shutter
			terminalPrinter.print("Closing shutter");
			shutter.moveTo("Close");
			checkThreadInterrupted();
			waitIfPaused();
			if (isFinishEarlyRequested()){
				return;
			}
		} else {
			moveSampleIntoPosition();
			terminalPrinter.print("Opening shutter");
			shutter.moveTo("Open");
		}
		if (!isChild()) {
			currentPointCount = -1;
		}

		logger.debug(toString() + " starting detector running...");
		terminalPrinter.print("Starting " + scanType.toString() + " " + motorPositions.getType().getLabel() + " scan");
		theDetector.collectData();
		// sleep for a moment to allow collection to start
		Thread.sleep(250);

		// poll tfg and fetch data
		pollDetectorAndFetchData();
		logger.debug(toString() + " doCollection finished.");
	}

	protected void pollDetectorAndFetchData() throws DeviceException, Exception {
		Integer nextFrameToRead = 0;
		try {
			DetectorStatus progressData = fetchStatusAndWait();
			Integer currentFrame = DetectorScanDataUtils.getAbsoluteFrameNumber(scanParameters, progressData.getCurrentScanInfo());
			while (!collectionFinished(progressData)) {
				// Review here we assume currentFrame - 1 is ready to read
				if (currentFrame > nextFrameToRead) {
					createDataPoints(nextFrameToRead, currentFrame - 1);
					nextFrameToRead = currentFrame;
				}
				Thread.sleep(100);
				waitIfPaused();
				if (isFinishEarlyRequested()){
					return;
				}
				progressData = fetchStatusAndWait();
				currentFrame = DetectorScanDataUtils.getAbsoluteFrameNumber(scanParameters, progressData.getCurrentScanInfo());
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

	protected void moveSampleIntoPosition() throws DeviceException, InterruptedException {
		logger.debug(toString() + " moving motors into position...");
		terminalPrinter.print("Moving motors for " + scanType.toString() + " " + motorPositions.getType().getLabel() + " scan");
		motorPositions.moveIntoPosition();
		checkThreadInterrupted();
		waitIfPaused();
		if (isFinishEarlyRequested()){
			return;
		}
	}

	/*
	 * fetch the latest status of the TFG, if it is paused (waiting for a trigger) then do not return until the pause
	 * has finished.
	 */
	private DetectorStatus fetchStatusAndWait() throws DeviceException, InterruptedException {
		DetectorStatus progressData = theDetector.fetchStatus();
		boolean sendMessage = true;
		while (progressData.getDetectorStatus() == Detector.PAUSED) {
			Thread.sleep(1000);
			waitIfPaused();
			if (sendMessage) {
				logger.info("Detector paused and waiting for a trigger. Abort the scan if this takes too long.");
				sendMessage = false;
			}
			progressData = theDetector.fetchStatus();
		}
		return progressData;
	}

	private Boolean collectionFinished(DetectorStatus progressData) {
		return progressData.getDetectorStatus() == Detector.IDLE || progressData.getDetectorStatus() == Detector.FAULT;
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

	protected void validate() throws IllegalArgumentException {
		if (motorPositions == null) {
			throw new IllegalArgumentException("Cannot run EdeScan as sample motor positions have not been supplied");
		}
		if (scanParameters == null) {
			throw new IllegalArgumentException("Cannot run EdeScan as scan parameters have not been supplied");
		}
	}

	private void readoutRestOfFrames(Integer nextFrameToRead) throws Exception {
		logger.debug(toString() + " detector finished, now reading the rest of the data...");
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
		Object[][] detData = readDetectors(lowFrame, highFrame);

		for (int thisFrame = lowFrame; thisFrame <= highFrame; thisFrame++) {
			checkThreadInterrupted();
			waitIfPaused();
			if (isFinishEarlyRequested()){
				return;
			}
			currentPointCount++;
			stepId = new ScanStepId(theDetector.getName(), currentPointCount);

			ScanDataPoint thisPoint = createScanDataPoint(lowFrame, detData, thisFrame);

			// then write data to data handler
			storeAndBroadcastSDP(thisFrame, thisPoint);
			getDataWriter().addData(thisPoint);

			checkThreadInterrupted();
			waitIfPaused();
			if (isFinishEarlyRequested()){
				return;
			}

			// update the filename (if this was the first data point and so filename would never be defined until first
			// data added
			thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());

			// then notify IObservers of this scan (e.g. GUI panels)
			getJythonServerNotifer().notifyServer(this, thisPoint);
		}
	}

	private ScanDataPoint createScanDataPoint(int lowFrame, Object[][] detData, int thisFrame)
			throws DeviceException {
		ScanDataPoint thisPoint = new ScanDataPoint();
		thisPoint.setUniqueName(name);
		thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());
		thisPoint.setStepIds(getStepIds());
		thisPoint.setScanPlotSettings(getScanPlotSettings());
		thisPoint.setScanDimensions(getDimensions());
		if (indexer != null) {
			indexer.setGroup(DetectorScanDataUtils.getGroupNum(scanParameters, thisFrame));
			indexer.setFrame(DetectorScanDataUtils.getFrameNum(scanParameters, thisFrame));
			thisPoint.addScannable(indexer);
			thisPoint.addScannablePosition(indexer.getPosition(), indexer.getOutputFormat());
		}
		addDetectorsToScanDataPoint(lowFrame, detData, thisFrame, thisPoint);
		thisPoint.setCurrentPointNumber(currentPointCount);
		thisPoint.setNumberOfPoints(getTotalNumberOfPoints());
		thisPoint.setInstrument(instrument);
		thisPoint.setCommand(getCommand());
		thisPoint.setScanIdentifier(getScanNumber());
		return thisPoint;
	}

	//private static final Double placeHolderValue = new Double(0);

	@SuppressWarnings("unused")
	protected void addDetectorsToScanDataPoint(int lowFrame, Object[][] detData, int thisFrame,
			ScanDataPoint thisPoint) throws DeviceException {
		thisPoint.addDetector(theDetector);
		//thisPoint.addDetector(injectionCounter);
		thisPoint.addDetectorData(detData[0][thisFrame - lowFrame], ScannableUtils.getExtraNamesFormats(theDetector));
		//thisPoint.addDetectorData(placeHolderValue, ScannableUtils.getExtraNamesFormats(injectionCounter));
	}

	protected Object[][] readDetectors(int lowFrame, int highFrame) throws Exception, DeviceException {
		NexusTreeProvider[][] detData = new NexusTreeProvider[1][];
		logger.info("reading data from detectors from frames " + lowFrame + " to " + highFrame);
		if (isSimulated) {
			detData[0] = SimulatedData.readSimulatedDataFromFile(lowFrame, highFrame, theDetector, this.getMotorPositions().getType(), this.getScanType());
		} else {
			detData[0] = theDetector.readFrames(lowFrame, highFrame);
		}
		logger.info("data read successfully");
		return detData;
	}

	private void storeAndBroadcastSDP(int absoulteFrameNumber, ScanDataPoint thisPoint) {
		rawData.add(thisPoint);
		if (progressUpdater != null) {
			int groupNumOfThisSDP = DetectorScanDataUtils.getGroupNum(scanParameters, absoulteFrameNumber);
			int frameNumOfThisSDP = DetectorScanDataUtils.getFrameNum(scanParameters, absoulteFrameNumber);
			EdeScanProgressBean progress = new EdeScanProgressBean(groupNumOfThisSDP, frameNumOfThisSDP, scanType,
					motorPositions.getType(), thisPoint);
			progressUpdater.update(this, progress);
		}
	}

	public DoubleDataset extractLastDetectorDataSet() {
		return ScanDataHelper.extractDetectorDataFromSDP(theDetector.getName(), rawData.get(rawData.size() - 1));
	}

	@Override
	public DoubleDataset extractEnergyDetectorDataSet() {
		return ScanDataHelper.extractDetectorEnergyFromSDP(theDetector.getName(), rawData.get(0));
	}

	@Override
	public DoubleDataset extractDetectorDataSet(int spectrumIndex) {
		return ScanDataHelper.extractDetectorDataFromSDP(theDetector.getName(), rawData.get(spectrumIndex));
	}

	@Override
	public List<ScanDataPoint> getData() {
		return getDataPoints(0, getNumberOfAvailablePoints() - 1);
	}

	@Override
	public EdeScanParameters getScanParameters() {
		return scanParameters;
	}

	@Override
	public void setScanParameters(EdeScanParameters scanParameters) {
		this.scanParameters = scanParameters;
	}

	public EdeScanPosition getMotorPositions() {
		return motorPositions;
	}

	public void setMotorPositions(EdeScanPosition motorPositions) {
		this.motorPositions = motorPositions;
	}

	@Override
	public EdeScanType getScanType() {
		return scanType;
	}

	@Override
	public void setScanType(EdeScanType scanType) {
		this.scanType = scanType;
	}

	@Override
	public Detector getDetector() {
		return theDetector;
	}
}
