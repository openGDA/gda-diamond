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

package gda.device.detector;

import gda.configuration.properties.LocalProperties;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.data.scan.datawriter.NexusDataWriter;
import gda.device.Detector;
import gda.device.DeviceException;
import gda.factory.FactoryException;
import gda.scan.ScanDataPoint;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;

import org.apache.commons.configuration.PropertiesConfiguration;
import org.apache.commons.lang.ArrayUtils;
import org.nexusformat.NexusFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.util.beans.xml.XMLHelpers;

/**
 * Operates the XStrip For High Energies Ge strip detector.
 * <p>
 * This is operated via a TFG/DAServer combination. It should return all 1024 counts in an array, a sum of all counts,
 * and sum of quadrants of the detector.
 * <p>
 * It should return the individual elements in the Nexus structure and the other values as scalers as well.
 * <p>
 * It is expected to only be operated via a series of frames.
 * <p>
 * Not implemented yet: beam orbit trigger, setup-leds. But these may not be required.
 * 
 * @author rjw82
 */
public class XHDetector extends DetectorBase implements StripDetector {

	private static final String STORENAME = "XH_rois";
	// strings to use in the get/set attributes methods
	public static final String ATTR_LOADPARAMETERS = "loadParameters";
	public static final String ATTR_READFIRSTFRAME = "readFirstFrame";
	public static final String ATTR_WRITEFIRSTFRAME = "writeFirstFrame";
	public static final String ATTR_ROIS = "regionsOfInterest";
	public static final String ROIS_CHANGED = "rois_changed";

	public static final double XSTRIP_CLOCKRATE = 20E-9; // s

	private static final Logger logger = LoggerFactory.getLogger(XHDetector.class);
	public static int NUMBER_ELEMENTS = 1024;

	// These are the objects this must know about.
	private String detectorName;
	private DAServer daServer = null;

	// must be in configuration info
	private String templateFileName;

	// da.server memory handles for reading back timing information and data
	private int timingHandle = -1;
	private int dataHandle = -1;
	
	private int scanDelayInMilliseconds = 0;

	private EdeScanParameters nextScan;

	private XHROI[] rois = new XHROI[0];
	private int lowerChannel = 0;
	private int upperChannel = NUMBER_ELEMENTS;
	private int[] excludedStrips;

	public XHDetector() {
		super();

		// defaults which will be updated when number of sectors changed
		this.inputNames = new String[] { "time" };
		this.extraNames = new String[] { "Group", "Frame", "Total", "sector1", "sector2", "sector3", "sector4" };
		this.outputFormat = new String[] { "%8.2f", "%8.2f", "%d", "%8.3f", "%8.3f", "%8.3f", "%8.3f", "%8.3f" };
	}

	@Override
	public void configure() throws FactoryException {
		try {
			if (getTemplateFileName() == null || getTemplateFileName().isEmpty()) {
				logger.error("template filename needs to be set.");
			} else {
				nextScan = (EdeScanParameters) XMLHelpers.createFromXML(EdeScanParameters.mappingURL,
					EdeScanParameters.class, EdeScanParameters.schemaURL, getTemplateFileName());
			}
		} catch (Exception e) {
			logger.error("Exception trying to read scan parameters into " + getName()
					+ " detector. Detector will not collect data correctly." + e.getMessage(), e);
		}

		loadROIsFromXML();

		try {
			close();
			// to read back data
			createNewDataHandle();
			// to read back timing data
			createNewTimingHandle();
		} catch (DeviceException e) {
			throw new FactoryException("Exception trying to create data readout handle to da.server", e);
		}
	}

	private void createNewTimingHandle() throws DeviceException {
		Object obj;
		if (daServer != null && !daServer.isConnected()) {
			daServer.connect();
		}

		if (daServer != null && daServer.isConnected()) {
			if ((obj = daServer.sendCommand("xstrip timing open \"xh0\"")) != null) {
				timingHandle = ((Integer) obj).intValue();
				if (timingHandle < 0) {
					throw new DeviceException("Failed to create the timing readback handle");
				}
				logger.info("open() using timingReadbackHandle " + timingHandle);
			}
		}
	}

