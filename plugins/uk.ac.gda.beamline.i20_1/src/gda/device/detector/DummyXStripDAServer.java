/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

import gda.device.Detector;

import java.util.StringTokenizer;
import java.util.Vector;

import org.apache.commons.lang.ArrayUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Extension for DummyDAServer which exclusively handles XH/xstrip commands
 */
public class DummyXStripDAServer extends DummyDAServer {

	public enum MODE {
		STEP, FLAT
	}

	private static Logger logger = LoggerFactory.getLogger(DummyXStripDAServer.class);

	private Vector<TimingGroup> groups = new Vector<TimingGroup>();
	private boolean lastFlagSeen = true;
	private TimeFrameGenerator timeFrameGenerator = new TimeFrameGenerator();

	private String[] recievedCommands = new String[0];

	private MODE readoutMode = MODE.STEP;

	private Double biasVoltage = 0.0;

	@SuppressWarnings("unused")
	@Override
	public int[] getIntBinaryData(String command, int data_size) {
		int[] data = null;
		int x = 0, y = 0, t = 0, dx = 0, dy = 0, dt = 0;
		StringTokenizer tokenizer = new StringTokenizer(command);
		tokenizer.nextToken(); // read
		x = Integer.valueOf(tokenizer.nextToken());
		y = Integer.valueOf(tokenizer.nextToken());
		t = Integer.valueOf(tokenizer.nextToken());
		dx = Integer.valueOf(tokenizer.nextToken());
		dy = Integer.valueOf(tokenizer.nextToken());
		dt = Integer.valueOf(tokenizer.nextToken()); // timeframes
		data = createDummyEDEMcaData(dt);
		return data;
	}

	private int[] createDummyEDEMcaData(int numberOfFrames) {

		int[] data = new int[numberOfFrames * XHDetector.NUMBER_ELEMENTS];

		for (int frame = 0; frame < numberOfFrames; frame++) {

			if (readoutMode == MODE.FLAT) {
				for (int i = 0; i < XHDetector.NUMBER_ELEMENTS; i++) {
					data[(frame * XHDetector.NUMBER_ELEMENTS) + i] = 1;
				}
				continue;
			}

			// for each time frame, choose a random location between 600 and 900 for the 'edge'
			int edge = (int) Math.round((Math.random() * 300) + 600);

			// create random step height for the edge between 100 and 1000
			double step = (Math.random() * 900) + 100;

			// create noise level between 20 and 75
			double noise = (Math.random() * 55) + 20;

			// generate random values with a step at the edge of the baseline
			for (int i = 0; i < edge; i++) {
				data[(frame * XHDetector.NUMBER_ELEMENTS) + i] = (int) Math.round((Math.random() * noise));
			}
			for (int i = edge; i < XHDetector.NUMBER_ELEMENTS; i++) {
				data[(frame * XHDetector.NUMBER_ELEMENTS) + i] = (int) Math.round((Math.random() * noise) + step);
			}
		}

		return data;
	}

	@Override
	public Object sendCommand(String msg, Boolean multiline) {
		if (!multiline) {
			return sendCommand(msg);
		}

		if (msg.startsWith("xstrip timing read-status")) {
			return sendCommand(msg);
		}

		return -1; // don;t recognise the command
	}

	@Override
	public Object sendCommand(String command) {
		recievedCommands = (String[]) ArrayUtils.add(recievedCommands, command.trim());

		Object rc = -1;
		// set fail true for the next command only (for JUNIT tests)
		// return in this block of code otherwise fail will be reset to false
		logger.info("command received: " + command);
		if (command.startsWith("Fail")) {
			fail = true;
			return 0;
		} else if (command.contains("xstrip timing open")) {
			// handle to the timing readback
			handles.put(++key, "xstrip");
			rc = (fail) ? -1 : key;
		} else if (command.startsWith("xstrip open")) {
			// data handle
			handles.put(++key, "xstrip");
			rc = (fail) ? -1 : key;
		} else if (command.startsWith("close")) {
			StringTokenizer tokenizer = new StringTokenizer(command);
			tokenizer.nextToken(); // close
			int handle = Integer.valueOf(tokenizer.nextToken());
			handles.remove(handle);
			rc = (fail) ? -1 : 0;
		} else if (command.startsWith("xstrip hv")) {
			rc = parseXstripHVCommand(command);
		} else if (command.startsWith("xstrip")) {
			rc = parseXstripTimingCommand(command);
		} else {
			return super.sendCommand(command);
		}

		fail = false;
		return rc;
	}

	private Object parseXstripHVCommand(String command) {
		StringTokenizer tokenizer = new StringTokenizer(command);
		tokenizer.nextToken(); // xstrip - ignore
		tokenizer.nextToken(); // hv - ignore
		String hvCommand = tokenizer.nextToken();
		switch (hvCommand) {
		case "init":
		case "enable":
			break;
		case "set-dac":
			tokenizer.nextToken(); // system name - ignore
			biasVoltage = Double.parseDouble(tokenizer.nextToken());
			return 0.0;
		case "get-adc":
			return biasVoltage;
		default:
			return -1;
		}
		return 0;
	}

