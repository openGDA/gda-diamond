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

import java.beans.PropertyChangeListener;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.TreeMap;
import java.util.stream.Collectors;

import org.apache.commons.math3.util.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.gson.annotations.Expose;

import gda.device.detector.DetectorData;
import gda.device.detector.EdeDetector;
import gda.device.detector.frelon.FrelonCcdDetectorData;
import gda.jython.InterfaceProvider;
import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject.TriggerOutputPort;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentUnit;

public class TFGTrigger extends ObservableModel implements Serializable {

	private static final long serialVersionUID = 1L;

	private static final Logger logger=LoggerFactory.getLogger(TFGTrigger.class);
	private static final double TFG_TIME_RESOLUTION = 0.000000001; // second

	public static final ExperimentUnit DEFAULT_DELAY_UNIT = ExperimentUnit.SEC;

	private static final double MIN_DEAD_TIME = 0.000001;
	private static final double MIN_LIVE_TIME = 0.000001;
	private transient EdeDetector detector;
	private boolean usingExternalScripts4TFG=false;

	@Expose
	private final List<TriggerableObject> sampleEnvironment = new ArrayList<>();

	public static final String TOTAL_TIME_PROP_NAME = "totalTime";
	private final transient PropertyChangeListener totalTimeChangeListener = event -> TFGTrigger.this.firePropertyChange(TOTAL_TIME_PROP_NAME, null, getTotalTime());

	@Expose
	private final DetectorDataCollection detectorDataCollection = new DetectorDataCollection();

	private boolean useCountFrameScalers = false;
	private boolean triggerOnRisingEdge = true; /** Whether detector starts on rising or falling edge of trigger signal from Tfg */
	private int livePauseTtlPort = 1; /** the 'live pause' TTL trigger input port on Tfg [0...3] */

	public TFGTrigger() {
		detectorDataCollection.addPropertyChangeListener(totalTimeChangeListener);
	}

	public PropertyChangeListener getTotalTimeChangeListener() {
		return totalTimeChangeListener;
	}

	public DetectorDataCollection getDetectorDataCollection() {
		return detectorDataCollection;
	}

