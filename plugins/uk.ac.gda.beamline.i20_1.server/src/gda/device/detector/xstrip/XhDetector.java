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

package gda.device.detector.xstrip;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.DeviceException;
import gda.device.detector.DAServer;
import gda.device.detector.DetectorStatus;
import gda.device.detector.EdeDetector;
import gda.device.detector.EdeDetectorBase;
import gda.factory.FactoryException;
import gda.jython.InterfaceProvider;
import uk.ac.gda.api.remoting.ServiceInterface;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

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
 */
@ServiceInterface(EdeDetector.class)
public class XhDetector extends EdeDetectorBase implements EdeDetector {

	private static final long serialVersionUID = 1L;

	private static final Logger logger = LoggerFactory.getLogger(XhDetector.class);

	// strings to use in the get/set attributes methods
	public static final String ATTR_LOADPARAMETERS = "loadParameters";
	public static final String ATTR_READFIRSTFRAME = "readFirstFrame";
	public static final String ATTR_WRITEFIRSTFRAME = "writeFirstFrame";
	public static final String ATTR_READALLFRAMES = "readAllFrames";

	// Detector activity levels in DAServer 'read-status' return string
	public static final String RUNNING = "Running";
	public static final String PAUSED = "Paused";
	public static final String IDLE = "Idle";

	public static final double XSTRIP_CLOCKRATE = 20E-9; // s
	public static final int MAX_PIXEL = 1024;

	private static final int DETECTOR_ERROR_CODE = -1;
	private static final String DETECTOR_ERROR_CODE_STR = Integer.toString(DETECTOR_ERROR_CODE);

	private static final int EXTERNAL_OUTPUT_WIDTH_AS_SIGNAL_CYCLES = 100;

	//	private static Integer[] STRIPS;

	// These are the objects this must know about.
	private String detectorName;
	private DAServer daServer = null;

	// da.server memory handles for reading back timing information and data
	private int timingHandle = -1;
	private int dataHandle = -1;

	private int scanDelayInMilliseconds = 0;

	// must be in configuration info
	private String templateFileName;
	private final XhDetectorTemperature detectorTemp;

	private boolean synchroniseToBeamOrbit;
	private int synchroniseBeamOrbitDelay = 0;
	private OrbitWaitType orbitWaitMethod = OrbitWaitType.ORBIT_SCAN;
	private int orbitMuxValue = 0;

	public enum OrbitWaitType {
		ORBIT_GROUP("orbit-group"),
		ORBIT_FRAME("orbit-frame"),
		ORBIT_SCAN("orbit-scan"),
		ORBIT_FRAME_ONLY("orbit-frame-only"),
		ORBIT_SCAN_ONLY("orbit-scan-only");

		private String orbitString;
		OrbitWaitType(String orbitString ) {
			this.orbitString = orbitString;
		}

		public String getString() {
			return orbitString;
		}
	}

	public XhDetector() {
		super();
		// defaults which will be updated when number of sectors changed
		inputNames = new String[] { "time" };
		detectorTemp=new XhDetectorTemperature(daServer, "xh_temperatures");
	}

	// Added so that correct daServer and detector name (not null!) are passed to XHDetectorTemperature when bean is created. imh 16/10/2015
	public XhDetector(DAServer daServer, String detectorName) {
		super();
		inputNames = new String[] { "time" };
		this.daServer = daServer;
		this.detectorName = detectorName;
		detectorTemp = new XhDetectorTemperature(daServer, detectorName);
	}

	/**
	 * Return configured state of underlying DAServer.
	 */
	@Override
	public boolean isConfigured() {
		return daServer.isConfigured();
	}