	private void createNewDataHandle() throws DeviceException {
		Object obj;
		if (daServer != null && !daServer.isConnected()) {
			daServer.connect();
		}

		if (daServer != null && daServer.isConnected()) {
			if ((obj = daServer.sendCommand("xstrip open \"xh0\"")) != null) {
				dataHandle = ((Integer) obj).intValue();
				if (dataHandle < 0) {
					throw new DeviceException("Failed to create the timing readback handle");
				}
				logger.info("open() using data handle " + dataHandle);
			}
		}
	}

	private double[][] performCorrections(int[] rawData) {
		// TODO need to implement corrections and calibrations when details available from William
		int frameCount = rawData.length / NUMBER_ELEMENTS;
		double[][] out = new double[frameCount][NUMBER_ELEMENTS];

		for (int frame = 0; frame < frameCount; frame++) {
			for (int element = 0; element < NUMBER_ELEMENTS; element++) {
				
				// simply set excluded strips to be zero
				if (ArrayUtils.contains(excludedStrips, element)){
					out[frame][element] = 0.0;
				} else {
					out[frame][element] = rawData[(frame * NUMBER_ELEMENTS) + element];
				}
			}
		}
		return out;
	}

	@Override
	public int getStatus() throws DeviceException {
		ExperimentStatus current = fetchStatus();
		return current.detectorStatus;
	}

	/**
	 * Reads the first frame only.
	 */
	@Override
	public NexusTreeProvider readout() throws DeviceException {
		return readFrames(0, 0)[0];
	}

	/**
	 * Reads out the given frame to an array of ints. No corrections, no data reduction.
	 * 
	 * @param frame
	 * @return int[] - the raw data
	 * @throws DeviceException 
	 */
	public int[] readFrameToArray(int frame) throws DeviceException {
		return readoutFrames(frame, frame);
	}

	/**
	 * Returns a NexusTreeProvider for every frame.
	 * 
	 * @param startFrame
	 *            - absolute frame index ignoring the group num
	 * @param finalFrame
	 *            - absolute frame index ignoring the group num
	 * @return NexusTreeProvider[]
	 * @throws DeviceException 
	 */
	public NexusTreeProvider[] readFrames(int startFrame, int finalFrame) throws DeviceException {
		int[] elements = readoutFrames(startFrame, finalFrame);
		int numberOfFrames = finalFrame - startFrame + 1;
		int[][] rawDataInFrames = unpackRawDataToFrames(elements, numberOfFrames);

		NexusTreeProvider[] results = new NexusTreeProvider[rawDataInFrames.length];

		int frameNum = startFrame;
		for (int i = 0; i < rawDataInFrames.length; i++) {
			results[i] = readoutFrame(frameNum, rawDataInFrames[i]);
			frameNum++;
		}

		return results;
	}

	private int[][] unpackRawDataToFrames(int[] scalerData, int numFrames) {

		int[][] unpacked = new int[numFrames][NUMBER_ELEMENTS];
		int iterator = 0;

		for (int frame = 0; frame < numFrames; frame++) {
			for (int datum = 0; datum < NUMBER_ELEMENTS; datum++) {
				unpacked[frame][datum] = scalerData[iterator];
				iterator++;
			}
		}
		return unpacked;
	}