	private Object parseXstripTimingCommand(String command) {
		Object rc = -1;
		StringTokenizer tokenizer = new StringTokenizer(command);
		tokenizer.nextToken(); // xstrip - ignore
		tokenizer.nextToken(); // timing - ignore
		String setupCommand = tokenizer.nextToken();
		tokenizer.nextToken(); // system name - ignore
		if (setupCommand.equalsIgnoreCase("setup-group") && !lastFlagSeen) {
			parseSetupGroupCommand(tokenizer);
			rc = (fail) ? -1 : 0;
		} else if (setupCommand.equalsIgnoreCase("setup-group") && lastFlagSeen) {
			groups.clear();
			parseSetupGroupCommand(tokenizer);
			rc = (fail) ? -1 : 0;
		} else if (setupCommand.equalsIgnoreCase("continue")) {
			timeFrameGenerator.continueRun();
			rc = (fail) ? -1 : 0;
		} else if (setupCommand.equalsIgnoreCase("start")) {
			rc = startTimingGroups();
		} else if (setupCommand.equalsIgnoreCase("stop")) {
			if (timeFrameGenerator.currentState != Detector.IDLE) {
				timeFrameGenerator.stop();
			}
			rc = (fail) ? -1 : 0;
		} else if (setupCommand.equalsIgnoreCase("read-status")) {
			return timeFrameGenerator.getProgress();
		} else if (setupCommand.equalsIgnoreCase("fixed")) {
			return 0; // this is a flag to enable optimisation and to prevent cross-talk
		} else if (setupCommand.equalsIgnoreCase("ext-output")) {
			return 0; // this sets up external TTL outputs
		}
		return rc;
	}

	protected Object startTimingGroups() {
		Object rc;
		if (timeFrameGenerator.currentState != Detector.IDLE) {
			logger.info("Tried to start TFG data collection when one already in progress");
			rc = -1;
		} else {
			timeFrameGenerator.start();
			rc = 0;
		}
		return rc;
	}

	protected void parseSetupGroupCommand(StringTokenizer tokenizer) {
		TimingGroup newGroup = new TimingGroup();
		newGroup.groupNum = Integer.valueOf(tokenizer.nextToken());
		newGroup.numFrames = Integer.valueOf(tokenizer.nextToken());
		newGroup.numScans = Integer.valueOf(tokenizer.nextToken());
		newGroup.integrationTime = Long.valueOf(tokenizer.nextToken());
		groups.add(newGroup.groupNum, newGroup);
		boolean lastSeenInThisGroup = false;
		while (tokenizer.hasMoreTokens()) {
			String next = tokenizer.nextToken();
			if (next.equalsIgnoreCase("last")) {
				lastFlagSeen = true;
				lastSeenInThisGroup = true;
			} else if (next.equalsIgnoreCase("group-delay")) {
				newGroup.delayBeforeGroup = Long.valueOf(tokenizer.nextToken());
			} else if (next.equalsIgnoreCase("frame-delay")) {
				newGroup.delayBeforeEachFrame = Long.valueOf(tokenizer.nextToken());
			} else if (next.equalsIgnoreCase("scan-period")) {
				newGroup.scanToScanDelayInClockCycles = Long.valueOf(tokenizer.nextToken());
			} else if (next.equalsIgnoreCase("ext-trig-group")) {
				newGroup.waitForTriggerAtGroupStart = true;
			} else if (next.equalsIgnoreCase("ext-trig-frame")) {
				newGroup.waitForTriggerBeforeEveryFrame = true;
			} else if (next.equalsIgnoreCase("ext-trig-scan")) {
				newGroup.waitForTriggerBeforeEveryScan = true;
			} else if (next.equalsIgnoreCase("ext-trig-frame-only")) {
				newGroup.waitForTriggerBeforeEveryFrameExceptFirst = true;
			} else if (next.equalsIgnoreCase("ext-trig-scan-only")) {
				newGroup.waitForTriggerBeforeEveryScanExceptFirst = true;
			} else if (next.equalsIgnoreCase("frame-time")) {
				newGroup.frameTime = Long.valueOf(tokenizer.nextToken());
			}
		}
		if (!lastSeenInThisGroup) {
			lastFlagSeen = false;
		}
	}

	public void setRecievedCommands(String[] recievedCommands) {
		this.recievedCommands = recievedCommands;
	}

	public String[] getRecievedCommands() {
		return recievedCommands;
	}

	public void clearRecievedCommands() {
		recievedCommands = new String[0];
	}

