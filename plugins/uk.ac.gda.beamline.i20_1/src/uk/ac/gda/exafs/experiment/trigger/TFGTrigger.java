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

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject.TriggerOutputPort;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentUnit;

import com.google.gson.annotations.Expose;

public class TFGTrigger extends ObservableModel implements Serializable {
	// The first 2 is reserved for photonShutter and detector
	private static final int MAX_PORTS_FOR_SAMPLE_ENV = TriggerableObject.TriggerOutputPort.values().length - 2;

	public static final ExperimentUnit DEFAULT_DELAY_UNIT = ExperimentUnit.SEC;
	public static final double DEFAULT_PULSE_WIDTH_IN_SEC = 0.001d;

	private static final double MIN_DEAD_TIME = 0.000001;
	private static final double MIN_LIVE_TIME = 0.000001;

	@Expose
	private final List<TriggerableObject> sampleEnvironment = new ArrayList<TriggerableObject>(MAX_PORTS_FOR_SAMPLE_ENV);
	//	@Expose
	//	private final PhotonShutter photonShutter = new PhotonShutter();
	@Expose
	private final DetectorDataCollection detectorDataCollection = new DetectorDataCollection();
	//
	//	public PhotonShutter getPhotonShutter() {
	//		return photonShutter;
	//	}

	public DetectorDataCollection getDetectorDataCollection() {
		return detectorDataCollection;
	}

	public List<TriggerableObject> getSampleEnvironment() {
		return sampleEnvironment;
	}

	public TriggerableObject createNewSampleEnvEntry() throws Exception {
		if (sampleEnvironment.size() == MAX_PORTS_FOR_SAMPLE_ENV) {
			throw new Exception("Maxium ports reached: " + MAX_PORTS_FOR_SAMPLE_ENV);
		}
		TriggerableObject obj = new TriggerableObject();
		obj.setName("Default");
		obj.setTriggerPulseLength(DEFAULT_PULSE_WIDTH_IN_SEC);
		obj.setTriggerDelay(0.1);
		obj.setTriggerOutputPort(TriggerOutputPort.values()[sampleEnvironment.size() + 2]);
		return obj;
	}

	//		Format of 'tfg setup-groups' as follows, 7 or 9 space-separated numbers:
	//			num_frames dead_time live_time dead_port live_port dead_pause live_pause [dead_tfinc live_tfinc]
	//			Followed by last line:
	//			-1 0 0 0 0 0 0
	//			Where num_frames       	= Number of frames in this group
	//			Dead_time, Live_time   	= time as floating point seconds
	//			Dead_port, Live_port    	= port data as integer (0<=port<=128k-1)
	//			Dead_pause, Live_pause 	= pause bit (0<=pause<=1)
	//			And For TFG2 only
	//			num_repeats sequence_name
	//			This repeats the pre-recorded sequence num_repeats times.
	public String getTfgSetupGrupsCommandParameters(int numberOfCycles, boolean shouldStartOnTopupSignal) {
		StringBuilder tfgCommand = new StringBuilder();
		List<TriggerPair> triggerPoints = processTimes();
		tfgCommand.append("tfg setup-groups");
		if (numberOfCycles > 1) {
			tfgCommand.append(" cycles ");
			tfgCommand.append(numberOfCycles);
		}
		tfgCommand.append("\n");
		if (shouldStartOnTopupSignal) {
			tfgCommand.append(String.format("1 %f 0 0 0 8 0\n", MIN_DEAD_TIME));
		}
		for (int i = 0; i < triggerPoints.size(); i++) {
			if (i + 1 < triggerPoints.size()) {
				double collectionStopTime = detectorDataCollection.getTriggerDelay() + detectorDataCollection.getCollectionDuration();
				if (triggerPoints.get(i + 1).time > detectorDataCollection.getTriggerDelay() && triggerPoints.get(i + 1).time < collectionStopTime) {
					// FIXME
				} else if (triggerPoints.get(i + 1).time >= collectionStopTime) {
					tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", (detectorDataCollection.getTriggerDelay() - triggerPoints.get(i).time), triggerPoints.get(i).port));
					tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", detectorDataCollection.getTriggerPulseLength(), detectorDataCollection.getTriggerOutputPort().getUsrPort() + triggerPoints.get(i).port));
					tfgCommand.append(String.format("%d 0 %f 0 %d 0 9\n", detectorDataCollection.getNumberOfFrames(), MIN_LIVE_TIME, detectorDataCollection.getTriggerOutputPort().getUsrPort() + triggerPoints.get(i).port)); // Review if this is dead or live port
					if (triggerPoints.get(i + 1).time == collectionStopTime) {
						tfgCommand.append(String.format("1 %f 0.0 0 0 9 0\n", MIN_DEAD_TIME));
					} else {
						tfgCommand.append(String.format("1 %f 0.0 %d 0 9 0\n", triggerPoints.get(i + 1).time - collectionStopTime, triggerPoints.get(i).port)); // Review if this is dead or live port
					}
				} else if (triggerPoints.get(i + 1).time == detectorDataCollection.getTriggerDelay()) {
					// FIXME
				} else {
					tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", triggerPoints.get(i + 1).time - triggerPoints.get(i).time, triggerPoints.get(i).port));
				}
			}
		}
		tfgCommand.append("-1 0 0 0 0 0 0");
		return tfgCommand.toString();
	}

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

	private List<TriggerPair> processTimes() {
		TreeMap<Double, List<TriggerableObject>> triggerTimesAndSamEnv = new TreeMap<Double, List<TriggerableObject>>();
		List<TriggerPair> triggerPoints = new ArrayList<TriggerPair>();
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
			triggerPoints.add(new TriggerPair(0.0d, 0));
		}
		for (Map.Entry<Double, List<TriggerableObject>> entry : triggerTimesAndSamEnv.entrySet()) {
			double currentTime = entry.getKey();
			for (TriggerableObject obj : entry.getValue()) {
				if (currentTime == obj.getTriggerDelay()) {
					currentLivePort += obj.getTriggerOutputPort().getUsrPort();
				} else {
					currentLivePort -= obj.getTriggerOutputPort().getUsrPort();
				}
			}
			triggerPoints.add(new TriggerPair(currentTime, currentLivePort));
		}
		return triggerPoints;
	}

	private static class TriggerPair {
		private final double time;
		private final int port;

		public TriggerPair(double aKey, int aValue)
		{
			time   = aKey;
			port = aValue;
		}
	}
}