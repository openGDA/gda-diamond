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
import gda.data.NumTracker;
import gda.data.PathConstructor;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.data.scan.datawriter.NexusDataWriter;
import gda.device.Detector;
import gda.device.DeviceException;
import gda.factory.FactoryException;
import gda.jython.InterfaceProvider;
import gda.scan.ScanDataPoint;
import gda.scan.ede.datawriters.EdeDataConstants;
import gda.scan.ede.datawriters.ScanDataHelper;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;

import org.apache.commons.configuration.ConfigurationException;
import org.apache.commons.configuration.PropertiesConfiguration;
import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang.ArrayUtils;
import org.dawnsci.plotting.tools.profile.DataFileHelper;
import org.eclipse.dawnsci.analysis.api.dataset.IDataset;
import org.eclipse.dawnsci.analysis.dataset.impl.DoubleDataset;
import org.nexusformat.NexusFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.exafs.calibration.data.CalibrationDetails;
import uk.ac.gda.exafs.detectortemperature.XCHIPTemperatureLogParser;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.util.beans.xml.XMLHelpers;

import com.google.gson.Gson;

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
public class XHDetector extends DetectorBase implements XCHIPDetector {

	private static final String ROIS_PROP_KEY = "ROIs";

	private static final String CONNECTED_KEY = "connected";

	private static final double MIN_BIAS_VOLTAGE = 1.0;
	private static final double MAX_BIAS_VOLTAGE = 137.0;

	private static final String EXCLUDED_STRIPS_PROPERTY = "excludedStrips";
	private static final String STORENAME = "XH_rois";
	// strings to use in the get/set attributes methods
	public static final String ATTR_LOADPARAMETERS = "loadParameters";
	public static final String ATTR_READFIRSTFRAME = "readFirstFrame";
	public static final String ATTR_WRITEFIRSTFRAME = "writeFirstFrame";
	public static final String ATTR_READALLFRAMES = "readAllFrames";
	public static final String ATTR_ROIS = "regionsOfInterest";
	public static final String ROIS_CHANGED = "rois_changed";

	public static final double XSTRIP_CLOCKRATE = 20E-9; // s

	private static final Gson GSON = new Gson();

	private static final Logger logger = LoggerFactory.getLogger(XHDetector.class);
	private static final String SENSOR0NAME = "Peltier Hotplate";
	private static final String SENSOR1NAME = "Peltier Coldplate";
	private static final String SENSOR2NAME = "PCB power supply";
	private static final String SENSOR3NAME = "PCB control";

	public static int NUMBER_ELEMENTS = 1024;
	public static int START_STRIP = 0;

	private static final int DETECTOR_ERROR_CODE = -1;
	private static final String DETECTOR_ERROR_CODE_STR = "-1";

	private static final int EXTERNAL_OUTPUT_WIDTH_AS_SIGNAL_CYCLES = 100;

	private static Integer[] STRIPS;

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
	private int lowerChannel = START_STRIP;
	private int upperChannel = STRIPS[STRIPS.length - 1];
	private Integer[] excludedStrips;
	private boolean connected;

	private CalibrationDetails calibration;

	private String tempLogFilename;

	static {
		STRIPS = new Integer[NUMBER_ELEMENTS];
		for (int i = 0; i < NUMBER_ELEMENTS; i++) {
			STRIPS[i] = new Integer(i + START_STRIP);
		}
	}

	public XHDetector() {
		super();
		// defaults which will be updated when number of sectors changed
		inputNames = new String[] { "time" };
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

		loadFromXML();

		loadExcludedStrips();

		try {
			connectIfWasBefore();
		} catch (DeviceException e) {
			logger.error(getName() + " was connected when GDA last run but failed to reconnect.", e);
		}
	}

	private void connectIfWasBefore() throws DeviceException {
		if (wasConnected()) {
			connect();
		}

	}

	private boolean wasConnected() {
		PropertiesConfiguration store;
		try {
			store = new PropertiesConfiguration(getStoreFileName());
			if (store.containsKey(CONNECTED_KEY)) {
				return store.getBoolean(CONNECTED_KEY);
			}
			return false;
		} catch (ConfigurationException e) {
		}
		return false;
	}

