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

package uk.ac.gda.exafs.experiment.trigger;

import gda.device.detector.EdeDetector;
import gda.jython.InterfaceProvider;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject.TriggerOutputPort;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentUnit;

import com.google.gson.annotations.Expose;

public class TFGTrigger extends ObservableModel implements Serializable {
	private static final Logger logger=LoggerFactory.getLogger(TFGTrigger.class);
	// The first 2 is reserved for photonShutter and detector
	private static final int MAX_PORTS_FOR_SAMPLE_ENV = TriggerableObject.TriggerOutputPort.values().length - 2;
	private static final double TFG_TIME_RESOLUTION=0.000000001; //second

	public static final ExperimentUnit DEFAULT_DELAY_UNIT = ExperimentUnit.SEC;
	public static final double DEFAULT_PULSE_WIDTH_IN_SEC = 0.001d;

	private static final double MIN_DEAD_TIME = 0.000001;
	private static final double MIN_LIVE_TIME = 0.000001;
	private EdeDetector detector;
	private boolean usingExternalScripts4TFG=false;

	@Expose
	private final List<TriggerableObject> sampleEnvironment = new ArrayList<TriggerableObject>(MAX_PORTS_FOR_SAMPLE_ENV);

	public final PropertyChangeListener totalTimeChangeListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			TFGTrigger.this.firePropertyChange(TOTAL_TIME_PROP_NAME, null, getTotalTime());
		}
	};

	@Expose
	private final DetectorDataCollection detectorDataCollection = new DetectorDataCollection();

	public TFGTrigger() {
		detectorDataCollection.addPropertyChangeListener(totalTimeChangeListener);
	}

	public DetectorDataCollection getDetectorDataCollection() {
		return detectorDataCollection;
	}

	public List<TriggerableObject> getSampleEnvironment() {
		return sampleEnvironment;
	}

	public static final String TOTAL_TIME_PROP_NAME = "totalTime";

	public double getTotalTime() {
		double total = 0.0;
		for (TriggerableObject obj : sampleEnvironment) {
			if (obj.getTriggerDelay() + obj.getTriggerPulseLength() > total) {
				total = obj.getTriggerDelay() + obj.getTriggerPulseLength();
			}
		}
		if (detectorDataCollection.getTriggerDelay() + detectorDataCollection.getCollectionDuration() > total) {
			total = detectorDataCollection.getTriggerDelay() + detectorDataCollection.getCollectionDuration();
		}
		return total;
	}

	public TriggerableObject createNewSampleEnvEntry() {
		// TODO clean-up once tested. the following is too restrictive, PBS/BS want to be able to select same port for
		// different triggers.
		// if (sampleEnvironment.size() == MAX_PORTS_FOR_SAMPLE_ENV) {
		// throw new Exception("Maxium ports reached: " + MAX_PORTS_FOR_SAMPLE_ENV);
		// }
		TriggerableObject obj = new TriggerableObject();
		obj.setName("Default");
		obj.setTriggerPulseLength(DEFAULT_PULSE_WIDTH_IN_SEC);
		obj.setTriggerDelay(0.1);
		// obj.setTriggerOutputPort(TriggerOutputPort.values()[sampleEnvironment.size() + 2]);
		obj.setTriggerOutputPort(TriggerOutputPort.values()[2]);
		return obj;
	}

	// Format of 'tfg setup-groups' as follows, 7 or 9 space-separated numbers:
	// num_frames dead_time live_time dead_port live_port dead_pause live_pause [dead_tfinc live_tfinc]
	// Followed by last line:
	// -1 0 0 0 0 0 0
	// Where num_frames = Number of frames in this group
	// Dead_time, Live_time = time as floating point seconds
	// Dead_port, Live_port = port data as integer (0<=port<=128k-1)
	// Dead_pause, Live_pause = pause bit (0<=pause<=1)
	// And For TFG2 only
	// num_repeats sequence_name
	// This repeats the pre-recorded sequence num_repeats times.
	public String getTfgSetupGrupsCommandParameters(int numberOfCycles, boolean shouldStartOnTopupSignal) {
		if (detector.getName().equalsIgnoreCase("frelon")) {
			if (isUsingExternalScripts4TFG()) {
				String tfgCommand=InterfaceProvider.getCommandRunner().evaluateCommand("getCommands4ExternalTFG()");
				return tfgCommand.toString();
			}
			return getTfgSetupGroupsCommandParameters4Frelon(numberOfCycles, shouldStartOnTopupSignal);
		}
		return getTfgSetupGrupsCommandParameters4XH(numberOfCycles, shouldStartOnTopupSignal);
	}

	public String getTfgSetupGrupsCommandParameters4XH(int numberOfCycles, boolean shouldStartOnTopupSignal) {
		// using TFG setup GUI for XH detector
		StringBuilder tfgCommand = new StringBuilder();
		List<TriggerPair> triggerPoints = processTimes(); //ensure there is at least one trigger point at time start point (0.0d,0,0)
		Collections.sort(triggerPoints);

		tfgCommand.append("tfg setup-groups");
		if (numberOfCycles > 1) {
			tfgCommand.append(" cycles ");
			tfgCommand.append(numberOfCycles);
		}
		tfgCommand.append("\n");
		if (shouldStartOnTopupSignal) {
			//ttl0 - TTL Trigger LEMO0 is used for waiting topup signal
			tfgCommand.append(String.format("1 %f 0 0 0 8 0\n", MIN_DEAD_TIME));
		}
		double iTcollectionEndTime = detectorDataCollection.getTotalDelay();
		double iTcollectionStartTime = detectorDataCollection.getTriggerDelay();
		double collectionDuration = detectorDataCollection.getCollectionDuration();
		int numberOfFrames = detectorDataCollection.getNumberOfFrames();
		double singleFrameTime=collectionDuration/numberOfFrames;
		boolean itCollectionAdded = false;
		boolean beginningFramesAdded=false;
		int totalnumberFramesSoFar=0;

		for (int i = 0; i < triggerPoints.size(); i++) {
			//process trigger points added by external triggers
			if (i + 1 < triggerPoints.size()) {
				// at least one external trigger which gives 2 trigger points
				TriggerPair thisPoint = triggerPoints.get(i);
				TriggerPair nextPoint = triggerPoints.get(i + 1);
				if (nextPoint.time >= iTcollectionStartTime && nextPoint.time < iTcollectionEndTime) {
					// external triggers fall inside data collection time - split frames collected in chunks between trigger points
					if (!beginningFramesAdded) {
						//wait frame before collection starts
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", (iTcollectionStartTime - thisPoint.time), thisPoint.port));
					}

					//sample environment trigger
					tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", thisPoint.length, detectorDataCollection.getTriggerOutputPort().getUsrPort() + thisPoint.port));

					int numberOfFramesBetweenAdjacentPoints=0;
					if (!beginningFramesAdded) {
						numberOfFramesBetweenAdjacentPoints=(int) ((nextPoint.time-iTcollectionStartTime)/singleFrameTime);
					} else {
						numberOfFramesBetweenAdjacentPoints=(int) ((nextPoint.time-thisPoint.time)/singleFrameTime);
					}
					if ((totalnumberFramesSoFar+numberOfFramesBetweenAdjacentPoints)<numberOfFrames) {
						tfgCommand.append(String.format("%d 0 %f 0 %d 0 9\n", numberOfFramesBetweenAdjacentPoints, MIN_LIVE_TIME, thisPoint.port)); // Review if this is dead or live port
					}
					totalnumberFramesSoFar += numberOfFramesBetweenAdjacentPoints;
					beginningFramesAdded=true;
					if (i+1==triggerPoints.size()-1) {
						//nextPoint is the last trigger point before iTCollectionEndTime
						if (totalnumberFramesSoFar<numberOfFrames) {
							//add last few frames in data acquisition before iTCollectionEndTime
							int numberOfFramesLeft = numberOfFrames-totalnumberFramesSoFar;
							tfgCommand.append(String.format("%d 0 %f 0 %d 0 9\n", numberOfFramesLeft, MIN_LIVE_TIME, thisPoint.port)); // Review if this is dead or live port
							totalnumberFramesSoFar += numberOfFramesLeft;
						}
						// at end of data collection, external TFG2 must wait for a single frame to allow detector collection to complete.
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", singleFrameTime, thisPoint.port));
						itCollectionAdded=true;
					}
				} else if (nextPoint.time >= iTcollectionEndTime  && !itCollectionAdded) {
					//external triggers at and after data collection end time
					if (beginningFramesAdded) {
						//finish what already started by previous trigger points
						if (totalnumberFramesSoFar<numberOfFrames) {
							//add last few frames in data acquisition before iTCollectionEndTime
							int numberOfFramesLeft = numberOfFrames-totalnumberFramesSoFar;
							tfgCommand.append(String.format("%d 0 %f 0 %d 0 9\n", numberOfFramesLeft, MIN_LIVE_TIME, thisPoint.port)); // Review if this is dead or live port
							totalnumberFramesSoFar += numberOfFramesLeft;
						}
					} else {
						//No external trigger falls inside data collection time
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", (iTcollectionStartTime - thisPoint.time), thisPoint.port));
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", detectorDataCollection.getTriggerPulseLength(), detectorDataCollection.getTriggerOutputPort().getUsrPort() + thisPoint.port));
						tfgCommand.append(String.format("%d 0 %f 0 %d 0 9\n", detectorDataCollection.getNumberOfFrames(), MIN_LIVE_TIME, thisPoint.port)); // Review if this is dead or live port
					}
					if (nextPoint.time == iTcollectionEndTime) {
						// at end of data collection wait for at least a single frame to allow detector collection to complete.
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", singleFrameTime, thisPoint.port));
					} else {
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", singleFrameTime + nextPoint.time	- iTcollectionEndTime, thisPoint.port)); // Review if this is dead or live port
					}
					itCollectionAdded = true;
				} else {
					//external triggers fall before data collection start time
					if (thisPoint.time != iTcollectionStartTime && thisPoint.time != iTcollectionEndTime) {
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", nextPoint.time - thisPoint.time, thisPoint.port));
					}
				}
			}
		}
		if (!itCollectionAdded) {
			//No external trigger after data collection start time
			if (!triggerPoints.isEmpty()) {
				tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", (iTcollectionStartTime - triggerPoints.get(triggerPoints.size() -1).time), 0));
			}
			tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", detectorDataCollection.getTriggerPulseLength(), detectorDataCollection.getTriggerOutputPort().getUsrPort()));
			tfgCommand.append(String.format("%d 0 %f 0 0 0 9\n", detectorDataCollection.getNumberOfFrames(), MIN_LIVE_TIME, detectorDataCollection.getTriggerOutputPort().getUsrPort())); // Review if this is dead or live port
			// at end of data collection external TFG2 must wait for a single frame to allow detector collection to complete.
			tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", singleFrameTime, 0));
		}
		tfgCommand.append("-1 0 0 0 0 0 0");
		//		String tfgCommand=InterfaceProvider.getCommandRunner().evaluateCommand("getCommands4ExternalTFG()");
		return tfgCommand.toString();
	}

	public List<TriggerPair> mergeTriggerPoints( List<TriggerPair> triggerPoints ) {
		List<TriggerPair> newTriggerPoints = new ArrayList<TFGTrigger.TriggerPair>();

		TriggerPair p1, p2;
		p1 = triggerPoints.get(0);
		int i = 1;
		int ports = 0;

		while( i<triggerPoints.size() ) {

			p2 = triggerPoints.get(i);

			double timeDiff = p2.getTime() - p1.getTime();

			if ( timeDiff>0 ) {
				ports = p1.getPort();
			} else { // p1 and p2 times are the same, merge active ports together
				ports |= p1.getPort() | p2.getPort();
			}

			if ( timeDiff > 0 ) {
				newTriggerPoints.add(new TriggerPair( p1.getTime(), ports, p1.getLength() ) );

				// add last trigger point
				if ( i == triggerPoints.size()-1 ) {
					newTriggerPoints.add(new TriggerPair( p2.getTime(), p2.getPort(), p2.getLength() ) );
				}

				ports = 0;
			}

			if ( timeDiff < 1e-10 &&
					i == triggerPoints.size()-1 ) { // last trigger point merged with previous one(s)
				newTriggerPoints.add(new TriggerPair( p1.getTime(), ports, p1.getLength() ) );
			}

			p1 = p2;
			i++;

		}
		return newTriggerPoints;
	}


	public String getTfgSetupGroupsCommandParameters4Frelon(int numberOfCycles, boolean shouldStartOnTopupSignal) {
		// using TFG setup GUI for XH detector
		StringBuilder tfgCommand = new StringBuilder();
		List<TriggerPair> origTriggerPoints = processTimes(); //ensure there is at least one trigger point at time start point (0.0d,0,0)
		Collections.sort(origTriggerPoints);

		List<TriggerPair> triggerPoints = mergeTriggerPoints( origTriggerPoints );

		tfgCommand.append("tfg setup-groups");
		if (numberOfCycles > 1) {
			tfgCommand.append(" cycles ");
			tfgCommand.append(numberOfCycles);
		}
		tfgCommand.append("\n");
		if (shouldStartOnTopupSignal) {
			//ttl0 - TTL Trigger LEMO0 is used for waiting topup signal
			tfgCommand.append(String.format("1 %f 0 0 0 8 0\n", MIN_DEAD_TIME));
		}
		double iTcollectionEndTime = detectorDataCollection.getTotalDelay();
		double iTcollectionStartTime = detectorDataCollection.getTriggerDelay();
		double collectionDuration = detectorDataCollection.getCollectionDuration();
		int numberOfFrames = detectorDataCollection.getNumberOfFrames()*getDetector().getNumberScansInFrame();
		double singleFrameTime=collectionDuration/numberOfFrames;
		boolean itCollectionAdded = false;
		boolean beginningFramesAdded=false;
		int totalnumberFramesSoFar=0;

		for (int i = 0; i < triggerPoints.size(); i++) {
			//process trigger points added by external triggers
			if (i + 1 < triggerPoints.size()) {
				// at least one external trigger which gives 2 trigger points
				TriggerPair thisPoint = triggerPoints.get(i);
				TriggerPair nextPoint = triggerPoints.get(i + 1);
				if (nextPoint.time >= iTcollectionStartTime && nextPoint.time < iTcollectionEndTime) {
					// external triggers fall inside data collection time - split frames collected in chunks between trigger points
					if (!beginningFramesAdded) {
						//wait frame before collection starts
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", (iTcollectionStartTime - thisPoint.time), thisPoint.port));

						//detector trigger to start
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", detectorDataCollection.getTriggerPulseLength(), detectorDataCollection.getTriggerOutputPort().getUsrPort() + thisPoint.port));
					}

					int numberOfFramesBetweenAdjacentPoints=0;
					if (!beginningFramesAdded) {
						numberOfFramesBetweenAdjacentPoints=(int) ((nextPoint.time-iTcollectionStartTime)/singleFrameTime);
					} else {
						numberOfFramesBetweenAdjacentPoints=(int) ((nextPoint.time-thisPoint.time)/singleFrameTime);
					}
					if ((totalnumberFramesSoFar+numberOfFramesBetweenAdjacentPoints)<numberOfFrames
							&& numberOfFramesBetweenAdjacentPoints>0 ) {
						tfgCommand.append(String.format("%d 0 %f 0 0 0 9\n", numberOfFramesBetweenAdjacentPoints, MIN_LIVE_TIME)); // Review if this is dead or live port
					}
					//sample environment trigger
					tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", nextPoint.length, nextPoint.port));

					totalnumberFramesSoFar += numberOfFramesBetweenAdjacentPoints;
					beginningFramesAdded=true;
				} else if (nextPoint.time >= iTcollectionEndTime  && !itCollectionAdded) {
					//external triggers at and after data collection end time
					if (beginningFramesAdded) {
						//finish what already started by previous trigger points
						if (totalnumberFramesSoFar<numberOfFrames) {
							//add last few frames in data acquisition before iTCollectionEndTime
							int numberOfFramesLeft = numberOfFrames-totalnumberFramesSoFar;
							tfgCommand.append(String.format("%d 0 %f 0 %d 0 9\n", numberOfFramesLeft, MIN_LIVE_TIME, thisPoint.port)); // Review if this is dead or live port
							totalnumberFramesSoFar += numberOfFramesLeft;
						}
					} else {
						//No external trigger falls inside data collection time
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", (iTcollectionStartTime - thisPoint.time), thisPoint.port));
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", detectorDataCollection.getTriggerPulseLength(), detectorDataCollection.getTriggerOutputPort().getUsrPort() + thisPoint.port));
						tfgCommand.append(String.format("%d 0 %f 0 %d 0 9\n", detectorDataCollection.getNumberOfFrames(), MIN_LIVE_TIME, thisPoint.port)); // Review if this is dead or live port
					}
					if (nextPoint.time == iTcollectionEndTime) {
						// at end of data collection wait for at least a single frame to allow detector collection to complete.
						tfgCommand.append(String.format("1 %f 0.0 0 0 0 0\n", singleFrameTime, thisPoint.port));
					} else {
						tfgCommand.append(String.format("1 %f 0.0 0 0 0 0\n", singleFrameTime + nextPoint.time	- iTcollectionEndTime, thisPoint.port)); // Review if this is dead or live port
					}
					itCollectionAdded = true;
				} else {
					//external triggers fall before data collection start time
					if (thisPoint.time != iTcollectionStartTime && thisPoint.time != iTcollectionEndTime) {
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", nextPoint.time - thisPoint.time, thisPoint.port));
					}
				}
				if (i+1==triggerPoints.size()-1) {
					//nextPoint is the last trigger point before iTCollectionEndTime
					if (totalnumberFramesSoFar<numberOfFrames) {
						//add last few frames in data acquisition before iTCollectionEndTime
						int numberOfFramesLeft = numberOfFrames-totalnumberFramesSoFar;
						tfgCommand.append(String.format("%d 0 %f 0 0 0 9\n", numberOfFramesLeft, MIN_LIVE_TIME)); // Review if this is dead or live port
						totalnumberFramesSoFar += numberOfFramesLeft;
					}
					// at end of data collection, external TFG2 must wait for a single frame to allow detector collection to complete.
					tfgCommand.append(String.format("1 %f 0.0 0 0 0 0\n", singleFrameTime));
					itCollectionAdded=true;
				}
			}
		}
		if (!itCollectionAdded) {
			//No external trigger after data collection start time
			if (!triggerPoints.isEmpty()) {
				tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", (iTcollectionStartTime - triggerPoints.get(triggerPoints.size() -1).time), 0));
			}
			tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", detectorDataCollection.getTriggerPulseLength(), detectorDataCollection.getTriggerOutputPort().getUsrPort()));
			tfgCommand.append(String.format("%d 0 %f 0 0 0 9\n", detectorDataCollection.getNumberOfFrames()*getDetector().getNumberScansInFrame(), MIN_LIVE_TIME, detectorDataCollection.getTriggerOutputPort().getUsrPort())); // Review if this is dead or live port
			// at end of data collection external TFG2 must wait for a single frame to allow detector collection to complete.
			tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", singleFrameTime, 0));
		}
		tfgCommand.append("-1 0 0 0 0 0 0");
		//		String tfgCommand=InterfaceProvider.getCommandRunner().evaluateCommand("getCommands4ExternalTFG()");
		return tfgCommand.toString();
	}

	private List<TriggerPair> processTimes() {
		TreeMap<Double, List<TriggerableObject>> triggerTimesAndSamEnv = new TreeMap<Double, List<TriggerableObject>>();
		List<TriggerPair> triggerPoints = new ArrayList<TriggerPair>();
		if (sampleEnvironment.isEmpty()) {
			return triggerPoints;
		}
		for (TriggerableObject entry : sampleEnvironment) {
			double startPulse = entry.getTriggerDelay();
			double endPulse = entry.getTriggerDelay() + entry.getTriggerPulseLength();
			if (triggerTimesAndSamEnv.containsKey(startPulse)) {
				triggerTimesAndSamEnv.get(startPulse).add(entry);
			} else {
				List<TriggerableObject> trigger = new ArrayList<TriggerableObject>();
				trigger.add(entry);
				triggerTimesAndSamEnv.put(startPulse, trigger);
			}
			if (triggerTimesAndSamEnv.containsKey(endPulse)) {
				triggerTimesAndSamEnv.get(endPulse).add(entry);
			} else {
				List<TriggerableObject> trigger = new ArrayList<TriggerableObject>();
				trigger.add(entry);
				triggerTimesAndSamEnv.put(endPulse, trigger);
			}
		}
		int currentLivePort = 0;
		if (triggerTimesAndSamEnv.firstKey() > 0d) {
			//define the time zero trigger point - note this is not a trigger.
			triggerPoints.add(new TriggerPair(0.0d, 0, 0.0));
		}
		if(isTriggerPulseOverlapForTheSamePort()) {
			//must not allow trigger pulse overlapping on the same output port
			throw new IllegalStateException("Signals on the same port are not allowed to overlap in time.");
		}
		HashMap<TriggerOutputPort, Integer> outputPort2LivePortIndex = new HashMap<TriggerOutputPort, Integer>();
		double currentTime=0.0;
		for (Map.Entry<Double, List<TriggerableObject>> entry : triggerTimesAndSamEnv.entrySet()) {
			currentTime = entry.getKey();
			for (TriggerableObject obj : entry.getValue()) {
				double triggerDelay = obj.getTriggerDelay();
				double triggerPulseLength = obj.getTriggerPulseLength();
				if (currentTime == triggerDelay) {
					TriggerOutputPort triggerOutputPort = obj.getTriggerOutputPort();
					if (outputPort2LivePortIndex.containsKey(triggerOutputPort)) {
						currentLivePort = outputPort2LivePortIndex.get(triggerOutputPort);
					} else {
						currentLivePort += obj.getTriggerOutputPort().getUsrPort();
						outputPort2LivePortIndex.put(triggerOutputPort, currentLivePort);
					}
					triggerPoints.add(new TriggerPair(currentTime, currentLivePort, triggerPulseLength));
				} else {
					TriggerOutputPort triggerOutputPort = obj.getTriggerOutputPort();
					if (outputPort2LivePortIndex.containsKey(triggerOutputPort)) {
						currentLivePort = outputPort2LivePortIndex.get(triggerOutputPort);
						currentLivePort -= obj.getTriggerOutputPort().getUsrPort();
						outputPort2LivePortIndex.remove(triggerOutputPort);
					} else {
						logger.error("Cannot find {} for the end pulse {}.",triggerOutputPort.getPortName(), triggerDelay+obj.getTriggerPulseLength());
					}
					triggerPoints.add(new TriggerPair(currentTime, currentLivePort, 0.0));
				}
			}
		}
		return triggerPoints;
	}

	private boolean isTriggerPulseOverlapForTheSamePort() {
		boolean overlapping=false;
		TreeMap<TriggerOutputPort, List<TriggerableObject>> triggerTimesAndSamEnv = new TreeMap<TriggerOutputPort, List<TriggerableObject>>();
		for (TriggerableObject entry : sampleEnvironment) {
			TriggerOutputPort outputPort = entry.getTriggerOutputPort();
			if (triggerTimesAndSamEnv.containsKey(outputPort)) {
				triggerTimesAndSamEnv.get(outputPort).add(entry);
			} else {
				List<TriggerableObject> trigger = new ArrayList<TriggerableObject>();
				trigger.add(entry);
				triggerTimesAndSamEnv.put(outputPort, trigger);
			}
		}
		for (Map.Entry<TriggerOutputPort, List<TriggerableObject>> entry : triggerTimesAndSamEnv.entrySet()) {
			TriggerOutputPort key = entry.getKey();
			List<TriggerableObject> values = entry.getValue();
			Collections.sort(values);
			for (int i=0; i<values.size()-1; i++) {
				TriggerableObject triggerableObject = values.get(i);
				TriggerableObject nextTriggerableObject = values.get(i+1);
				overlapping = overlapping || overlap(triggerableObject.getTriggerDelay(),triggerableObject.getTriggerDelay()+triggerableObject.getTriggerPulseLength(),
						nextTriggerableObject.getTriggerDelay(),nextTriggerableObject.getTriggerDelay()+nextTriggerableObject.getTriggerPulseLength());
				if (overlapping) {
					logger.warn("Triggers at {} and {} are overlapping on port {}.",triggerableObject.getTriggerDelay(), nextTriggerableObject.getTriggerDelay(),key.getPortName());
					break;
				}
			}
		}
		return overlapping;
	}
	private boolean overlap(double min1, double max1, double min2, double max2) {
		double start = Math.max(min1,min2);
		double end = Math.min(max1,max2);
		double d = end - start + TFG_TIME_RESOLUTION; //ensure minimum pulse separation - TFG2 time resolution
		if (d < 0.0) {
			return false;
		}
		return true;
	}

	private static class TriggerPair implements Comparable<TriggerPair>{
		private final double time;
		private final int port;
		private final double length;

		public TriggerPair(double aKey, int aValue, double pulseLength) {
			time = aKey;
			port = aValue;
			length=pulseLength;
		}

		@Override
		public int compareTo(TriggerPair o) {
			double diff=time-o.time;
			if (diff<0) {
				return -1;
			} else if (diff>0) {
				return 1;
			} else {
				return 0;
			}
		}

		// Added imh 13Aug
		double getTime() {
			return time;
		}
		int getPort() {
			return port;
		}
		double getLength() {
			return length;
		}
	}

	public void updateTotalTime() {
		firePropertyChange(TOTAL_TIME_PROP_NAME, null, getTotalTime());
	}

	public EdeDetector getDetector() {
		return detector;
	}

	public void setDetector(EdeDetector detector) {
		this.detector = detector;
	}

	public boolean isUsingExternalScripts4TFG() {
		return usingExternalScripts4TFG;
	}

	public void setUsingExternalScripts4TFG(boolean usingExternalScripts4TFG) {
		this.usingExternalScripts4TFG = usingExternalScripts4TFG;
	}

}