	/*
	 * Assumes it is given a NUMBER_ELEMENTS array of raw values
	 * 
	 * @param frameNum
	 *            - the absolute frame number
	 * @param elements
	 * @return NexusTreeProvider
	 */
	protected NXDetectorData readoutFrame(int frameNum, int[] elements) {
		double[] correctedData = performCorrections(elements)[0];

		NXDetectorData thisFrame = new NXDetectorData(this);
		thisFrame
				.addData(getName(), new int[] { 1, NUMBER_ELEMENTS }, NexusFile.NX_FLOAT64, correctedData, "counts", 1);

		double[] extraValues = getExtraValues(elements);
		String[] names = getExtraNames();

		// get values which match to da.server memory
		int absGroupNum = ExperimentLocationUtils.getGroupNum(nextScan, frameNum);
		int absFrameNum = ExperimentLocationUtils.getFrameNum(nextScan, frameNum);

		// add 1 to make the values understandable by users
		absGroupNum++;
		absFrameNum++;

		thisFrame.setPlottableValue(names[0], (double) absGroupNum);
		thisFrame.setPlottableValue(names[1], (double) absFrameNum);

		for (int i = 2; i < names.length; i++) {
			thisFrame.setPlottableValue(names[i], extraValues[i - 2]);
		}
		return thisFrame;
	}

	/*
	 * Returns an array of total counts, then totals counts in each ROI NB: this does not include the frame number which
	 * is the first of the plottableValues (extraNames)
	 */
	private double[] getExtraValues(int[] elements) {
		double[] extras = new double[getRois().length + 1];

		for (int elementNum = 0; elementNum < NUMBER_ELEMENTS; elementNum++) {
			extras[0] += elements[elementNum];
			int roi = whichROI(elementNum);
			if (roi >= 0) {
				extras[roi + 1] += elements[elementNum];
			}
		}
		return extras;
	}

	private int whichROI(int elementNum) {
		for (int i = 0; i < getRois().length; i++) {
			XHROI roi = getRois()[i];
			if (insideROI(elementNum, roi)) {
				return i;
			}
		}
		return -1;
	}

	private boolean insideROI(int elementNum, XHROI roi) {
		return elementNum >= roi.getLowerLevel() && elementNum <= roi.getUpperLevel();
	}

	/*
	 * @param startFrame
	 *            - absolute frame index ignoring the group num
	 * @param finalFrame
	 *            - absolute frame index ignoring the group num
	 * @return int[] - raw data from da.server memory
	 * @throws DeviceException 
	 */
	private synchronized int[] readoutFrames(int startFrame, int finalFrame) throws DeviceException {
		int[] value = null;
		if (hasValidDataHandle()) {
			int numFrames = finalFrame - startFrame + 1;
			try {
				value = daServer.getIntBinaryData("read 0 0 " + startFrame + " " + NUMBER_ELEMENTS + " 1 " + numFrames
						+ " from " + dataHandle + " raw motorola", 1024 * numFrames);
			} catch (Exception e) {
				throw new DeviceException("Exception while reading data from da.server",e);
			}
		}
		return value;
	}

	@Override
	public void collectData() throws DeviceException {
		start();
	}

	@Override
	public void atScanStart() throws DeviceException {
		clear();
	}

	@Override
	public void atScanEnd() throws DeviceException {
		stop();
	}

	@Override
	public void stop() throws DeviceException {
		daServer.sendCommand(createTimingCommand("stop"));

		if (hasValidDataHandle()) {
			sendCommand("disable "+ dataHandle);
		}
	}

	@Override
	public void close() throws DeviceException {
		if (hasValidTimingHandle()) {
			sendCommand("close "+ timingHandle);
			timingHandle = -1;
		}
		if (hasValidDataHandle()) {
			sendCommand("close "+ dataHandle);
			dataHandle = -1;
		}
	}

	public void clear() throws DeviceException {
		if (!hasValidDataHandle()) {
			createNewDataHandle();
		}
		if (hasValidDataHandle()) {
			sendCommand("clear "+ dataHandle);
		}
	}

	private boolean hasValidTimingHandle() {
		return this.timingHandle >= 0 && daServer != null && daServer.isConnected();
	}

	private boolean hasValidDataHandle() {
		return this.dataHandle >= 0 && daServer != null && daServer.isConnected();
	}