	private void saveConnectedState() {
		PropertiesConfiguration store;
		try {
			store = new PropertiesConfiguration(getStoreFileName());
			store.setProperty(CONNECTED_KEY, isConnected());
			store.save();
		} catch (ConfigurationException e) {
			logger.error("Unable to store connected state", e);
		}

	}

	@Override
	public void connect() throws DeviceException {
		synchronized (getName()) {
			if (connected) {
				return;
			}
			logger.debug("connecting");
			try {
				disconnect();
				// to read back data
				createNewDataHandle();
				// to read back timing data
				createNewTimingHandle();
				// startTemperatureLogging();
				connected = true;
			} catch (DeviceException e) {
				connected = false;
				throw new DeviceException("Exception trying to create data readout handle to da.server", e);
			} finally {
				saveConnectedState();
			}
		}
	}

	@Override
	public void startTemperatureLogging() throws DeviceException {
		// derive the filename
		DateFormat dateFormat = new SimpleDateFormat("yyyy_MM_dd_HH_mm_ss");
		Date date = new Date();
		tempLogFilename = PathConstructor.createFromDefaultProperty() + "spool/" + getName() + "_temperatures_"
				+ dateFormat.format(date) + ".log";

		// tell the detector to start temp logging to the filename
		int result = (int) daServer.sendCommand("xstrip tc set \"xh0\" autoinc -1 logt '" + tempLogFilename +"'");
		if (result == -1) {
			throw new DeviceException("Failed to start logging " + getName() + " tempratures to " + tempLogFilename);
		}

		logger.info(getName() + " temperatures now being logged to " + tempLogFilename);

	}

	@Override
	public void stopTemperatureLogging() throws DeviceException {
		// tell the detector to start temp logging to the filename
		int result = (int) daServer.sendCommand("xstrip tc set \"xh0\" autoinc 0");
		if (result == -1) {
			throw new DeviceException("Failed to start logging " + getName() + " tempratures to " + tempLogFilename);
		}

		logger.info(getName() + " temperature logging stopped.");

	}


	@Override
	public void disconnect() throws DeviceException {
		if (isConnected()) {
			try {
				stopTemperatureLogging();
			} catch (Exception e) {
				logger.error("Exception when stopping temperature logging when disconnecting", e);
			}
			close();
		}
		connected = false;
		saveConnectedState();
	}