	public List<TriggerableObject> getSampleEnvironment() {
		return sampleEnvironment;
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
	public String getTfgSetupGroupCommandParameters(int numberOfCycles, boolean shouldStartOnTopupSignal) {
		if (isUsingExternalScripts4TFG()) {
			return InterfaceProvider.getCommandRunner().evaluateCommand("getCommands4ExternalTFG()");
		}
		return getTfgSetupGroupsCommandParameters(numberOfCycles, shouldStartOnTopupSignal);
	}

	private String getTfgSetupGroupsCommandParameters(int numberOfCycles, boolean shouldStartOnTopupSignal) {

		StringBuilder tfgCommand = new StringBuilder();
		List<TriggerParams> triggerPoints = processTimes(true); // also includes trigger to start camera
		Collections.sort(triggerPoints);

		tfgCommand.append("tfg setup-groups");
		if (numberOfCycles > 1) {
			tfgCommand.append(" cycles ");
			tfgCommand.append(numberOfCycles);
		}
		tfgCommand.append("\n");
		if (shouldStartOnTopupSignal) {
			// trigger on falling edge of port 0 (OR with 32 for falling edge) = 8|32 = 40
			tfgCommand.append(getTimeFrameString(1, MIN_DEAD_TIME, 0, 0, 0, 40, 0));
		}

		int totalNumberOfFrames = getTotalNumberOfFrames();
		boolean itCollectionAdded = false;
		int totalnumberFramesSoFar=0;
		int numberOfCollectionFramesToNotCount = 0;

		// NB: Counting for Frelon occurs on rising edge of accumulation readout signal, in middle of frame.
		// Counting for Xh/Xstrip uses frame trigger (i.e. pulse at *start* of each spectrum).
		// For Xh/Xstrip, first detector pulse after trigger signal can't be counted since the
		// trigger and rising edge of first frame coincide in time.

		for (int i = 0; i < triggerPoints.size()-1; i++) {
			TriggerParams thisPoint = triggerPoints.get(i);
			TriggerParams nextPoint = triggerPoints.get(i + 1);

			if ( !thisPoint.isTriggerIsDuringDetectorCollection() ) {
				// ... TriggerPoints *outside* of detector collection

				if (totalnumberFramesSoFar > 0 && !itCollectionAdded) {
					// For trigger points taking place *after* collection first add any remaining uncounted frames.
					int framesLeft = totalNumberOfFrames - totalnumberFramesSoFar - numberOfCollectionFramesToNotCount;

					if (framesLeft > 0) {
						tfgCommand.append( getCountFrameString(framesLeft, 0 ) );

						// How long to wait after counting the last rising edge of the detector pulse
						// to put next Tfg trigger at correct time
						double timeToNextPulse = thisPoint.getTimeFromDetectorTriggerToFrameEnd();
						tfgCommand.append( getWaitForTimeString(timeToNextPulse, 0) );
					}

					itCollectionAdded = true;
				}
				tfgCommand.append( getWaitForTimeString(thisPoint.getLength(), thisPoint.getPort() ) );
			} else {
				// ... TriggerPoints during detector collection

				// Determine number of detector signal 'rising edges' between triggers :
				int numRisingEdgesBetweenTriggers = nextPoint.getDetectorFrameNumber()-thisPoint.getDetectorFrameNumber();

				// Current trigger start time is *after* rising edge signal
				if (thisPoint.isTriggerAfterRisingEdge()) {
					numRisingEdgesBetweenTriggers--;
				}
				// Next trigger is after a rising edge and during data collection
				if (nextPoint.isTriggerAfterRisingEdge() && nextPoint.isTriggerIsDuringDetectorCollection()) {
					numRisingEdgesBetweenTriggers++;
				}

				if (thisPoint.getPort() == 0 && numRisingEdgesBetweenTriggers > 0) {
					// Wait (i.e. count some detector frames)
					tfgCommand.append( getCountFrameString(numRisingEdgesBetweenTriggers, 0 ) );

					// Insert a small wait after counting, so that next trigger point starts at correct time
					double timeToNextPulse = nextPoint.getTimeFromDetectorTriggerToFrameEnd();
					tfgCommand.append( getWaitForTimeString(timeToNextPulse, 0) );

					totalnumberFramesSoFar += numRisingEdgesBetweenTriggers;
				}
				else {
					// Normal trigger signal
					tfgCommand.append( getWaitForTimeString(thisPoint.getLength(), thisPoint.getPort()) );

					// determine number of count signals the frame overlaps with (and therefore can't be counted)
					numberOfCollectionFramesToNotCount += numRisingEdgesBetweenTriggers;
				}
			}
		}

		// Add data collection, after adding all trigger points if not already added
		int framesLeft = totalNumberOfFrames - totalnumberFramesSoFar - numberOfCollectionFramesToNotCount;

		if (framesLeft > 0) {
			tfgCommand.append( getCountFrameString(framesLeft, 0 ) );

			TriggerParams firstPoint = triggerPoints.get(0);
			double frameReadoutTime = firstPoint.getDetectorFrameLength() - firstPoint.getAccumulationTime();

			// at end of data collection external TFG2 must wait for a single detector frame to allow detector collection to complete.
			tfgCommand.append( getWaitForTimeString(frameReadoutTime, 0) );
		}

		tfgCommand.append("-1 0 0 0 0 0 0");

		if (useCountFrameScalers) {
			tfgCommand.append( getPrepareScalerString() );
		}
		return tfgCommand.toString();
	}

	/**
	 *
	 * Number of trigger signals produced per spectrum by detector
	 * (these are counted to keep detector and Tfg synchronized)
	 * Frelon - number of spectra*num accumulations per spectrum
	 * Xh - number of spectra (i.e. 1 trig. per spectrum)
	 */
	private int getTotalNumberOfFrames() {
		int framesPerSpectrum = 1;
		if (detectorIsFrelon()) {
			framesPerSpectrum = getDetector().getNumberScansInFrame();
		} else {
			framesPerSpectrum = 1;
		}
		return detectorDataCollection.getNumberOfFrames()*framesPerSpectrum;
	}

	private String getCountFrameString( int numFrames, int port ) {
		int livePause = livePauseTtlPort + 8; // Use rising edge of input TTL port for live pause (+32 for falling edge);
		if ( useCountFrameScalers )
			return getTimeFrameString(numFrames, 0, MIN_LIVE_TIME, 0, 256, 0, livePause);
		else
			return getTimeFrameString(numFrames, 0, MIN_LIVE_TIME, 0, port, 0, livePause);
	}

	private String getWaitForTimeString( double length, int port ) {
		return getTimeFrameString(1, length, 0, port, 0, 0, 0);
	}

	private String getTimeFrameString( int numFrames, double deadTime, double liveTime, int deadPort, int livePort, int deadPause, int livePause ) {
		return String.format("%d %.9f %.9f %d %d %d %d\n", numFrames, deadTime, liveTime, deadPort, livePort, deadPause, livePause);
	}

	private String getPrepareScalerString() {
		String scalerMode = "\ntfg setup-cc-mode scaler64\n" +
		"tfg setup-cc-chan 0 vetoed-level\n" +
		"tfg setup-cc-chan 1 vetoed-level\n";

		String scalerOpen = "set-func \"path\" \"tfg open-cc\" \n" +
		"clear %path\n" +
		"enable %path\n";

		return scalerMode + scalerOpen;
	}

	private boolean detectorIsFrelon() {
		DetectorData detectorSettings = getDetector().getDetectorData();
		return detectorSettings instanceof FrelonCcdDetectorData;
	}

	/**
	 * Add/append new key, value pair to the map (key = K, value = List of Vs).
	 * Creates new list for the key if it is not already present.
	 * @param mapOfLists {@code Map<K, List<V>> }
	 * @param K key
	 * @param V value
	 */
	private <V, K> void addToListInMap(Map<K, List<V>> mapOfLists, K key, V value) {
		List<V> listForKey = mapOfLists.computeIfAbsent(key, k -> new ArrayList<V>() );
		listForKey.add(value);
	}

	/**
	 * Refactored from 'processTimes'
	 * Make map from pulse edge times to list of triggerable objects that start/end at those times.
	 * Map keys are in order of ascending time.
	 * @since 18/9/2015
	 * @param triggerObjList
	 * @return TreeMap with List of TriggerableObjects for each time.
	 */
	private TreeMap<Double, List<TriggerableObject>> getMapPulseEdge2TriggerObj( List<TriggerableObject> triggerObjList ) {

		TreeMap<Double, List<TriggerableObject>> pulseEdgeTime2TriggerObj = new TreeMap<>();
		// Make map from pulse edge times to list of triggerable objects that start/end at those times
		for (TriggerableObject triggerObjForPulse : triggerObjList ) {
			double pulseStartTime = triggerObjForPulse.getTriggerDelay();
			double pulseEndTime = triggerObjForPulse.getTriggerDelay() + triggerObjForPulse.getTriggerPulseLength();
			addToListInMap(pulseEdgeTime2TriggerObj, pulseStartTime, triggerObjForPulse);
			addToListInMap(pulseEdgeTime2TriggerObj, pulseEndTime, triggerObjForPulse);
		}

		return pulseEdgeTime2TriggerObj;
	}

	/**
	 * For each trigger, set data accumulation frame number that the trigger lies within,
	 * the trigger time relative to frame start, and frame start time.
	 * @since 24/9/2015
	 * @param triggerParams
	 */
	private void setTriggerPointFrameInfo( List<TriggerParams> triggerParams ) {

		double firstFrameLength = triggerParams.get(1).getTime() - triggerParams.get(0).getTime();
		triggerParams.get(0).setLength( firstFrameLength );

		double iTcollectionEndTime = detectorDataCollection.getTotalDelay();
		double iTcollectionStartTime = detectorDataCollection.getTriggerDelay();

		// If data collection starts on *falling edge* of trigger signal, add trigger pulse length to start and end collection time;
		if (!triggerOnRisingEdge) {
			double triggerPulseLength = detectorDataCollection.getTriggerPulseLength();
			iTcollectionStartTime += triggerPulseLength;
			iTcollectionEndTime += triggerPulseLength;
		}

		double collectionDuration = detectorDataCollection.getCollectionDuration();
		int totalNumberOfFrames = getTotalNumberOfFrames();
		double singleFrameTime=collectionDuration/totalNumberOfFrames;

		double accumulationTime = 0.0;
		if (detectorIsFrelon()) {
			accumulationTime = ((FrelonCcdDetectorData)getDetector().getDetectorData()).getAccumulationMaximumExposureTime();
		}

		for(TriggerParams triggerParam : triggerParams) {
			double triggerTime = triggerParam.getTime();
			double timeInCollection = triggerTime - iTcollectionStartTime;
			int frameNumber = (int) Math.floor(timeInCollection / singleFrameTime);
			double frameStartTime =  iTcollectionStartTime+frameNumber*singleFrameTime;
			boolean insideDetectorCollection = true;

			if (timeInCollection < TFG_TIME_RESOLUTION || timeInCollection >= collectionDuration) {
				insideDetectorCollection = false;
			}

			if (frameNumber >= totalNumberOfFrames) {
				frameNumber = totalNumberOfFrames;
				frameStartTime = iTcollectionEndTime - singleFrameTime;
			}

			// For XH detector, trigger signal and detector frame both coincide - so for
			// frame counting purposes, mark the trigger as being *inside* the detector collection
			if (!detectorIsFrelon() &&
				triggerParam.getPort() == detectorDataCollection.getTriggerOutputPort().getUsrPort()) {
				insideDetectorCollection = true;
			}
			triggerParam.setDetectorFrameNumber(frameNumber);
			triggerParam.setDetectorFrameLength(singleFrameTime);
			triggerParam.setDetectorFrameStartTime(frameStartTime);
			triggerParam.setAccumulationTime(accumulationTime);
			triggerParam.setTriggerDuringDetectorCollection(insideDetectorCollection);
		}
	}

	/**
	 * Generate list of trigger parameters. Derived from old processTimes function (originally written for XH).
	 * Works correctly for multiple overlapping pulses on different ports.
	 * @since 18/9/2015
	 * @param addDetectorTriggerToSampleEnvironment
	 * @return
	 */
	private List<TriggerParams> processTimes( boolean addDetectorTriggerToSampleEnvironment ) {

		if (sampleEnvironment.isEmpty() && !addDetectorTriggerToSampleEnvironment) {
			return Collections.emptyList();
		}

		List<TriggerableObject> newSampleEnvironment = sampleEnvironment.stream().collect(Collectors.toList());

		// Also add pulse to start detector to list of triggers
		if (addDetectorTriggerToSampleEnvironment) {
			newSampleEnvironment.add( detectorDataCollection );
		}

		List<TriggerParams> triggerPoints = new ArrayList<>();

		TreeMap<Double, List<TriggerableObject>> pulseEdgeTime2TriggerObj = getMapPulseEdge2TriggerObj(newSampleEnvironment);
		if (pulseEdgeTime2TriggerObj.firstKey() > 0d) {
			//define the time zero trigger point - note this is not a trigger.
			triggerPoints.add(new TriggerParams(0.0d, 0, 0.0));
		}

		if (isTriggerPulseOverlapForTheSamePort(newSampleEnvironment)) {
			//must not allow trigger pulse overlapping on the same output port
			throw new IllegalStateException("Signals on the same port are not allowed to overlap in time.");
		}

		// Array used to track on/off status of each port
		boolean [] activePortArray = new boolean[ TriggerOutputPort.getTotalNumPorts() ];
		Arrays.fill( activePortArray, false );

		// Get List of times of all pulse edges from map
		List<Double> edgeTimes = new ArrayList<>( pulseEdgeTime2TriggerObj.keySet() );
		int edgeCount = 0;

		// For each pulse edge there may be several TriggerableObjects. Create *one* entry in triggerPoints list
		// per edge, using live port corresponding to currently 'on' set of live ports.
		// On/off status of each port with time is tracked using array of bools (activePortArray)
		for (Entry<Double, List<TriggerableObject>> entry : pulseEdgeTime2TriggerObj.entrySet()) {
			double currentEdgeTime = entry.getKey();
			for (TriggerableObject triggerObjForTime : entry.getValue()) {
				double pulseStartTime = triggerObjForTime.getTriggerDelay();
				TriggerOutputPort triggerOutputPort = triggerObjForTime.getTriggerOutputPort(); // i.e. USR_OUT_0, USR_OUT_1 etc.
				if (Math.abs(currentEdgeTime - pulseStartTime) < TFG_TIME_RESOLUTION) {
					// TriggerableObject corresponding to start of pulse (switch port on)
					activePortArray[triggerOutputPort.getUsrPortNumber()] = true;
				} else {
					// TriggerableObject corresponding to end of pulse (switch port off)
					activePortArray[triggerOutputPort.getUsrPortNumber()] = false;
				}
			}

			// set active port bit field from array of active ports.
			int activePortBitfield = 0;
			for (int i = 0; i < activePortArray.length; i++) {
				if (activePortArray[i]) {
					activePortBitfield += Math.pow(2, i);
				}
			}

			// Framelength is time between current and next edge - this will be different to total pulse length
			// on a port if several pulses on different ports overlap in time.
			double frameLength = 0.0; // if on last edge, everything is switched off and length = 0
			if (edgeCount < edgeTimes.size() - 1) {
				frameLength = edgeTimes.get(edgeCount + 1) - edgeTimes.get(edgeCount);
			}
			edgeCount++;

			triggerPoints.add(new TriggerParams(currentEdgeTime, activePortBitfield, frameLength));

		}

		setTriggerPointFrameInfo(triggerPoints);

		return triggerPoints;
	}

	/**
	 *
	 * @param triggerParams
	 * @param startTime
	 * @param endTime
	 * @return List of TriggerParams that have a trigger taking place between startTime and endTime and a port output > 0
	 */
	private List<TriggerParams> getParamsForTimes(List<TriggerParams> triggerParams, double startTime, double endTime) {
		return triggerParams.stream()
				.filter(triggerParam -> triggerParam.getPort() > 0 && triggerParam.isOverlap(startTime, endTime))
				.collect(Collectors.toList());
	}

	public Map<Integer, Pair<Integer, Integer> > getFramesForSpectra() {
		List<TriggerParams> triggerParams = processTimes(true);
		// Each TriggerParams corresponds to pulse edge.
		// Each TriggerParams occurs at time t, has length l and specifies a number for the output signal on the USR ports.

		int numSpectra = detectorDataCollection.getNumberOfFrames();
		int totalNumDetectorPulses = getTotalNumberOfFrames();
		int numDetectorPulsesPerSpectrum = totalNumDetectorPulses/numSpectra;

		double firstSpectrumStartTime = detectorDataCollection.getTriggerDelay() + detectorDataCollection.getTriggerPulseLength();
		double timePerSpectrum = getTimePerSpectrum();
		double timePerDetectorPulse = timePerSpectrum/numDetectorPulsesPerSpectrum;

		// Map from spectrum number -> scaler start frame, scaler end frame
		Map<Integer, Pair<Integer, Integer> > framesForSpectra = new LinkedHashMap<>();
		int startScalerFrame = 0;
		int endScalerFrame = 0;

		// Loop over spectra and set the start and end scaler frame for each one.
		//  No Tfg output -> scaler frames all same length, one per detector readout
		//  Tfg output -> scaler frame length from length of output signal, scaler start and end frame
		// for each spectrum needs adjusting to account for non even in frame length.

		for(int i=0; i<numSpectra; i++) {
			double spectrumStartTime = firstSpectrumStartTime + i*timePerSpectrum;

			// Get list of trigger params that overlap in time with this spectrum
			List<TriggerParams> paramForSpectra = getParamsForTimes(triggerParams, spectrumStartTime, spectrumStartTime+timePerSpectrum);

			startScalerFrame = endScalerFrame;

			// Count the number of detector pulses that occur at same same as Tfg output signal
			int numCoincidentPulses = 0;
			if (paramForSpectra.isEmpty()) {
				endScalerFrame += numDetectorPulsesPerSpectrum;
			} else {
				for (int detPulse = 0; detPulse < numDetectorPulsesPerSpectrum; detPulse++) {
					double pulseTime = spectrumStartTime + detPulse * timePerDetectorPulse;
					boolean overlap = paramForSpectra.stream()
							.anyMatch(param -> param.isOverlap(pulseTime) && param.getPort() > 0);

					if (overlap) {
						numCoincidentPulses++;
					}
				}
				endScalerFrame += numDetectorPulsesPerSpectrum - numCoincidentPulses;
			}

			framesForSpectra.put(i, Pair.create(startScalerFrame, endScalerFrame));
		}
		return framesForSpectra;
	}

	private double getTimePerSpectrum() {
		double collectionDuration = detectorDataCollection.getCollectionDuration();
		int totalNumberOfFrames = detectorDataCollection.getNumberOfFrames();
		return collectionDuration/totalNumberOfFrames;
	}

	private boolean isTriggerPulseOverlapForTheSamePort(List<TriggerableObject> triggerableObjList) {
		// Make list of triggerable objects for each output port
		Map<TriggerOutputPort, List<TriggerableObject>> outputPort2TriggerObj = new HashMap<>();
		for (TriggerableObject triggerObjForPulse : triggerableObjList) {
			addToListInMap(outputPort2TriggerObj, triggerObjForPulse.getTriggerOutputPort(), triggerObjForPulse);
		}

		boolean overlapping = false;
		for (Entry<TriggerOutputPort, List<TriggerableObject>> entry : outputPort2TriggerObj.entrySet()) {
			List<TriggerableObject> triggerObjList = entry.getValue();
			Collections.sort(triggerObjList);
			for (int i=0; i<triggerObjList.size()-1; i++) {
				TriggerableObject thisPulse = triggerObjList.get(i);
				TriggerableObject nextPulse = triggerObjList.get(i+1);
				overlapping = overlapping || overlap(thisPulse, nextPulse);
				if (overlapping) {
					TriggerOutputPort outputPort = entry.getKey();
					logger.warn("Triggers at {} and {} are overlapping on port {}.", thisPulse.getTriggerDelay(),
							nextPulse.getTriggerDelay(), outputPort.getPortName());
					break;
				}
			}
		}
		return overlapping;
	}


	/**
	 *
	 * @param min1
	 * @param max1
	 * @param min2
	 * @param max2
	 * @return True if the time ranges (min1... max1) and (min2... max2) overlap.
	 */
	private static boolean overlap(double min1, double max1, double min2, double max2) {
		double start = Math.max(min1, min2);
		double end = Math.min(max1, max2);
		double d = end - start + TFG_TIME_RESOLUTION; // ensure minimum pulse separation - TFG2 time resolution
		return d >= 0.0;
	}

	/**
	 * @param t1
	 * @param t2
	 * @return Return true if trigger pulses t1 and t2 overlap in time
	 */
	private static boolean overlap(TriggerableObject t1, TriggerableObject t2) {
		return overlap(t1.getTriggerDelay(), t1.getTriggerDelay() + t1.getTriggerPulseLength(),
				       t2.getTriggerDelay(), t2.getTriggerDelay() + t2.getTriggerPulseLength());

	}

	private static class TriggerParams implements Comparable<TriggerParams>{
		private double time;
		private int port;
		private double length;

		private int detectorFrameNumber;
		private double detectorSignalRisingEdgeStartTime;
		private double detectorFrameStartTime;
		private double detectorFrameLength;
		private boolean triggerIsDuringDetectorCollection;

		public TriggerParams(double aKey, int aValue, double pulseLength) {
			time = aKey;
			port = aValue;
			length=pulseLength;
		}

		@Override
		public int compareTo(TriggerParams o) {
			double diff=time-o.time;
			if (diff<0) {
				return -1;
			} else if (diff>0) {
				return 1;
			} else {
				return 0;
			}
		}

		double getTime() {
			return time;
		}

		void setTime( double time ) {
			this.time = time;
		}

		int getPort() {
			return port;
		}

		void setPort( int port ) {
			this.port = port;
		}

		double getLength() {
			return length;
		}

		public void setLength(double length) {
			this.length = length;
		}

		/**
		 *
		 * @return Frame number on the detector for this trigger point
		 */
		public int getDetectorFrameNumber() {
			return detectorFrameNumber;
		}

		public void setDetectorFrameNumber(int detectorFrameNumber) {
			this.detectorFrameNumber = detectorFrameNumber;
		}

		public void setAccumulationTime(double accumulationTime ) {
			this.detectorSignalRisingEdgeStartTime = accumulationTime;
		}
		public double getAccumulationTime() {
			return detectorSignalRisingEdgeStartTime;
		}

		/**
		 *
		 * @param detectorFrameStartTime Start time of detector frame
		 */
		public void setDetectorFrameStartTime(double detectorFrameStartTime) {
			this.detectorFrameStartTime = detectorFrameStartTime;
		}

		public void setDetectorFrameLength(double detectorFrameTotalLength) {
			this.detectorFrameLength = detectorFrameTotalLength;
		}

		public double getDetectorFrameLength() {
			return detectorFrameLength;
		}

		public boolean isTriggerAfterRisingEdge() {
			double relTime = time - detectorFrameStartTime;
			if (relTime > detectorFrameLength) {
				relTime = 0;
			}
			return relTime > detectorSignalRisingEdgeStartTime + TFG_TIME_RESOLUTION;
		}

		/**
		 * Time between rising edge in detector signal and trigger time
		 * @return
		 */
		public double getTimeFromDetectorTriggerToFrameEnd() {
				double detectorRisingEdgeTime = detectorFrameStartTime+detectorSignalRisingEdgeStartTime;
				if (time > detectorRisingEdgeTime + TFG_TIME_RESOLUTION) {
					return time-detectorRisingEdgeTime;
				}
				// Return time relative to rising edge in previous frame

				// Time between detector rising and end of frame
				double timeAfterRisingEdge = detectorFrameLength - detectorSignalRisingEdgeStartTime;
				// Position of the trigger relative to start of detector frame
				double triggerTimeInFrame = time - detectorFrameStartTime;

				return timeAfterRisingEdge + triggerTimeInFrame;
		}

		/**
		 *
		 * @return True if trigger occurs during detector collection.
		 */
		public boolean isTriggerIsDuringDetectorCollection() {
			return triggerIsDuringDetectorCollection;
		}


		public void setTriggerDuringDetectorCollection(boolean triggerIsDuringDetectorCollection) {
			this.triggerIsDuringDetectorCollection = triggerIsDuringDetectorCollection;
		}

		/**
		 * @param testTime
		 * @return true it testTime occurs within pulse start and pulse start + pulse length
		 */
		public boolean isOverlap(double testTime) {
			return testTime > time && testTime < time + length;
		}

		/**
		 *
		 * @param startTime
		 * @param endTime
		 * @return True if any part of pulse is between startTime and endTime
		 */
		public boolean isOverlap(double startTime, double endTime) {
			return overlap(time, time + length, startTime, endTime);
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

	public boolean getUseCountFrameScalers() {
		return useCountFrameScalers;
	}

	public void setUseCountFrameScalers(boolean useCountFrameScalers) {
		this.useCountFrameScalers = useCountFrameScalers;
	}

	public void setTriggerOnRisingEdge(boolean triggerOnRisingEdge) {
		this.triggerOnRisingEdge = triggerOnRisingEdge;
	}

	public boolean getTriggerOnRisingEdge() {
		return triggerOnRisingEdge;
	}
}