	@Override
	public void start() throws DeviceException {
		if (!hasValidDataHandle()) {
			createNewDataHandle();
		}
		if (!hasValidTimingHandle()) {
			createNewTimingHandle();
		}
		if (hasValidDataHandle() && hasValidTimingHandle()) {
			daServer.sendCommand(createTimingCommand("start"));
		}
	}

	private synchronized void sendCommand(String command) throws DeviceException {
		Object obj;
		if ((obj = daServer.sendCommand(command)) == null) {
			throw new DeviceException("Null reply received from daserver during " + command);
		} else if (((Integer) obj).intValue() == -1) {
			logger.error(getName() + ": " + command + " failed");
			close();
			throw new DeviceException("Xspress2System " + getName() + " " + command + " failed");
		}
	}

	/*
	 * @return  the given command with 'xstrip timing' prefixed and detectorName suffixed
	 */
	private String createTimingCommand(String command, Object... otherArgs) {
		String theCommand = "xstrip timing " + command + " \"" + detectorName + "\"";
		for (Object arg : otherArgs) {
			if (!arg.toString().isEmpty()) {
				theCommand += " " + arg.toString();
			}
		}
		return theCommand;
	}

	/**
	 * Setup the TFG from parameters held by the template xml file. The template file would be been created during
	 * configuration of this object
	 * @throws DeviceException 
	 */
	@Override
	public void loadTemplateParameters() throws DeviceException {
		defineDataCollectionFromScanParameters();
	}

	/**
	 * Setup the TFG from parameters from the given scan object. Does not start any data collection, that should be
	 * initiated by collectData().
	 * 
	 * @param newParameters
	 * @throws DeviceException 
	 */
	@Override
	public void loadParameters(EdeScanParameters newParameters) throws DeviceException {
		nextScan = newParameters;
		defineDataCollectionFromScanParameters();
	}

	/**
	 * Return the scan that would be run by the next call to collectData, or that is underway.
	 * 
	 * @return EdeScanParameters
	 */
	@Override
	public EdeScanParameters getLoadedParameters() {
		return nextScan;
	}

	/**
	 * Setup the TFG from parameters from the given xml file. Does not start any data collection, that should be
	 * initiated by collectData().
	 * 
	 * @param xmlFilename
	 */
	public void loadParameters(String xmlFilename) throws Exception {
		nextScan = (EdeScanParameters) XMLHelpers.createFromXML(EdeScanParameters.mappingURL, EdeScanParameters.class,
				EdeScanParameters.schemaURL, xmlFilename);
		defineDataCollectionFromScanParameters();
	}

	@Override
	public ExperimentStatus fetchStatus() throws DeviceException {
		String statusMessage = (String) daServer.sendCommand(createTimingCommand("read-status", "verbose"), true);
		if (statusMessage.startsWith("#")) {
			statusMessage = statusMessage.substring(1).trim();
		}
		String[] messageParts = statusMessage.split("[\n#:,]");

		ExperimentStatus newStatus = new ExperimentStatus();

		if (messageParts[0].trim().equalsIgnoreCase("running")) {
			newStatus.detectorStatus = Detector.BUSY;
		} else if (messageParts[0].trim().equalsIgnoreCase("paused")) {
			newStatus.detectorStatus = Detector.PAUSED;
		} else {
			newStatus.detectorStatus = Detector.IDLE;
		}

		for (String part : messageParts) {
			part = part.trim();
			if (part.contains("group_num")) {
				int group = Integer.parseInt(part.substring(part.indexOf("=") + 1));
				newStatus.loc.groupNum = group;
			}
			if (part.contains("frame_num")) {
				int group = Integer.parseInt(part.substring(part.indexOf("=") + 1));
				newStatus.loc.frameNum = group;
			}
			if (part.contains("scan_num")) {
				int group = Integer.parseInt(part.substring(part.indexOf("=") + 1));
				newStatus.loc.scanNum = group;
			}
		}

		return newStatus;
	}

