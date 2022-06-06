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

import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import org.apache.commons.lang.ArrayUtils;
import org.dawnsci.ede.EdePositionType;
import org.dawnsci.ede.EdeScanType;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.january.DatasetException;
import org.eclipse.january.dataset.DoubleDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.nexus.extractor.NexusGroupData;
import gda.data.nexus.tree.INexusTree;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.data.scan.datawriter.DataWriter;
import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.DetectorStatus;
import gda.device.detector.EdeDetector;
import gda.device.detector.EdeDummyDetector;
import gda.device.detector.NXDetectorData;
import gda.device.detector.frelon.EdeFrelon;
import gda.device.detector.xstrip.DetectorScanDataUtils;
import gda.device.detector.xstrip.XhDetector;
import gda.device.enumpositioner.ValvePosition;
import gda.device.scannable.FrameIndexer;
import gda.device.scannable.ScannableUtils;
import gda.device.scannable.TopupChecker;
import gda.jython.ITerminalPrinter;
import gda.jython.InterfaceProvider;
import gda.observable.IObserver;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.EdeScanProgressBean;
import gda.scan.ede.datawriters.ScanDataHelper;
import gda.scan.ede.position.EdeScanMotorPositions;
import gda.scan.ede.position.EdeScanPosition;
import gda.util.NexusTreeWriter;
import uk.ac.gda.ede.data.DetectorSetupType;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.server.exafs.epics.device.scannable.ShutterChecker;

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

	private static final long serialVersionUID = 1L;

	private static final Logger logger = LoggerFactory.getLogger(EdeScan.class);

	protected final EdeDetector theDetector;
	// also keep SDPs in memory for quick retrieval for online data reduction and storage to ASCII files.


	// This rawData is only used for sending data to client for 'live plotting' during a scan(? TBC).
	// Don't need *all* the rawData for lightIt scan; only latest frame is needed; first frame might be used for getting the energy axis valuesl
	// Need to store all the darkI0,It light I0 data so can correct for dark counts when have multiple timing groups.
	protected final List<ScanDataPoint> rawData = new ArrayList<>();

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

	private boolean useFastShutter;
	private Scannable fastShutter;

	private Scannable motorToMoveDuringScan;
	private boolean moveMotorDuringScan;

	/** List of scannables whose positions should also be recorded in the each scan data point */
	private Set<Scannable> scannablesToMonitorDuringScan = new LinkedHashSet<>();

	/** This is used to cache the position of scannables being monitored , to help speed up filewriting */
	private Map<Scannable, Object> scannablePositions = new ConcurrentHashMap<>();
	private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);

	private NexusTreeWriter nexusTreeWriter;
	private boolean useNexusTreeWriter = false;

	private ShutterChecker shutterChecker = null;

	/** Absolute number of frames published for the currently running collection (set to 0 at start of {@link #collectDetectorData() }*/
	private int absFrameNumber;
	private double noOfSecPerSpectrumToPublish = 1;

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

		//injectionCounter = Finder.find("injectionCounter");

		terminalPrinter = InterfaceProvider.getTerminalPrinter();
		useFastShutter = false;
		fastShutter = null;
		setupShutterChecker();
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
		if (useFastShutter && fastShutter != null) {
			try {
				String message = "Fast shutter move to \'" + position + "\'";
				logger.info(message);
				InterfaceProvider.getTerminalPrinter().print(message);

				// Use shutter checker to make sure main shutter has been opened; block until opened.
				if (shutterChecker != null && position.equals(ValvePosition.OPEN)) {
					shutterChecker.atPointStart();
				}

				fastShutter.moveTo(position);

				message = "Fast shutter move finished";
				logger.info(message);
				InterfaceProvider.getTerminalPrinter().print(message);
			} catch (DeviceException e) {
				logger.warn("Problem moving fast shutter to '{}' position during scan", position, e);
				throw new DeviceException(e);
			}
		}
	}

	private long moveTimeoutMs = 20000;

	/**
	 * Wait for position of scannable 'scn' to match demandPosition.
	 * Polls the scannable every 100ms, with timeout of {@link moveTimeoutMs} ms.
	 * @param scn
	 * @param requiredPos
	 * @throws DeviceException
	 * @throws InterruptedException
	 */
	private void waitForValue(Scannable scn, String requiredPos) throws DeviceException, InterruptedException {
		logger.debug("Waiting for {} to move to {}", scn.getName(), requiredPos);
		final long pollIntervalMs = 100;
		final long timeOut = 10000;
		long timeUsed = 0;
		while(timeUsed < moveTimeoutMs) {
			String pos = scn.getPosition().toString();
			if (pos.equals(requiredPos)) {
				logger.debug("{} in position after {} ms", scn.getName(), timeUsed);
				return;
			}
			Thread.sleep(pollIntervalMs);
			timeUsed += pollIntervalMs;
		}
		String message = "Reached "+timeOut+" ms timeout waiting for "+scn.getName()+" to move to "+requiredPos;
		logger.warn(message);
		throw new DeviceException(message);
	}

	/**
	 * Try to get reference to shutterchecker to use for {@link #shutter} from {@link #allScannables}.
	 * (Default scannables are added to {{@link #allScannables} added by call to {@link #setUp()} in constructor).
	 */
	private void setupShutterChecker() {
		Optional<ShutterChecker> foundShutterChecker = allScannables.stream()
				.filter(scn -> scn instanceof ShutterChecker)
				.map(scn -> (ShutterChecker) scn)
				.filter(scn -> scn.getShutter().getName().equals(shutter.getName()))
				.findFirst();

		if (foundShutterChecker.isPresent()) {
			shutterChecker = foundShutterChecker.get();
			logger.debug("Found shutter checker {} to use for scan", shutterChecker.getName());
		} else {
			shutterChecker = null;
		}
	}

	private void mainShutterMoveTo(String position) throws DeviceException, InterruptedException {
		logger.info("Moving {} to position {}", shutter.getName(), position);

		if (shutterChecker == null) {
			logger.debug("Shutter checker is not present - not moving shutter");
			return;
		}

		if (shutter.getPosition().equals(position)) {
			logger.debug("{} is already in position", shutter.getName());
			return;
		}

		shutter.moveTo(position);
		waitForValue(shutter, position);
	}

	protected void moveShutter(String position) throws DeviceException, InterruptedException {
		if (useFastShutter) {
			fastShutterMoveTo(position);
		} else {
			mainShutterMoveTo(position);
		}
	}

	@Override
	public void doCollection() throws Exception {
		validate();

		// Periodically update cache of positions of scannables being monitored
		if (useNexusTreeWriter) {
			scheduler.scheduleAtFixedRate(this::updatePositions, 0, 100, TimeUnit.MILLISECONDS);
		}

		logger.debug(toString() + " loading detector parameters...");
		theDetector.prepareDetectorwithScanParameters(scanParameters);

		if (!useFastShutter) {
			shutter.moveTo(ValvePosition.RESET);
		}

		if (scanType == EdeScanType.DARK) {
			// close the shutter
			terminalPrinter.print("Closing shutter");
			moveShutter(ValvePosition.CLOSE);

			if (checkEarlyFinish()) {
				return;
			}
		} else {

			// close shutter while moving motors and waiting for topup. imh 27/1/2016
			moveShutter(ValvePosition.CLOSE);

			// Move into position before topupchecker, so we are ready to start collecting data. imh 22/1/2016
			moveSampleIntoPosition();

			if (topupChecker != null) {
				topupChecker.atScanStart();
			}

			waitBeforeCycle();

			terminalPrinter.print("Opening shutter");
			moveShutter(ValvePosition.OPEN);
		}
		if (!isChild()) {
			currentPointCount = -1;
		}

		terminalPrinter.print("Starting " + scanType.toString() + " " + motorPositions.getType().getLabel() + " scan");
		moveMotorDuringScan = false;
		if (motorPositions instanceof EdeScanMotorPositions) {
			EdeScanMotorPositions scanMotorPositions = (EdeScanMotorPositions)motorPositions;
			List<Object> motorPositionsToScan = scanMotorPositions.getMotorPositionsDuringScan();
			motorToMoveDuringScan = scanMotorPositions.getScannableToMoveDuringScan();

			// Record position of the motor in Nexus file
			if (motorToMoveDuringScan != null) {
				addScannableToMonitorDuringScan(motorToMoveDuringScan);
			}

			if (isLightItScan() && motorToMoveDuringScan !=null && motorPositionsToScan != null && motorPositionsToScan.size()>0) {
				int count = 1;
				moveMotorDuringScan = true;
				for(Object pos : motorPositionsToScan) {
					logger.info("Moving motor {} to position {} (step {} of {})...", motorToMoveDuringScan.getName(), pos, count++, motorPositionsToScan.size());
					motorToMoveDuringScan.waitWhileBusy();
					motorToMoveDuringScan.asynchronousMoveTo(pos);
					if (checkEarlyFinish()) {
						break;
					}
					while(motorToMoveDuringScan.isBusy()) {
						if (checkEarlyFinish()) {
							break;
						}
						Thread.sleep(100);
					}
					collectDetectorData();
					logger.info("Status = {}", getStatus());
					if (isFinishEarlyRequested()) {
						logger.info("Stopping motor move loop before all positions have been reached - 'finishing early' requested");
						break;
					}
				}
			} else {
				collectDetectorData();
			}
		} else {
			logger.debug(toString() + " starting detector running...");
			collectDetectorData();
		}
		fastShutterMoveTo(ValvePosition.CLOSE);
	}

	private boolean isLightItScan() {
		return scanType == EdeScanType.LIGHT && motorPositions.getType() == EdePositionType.INBEAM;
	}
	/**
	 *  For 'light It' measurement wait for required time if {@link TimingGroup#getPreceedingTimeDelay()} is > 0.
	 * @throws InterruptedException
	 */
	protected void waitBeforeCycle() throws InterruptedException {
		if (motorPositions.getType() == EdePositionType.INBEAM) {
			double delayBeforeMeasurement  = scanParameters.getGroups().get(0).getPreceedingTimeDelay();
			if (delayBeforeMeasurement > 0) {
				terminalPrinter.print("Waiting for "+delayBeforeMeasurement+" seconds before starting measurement");
				logger.debug("Waiting for {} secs before starting scan", delayBeforeMeasurement);
				Thread.sleep((long) delayBeforeMeasurement * 1000);
			}
		}
	}

	/**
	 * Check for interrupted exception, wait if paused; return true if finish 'early request' has been made.
	 * @return isFinishEarlyRequested
	 * @throws InterruptedException
	 */
	private boolean checkEarlyFinish() throws InterruptedException {
		checkThreadInterrupted();
		waitIfPaused();
		return isFinishEarlyRequested();
	}

	protected void collectDetectorData() throws Exception {
		absFrameNumber = 0;
		logger.debug(toString() + " collectDetectorData started...");
		if (theDetector instanceof EdeFrelon) {
			for (Integer i = 0; i < scanParameters.getGroups().size(); i++) {
				if (Thread.currentThread().isInterrupted()) {
					break;
				}
				((EdeFrelon) theDetector).setDropFirstFrame(true);
				theDetector.configureDetectorForTimingGroup(scanParameters.getGroups().get(i));
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
					if (isSmartstop()) {
						theDetector.stop();
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
			} else if (theDetector instanceof EdeDummyDetector) {
				for(TimingGroup group : scanParameters.getGroups()) {
					createDataPoints(0, group.getNumberOfFrames()-1);
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
				if (isSmartstop()) {
					int groupNum = DetectorScanDataUtils.getGroupNum(scanParameters, nextFrameToRead);
					scanParameters.getGroups().get(groupNum).setNumberOfFrames(nextFrameToRead);
					for(int i=groupNum+1; i<scanParameters.getGroups().size(); i++) {
						scanParameters.getGroups().get(i).setNumberOfFrames(0);
					}
					setSmartstop(false);
				} else {
					readoutRestOfFrames(nextFrameToRead);
				}
			}
			if (theDetector instanceof EdeFrelon) {
				// Get final image number available on detector
				int finalImage = ((EdeFrelon) theDetector).getLimaCcd().getLastImageReady();
				logger.debug("Finished reading out {}. lastImageRead = {}, lastImageReady = {}, finalImage = {}",
						theDetector.getName(), lastImageRead, lastImageReady, finalImage);
				if (isSmartstop()) {
					TimingGroup currentTimingGroup = ((EdeFrelon) theDetector).getCurrentTimingGroup();
					currentTimingGroup.setNumberOfFrames(finalImage);
					int indexOf = scanParameters.getGroups().indexOf(currentTimingGroup);
					if (indexOf<scanParameters.getGroups().size()) {
						for (int i=indexOf+1; i<scanParameters.getGroups().size(); i++) {
							scanParameters.getGroups().get(i).setNumberOfFrames(0);
						}
					}
					setSmartstop(false);
				}
				if (lastImageRead != finalImage) {
					if (finalImage != -1) {
						createDataPoints(lastImageRead + 1, finalImage);
					} else {
						logger.warn("detector {} does not take any data yet. The finalImage = {}", getName(), finalImage);
					}
				}
			}

			// Make sure NexusTreeWriter writes any remaining data and releases file handle.
			if (nexusTreeWriter != null) {
				nexusTreeWriter.writeNexusData();
				nexusTreeWriter.closeFile();
			}
		}
	}

	protected void moveSampleIntoPosition() throws DeviceException, InterruptedException {
		logger.debug(toString() + " moving motors into position...");
		terminalPrinter.print("Moving motors for " + scanType.toString() + " " + motorPositions.getType().getLabel() + " scan");
		motorPositions.moveIntoPosition();
		checkEarlyFinish();
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

	private void writeDetectorData(NexusTreeProvider[] detectorData, int lowFrame, int highFrame) throws NexusException, DatasetException {
		logger.debug("writeDetectorData() called for frames {}...{}", lowFrame, highFrame);
		long time = System.currentTimeMillis();
		if (nexusTreeWriter == null) {
			logger.debug("Creating NexusTreeWriter for {} data", theDetector.getName());
			nexusTreeWriter = new NexusTreeWriter();
		}
		nexusTreeWriter.addData(detectorData);

		String nexusFileName = nexusTreeWriter.getScanNexusFilename();
		if (!nexusFileName.isEmpty()) {
			logger.debug("Setting Nexus tree writer output filename to {}", nexusFileName);
			nexusTreeWriter.setFullpathToNexusFile(nexusFileName);
		}

		if (!nexusTreeWriter.getFullpathToNexusFile().isEmpty()) {
			logger.debug("Writing detector data to Nexus file using NexusTreeWriter");
			nexusTreeWriter.writeNexusData();
		}
		logger.info("NexusTreeWriter finished : {} ms", System.currentTimeMillis() - time);
	}

	private void createDataPoints(int lowFrame, int highFrame) throws Exception {
		logger.info("Reading out frames : {} .... {}", lowFrame, highFrame);
		int startFrame = lowFrame;
		long time = System.currentTimeMillis();
		while(startFrame <= highFrame) {
			int endFrame = Math.min(startFrame+theDetector.getMaxNumFramesToRead(), highFrame);
			logger.info("Frames : {} ... {}", startFrame, endFrame);
			collectData(startFrame, endFrame);
			startFrame = endFrame+1;
		}
		logger.info("Frame readout finished : {} ms", System.currentTimeMillis() - time);
	}

	/**
	 * @param lowFrame
	 *            - where 0 is the first frame
	 * @param highFrame
	 *            - where number scan points -1 is the last frame
	 * @throws Exception
	 */
	private void collectData(int lowFrame, int highFrame) throws Exception {
		// readout the correct frame from the detectors
		Object[] detData = readDetectors(lowFrame, highFrame);
		if (useNexusTreeWriter) {
			writeDetectorData((NexusTreeProvider[]) detData, lowFrame, highFrame);
		}

		DataWriter dataWriter = getDataWriter();

		int totalNumFrames = scanParameters.getTotalNumberOfFrames();
		int publishInterval = 1;
		if (isLightItScan()) {
			double framesPerSecond = totalNumFrames/scanParameters.getTotalTime();
			publishInterval =  (int) Math.max(1, noOfSecPerSpectrumToPublish * framesPerSecond);
		}

		long startTime = System.currentTimeMillis();
		for (int thisFrame = lowFrame; thisFrame <= highFrame; thisFrame++) {

			if (checkEarlyFinish()) {
				return;
			}

			currentPointCount++;
			stepId = new ScanStepId(theDetector.getName(), currentPointCount);

			ScanDataPoint thisPoint;
			int realFrameNumber=0;
			if (theDetector.isDropFirstFrame()) {
				realFrameNumber=thisFrame-1;
				thisPoint = createScanDataPoint(lowFrame-1, detData, realFrameNumber);
			} else {
				realFrameNumber = thisFrame;
				thisPoint = createScanDataPoint(lowFrame, detData, realFrameNumber);
			}

			if (absFrameNumber%publishInterval==0 || absFrameNumber==totalNumFrames-1) {
				rawData.add(thisPoint);
				broadcastSDP(realFrameNumber, dataWriter.getCurrentFileName());
				InterfaceProvider.getJythonServerNotifer().notifyServer(this, thisPoint);
			}

			// Remove detector and scannables from ScanDataPoint so that NexusDataWriter doesn't also try to
			// write the same data into Nexus file. Do it *after* broadcasting the SDP, since need to store the
			// datapoint and broadcast energy and spectrum data to client...
			if (useNexusTreeWriter && nexusTreeWriter != null) {
				thisPoint.getDetectors().clear();
				thisPoint.getScannables().clear();
			}

			// then write data to data handler
			dataWriter.addData(thisPoint);

			absFrameNumber++;

		}
		logger.info("Finished writing data : {} ms", System.currentTimeMillis() - startTime);
	}

	private void setupFrameIndexer(int frameNumber) {
		if (theDetector.getDetectorSetupType() == DetectorSetupType.FRELON) {
			TimingGroup currentTimingGroup = ((EdeFrelon)theDetector).getCurrentTimingGroup();
			indexer.setGroup(scanParameters.getGroups().indexOf(currentTimingGroup));
			indexer.setFrame(frameNumber);
		} else {
			indexer.setGroup(DetectorScanDataUtils.getGroupNum(scanParameters, frameNumber));
			indexer.setFrame(DetectorScanDataUtils.getFrameNum(scanParameters, frameNumber));
		}
	}

	private ScanDataPoint createScanDataPoint(int lowFrame, Object[] detData, int thisFrame)
			throws DeviceException {
		ScanDataPoint thisPoint = new ScanDataPoint();
		thisPoint.setUniqueName(name);
		thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());
		thisPoint.setStepIds(getStepIds());
		thisPoint.setScanPlotSettings(getScanPlotSettings());
		thisPoint.setScanDimensions(getDimensions());
		if (indexer != null) {
			indexer.setName(theDetector.getName() + "_progress"); // make sure indexer name is consistent with detector name (in case detector was renamed after EdeScan was created)
			setupFrameIndexer(thisFrame);
			thisPoint.addScannable(indexer);
			thisPoint.addScannablePosition(indexer.getPosition(), indexer.getOutputFormat());
		}

		addScannablesToScanDataPoint(thisPoint);

		addDetectorsToScanDataPoint(lowFrame, detData, thisFrame, thisPoint);
		thisPoint.setCurrentPointNumber(currentPointCount);
		thisPoint.setNumberOfPoints(getTotalNumberOfPoints());
		thisPoint.setInstrument(instrument);
		thisPoint.setCommand(getCommand());
		thisPoint.setScanIdentifier(getScanNumber());
		return thisPoint;
	}

	/**
	 * Add positions of any scannables to be monitored to the scan datapoint.
	 * @param thisPoint
	 * @throws DeviceException
	 */
	private void addScannablesToScanDataPoint(ScanDataPoint thisPoint) throws DeviceException {
		if (scannablesToMonitorDuringScan != null && scannablesToMonitorDuringScan.size()>0) {
			for(Scannable scn : scannablesToMonitorDuringScan) {
				thisPoint.addScannable(scn);
				thisPoint.addScannablePosition(scn.getPosition(), scn.getOutputFormat());
			}
		}
	}

	public Collection<Scannable> getScannablesToMonitorDuringScan() {
		return scannablesToMonitorDuringScan;
	}

	public void setScannablesToMonitorDuringScan(Collection<Scannable> scannablesToMonitorDuringScan) {
		if (scannablesToMonitorDuringScan != null) {
			this.scannablesToMonitorDuringScan.clear();
			this.scannablesToMonitorDuringScan.addAll(scannablesToMonitorDuringScan);
		}
	}

	public void addScannableToMonitorDuringScan(Scannable scannableToMonitorDuringScan) {
		scannablesToMonitorDuringScan.add(scannableToMonitorDuringScan);
	}

	protected void addDetectorsToScanDataPoint(int lowFrame, Object[] detData, int thisFrame,
			ScanDataPoint thisPoint) throws DeviceException {

		thisPoint.addDetector(theDetector);
		thisPoint.addDetectorData(detData[thisFrame - lowFrame], ScannableUtils.getExtraNamesFormats(theDetector));
	}

	/**
	 * Update cache with latest positions of any scannables being monitored.
	 */
	private void updatePositions() {
		if (scannablesToMonitorDuringScan != null) {
			for(Scannable scn : scannablesToMonitorDuringScan) {
				try {
					scannablePositions.put(scn, scn.getPosition());
				} catch (DeviceException e) {
					logger.error("Problem updating position map for scannable {}", e);
				}
			}
		}
	}

	/**
	 * Add values from a scannable to NexusTree.
	 * This will attempt to retrieve the position from the cache in {@link #scannablePositions} (if available),
	 * otherwise {@link Scannable#getPosition()} is called.
	 *
	 * @param detTree
	 * @param scn
	 * @throws DeviceException
	 */
	private void addToNexusTree(INexusTree detTree, Scannable scn) throws DeviceException {
		Object position = scannablePositions.get(scn);
		if (position == null) {
			position = scn.getPosition();
		}
		if (position instanceof Double) {
			NXDetectorData.addData(detTree, scn.getName(), new NexusGroupData((Double)position), "counts", 1);
		} else {
			String[] allNames = (String[]) ArrayUtils.addAll(scn.getInputNames(), scn.getExtraNames());
			double[] positions = ScannableUtils.getCurrentPositionArray(scn);
			for(int i=0; i<allNames.length; i++) {
				NXDetectorData.addData(detTree, allNames[i], new NexusGroupData(positions[i]), "counts", 1);
			}
		}
	}

	protected NexusTreeProvider[] readDetectors(int lowFrame, int highFrame) throws Exception, DeviceException {
		logger.info("reading data from detectors from frames " + lowFrame + " to " + highFrame);
		NexusTreeProvider[] detData = theDetector.readFrames(lowFrame, highFrame);

		if (useNexusTreeWriter) {
			logger.info("Adding indexer data to NexusTree");
			// Add frame indexer information for each spectrum to the Nexus tree
			int numFrames = highFrame - lowFrame + 1;
			int startFrame = theDetector.isDropFirstFrame() ? lowFrame-1 : lowFrame;
			if (indexer != null) {
				for(int i=0; i<numFrames; i++) {
					setupFrameIndexer(i + startFrame);
					indexer.addToNexusTree((NXDetectorData)detData[i], theDetector.getName());
				}
			}

			// Add scannable position information for each spectrum to the Nexus tree
			if (scannablesToMonitorDuringScan != null) {
				logger.info("Adding scannable data to NexusTree");
				for(int i=0; i<numFrames; i++) {
					INexusTree tree = ((NXDetectorData)detData[i]).getDetTree(theDetector.getName());
					for(Scannable scn : scannablesToMonitorDuringScan) {
						addToNexusTree(tree, scn);
					}
				}
			}
			logger.info("Finished adding data to NexusTree");
		}

		logger.info("data read successfully");
		return detData;
	}

	/**
	 * Store the ScanDataPoint and call {@link EdeExperiment#update(Object, Object)} to broadcast
	 * data to the client.
	 * @param absoulteFrameNumber
	 * @param thisPoint
	 */
	private void broadcastSDP(int absoulteFrameNumber, String currentFileName) {
		if (progressUpdater != null) {
			int frameNumOfThisSDP = 0;
			int groupNumOfThisSDP = 0;
			if (indexer != null) {
				frameNumOfThisSDP = indexer.getFrame();
				groupNumOfThisSDP = indexer.getGroup();
			}
			EdeScanProgressBean progress = new EdeScanProgressBean(groupNumOfThisSDP, frameNumOfThisSDP, scanType,
					motorPositions.getType(), currentFileName);
			String customLabelForSDP = getLabelForScanDataPoint(groupNumOfThisSDP, frameNumOfThisSDP);
			progress.setCustomLabelForSDP(customLabelForSDP);
			progressUpdater.update(this, progress);
		}
	}

	private boolean includeCycleInPlotLabel = false;

	public boolean isIncludeGroupNumberInSDPLabel() {
		return includeCycleInPlotLabel;
	}

	public void setIncludeCyclePlotLabel(boolean includeGroupNumberInSDPLabel) {
		this.includeCycleInPlotLabel = includeGroupNumberInSDPLabel;
	}

	/**
	 * Create a label for scan data point showing the group, spectrum number of scan data point.
	 * The current position of any scannable being moved during the scan is also included.
	 * (this is used for the label in the 'Ede experiment plot' view).
	 * @param groupNum
	 * @param frameNum
	 * @since 17/5/2017
	 * @return
	 */
	private String getLabelForScanDataPoint(int groupNum, int frameNum) {
		String label = "";

		if (includeCycleInPlotLabel) {
			label += "Cycle "+indexer.getRepetition()+" ";
		}

		// Only include group part of label if there's more than one timing group
		if (scanParameters.getGroups().size()>1) {
			label += "Group "+groupNum+" ";
		}

		label += "Spectrum "+frameNum;

		// Add motor position (if it's being used)
		if (moveMotorDuringScan) {
			try {
				String pos = ScannableUtils.getFormattedCurrentPosition(motorToMoveDuringScan);
				label += " Position : "+pos;
			} catch (DeviceException e) {
				logger.warn("Problem getting position from {}", motorToMoveDuringScan.getName(), e);
			}
		}
		return label;
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

	public boolean isUseNexusTreeWriter() {
		return useNexusTreeWriter;
	}

	public void setUseNexusTreeWriter(boolean useNexusTreeWriter) {
		this.useNexusTreeWriter = useNexusTreeWriter;
	}

	public void setNoOfSecPerSpectrumToPublish(double noOfSecPerSpectrumToPublish) {
		this.noOfSecPerSpectrumToPublish = noOfSecPerSpectrumToPublish;
	}
}
