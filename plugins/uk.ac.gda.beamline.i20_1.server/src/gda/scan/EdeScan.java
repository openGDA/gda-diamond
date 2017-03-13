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

import java.util.List;
import java.util.Vector;

import org.eclipse.dawnsci.analysis.dataset.impl.DoubleDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.DetectorStatus;
import gda.device.detector.EdeDetector;
import gda.device.detector.frelon.EdeFrelon;
import gda.device.detector.xstrip.DetectorScanDataUtils;
import gda.device.detector.xstrip.XhDetector;
import gda.device.scannable.FrameIndexer;
import gda.device.scannable.ScannableUtils;
import gda.device.scannable.TopupChecker;
import gda.jython.ITerminalPrinter;
import gda.jython.InterfaceProvider;
import gda.observable.IObserver;
import gda.scan.ede.EdeScanProgressBean;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.datawriters.ScanDataHelper;
import gda.scan.ede.position.EdePositionType;
import gda.scan.ede.position.EdeScanMotorPositions;
import gda.scan.ede.position.EdeScanPosition;
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

	protected final EdeDetector theDetector;
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

	private final ITerminalPrinter terminalPrinter;

	private boolean smartstop=false;

	protected TimingGroup currentTimingGroup;

	private boolean useFastShutter;
	private Scannable fastShutter;

	private Scannable motorToMoveDuringScan;

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
			EdeDetector theDetector, Integer repetitionNumber, Scannable shutter, TopupChecker topupChecker) {
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

		//injectionCounter = Finder.getInstance().find("injectionCounter");

		terminalPrinter = InterfaceProvider.getTerminalPrinter();
		useFastShutter = false;
		fastShutter = null;
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

	/**
	 * Move the fast shutter to specified position (e.g. "Open" , "Close" )
	 * moveTo doesn't block so sleep until shutter has actually moved to the new position is also implemented here
	 * @param position
	 * @throws DeviceException
	 * @throws InterruptedException
	 * @since 28/1/2016.
	 */
	public void fastShutterMoveTo(String position) throws DeviceException, InterruptedException {
		final int pollSleepInterval = 250;
		final int maxWaitTime = 10000;

		if ( useFastShutter == false || fastShutter == null ) {
			return;
		}

		String currentPosition = (String) fastShutter.getPosition();
		String finalPosition = position;
		if ( position.equals("Close") ) {
			finalPosition = "Closed";
		}

		if ( currentPosition.equals(finalPosition) ) {
			logger.info("Fast shutter move - already in requested position ("+finalPosition+")");
			return;
		}

		if ( useFastShutter && fastShutter != null ) {

			String message = "Fast shutter move to \'"+position+"\'";
			logger.info(message);
			InterfaceProvider.getTerminalPrinter().print(message);

			fastShutter.moveTo(position); // does not block!

			// Sleep until fast shutter has moved, been interrupted or failed to move for some reason...
			int waitTime = 0;
			String shutterExceptionMessage = "";
			while( !currentPosition.equals( finalPosition ) ) {
				try {
					//InterfaceProvider.getTerminalPrinter().print("Sleep for "+pollSleepInterval+" ms ... ");

					Thread.sleep( pollSleepInterval );
					currentPosition = (String) fastShutter.getPosition();

					//InterfaceProvider.getTerminalPrinter().print("Fast shutter position : "+currentPosition);

					waitTime += pollSleepInterval;
				}
				catch( gda.device.DeviceException deviceException ) {
					// Ignore this exception - happens when getPosition is called whilst shutter is still in process of moving.
					shutterExceptionMessage = deviceException.getMessage();
					//InterfaceProvider.getTerminalPrinter().print("Fast shutter exception caught : "+shutterExceptionMessage);
				}

				// Max wait time exceeded - something probably really is wrong with shutter
				if ( waitTime > maxWaitTime ) {
					String exceptionMessage = "Maximum wait time exceeded for fast shutter, last shutter exception - "+shutterExceptionMessage;
					logger.info(exceptionMessage);
					InterfaceProvider.getTerminalPrinter().print(exceptionMessage);
					throw new DeviceException(exceptionMessage);
				}
			}

			message = "Fast shutter move finished";
			logger.info(message);
			// InterfaceProvider.getTerminalPrinter().print(message);
		}
	}

	@Override
	public void doCollection() throws Exception {
		// FIXME This is temporary solution as real data in unavailable
		// SimulatedData.reset();

		validate();

		// Topup checker moved to *after* motor move and shutter close have been done. imh 22/1/2016
		//		if (topupChecker != null) {
		//			topupChecker.atScanStart();
		//		}

		logger.debug(toString() + " loading detector parameters...");
		theDetector.prepareDetectorwithScanParameters(scanParameters);
		shutter.moveTo("Reset");
		if (scanType == EdeScanType.DARK) {
			// close the shutter
			terminalPrinter.print("Closing shutter");
			shutter.moveTo("Close");
			fastShutterMoveTo("Close");

			// Topup checker not needed for Dark scan imh 22/1/2016
			//if (topupChecker != null) {
			//	topupChecker.atScanStart();
			//}

			checkThreadInterrupted();
			waitIfPaused();
			if (isFinishEarlyRequested()){
				return;
			}
		} else {

			// close shutter while moving motors and waiting for topup. imh 27/1/2016
			fastShutterMoveTo("Close");

			// close main shutter if not using fast shutter
			if ( useFastShutter == false ) {
				shutter.moveTo("Close");
			}

			// Move into position before topupchecker, so we are ready to start collecting data. imh 22/1/2016
			moveSampleIntoPosition();

			if (topupChecker != null) {
				topupChecker.atScanStart();
			}

			terminalPrinter.print("Opening shutter");
			shutter.moveTo("Open"); // must be open for Light scan, whether using fast shutter or not
			fastShutterMoveTo("Open");
		}
		if (!isChild()) {
			currentPointCount = -1;
		}

		terminalPrinter.print("Starting " + scanType.toString() + " " + motorPositions.getType().getLabel() + " scan");
		if (motorPositions instanceof EdeScanMotorPositions) {
			EdeScanMotorPositions scanMotorPositions = (EdeScanMotorPositions)motorPositions;
			List<Double> motorPositionsToScan = scanMotorPositions.getMotorPositionsDuringScan();
			motorToMoveDuringScan = scanMotorPositions.getMotorToMoveDuringScan();
			boolean lightItScan = scanType == EdeScanType.LIGHT && motorPositions.getType() == EdePositionType.INBEAM;

			if (lightItScan && motorToMoveDuringScan !=null && motorPositionsToScan != null && motorPositionsToScan.size()>0) {
				int count = 1;
				for(Double pos : motorPositionsToScan) {
					logger.info("Moving motor {} to position {} (step {} of {})...", motorToMoveDuringScan.getName(), pos, count++, motorPositionsToScan.size());
					motorToMoveDuringScan.moveTo(pos);
					collectDetectorData();
				}
			} else {
				collectDetectorData();
			}
		} else {
			logger.debug(toString() + " starting detector running...");
			collectDetectorData();
		}
		fastShutterMoveTo("Close");
	}

	protected void collectDetectorData() throws Exception {
		logger.debug(toString() + " collectDetectorData started...");
		if (theDetector instanceof EdeFrelon) {
			for (Integer i = 0; i < scanParameters.getGroups().size(); i++) {
				if (Thread.currentThread().isInterrupted()) {
					break;
				}
				currentTimingGroup=scanParameters.getGroups().get(i);
				((EdeFrelon) theDetector).setDropFirstFrame(true);
				theDetector.configureDetectorForTimingGroup(currentTimingGroup);
				theDetector.collectData();
				Thread.sleep(250);

				// poll tfg and fetch data
				pollDetectorAndFetchData();
			}
		} else {
			theDetector.collectData();
			Thread.sleep(250);

			// poll tfg and fetch data
			pollDetectorAndFetchData();
		}
		logger.debug(toString() + " collectDetectorData finished.");
	}

	protected void pollDetectorAndFetchData() throws DeviceException, Exception {
		Integer nextFrameToRead = 0;
		int lastImageRead=-1;
		boolean firstReading=false;
		int lastImageReady=-1;
		try {
			DetectorStatus progressData = fetchStatusAndWait();
			if (theDetector instanceof XhDetector) {
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
			} else if (theDetector instanceof EdeFrelon) {
				if (theDetector.isDropFirstFrame()) {
					lastImageRead=0;
					firstReading=true;
				}
				EdeFrelon detector=((EdeFrelon)theDetector);
				lastImageReady = detector.getLimaCcd().getLastImageReady();
				while (theDetector.isBusy()) {
					if (lastImageReady > lastImageRead) {
						if (firstReading) {
							//frames including the first frame, only read from 2nd frame onward
							createDataPoints(1,lastImageReady);
							firstReading=false;
						} else {
							createDataPoints(lastImageRead+1,lastImageReady);
						}
						lastImageRead=lastImageReady;
					}
					Thread.sleep(100);
					waitIfPaused();
					if (isFinishEarlyRequested()){
						return;
					}
					if (isSmartstop()) {
						theDetector.stop();
					}
					lastImageReady=detector.getLimaCcd().getLastImageReady();
				}
			}
		} catch (Exception e) {
			// scan has been aborted, so stop the collection and let the scan write out the rest of the data point which
			// have been collected so far
			theDetector.stop();
			throw e;
		} finally {
			// have we read all the frames?
			if (theDetector instanceof XhDetector) {
				readoutRestOfFrames(nextFrameToRead);
			}
			if (theDetector instanceof EdeFrelon) {
				if (isSmartstop()) {
					TimingGroup currentTimingGroup = ((EdeFrelon) theDetector).getCurrentTimingGroup();
					int indexOf = scanParameters.getGroups().indexOf(currentTimingGroup);
					scanParameters.getGroups().get(indexOf).setNumberOfFrames(lastImageReady);
					if (indexOf<scanParameters.getGroups().size()) {
						for (int i=indexOf+1; i<scanParameters.getGroups().size(); i++) {
							scanParameters.getGroups().get(i).setNumberOfFrames(0);
						}
					}
					setSmartstop(false);
				}
				if (lastImageRead!=lastImageReady) {
					if (lastImageReady!=-1) {
						createDataPoints(lastImageRead+1,lastImageReady);
					} else {
						logger.warn("detector {} does not take any data yet. The lastImageReady = {}", getName(), lastImageReady);
					}
				}
			}
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
		while (progressData.getDetectorStatus() == Detector.PAUSED ) {
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
		return progressData.getDetectorStatus() == EdeDetector.IDLE || progressData.getDetectorStatus() == EdeDetector.FAULT;
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
		int realFrameNumber=0;
		int realLowFrameNumber=0;
		ScanDataPoint thisPoint;
		for (int thisFrame = lowFrame; thisFrame <= highFrame; thisFrame++) {
			checkThreadInterrupted();
			waitIfPaused();
			if (isFinishEarlyRequested()){
				return;
			}
			currentPointCount++;
			stepId = new ScanStepId(theDetector.getName(), currentPointCount);

			if (theDetector.isDropFirstFrame()) {
				realFrameNumber=thisFrame-1;
				realLowFrameNumber=lowFrame-1;
				thisPoint = createScanDataPoint(realLowFrameNumber, detData, realFrameNumber);
				storeAndBroadcastSDP(realFrameNumber, thisPoint);
			} else {
				thisPoint = createScanDataPoint(lowFrame, detData, thisFrame);
				storeAndBroadcastSDP(thisFrame, thisPoint);
			}

			// then write data to data handler
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
			if (theDetector instanceof EdeFrelon) {
				indexer.setGroup(scanParameters.getGroups().indexOf(currentTimingGroup));
				indexer.setFrame(thisFrame);
			} else {
				indexer.setGroup(DetectorScanDataUtils.getGroupNum(scanParameters, thisFrame));
				indexer.setFrame(DetectorScanDataUtils.getFrameNum(scanParameters, thisFrame));
			}
			thisPoint.addScannable(indexer);
			thisPoint.addScannablePosition(indexer.getPosition(), indexer.getOutputFormat());
		}

		if (motorToMoveDuringScan != null) {
			thisPoint.addScannable(motorToMoveDuringScan);
			thisPoint.addScannablePosition(motorToMoveDuringScan.getPosition(), motorToMoveDuringScan.getOutputFormat());
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
		detData[0] = theDetector.readFrames(lowFrame, highFrame);
		logger.info("data read successfully");
		return detData;
	}

	private void storeAndBroadcastSDP(int absoulteFrameNumber, ScanDataPoint thisPoint) {
		rawData.add(thisPoint);
		if (progressUpdater != null) {
			int frameNumOfThisSDP;
			int groupNumOfThisSDP;
			if (theDetector instanceof EdeFrelon) {
				groupNumOfThisSDP = scanParameters.getGroups().indexOf(currentTimingGroup);
				frameNumOfThisSDP = absoulteFrameNumber;

			} else {
				groupNumOfThisSDP = DetectorScanDataUtils.getGroupNum(scanParameters, absoulteFrameNumber);
				frameNumOfThisSDP = DetectorScanDataUtils.getFrameNum(scanParameters, absoulteFrameNumber);
			}
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
	public EdeDetector getDetector() {
		return theDetector;
	}

	public boolean isSmartstop() {
		return smartstop;
	}

	public void setSmartstop(boolean smartstop) {
		this.smartstop = smartstop;
	}

	public boolean gsUseFastShutter() {
		return useFastShutter;
	}

	public void setUseFastShutter(boolean useFastShutter) {
		this.useFastShutter = useFastShutter;
	}

	public Scannable getFastShutter() {
		return fastShutter;
	}

	public void setFastShutter(Scannable fastShutter) {
		this.fastShutter = fastShutter;
	}
}