	private void defineDataCollectionFromScanParameters() throws DeviceException {
		// read nextScan attribute and convert into daserver commands...

		addOutSignals();

		for (Integer i = 0; i < nextScan.getGroups().size(); i++) {

			TimingGroup timingGroup = nextScan.getGroups().get(i);

			// basic times
			Integer numFrames = timingGroup.getNumberOfFrames();
			double frameTimeInS = timingGroup.getTimePerFrame();
			String frameTimeInCycles = secondsToClockCyclesString(frameTimeInS);
			int numberOfScansPerFrame = timingGroup.getNumberOfScansPerFrame();
			double scanTimeInS = timingGroup.getTimePerScan();
			String scanTimeInClockCycles = secondsToClockCyclesString(scanTimeInS);

			String extTrig = buildExtTriggerCommand(timingGroup);

			String lemoOut = buildLemoOutCommand(timingGroup);

			String delays = buildDelaysCommand(timingGroup);

			String command;
			if (numberOfScansPerFrame == 0) {
				// use the frame-time qualifier
				command = createTimingCommand("setup-group", i, numFrames, 0, scanTimeInClockCycles, "frame-time",
						frameTimeInCycles, delays, lemoOut, extTrig);
			} else {

				command = createTimingCommand("setup-group", i, numFrames, numberOfScansPerFrame, frameTimeInCycles,
						 delays, lemoOut, extTrig);
				
				if (scanDelayInMilliseconds > 0) {
					float scanDelayInSeconds = (float) (scanDelayInMilliseconds / 1000.0);
					String scanPeriodInClockCycles = secondsToClockCyclesString(scanTimeInS + scanDelayInSeconds);
					command += " scan-period " + scanPeriodInClockCycles;
				}
			}
			

			if (i == nextScan.getGroups().size() - 1) {
				command = command.trim() + " last";
			}

			logger.info("Sending group to XH: " + command);
			daServer.sendCommand(command);
		}
	}

	private String buildDelaysCommand(TimingGroup timingGroup) {
		String toReturn = "";

		Double groupDelayInS = timingGroup.getPreceedingTimeDelay();
		if (groupDelayInS > 0) {

			String groupDelay = secondsToClockCyclesString(groupDelayInS);
			toReturn += "group-delay " + groupDelay;
		}

		Double frameDelayInS = timingGroup.getDelayBetweenFrames();
		if (frameDelayInS > 0) {
			long frameDelay = secondsToClockCycles(frameDelayInS);
			toReturn += " frame-delay " + frameDelay;
		}

		return toReturn.trim();
	}

	protected String buildLemoOutCommand(TimingGroup timingGroup) {
		String lemoOut = "";
		boolean[] outChoices = timingGroup.getOutLemos();
		int sum = 0;
		boolean any = false;
		for (int pow = 0; pow < outChoices.length; pow++) {
			if (outChoices[pow]) {
				sum += Math.pow(4, pow);
				any = true;
			}
		}
		if (any) {
			lemoOut = "lemo-out " + sum;
		}
		return lemoOut;
	}

	protected String buildExtTriggerCommand(TimingGroup timingGroup) {
		String extTrig = "";
		if (timingGroup.isGroupTrig()) {
			int lemo = timingGroup.getGroupTrigLemo();
			extTrig = "ext-trig-group trig-mux " + lemo;
			if (!timingGroup.isGroupTrigRisingEdge()) {
				extTrig += " trig-falling";
			}
		}
		if (timingGroup.isAllFramesTrig()) {
			int lemo = timingGroup.getAllFramesTrigLemo();
			extTrig += " ext-trig-frame trig-mux " + lemo;
			if (!timingGroup.isAllFramesTrigRisingEdge()) {
				extTrig += " trig-falling";
			}
		}
		if (timingGroup.isFramesExclFirstTrig()) {
			int lemo = timingGroup.getFramesExclFirstTrigLemo();
			extTrig += " ext-trig-frame-only trig-mux " + lemo;
			if (!timingGroup.isFramesExclFirstTrigRisingEdge()) {
				extTrig += " trig-falling";
			}
		}
		if (timingGroup.isScansTrig()) {
			int lemo = timingGroup.getScansTrigLemo();
			extTrig += " ext-trig-scan trig-mux " + lemo;
			if (!timingGroup.isScansTrigRisingEdge()) {
				extTrig += " trig-falling";
			}
		}
		extTrig = extTrig.trim();
		return extTrig;
	}