	@Override
	public boolean isConnected() {
		return connected;
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

	@Override
	public int getNumberChannels() {
		return NUMBER_ELEMENTS;
	}

	private double[][] performCorrections(int[] rawData, boolean checkForExcludedStrips) {
		int frameCount = rawData.length / NUMBER_ELEMENTS;
		double[][] out = new double[frameCount][NUMBER_ELEMENTS];
		for (int frame = 0; frame < frameCount; frame++) {
			for (int stripIndex = 0; stripIndex < STRIPS.length; stripIndex++) {
				if (checkForExcludedStrips) {
					// simply set excluded strips to be zero
					if (ArrayUtils.contains(excludedStrips, STRIPS[stripIndex])) {
						out[frame][stripIndex] = 0.0;
					} else if (!nextScan.getIncludeCountsOutsideROIs() && STRIPS[stripIndex] < lowerChannel
							|| STRIPS[stripIndex] > upperChannel) {
						out[frame][stripIndex] = 0.0;
					} else {
						out[frame][stripIndex] = rawData[(frame * NUMBER_ELEMENTS) + stripIndex];
					}
				} else {
					out[frame][stripIndex] = rawData[(frame * NUMBER_ELEMENTS) + stripIndex];
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
	@Override
	public NexusTreeProvider[] readFrames(int startFrame, int finalFrame) throws DeviceException {
		int[] elements = readoutFrames(startFrame, finalFrame);
		int numberOfFrames = finalFrame - startFrame + 1;
		int[][] rawDataInFrames = unpackRawDataToFrames(elements, numberOfFrames);

		NexusTreeProvider[] results = new NexusTreeProvider[rawDataInFrames.length];

		for (int i = 0; i < rawDataInFrames.length; i++) {
			results[i] = readoutFrame(rawDataInFrames[i]);
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
	 * @param frameNum - the absolute frame number
	 * @param elements
	 * @return NexusTreeProvider
	 */
	protected NXDetectorData readoutFrame(int[] elements) {

		double[] correctedData = performCorrections(elements, true)[0];
		NXDetectorData thisFrame = new NXDetectorData(this);

		double[] energies = this.getEnergyForChannels();

		thisFrame.addAxis(getName(), EdeDataConstants.ENERGY_COLUMN_NAME, new int[] { NUMBER_ELEMENTS }, NexusFile.NX_FLOAT64, energies, 1, 1, "eV", false);
		thisFrame.addData(getName(), EdeDataConstants.DATA_COLUMN_NAME, new int[] { NUMBER_ELEMENTS }, NexusFile.NX_FLOAT64, correctedData, "eV", 1);

		double[] extraValues = getExtraValues(elements);
		String[] names = getExtraNames();

		int offset = 0;

		for (int i = offset; i < names.length; i++) {
			thisFrame.setPlottableValue(names[i], extraValues[i - offset]);
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
			int roi = whichROI(elementNum);
			if (roi >= 0) {
				extras[0] += elements[elementNum];
				extras[roi + 1] += elements[elementNum];
			}
		}
		return extras;
	}

	private int whichROI(int elementIndex) {
		for (int i = 0; i < getRois().length; i++) {
			XHROI roi = getRois()[i];
			if (insideROI(STRIPS[elementIndex], roi)) {
				return i;
			}
		}
		return -1;
	}

	private boolean insideROI(int elementNumber, XHROI roi) {
		return elementNumber >= roi.getLowerLevel() && elementNumber <= roi.getUpperLevel();
	}

	/*
	 * @param startFrame - absolute frame index ignoring the group num
	 * @param finalFrame - absolute frame index ignoring the group num
	 * @return int[] - raw data from da.server memory
	 * @throws DeviceException
	 */
	private synchronized int[] readoutFrames(int startFrame, int finalFrame) throws DeviceException {
		int[] value = null;
		if (hasValidDataHandle()) {
			int numFrames = finalFrame - startFrame + 1;
			try {
				String readCommand = "read 0 0 " + startFrame + " " + NUMBER_ELEMENTS + " 1 " + numFrames + " from "
						+ dataHandle + " raw motorola";
				value = daServer.getIntBinaryData(readCommand, 1024 * numFrames);
			} catch (Exception e) {
				throw new DeviceException("Exception while reading data from da.server", e);
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
			sendCommand("disable " + dataHandle);
		}
	}

	@Override
	public void close() throws DeviceException {
		if (hasValidTimingHandle()) {
			sendCommand("close " + timingHandle);
			timingHandle = -1;
		}
		if (hasValidDataHandle()) {
			sendCommand("close " + dataHandle);
			dataHandle = -1;
		}
	}

	public void clear() throws DeviceException {
		if (!hasValidDataHandle()) {
			createNewDataHandle();
		}
		if (hasValidDataHandle()) {
			sendCommand("clear " + dataHandle);
		}
	}

	private boolean hasValidTimingHandle() {
		return timingHandle >= 0 && daServer != null && daServer.isConnected();
	}

	private boolean hasValidDataHandle() {
		return dataHandle >= 0 && daServer != null && daServer.isConnected();
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
			throw new DeviceException("Detector " + getName() + " " + command + " failed");
		}
	}

	/*
	 * @return the given command with 'xstrip timing' prefixed and detectorName suffixed
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
	 * 
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

		String stateString = messageParts[0];
		if (stateString.contains("*")){
			stateString = messageParts[1];
		}
		stateString = stateString.trim();

		ExperimentStatus newStatus = new ExperimentStatus();

		if (stateString.startsWith("Running")) {
			newStatus.detectorStatus = Detector.BUSY;
		} else if (stateString.startsWith("Paused")) {
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

			// TODO Review this, may be warn the user
			if (scanTimeInS == frameTimeInS) {
				frameTimeInCycles = "0";
				frameTimeInS = 0;
				numberOfScansPerFrame = 1;
			}

			if (scanTimeInClockCycles.isEmpty() && numberOfScansPerFrame != 0) {
				// something's wrong, so switch frame time to scan time.
				scanTimeInS = frameTimeInS / numberOfScansPerFrame;
				scanTimeInClockCycles = secondsToClockCyclesString(scanTimeInS);
				frameTimeInCycles = "";
			}

			String extTrig = buildExtTriggerCommand(timingGroup);

			String lemoOut = buildLemoOutCommand(timingGroup);

			String delays = buildDelaysCommand(timingGroup);

			String command;
			if (numberOfScansPerFrame == 0) {
				// use the frame-time qualifier
				command = createTimingCommand("setup-group", i, numFrames, 0, scanTimeInClockCycles, "frame-time",
						frameTimeInCycles, delays, lemoOut, extTrig);
			} else {

				command = createTimingCommand("setup-group", i, numFrames, numberOfScansPerFrame,
						scanTimeInClockCycles, delays, lemoOut, extTrig);

				if (scanDelayInMilliseconds > 0) {
					float scanDelayInSeconds = (float) (scanDelayInMilliseconds / 1000.0);
					String scanPeriodInClockCycles = secondsToClockCyclesString(scanTimeInS + scanDelayInSeconds);
					command += " scan-period " + scanPeriodInClockCycles;
				}
			}

			if (i == nextScan.getGroups().size() - 1) {
				command = command.trim() + " last";
			}

			sendExternalOutputCommand();

			logger.info("Sending group to XH: " + command);
			Object result = daServer.sendCommand(command);
			if (result.toString().compareTo("-1") == 0) {
				throw new DeviceException(
						"The given parameters were not accepted by da.server! Check frame and scan times.");
			}
		}
	}

	private void sendExternalOutputCommand() throws DeviceException {
		List<String> commands = new ArrayList<String>();
		commands.add("xstrip timing ext-output \"xh0\" 0 " + "group-pre-delay" + " width " + EXTERNAL_OUTPUT_WIDTH_AS_SIGNAL_CYCLES);
		commands.add("xstrip timing ext-output \"xh0\" 1 " + "group-post-delay" + " width " + EXTERNAL_OUTPUT_WIDTH_AS_SIGNAL_CYCLES);
		commands.add("xstrip timing ext-output \"xh0\" 2 " + "frame-pre-delay" + " width " + EXTERNAL_OUTPUT_WIDTH_AS_SIGNAL_CYCLES);
		commands.add("xstrip timing ext-output \"xh0\" 3 " + "frame-post-delay" + " width " + EXTERNAL_OUTPUT_WIDTH_AS_SIGNAL_CYCLES);
		commands.add("xstrip timing ext-output \"xh0\" 4 " + "scan-pre-delay" + " width " + EXTERNAL_OUTPUT_WIDTH_AS_SIGNAL_CYCLES);
		commands.add("xstrip timing ext-output \"xh0\" 5 " + "scan-post-delay" + " width " + EXTERNAL_OUTPUT_WIDTH_AS_SIGNAL_CYCLES);
		commands.add("xstrip timing ext-output \"xh0\" 6 " + "integration");
		commands.add("xstrip timing ext-output \"xh0\" 7 " + "aux1");
		for (String extCommand : commands) {
			logger.info("Sending external output configuration to XH: " + extCommand);
			Object result = daServer.sendCommand(extCommand);
			if (result.toString().compareTo(DETECTOR_ERROR_CODE_STR) == 0) {
				throw new DeviceException(
						"The given parameters were not accepted by da.server! Check frame and scan times.");
			}
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
				throw new DeviceException("Exception while setting timing data from da.server", e);
			}
		}
		return value;
	}

	@Override
	public Object getAttribute(String attributeName) throws DeviceException {
		if (attributeName.equals(ATTR_READFIRSTFRAME)) {
			int[] elements = readoutFrames(0, 0);
			double[] correctedData = performCorrections(elements, true)[0];
			return correctedData;
		} else if (attributeName.equals(ATTR_READALLFRAMES)) {
			int[] elements = readoutFrames(0, 0);
			double[] correctedData = performCorrections(elements, false)[0];
			return correctedData;
		} else if (attributeName.equals(ATTR_WRITEFIRSTFRAME)) {
			writeLiveDataFiles();
			return null;
		} else if (attributeName.equals(ATTR_ROIS)) {
			return getRois();
		}
		return super.getAttribute(attributeName);
	}

	protected void writeLiveDataFiles() throws DeviceException {
		try {
			ScanDataPoint sdp = new ScanDataPoint();
			sdp.addDetector(this);
			sdp.addDataFromDetector(this);
			sdp.setCurrentPointNumber(0);
			sdp.setNumberOfPoints(1);
			sdp.setScanDimensions(new int[1]);

			NumTracker runNumber = new NumTracker("scanbase_numtracker");
			int scanNumber = runNumber.incrementNumber();

			NexusDataWriter writer = new NexusDataWriter();
			writer.configureScanNumber(scanNumber);
			writer.addData(sdp);

			writeAsciiFile(sdp, writer.getCurrentFileName());
		} catch (Exception e) {
			throw new DeviceException(e.getMessage(), e);
		}
	}

	private void writeAsciiFile(ScanDataPoint sdp,String nexusFilePath) throws Exception {
		DoubleDataset dataSet = ScanDataHelper.extractDetectorDataFromSDP(this.getName(), sdp);
		String asciiFileFolder = DataFileHelper.convertFromNexusToAsciiFolder(nexusFilePath);
		String asciiFilename = FilenameUtils.getBaseName(nexusFilePath);
		File asciiFile = new File(asciiFileFolder, asciiFilename + "." + EdeDataConstants.ASCII_FILE_EXTENSION);
		if (asciiFile.exists()) {
			throw new Exception("File " + asciiFilename + " already exists!");
		}
		FileWriter asciiFileWriter = null;
		String line = System.getProperty("line.separator");
		try {
			asciiFileWriter = new FileWriter(asciiFile);
			asciiFileWriter.write(String.format("#%s\t%s", EdeDataConstants.STRIP_COLUMN_NAME, EdeDataConstants.ENERGY_COLUMN_NAME));
			asciiFileWriter.write(line);
			for (int i = 0; i < dataSet.getSize(); i++) {
				asciiFileWriter.write(String.format("%d\t%f", i, dataSet.get(i)));
				asciiFileWriter.write(line);
			}
		} catch(Exception ex) {
			throw new Exception("Unable to write ascii data");
		} finally {
			if (asciiFileWriter != null) {
				asciiFileWriter.close();
				InterfaceProvider.getTerminalPrinter().print("Writing data to file (Ascii): " + asciiFile.getAbsolutePath());
			}
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
		saveToXML();
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
		XHROI[] xhrois = createRois(numberOfRois);
		setRois(xhrois);
	}

	private XHROI[] createRois(int numberOfRois) {
		XHROI[] xhrois = new XHROI[numberOfRois];
		int useableRegion = upperChannel - (lowerChannel - 1); // Inclusive of the first
		int increment = useableRegion / numberOfRois;
		int start = lowerChannel;
		for (int i = 0; i < numberOfRois; i++) {
			XHROI xhroi = new XHROI("ROI_" + (i + 1));
			xhroi.setLowerLevel(start);
			xhroi.setUpperLevel(start + increment - 1);
			xhrois[i] = xhroi;
			start = start + increment;
		}
		if (xhrois[xhrois.length - 1].getUpperLevel() < upperChannel) {
			xhrois[xhrois.length - 1].setUpperLevel(upperChannel);
		}
		return xhrois;
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
			logger.debug("set " + rois.length);
		} else {
			numROI = 0;
			this.rois = new XHROI[0];
		}

		extraNames = new String[numROI + 1];
		outputFormat = new String[numROI + 2];
		outputFormat[0] = "%8.3f";
		extraNames[0] = "Total";
		outputFormat[1] = "%8.3f";

		if (rois != null && numROI > 0) {
			for (int i = 0; i < numROI; i++) {
				extraNames[i + 1] = rois[i].getName();
				outputFormat[i + 2] = "%8.3f";
			}
		}
	}

	private String getStoreFileName() {
		String propertiesFileName = LocalProperties.getVarDir() + getName() + STORENAME;
		return propertiesFileName;
	}

	private void saveToXML() {
		try {
			String propertiesFileName = getStoreFileName();
			File propertiesFile = new File(propertiesFileName);
			if (!propertiesFile.exists()) {
				try {
					propertiesFile.createNewFile();
				} catch (IOException e) {
					throw e;
				}
			}

			PropertiesConfiguration store = new PropertiesConfiguration();
			store.setDelimiterParsingDisabled(true);
			store.setFile(propertiesFile);
			store.load();
			store.clear();
			store.setProperty(ROIS_PROP_KEY, GSON.toJson(getRois()));
			if (calibration != null) {
				store.setProperty(CALIBRATION_PROP_KEY, GSON.toJson(calibration));
			}
			store.save();
		} catch (Exception e) {
			logger.warn("Exception writing XH ROIs to xml file");
		}
	}

	private void loadFromXML() {
		try {
			String propertiesFileName = getStoreFileName();
			File propertiesFile = new File(propertiesFileName);
			if (!propertiesFile.exists()) {
				setDefaultROIs();
				return;
			}
			PropertiesConfiguration store = new PropertiesConfiguration();
			store.setDelimiterParsingDisabled(true);
			store.setFile(propertiesFile);
			store.load();
			String roisJsonArray = store.getString(ROIS_PROP_KEY);
			if (roisJsonArray == null) {
				this.setDefaultROIs();
			} else {
				setRoisWithoutStoringAndNotifying(GSON.fromJson(roisJsonArray, XHROI[].class));
			}
			String storeCalibration = store.getString(CALIBRATION_PROP_KEY);
			if (storeCalibration != null && !storeCalibration.isEmpty()) {
				String[] coeffsString = storeCalibration.split(" ");
				double[] coeffs = new double[coeffsString.length];
				for (int index = 0; index < coeffsString.length; index++) {
					coeffs[index] = Double.parseDouble(coeffsString[index]);
				}
				calibration = GSON.fromJson(storeCalibration, CalibrationDetails.class);
			}
		} catch (Exception e) {
			logger.error("Error loading ROIs, now loading defaults", e);
			setDefaultROIs();
		}
	}

	@Override
	public void setLowerChannel(int channel) {
		lowerChannel = channel;
		setNumberRois(getNumberRois());
	}

	@Override
	public int getLowerChannel() {
		return lowerChannel;
	}

	@Override
	public void setUpperChannel(int channel) {
		upperChannel = channel;
		setNumberRois(getNumberRois());
	}

	@Override
	public int getUpperChannel() {
		return upperChannel;
	}

	@Override
	public void setBias(Double biasVoltage) throws DeviceException {
		if (biasVoltage < getMinBias() | biasVoltage > getMaxBias()) {
			throw new DeviceException("Bias voltage of " + biasVoltage + " is unacceptable.");
		}

		Double currentValue = getBias();
		if (currentValue == 0.0) {
			daServer.sendCommand("xstrip hv init");
			daServer.sendCommand("xstrip hv enable \"" + detectorName + "\"");
		}
		daServer.sendCommand("xstrip hv set-dac \"" + detectorName + "\" " + biasVoltage + " hv");
	}

	@Override
	public Double getBias() throws DeviceException {
		return (Double) daServer.sendCommand("xstrip hv get-adc \"" + detectorName + "\" hv");
	}

	@Override
	public void setExcludedStrips(Integer[] excludedStrips) throws DeviceException {
		this.excludedStrips = excludedStrips;
		saveExcludedStrips();
	}

	private void saveExcludedStrips() {
		PropertiesConfiguration store;
		try {
			store = new PropertiesConfiguration(getStoreFileName());
			store.setProperty(EXCLUDED_STRIPS_PROPERTY, DataHelper.toString(excludedStrips));
			store.save();
		} catch (ConfigurationException e) {
		}
	}

	@Override
	public Integer[] getExcludedStrips() {
		return excludedStrips;
	}

	private void loadExcludedStrips() {
		PropertiesConfiguration store;
		try {
			store = new PropertiesConfiguration(getStoreFileName());
			String[] excludedStripsArray = store.getStringArray(EXCLUDED_STRIPS_PROPERTY);
			if ((excludedStripsArray.length == 0)
					|| (excludedStripsArray.length == 1 && excludedStripsArray[0].isEmpty())) {
				excludedStrips = new Integer[] {};
				return;
			}

			excludedStrips = new Integer[excludedStripsArray.length];
			for (int i = 0; i < excludedStripsArray.length; i++) {
				// TODO Review and find a generic way to convert index to value
				excludedStrips[i] = STRIPS[Integer.parseInt(excludedStripsArray[i]) - START_STRIP];
			}
		} catch (ConfigurationException e) {
			excludedStrips = new Integer[] {};
		}
	}

	public static Integer[] getStrips() {
		return STRIPS;
	}


	public static double[] getStripsInDouble() {
		double[] energy = new double[STRIPS.length];
		for (int i = 0; i < STRIPS.length; i++) {
			energy[i] = STRIPS[i];
		}
		return energy;
	}

	@Override
	public Double getMaxBias() {
		return MAX_BIAS_VOLTAGE;
	}

	@Override
	public Double getMinBias() {
		return MIN_BIAS_VOLTAGE;
	}

	@Override
	public HashMap<String, Double> getTemperatures() throws DeviceException {
		openTCSocket();

		HashMap<String, Double> temps = new HashMap<String, Double>();
		Double sensor0Temp = Double.parseDouble(daServer.sendCommand("xstrip tc get \"" + detectorName + "\" ch 0 t")
				.toString());
		temps.put(SENSOR0NAME, sensor0Temp);
		Double sensor1Temp = Double.parseDouble(daServer.sendCommand("xstrip tc get \"" + detectorName + "\" ch 1 t")
				.toString());
		temps.put(SENSOR1NAME, sensor1Temp);
		Double sensor2Temp = Double.parseDouble(daServer.sendCommand("xstrip tc get \"" + detectorName + "\" ch 2 t")
				.toString());
		temps.put(SENSOR2NAME, sensor2Temp);
		Double sensor3Temp = Double.parseDouble(daServer.sendCommand("xstrip tc get \"" + detectorName + "\" ch 3 t")
				.toString());
		temps.put(SENSOR3NAME, sensor3Temp);
		return temps;
	}

	private void openTCSocket() throws DeviceException {
		int tcIsOpen = (int) daServer.sendCommand("xstrip tc print \"" + detectorName + "\"");
		if (tcIsOpen == -1) {
			daServer.sendCommand("xstrip tc open \"" + detectorName + "\"");
			tcIsOpen = (int) daServer.sendCommand("xstrip tc print \"" + detectorName + "\"");
			if (tcIsOpen == -1) {
				throw new DeviceException(
						"Could not open temperature controller to find out current temperature values");
			}
		}
	}

	@Override
	public CalibrationDetails getEnergyCalibration() throws DeviceException {
		return calibration;
	}

	@Override
	public boolean isEnergyCalibrationSet() {
		return (calibration != null);
	}

	@Override
	public void setEnergyCalibration(CalibrationDetails calibration) throws DeviceException {
		this.calibration = calibration;
		saveToXML();
		this.notifyIObservers(this, CALIBRATION_PROP_KEY);
	}

	public double[] getEnergyForChannels() {
		double[] energy = new double[STRIPS.length];
		for (int i = 0; i < STRIPS.length; i++) {
			double result = getEnergyForChannel(STRIPS[i]);
			energy[i] = result;
		}
		return energy;
	}

	private double getEnergyForChannel(int channel) {
		if (calibration == null) {
			return channel;
		}
		return calibration.getCalibrationResult().value((double) channel / (double) NUMBER_ELEMENTS);
	}

	@Override
	public int getNumberScansInFrame(double frameTime, double scanTime, int numberOfFrames) throws DeviceException {
		// TODO is simply isBusy() enough to protect the experiment?
		int result = 0;
		if (isBusy()) {
			return result;
		}

		if (!hasValidDataHandle()) {
			return result;
		}

		String frameTime_clockcycles = secondsToClockCyclesString(frameTime);
		String scanTime_clockcycles = secondsToClockCyclesString(scanTime);
		try {
			String command = "xstrip timing setup-group \"xh0\" 0 " + numberOfFrames + " 0 " + scanTime_clockcycles + " frame-time "
					+ frameTime_clockcycles + " last";
			daServer.sendCommand(command);
			int[] value = daServer.getIntBinaryData("read 0 0 0 30 1024 1 from " + timingHandle + " raw motorola",
					30 * 1024);
			result = value[1]; // 1 is Number of scans per frame (See spec)
		} catch (Exception e) {
			throw new DeviceException("Error trying to read back from timing handle");
		}
		if (result == DETECTOR_ERROR_CODE) {
			throw new DeviceException("Error trying to read back from timing handle");
		}
		return result;
	}

	@Override
	public IDataset[][] fetchTemperatureData() throws DeviceException {
		return new XCHIPTemperatureLogParser(tempLogFilename).getTemperatures();
	}

	@Override
	public String getTemperatureLogFile() {
		return tempLogFilename;
	}
}