	public MODE getReadoutMode() {
		return readoutMode;
	}

	public void setReadoutMode(MODE readoutMode) {
		this.readoutMode = readoutMode;
	}

	private class TimingGroup {
		// all times in this internal class in clock cycles
		public boolean waitForTriggerBeforeEveryScanExceptFirst = false;
		public boolean waitForTriggerBeforeEveryFrameExceptFirst = false;
		public boolean waitForTriggerBeforeEveryScan = false;
		public boolean waitForTriggerBeforeEveryFrame = false;
		public boolean waitForTriggerAtGroupStart = false;
		public long scanToScanDelayInClockCycles = 0l;
		public long delayBeforeEachFrame = 0l;
		public long delayBeforeGroup = 0l;
		public long frameTime = 0l;
		int groupNum;
		long numFrames;
		long numScans;
		long integrationTime;
	}

	private class TimeFrameGenerator implements Runnable {
		Thread runner;
		private volatile int currentState;
		private volatile boolean stopRun = false;
		private boolean continueFlag = false;
		private volatile int currentGroup;
		private volatile int currentFrame;
		private volatile int currentScan;

		public synchronized void start() {
			runner = uk.ac.gda.util.ThreadManager.getThread(this, getClass().getName());
			currentState = Detector.BUSY;
			runner.start();
		}

		public Object getProgress() {
			String statusString = "";
			if (currentState == Detector.BUSY) {
				statusString = "RUNNING\n# Running";
			} else if (currentState == Detector.IDLE) {
				statusString = "IDLE\n# Idle";
			} else if (currentState == Detector.PAUSED) {
				statusString = "PAUSED\n# Paused";
			}

			return statusString + ": group_num=" + currentGroup + ", frame_num=" + currentFrame + ", scan_num="
					+ currentScan + "\n";
		}

		public void stop() {
			if (currentState != Detector.IDLE) {
				stopRun = true;
				runner.interrupt();
			}
		}

		public void continueRun() {
			continueFlag = true;
		}

		@Override
		public synchronized void run() {
			try {
				stopRun = false;
				currentState = Detector.BUSY;
				currentGroup = currentFrame = currentScan = -1;

				for (TimingGroup thisGroup : groups) {
					if (thisGroup == null)
						continue;

					currentGroup = thisGroup.groupNum;

					if (stopRun) {
						throw new InterruptedException("Stopping run");
					}

					if (thisGroup.waitForTriggerAtGroupStart) {
						waitForContinueSignal();
					}

					if (thisGroup.delayBeforeGroup != 0) {
						sleepClockCycles(thisGroup.delayBeforeGroup);
					}

					for (currentFrame = 0; currentFrame < thisGroup.numFrames; currentFrame++) {

						if (stopRun) {
							throw new InterruptedException("Stopping run");
						}

						if (thisGroup.waitForTriggerBeforeEveryFrameExceptFirst && currentFrame != 0) {
							waitForContinueSignal();
						} else if (thisGroup.waitForTriggerBeforeEveryFrame) {
							waitForContinueSignal();
						}

						if (currentFrame != 0 && thisGroup.delayBeforeEachFrame != 0) {
							sleepClockCycles(thisGroup.delayBeforeEachFrame);
						}

						// number of scans defined by explicit value or by frame time
						long numberOfScans = thisGroup.numScans;
						if (numberOfScans == 0) {
							numberOfScans = Math.round(thisGroup.frameTime / thisGroup.integrationTime);
						}

						for (currentScan = 0; currentScan < numberOfScans; currentScan++) {

							if (stopRun) {
								throw new InterruptedException("Stopping run");
							}

							if (thisGroup.waitForTriggerBeforeEveryScanExceptFirst && currentScan != 0) {
								waitForContinueSignal();
							} else if (thisGroup.waitForTriggerBeforeEveryScan) {
								waitForContinueSignal();
							}

							if (currentScan != 0 && thisGroup.scanToScanDelayInClockCycles != 0) {
								sleepClockCycles(thisGroup.scanToScanDelayInClockCycles);
							}

							sleepClockCycles(thisGroup.integrationTime);
						}
					}
				}
			} catch (InterruptedException e) {
				logger.info("Timing groups aborted");
			} finally {
				stopRun = false;
				currentState = Detector.IDLE;
				currentGroup = 0;
				currentFrame = 0;
				currentScan = 0;
				logger.info("Timing groups complete");
			}
		}

		private void sleepClockCycles(Long integrationTime) throws InterruptedException {
			Thread.sleep(Math.round(integrationTime * XHDetector.XSTRIP_CLOCKRATE * 1E3));
		}

		private void waitForContinueSignal() throws InterruptedException {
			currentState = Detector.PAUSED;
			while (!continueFlag) {
				if (stopRun) {
					throw new InterruptedException("Stopping run while waiting for continue signal");
				}
			}
		}
	}

}