	protected long secondsToClockCycles(double timeInS) {
		return Math.round(timeInS / XSTRIP_CLOCKRATE);
	}

	protected String secondsToClockCyclesString(double timeInS) {
		if (timeInS == 0) {
			return "";
		}

		return String.format("%d", Math.round(timeInS / XSTRIP_CLOCKRATE));
	}

	private void addOutSignals() throws DeviceException {
		double[] delaysInS = nextScan.getOutputWidths();
		String[] delays = new String[delaysInS.length];
		for (int i = 0; i < delaysInS.length; i++) {
			delays[i] = secondsToClockCyclesString(delaysInS[i]);
		}

		String[] extOuts = nextScan.getOutputsChoices();
		daServer.sendCommand(createTimingCommand("ext-output", -1, "dc"));
		for (int i = 0; i < 8; i++) {
			if (!delays[i].isEmpty() && !extOuts[i].equals(EdeScanParameters.TRIG_NONE)) {
				daServer.sendCommand(createTimingCommand("ext-output", i, userToDAServerTrigOut(extOuts[i]), "width",
						delays[i]));
			} else if (!extOuts[i].equals(EdeScanParameters.TRIG_NONE)) {
				daServer.sendCommand(createTimingCommand("ext-output", i, userToDAServerTrigOut(extOuts[i])));
			}
		}
	}

	private String userToDAServerTrigOut(String userString) {
		if (userString == EdeScanParameters.TRIG_FRAME_AFTER) {
			return "frame-post-delay";
		} else if (userString == EdeScanParameters.TRIG_FRAME_BEFORE) {
			return "frame-pre-delay";
		} else if (userString == EdeScanParameters.TRIG_GROUP_AFTER) {
			return "group-post-delay";
		} else if (userString == EdeScanParameters.TRIG_GROUP_BEFORE) {
			return "group-pre-delay";
		} else if (userString == EdeScanParameters.TRIG_SCAN_BEFORE) {
			return "scan-pre-delay";
		}
		return "unknown/unused user string";
	}

	/**
	 * To send the continue command when a group has been setup to wait for an input from a software trigger (LEMO #9)
	 * 
	 * @throws DeviceException 
	 */
	@Override
	public void fireSoftTrig() throws DeviceException {
		daServer.sendCommand(createTimingCommand("continue"));
	}

	/**
	 * This information should be wrapped better in the future but need to know if this works and how it will be used
	 * first.
	 * 
	 * @return raw data from the timing settings part of the TFG memory
	 * @throws DeviceException
	 */
	public int[] getRawTimingSettings() throws DeviceException {
		int[] value = null;
		if (!hasValidTimingHandle()) {
			createNewTimingHandle();
		}
		if (hasValidTimingHandle()) {
			try {
				value = daServer.getIntBinaryData("read 0 0 0 30 1024 1 from " + timingHandle + " raw motorola",
						30 * 1024);
			} catch (Exception e) {
				throw new DeviceException("Exception while setting timing data from da.server",e);
			}
		}
		return value;
	}

	@Override
	public Object getAttribute(String attributeName) throws DeviceException {
		if (attributeName.equals(ATTR_READFIRSTFRAME)) {
			int[] elements = readoutFrames(0, 0);
			double[] correctedData = performCorrections(elements)[0];
			return correctedData;
		} else if (attributeName.equals(ATTR_WRITEFIRSTFRAME)) {
			writeNexusFile();
			return null;
		} else if (attributeName.equals(ATTR_ROIS)) {
			return getRois();
		}
		return super.getAttribute(attributeName);
	}