	/**
	 * Release timing,data handles and try to reconnect to DAServer.
	 */
	@Override
	public void reconfigure() throws FactoryException {
		try {
			logger.debug("reconfigure() called on {}", getName());
			close();
			daServer.reconfigure();
		} catch (DeviceException e) {
			throw new FactoryException("Problem reconfiguring "+getName(), e);
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

	@Override
	public NexusTreeProvider readout() throws DeviceException {
		// Read 1st frame from detector (used for live mode).
		return readFrames(0,0)[0];
	}


	@Override
	public synchronized int[] readoutFrames(int startFrame, int finalFrame) throws DeviceException {
		int[] value = null;
		if (hasValidDataHandle()) {
			int numFrames = finalFrame - startFrame + 1;
			try {
				String readCommand = "read 0 0 " + startFrame + " " + MAX_PIXEL + " 1 " + numFrames + " from "
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

	//	@Override
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

	@Override
	public DetectorStatus fetchStatus() throws DeviceException {
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

		DetectorStatus newStatus = new DetectorStatus();

		if (stateString.startsWith(RUNNING)) {
			newStatus.setDetectorStatus(gda.device.Detector.BUSY);
		} else if (stateString.startsWith(PAUSED)) {
			newStatus.setDetectorStatus(gda.device.Detector.PAUSED);
		} else {
			newStatus.setDetectorStatus(gda.device.Detector.IDLE);
		}

		for (String part : messageParts) {
			part = part.trim();
			if (part.contains("group_num")) {
				int group = Integer.parseInt(part.substring(part.indexOf("=") + 1));
				newStatus.getCurrentScanInfo().groupNum = group;
			}
			if (part.contains("frame_num")) {
				int group = Integer.parseInt(part.substring(part.indexOf("=") + 1));
				newStatus.getCurrentScanInfo().frameNum = group;
			}
			if (part.contains("scan_num")) {
				int group = Integer.parseInt(part.substring(part.indexOf("=") + 1));
				newStatus.getCurrentScanInfo().scanNum = group;
			}
		}
		return newStatus;
	}

	@Override
	public void configureDetectorForCollection() throws DeviceException {
		// read nextScan attribute and convert into daserver commands...

		addOutSignals();

		for (Integer i = 0; i < currentScanParameter.getGroups().size(); i++) {

			TimingGroup timingGroup = currentScanParameter.getGroups().get(i);

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
			//			if (numberOfScansPerFrame == 0) {
			if (currentScanParameter.isUseFrameTime()){
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

				// Set option for synchronising to beam orbit.
				if ( synchroniseToBeamOrbit ) {
					String orbitMethodString = orbitWaitMethod.getString();
					command += " " + orbitMethodString + " orbit-mux "+orbitMuxValue;
				}
			}


			if (i == currentScanParameter.getGroups().size() - 1) {
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
			extTrig = " ext-trig-group trig-mux " + lemo;
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
		double[] delaysInS = currentScanParameter.getOutputWidths();
		String[] delays = new String[delaysInS.length];
		for (int i = 0; i < delaysInS.length; i++) {
			delays[i] = secondsToClockCyclesString(delaysInS[i]);
		}

		String[] extOuts = currentScanParameter.getOutputsChoices();
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
	//	@Override
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


	public int getScanDelayInMilliseconds() {
		return scanDelayInMilliseconds;
	}

	public void setScanDelayInMilliseconds(int scanDelayInMilliseconds) {
		this.scanDelayInMilliseconds = scanDelayInMilliseconds;
	}

	public void setBias(Double biasVoltage) throws DeviceException {
		XhDetectorData xhDetectorData = (XhDetectorData) getDetectorData();
		if (biasVoltage < xhDetectorData.getMinBias() | biasVoltage > xhDetectorData.getMaxBias()) {
			throw new DeviceException("Bias voltage of " + biasVoltage + " is unacceptable.");
		}

		Double currentValue = getBias();
		if (currentValue == 0.0) {
			daServer.sendCommand("xstrip hv init");
			daServer.sendCommand("xstrip hv enable \"" + detectorName + "\"");
		}
		daServer.sendCommand("xstrip hv set-dac \"" + detectorName + "\" " + biasVoltage + " hv");
	}

	public Double getBias() throws DeviceException {
		return (Double) daServer.sendCommand("xstrip hv get-adc \"" + detectorName + "\" hv");
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
	public int getMaxPixel() {
		return MAX_PIXEL;
	}

	@Override
	public void fetchDetectorSettings() {
		// TODO Auto-generated method stub
		//No-op
	}

	@Override
	public HashMap<String, Double> getTemperatures() throws DeviceException {
		return detectorTemp.getTemperatures();
	}


	@Override
	public int getNumberOfSpectra() throws DeviceException {
		Integer numFrames=0;
		for (Integer i = 0; i < currentScanParameter.getGroups().size(); i++) {

			TimingGroup timingGroup = currentScanParameter.getGroups().get(i);

			// basic times
			numFrames += timingGroup.getNumberOfFrames();
		}
		return numFrames;
	}


	@Override
	public int getNumberScansInFrame() {
		// This detector does not require number of scans in a frame information as it is configured via internal TFG
		return 0;
	}

	@Override
	public void setNumberScansInFrame( int num ) {
	}

	@Override
	public void configureDetectorForTimingGroup(TimingGroup group) throws DeviceException {
		throw new UnsupportedOperationException("This detector processes timing groups in configureDetectorForCollection()");

	}


	@Override
	public void configureDetectorForROI(int verticalBinning, int ccdLineBegin) throws DeviceException {
		throw new UnsupportedOperationException("This detector does not support vertival binning and offset.");

	}

	@Override
	public int getLastImageAvailable() throws DeviceException {
		DetectorStatus status = fetchStatus();
		Integer currentFrame = DetectorScanDataUtils.getAbsoluteFrameNumber(currentScanParameter, status.getCurrentScanInfo());
		return currentFrame;
	}

	// Implementation of beam orbit synchronization. imh 11/12/2015
	@Override
	public void setSynchroniseToBeamOrbit( boolean synchroniseToBeamOrbit ) {
		this.synchroniseToBeamOrbit = synchroniseToBeamOrbit;
	}

	@Override
	public boolean getSynchroniseToBeamOrbit() {
		return synchroniseToBeamOrbit;
	}

	@Override
	public void setSynchroniseBeamOrbitDelay( int synchroniseBeamOrbitDelay ) throws DeviceException {
		this.synchroniseBeamOrbitDelay = synchroniseBeamOrbitDelay;
		String delayString = String.format("%d", synchroniseBeamOrbitDelay );
		String command = "xstrip timing setup-orbit \"xh0\" " + delayString;

		logger.info("Sending orbit delay command to XH: " + command);
		Object result = daServer.sendCommand( command );

		if (result.toString().compareTo("-1") == 0) {
			throw new DeviceException(
					"The given parameters were not accepted by da.server! Check frame and scan times.");
		}
	}

	@Override
	public int getSynchroniseBeamOrbitDelay() {
		return synchroniseBeamOrbitDelay;
	}

	@Override
	public void setOrbitWaitMethod( String methodString ) {
		boolean found = false;
		for( OrbitWaitType orbitType : OrbitWaitType.values() ) {
			if ( methodString.trim().equals( orbitType.getString() ) ) {
				orbitWaitMethod = orbitType;
				found = true;
			}
		}
		String message;
		if ( found ) {
			message = "Setting orbit wait mode to \'" + orbitWaitMethod.getString() + "\'";
		} else {
			message = "Orbit wait mode \'" + methodString + "\' not recognised";
		}
		InterfaceProvider.getTerminalPrinter().print(message);
	}

	@Override
	public String getOrbitWaitMethod() {
		return orbitWaitMethod.getString();
	}

	public void showOrbitWaitMethods() {
		InterfaceProvider.getTerminalPrinter().print("Xh orbit methods :");
		for( OrbitWaitType orbitType : OrbitWaitType.values() ) {
			InterfaceProvider.getTerminalPrinter().print( orbitType.getString() );
		}
	}

	public int getOrbitMuxValue() {
		return orbitMuxValue;
	}

	public void setOrbitMuxValue(int orbitMuxValue) {
		if (orbitMuxValue>=0 && orbitMuxValue<=3) {
			this.orbitMuxValue = orbitMuxValue;
		} else {
			logger.warn("Cannot set beam orbit mux to {}. Value should be between 0 and 3", orbitMuxValue);
		}
	}
}