	protected void writeNexusFile() throws DeviceException {
		try {
			ScanDataPoint sdp = new ScanDataPoint();
			sdp.addDetector(this);
			sdp.addDataFromDetector(this);
			sdp.setCurrentPointNumber(0);
			sdp.setNumberOfPoints(1);
			sdp.setScanDimensions(new int[1]);

			NexusDataWriter writer = new NexusDataWriter();
			writer.configureScanNumber(null);
			writer.addData(sdp);

		} catch (Exception e) {
			throw new DeviceException(e.getMessage(), e);
		}
	}

	@Override
	public void setAttribute(String attributeName, Object value) throws DeviceException {
		if (attributeName.equals(ATTR_LOADPARAMETERS) && value instanceof EdeScanParameters) {
			loadParameters((EdeScanParameters) value);
		} else if (attributeName.equals(ATTR_ROIS) && value instanceof XHROI[]) {
			setRois((XHROI[]) value);
		} else {
			super.setAttribute(attributeName, value);
		}
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {
		return false;
	}

	@Override
	public String getDescription() throws DeviceException {
		return "XSTRIP for high Energies";
	}

	@Override
	public String getDetectorID() throws DeviceException {
		return "XH for I20 Energy Dispersive EXAFS branchline";
	}

	@Override
	public String getDetectorType() throws DeviceException {
		return "XSTRIP for high Energies";
	}

	public String getDetectorName() {
		return detectorName;
	}

	public void setDetectorName(String detectorName) {
		this.detectorName = detectorName;
	}

	public DAServer getDaServer() {
		return daServer;
	}

	public void setDaServer(DAServer daServer) {
		this.daServer = daServer;
	}

	public void setTemplateFileName(String templateFileName) {
		this.templateFileName = templateFileName;
	}

	public String getTemplateFileName() {
		return templateFileName;
	}

	@Override
	public XHROI[] getRois() {
		return rois;
	}

	@Override
	public void setRois(XHROI[] rois) {
		setRoisWithoutStoringAndNotifying(rois);
		saveROIsToXML();
		notifyIObservers(this, XHDetector.ROIS_CHANGED);
	}

	public int getScanDelayInMilliseconds() {
		return scanDelayInMilliseconds;
	}

	public void setScanDelayInMilliseconds(int scanDelayInMilliseconds) {
		this.scanDelayInMilliseconds = scanDelayInMilliseconds;
	}

	@Override
	public void setNumberRois(int numberOfRois) {
		
		XHROI[] newRois = new XHROI[numberOfRois];

		int numberChannelsInUse = upperChannel - lowerChannel + 1;
		int roiSize = numberChannelsInUse / numberOfRois;

		for (int i = 0; i < numberOfRois; i++) {
			XHROI thisRoi = new XHROI();
			thisRoi.setLabel("ROI_" + i);
			int lowerChannelForThisROI = roiSize * i + lowerChannel;
			thisRoi.setLowerLevel(lowerChannelForThisROI);
			thisRoi.setUpperLevel(lowerChannelForThisROI + roiSize - 1);
			newRois[i] = thisRoi;
		}
		setRois(newRois);
	}

	/**
	 * @return the number of ROIS, whether they have been set via the setNumberRois or setRois methods.
	 */
	public int getNumberRois() {
		return rois.length;
	}

	private void setDefaultROIs() {
		setNumberRois(4);
	}

	private void setRoisWithoutStoringAndNotifying(XHROI[] rois) {
		int numROI;
		if (rois != null) {
			numROI = rois.length;
			this.rois = rois;
		} else {
			numROI = 0;
			this.rois = new XHROI[0];
		}

		extraNames = new String[numROI + 3];
		outputFormat = new String[numROI + 4];
		extraNames[0] = "Group";
		extraNames[1] = "Frame";
		extraNames[2] = "Total";
		outputFormat[0] = "%8.3f";
		outputFormat[1] = "%8.3f";
		outputFormat[2] = "%d";
		outputFormat[3] = "%8.3f";

		if (rois != null && numROI > 0) {
			for (int i = 0; i < numROI; i++) {
				extraNames[i + 3] = rois[i].getName();
				outputFormat[i + 3] = "%8.3f";
			}
		}
	}
	
	private String getStoreFileName() {
		String propertiesFileName = LocalProperties.getVarDir() + getName() + STORENAME;
		return propertiesFileName;
	}


	private void saveROIsToXML() {
		try {
			String propertiesFileName = getStoreFileName();
			File test = new File(propertiesFileName);
			if (!test.exists()){
				try {
					test.createNewFile();
				} catch (IOException e) {
					throw e;
				}
			}
			
			PropertiesConfiguration store = new PropertiesConfiguration(propertiesFileName);	
			for (XHROI roi : getRois()) {
				store.setProperty(roi.getName() + "_lowerlevel", roi.getLowerLevel());
				store.setProperty(roi.getName() + "_upperlevel", roi.getUpperLevel());
			}
			store.save();
		} catch (Exception e) {
			logger.error("Exception writing XH ROIs to xml file", e);
		}
	}

	private void loadROIsFromXML() {

		HashMap<String, XHROI> tempROIs = new LinkedHashMap<String, XHROI>();
		try {
			PropertiesConfiguration store = new PropertiesConfiguration(getStoreFileName());
			@SuppressWarnings("unchecked")
			Iterator<String> i = store.getKeys();
			while (i.hasNext()) {
				String key = i.next();

				if (key.isEmpty()) {
					continue;
				}

				String[] partsString = key.split("_");
				if (!tempROIs.keySet().contains(partsString[0])) {
					tempROIs.put(partsString[0], new XHROI(partsString[0]));
				}

				XHROI thisROI = tempROIs.get(partsString[0]);
				if (partsString[1].equals("lowerlevel")) {
					thisROI.setLowerLevel(store.getInteger(key, 0));
				} else if (partsString[1].equals("upperlevel")) {
					thisROI.setUpperLevel(store.getInteger(key, 1023));
				}
			}
			setRoisWithoutStoringAndNotifying(tempROIs.values().toArray(new XHROI[0]));
		} catch (Exception e) {
			setDefaultROIs();
		}
	}

	@Override
	public void setLowerChannel(int channel) {
		this.lowerChannel = channel;
		
	}

	@Override
	public int getLowerChannel() {
		return lowerChannel;
	}

	@Override
	public void setUpperChannel(int channel) {
		this.upperChannel = channel;
	}

	@Override
	public int getUpperChannel() {
		return upperChannel;
	}

	@Override
	public void setBias(Double biasVoltage) throws DeviceException {
		// TODO what should be the volatge upper limit?
		if (biasVoltage < 0.0 || biasVoltage > 10000) {
			throw new DeviceException ("Bias volatge of " + biasVoltage + " is unacceptable.");
		}
		
		// TODO test with hardware
		// TODO add to dummydaserver the correct response from da.server
		Double currentValue = getBias();
		if (currentValue == 0.0) {
			daServer.sendCommand("xstrip hv init");
			daServer.sendCommand("xstrip hv enable " + detectorName);
		}
		daServer.sendCommand("xstrip hv set-dac " + detectorName + " " + biasVoltage);
		
	}

	@Override
	public Double getBias() throws DeviceException {
		// TODO test against hardware
		String result = (String) daServer.sendCommand("xstrip hv summary " + detectorName);
		// TODO parse the result string at this point
		if (!result.isEmpty()) {
			return (Double) daServer.sendCommand("xstrip hv get-adc hv " + detectorName);
		}
		return 0.0;
	}

	@Override
	public void setExcludedStrips(int[] excludedStrips) throws DeviceException {
		this.excludedStrips = excludedStrips;
	}

	@Override
	public int[] getExcludedStrips() {
		return excludedStrips;
	}
}
