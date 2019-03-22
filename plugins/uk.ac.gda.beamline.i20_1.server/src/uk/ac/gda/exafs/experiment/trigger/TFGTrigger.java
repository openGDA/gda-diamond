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

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

import org.apache.commons.math3.util.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.gson.annotations.Expose;

import gda.device.detector.DetectorData;
import gda.device.detector.EdeDetector;
import gda.device.detector.frelon.EdeFrelon;
import gda.device.detector.frelon.FrelonCcdDetectorData;
import gda.device.detector.xstrip.XhDetector;
import gda.jython.InterfaceProvider;
import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject.TriggerOutputPort;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentUnit;

public class TFGTrigger extends ObservableModel implements Serializable {

	private static final long serialVersionUID = 1L;

	private static final Logger logger=LoggerFactory.getLogger(TFGTrigger.class);
	// The first 2 is reserved for photonShutter and detector
	private static final int MAX_PORTS_FOR_SAMPLE_ENV = TriggerableObject.TriggerOutputPort.values().length - 2;
	private static final double TFG_TIME_RESOLUTION=0.000000001; //second

	public static final ExperimentUnit DEFAULT_DELAY_UNIT = ExperimentUnit.SEC;
	public static final double DEFAULT_PULSE_WIDTH_IN_SEC = 0.001d;

	private static final double MIN_DEAD_TIME = 0.000001;
	private static final double MIN_LIVE_TIME = 0.000001;
	private transient EdeDetector detector;
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
	private boolean useCountFrameScalers = false;
	private boolean triggerOnRisingEdge = true; //generally true for Frelon, False for Xh

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

	public double getTimePerSpectrum() {
		double collectionDuration = detectorDataCollection.getCollectionDuration();
		int totalNumberOfFrames = detectorDataCollection.getNumberOfFrames();
		return collectionDuration/totalNumberOfFrames;
	}

	public TriggerableObject createNewSampleEnvEntry() {
		TriggerableObject obj = new TriggerableObject();
		obj.setName("Default");
		obj.setTriggerPulseLength(DEFAULT_PULSE_WIDTH_IN_SEC);
		obj.setTriggerDelay(0.1);
		obj.setTriggerOutputPort(TriggerOutputPort.values()[2]);
		return obj;
	}

	public TriggerableObject createNewSampleEnvEntry( double startTime, double length, TriggerableObject.TriggerOutputPort port ) {
		TriggerableObject obj = createNewSampleEnvEntry();
		obj.setTriggerDelay( startTime );
		obj.setTriggerPulseLength( length );
		obj.setTriggerOutputPort(port);
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
	public String getTfgSetupGroupCommandParameters(int numberOfCycles, boolean shouldStartOnTopupSignal) {
		if (isUsingExternalScripts4TFG()) {
			String tfgCommand = InterfaceProvider.getCommandRunner().evaluateCommand("getCommands4ExternalTFG()");
			return tfgCommand.toString();
		}
		return getTfgSetupGroupsCommandParameters(numberOfCycles, shouldStartOnTopupSignal);
	}

	// Functions to generate commonly used TFG command strings. imh 18/9/2015
	public String getBeginningFrameString( TriggerParams trigPoint ) {
		double iTcollectionStartTime = detectorDataCollection.getTriggerDelay();
		// wait frame before collection starts
		String line1 = String.format( "1 %f 0.0 %d 0 0 0\n", (iTcollectionStartTime - trigPoint.getTime()), trigPoint.getPort());
		// trigger to start detector
		String line2 = String.format( "1 %f 0.0 %d 0 0 0\n", detectorDataCollection.getTriggerPulseLength(), detectorDataCollection.getTriggerOutputPort().getUsrPort() );
		return line1 + line2;
	}

	public String getCountFrameString( int numFrames, int port ) {
		if ( useCountFrameScalers )
			return getTimeFrameString( numFrames, 0, MIN_LIVE_TIME, 0, 256, 0, 9 );
		else
			return String.format( "%d 0 %f 0 %d 0 9\n", numFrames, MIN_LIVE_TIME, port);
	}

	public String getWaitForTimeString( double length, int port ) {
		return String.format( "1 %f 0.0 %d 0 0 0\n", length, port );
	}

	public String getTimeFrameString( int numFrames, double deadTime, double liveTime, int deadPort, int livePort, int deadPause, int livePause ) {
		return String.format( "%d %f %f %d %d %d %d\n", numFrames, deadTime, liveTime, deadPort, livePort, deadPause, livePause );
	}

	public String getPrepareScalerString() {
		String scalerMode = new  String( "\ntfg setup-cc-mode scaler64\n" +
		"tfg setup-cc-chan 0 vetoed-level\n" +
		"tfg setup-cc-chan 1 vetoed-level\n" );

		String scalerOpen = new String( "set-func \"path\" \"tfg open-cc\" \n" +
		"clear %path\n" +
		"enable %path\n" );

		return scalerMode + scalerOpen;
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
		if (getDetector() instanceof EdeFrelon) {
			framesPerSpectrum = getDetector().getNumberScansInFrame();
		} else {
			framesPerSpectrum = 1;
		}
		return detectorDataCollection.getNumberOfFrames()*framesPerSpectrum;
	}

	private boolean detectorIsXh() {
		return getDetector() instanceof XhDetector;
	}

	public String getTfgSetupGroupsCommandParameters(int numberOfCycles, boolean shouldStartOnTopupSignal) {

		StringBuilder tfgCommand = new StringBuilder();
		List<TriggerParams> triggerPoints = processTimes( true ); // also includes trigger to start camera
		Collections.sort(triggerPoints);

		tfgCommand.append("tfg setup-groups");
		if (numberOfCycles > 1) {
			tfgCommand.append(" cycles ");
			tfgCommand.append(numberOfCycles);
		}
		tfgCommand.append("\n");
		if (shouldStartOnTopupSignal) {
			// tfgCommand.append(String.format("1 %f 0 0 0 8 0\n", MIN_DEAD_TIME));
			// trigger on falling edge of port 0 (OR with 32 for falling edge) = 8|32 = 40
			tfgCommand.append(String.format("1 %f 0 0 0 %d 0\n", MIN_DEAD_TIME, 40 ));
		}

		int totalNumberOfFrames = getTotalNumberOfFrames();
		boolean itCollectionAdded = false;
		int totalnumberFramesSoFar=0;
		int numberOfCollectionFramesToNotCount = 0;

		boolean adjustToExactStartTime = true;

		TriggerParams firstPoint = triggerPoints.get(0);
		double accumulationReadoutTime = firstPoint.getAccumulationFrameLength() - firstPoint.getAccumulationLength();;


		// NB: Counting for Frelon occurs on rising edge of accumulation readout signal, in middle of frame
		// Counting for Xh/Xstrip uses frame trigger (i.e. pulse at *start* of each spectrum).
		// For Xh/Xstrip trigger signal is not produced for first spectrum.

		for (int i = 0; i < triggerPoints.size()-1; i++) {
			TriggerParams thisPoint = triggerPoints.get(i);
			TriggerParams nextPoint = triggerPoints.get(i + 1);

			if ( !thisPoint.getTriggerIsDuringAccumulation() ) {
				// ... TriggerPoints *outside* of detector accumulation

				if ( totalnumberFramesSoFar > 0 && !itCollectionAdded) {
					// For trigger points taking place *after* collection first add any remaining uncounted frames.
					int framesLeft = totalNumberOfFrames - totalnumberFramesSoFar - numberOfCollectionFramesToNotCount;

					if ( framesLeft > 0 ) {
						tfgCommand.append( getCountFrameString(framesLeft, 0 ) );

						double timeToNextPulse = thisPoint.getTimeFromAccumulationEnd();
						tfgCommand.append( getWaitForTimeString(timeToNextPulse, 0) );
					}

					itCollectionAdded = true;
				}
				tfgCommand.append( getWaitForTimeString(thisPoint.getLength(), thisPoint.getPort() ) );
			} else {
				// ... TriggerPoints during detector accumulation

				// Determine number of count signals covered by this frame
				int numberCountSignalsBetweenAdjacentPoints = nextPoint.getAccumulationFrameNumber()-thisPoint.getAccumulationFrameNumber();
				if ( thisPoint.getAccumulationFramePart() > 0 ) { // triggerpoint start time is *after* count signal
					numberCountSignalsBetweenAdjacentPoints--;
				}
				if ( nextPoint.getAccumulationFramePart() > 0 ) { // end triggerpoint *after* count
					numberCountSignalsBetweenAdjacentPoints++;
				}

				if ( thisPoint.getPort() == 0 && numberCountSignalsBetweenAdjacentPoints > 0 ) {
					// Wait (i.e. count some data accumulation frames)
					tfgCommand.append( getCountFrameString(numberCountSignalsBetweenAdjacentPoints, 0 ) );

					// Insert a small wait after the 'count' signal, so that next trigger point starts at correct time
					if ( adjustToExactStartTime ) {
						double timeToNextPulse = nextPoint.getTimeFromAccumulationEnd();
						tfgCommand.append( getWaitForTimeString(timeToNextPulse, 0) );
					}
					totalnumberFramesSoFar += numberCountSignalsBetweenAdjacentPoints;
				}
				else {
					// Normal trigger signal
					tfgCommand.append( getWaitForTimeString(thisPoint.getLength(), thisPoint.getPort()) );

					// determine number of count signals the frame overlaps with (and therefore can't be counted)
					numberOfCollectionFramesToNotCount += numberCountSignalsBetweenAdjacentPoints;
				}
			}
		}

		// Add data collection, after adding all trigger points if not already added
		int framesLeft = totalNumberOfFrames - totalnumberFramesSoFar - numberOfCollectionFramesToNotCount;

		// For Xh, frame trigger for first frame/spectrum is not produced
		if (detectorIsXh()) {
			framesLeft--;
		}

		if ( framesLeft > 0 ) {
			tfgCommand.append( getCountFrameString(framesLeft, 0 ) );

			// at end of data collection external TFG2 must wait for a single accumulation readout to allow detector collection to complete.
			tfgCommand.append( getWaitForTimeString(accumulationReadoutTime, 0) );
		}

		tfgCommand.append("-1 0 0 0 0 0 0");

		if ( useCountFrameScalers )
			tfgCommand.append( getPrepareScalerString() );

		return tfgCommand.toString();
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

		TreeMap<Double, List<TriggerableObject>> pulseEdgeTime2TriggerObj = new TreeMap<Double, List<TriggerableObject>>();
		// Make map from pulse edge times to list of triggerable objects that start/end at those times
		for (TriggerableObject triggerObjForPulse : triggerObjList ) {
			double pulseStartTime = triggerObjForPulse.getTriggerDelay();
			double pulseEndTime = triggerObjForPulse.getTriggerDelay() + triggerObjForPulse.getTriggerPulseLength();
			if (pulseEdgeTime2TriggerObj.containsKey(pulseStartTime)) {
				pulseEdgeTime2TriggerObj.get(pulseStartTime).add(triggerObjForPulse);
			} else {
				List<TriggerableObject> trigger = new ArrayList<TriggerableObject>();
				trigger.add(triggerObjForPulse);
				pulseEdgeTime2TriggerObj.put(pulseStartTime, trigger);
			}
			if (pulseEdgeTime2TriggerObj.containsKey(pulseEndTime)) {
				pulseEdgeTime2TriggerObj.get(pulseEndTime).add(triggerObjForPulse);
			} else {
				List<TriggerableObject> trigger = new ArrayList<TriggerableObject>();
				trigger.add(triggerObjForPulse);
				pulseEdgeTime2TriggerObj.put(pulseEndTime, trigger);
			}
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
		// (Frelon triggers on rising edge, Xh usually on falling edge)
		if (!triggerOnRisingEdge) {
			double triggerPulseLength = detectorDataCollection.getTriggerPulseLength();
			iTcollectionStartTime += triggerPulseLength;
			iTcollectionEndTime += triggerPulseLength;
		}

		double collectionDuration = detectorDataCollection.getCollectionDuration();
		int totalNumberOfFrames = getTotalNumberOfFrames();
		double singleFrameTime=collectionDuration/totalNumberOfFrames;

		double accumulationTime = 0.0;
		DetectorData detectorSettings = getDetector().getDetectorData();
		if ( detectorSettings instanceof FrelonCcdDetectorData ) {
			accumulationTime = ((FrelonCcdDetectorData)detectorSettings).getAccumulationMaximumExposureTime();
			// ExperimentUnit.MILLI_SEC.convertTo(accumulationTimeMilliSec, ExperimentUnit.SEC );
		}

		for(int i = 0; i<triggerParams.size(); i++ ) {
			double triggerTime = triggerParams.get(i).getTime();
			double timeInCollection = triggerTime - iTcollectionStartTime;
			int frameNumber = (int) Math.floor( timeInCollection/singleFrameTime );
			double frameStartTime =  iTcollectionStartTime+frameNumber*singleFrameTime;
			boolean insideDetectorAccumulation = true;

			if ( timeInCollection < TFG_TIME_RESOLUTION || timeInCollection > collectionDuration+TFG_TIME_RESOLUTION ) {

				insideDetectorAccumulation = false;
			}
			if ( frameNumber > totalNumberOfFrames ) {
				frameNumber = totalNumberOfFrames;
				frameStartTime = iTcollectionEndTime - singleFrameTime;
			}

			triggerParams.get(i).setAccumulationFrameNumber(frameNumber);
			triggerParams.get(i).setAccumulationFrameStartTime(frameStartTime);
			triggerParams.get(i).setAccumulationTime( accumulationTime );
			triggerParams.get(i).setAccumulationFrameLength( singleFrameTime );
			triggerParams.get(i).setTriggerIsDuringAccumulation( insideDetectorAccumulation );
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

		List<TriggerParams> triggerPoints = new ArrayList<TriggerParams>();
		if (sampleEnvironment.isEmpty() && !addDetectorTriggerToSampleEnvironment) {
			return triggerPoints;
		}

		List<TriggerableObject> newSampleEnvironment = new ArrayList<TriggerableObject>();
		for(int i = 0; i<sampleEnvironment.size(); i++ ) {
			newSampleEnvironment.add( sampleEnvironment.get(i) );
		}
		// Also add pulse to start detector to list of triggers
		if ( addDetectorTriggerToSampleEnvironment ) {
			newSampleEnvironment.add( detectorDataCollection );
		}

		TreeMap<Double, List<TriggerableObject>> pulseEdgeTime2TriggerObj = getMapPulseEdge2TriggerObj(newSampleEnvironment);

		if (pulseEdgeTime2TriggerObj.firstKey() > 0d) {
			//define the time zero trigger point - note this is not a trigger.
			triggerPoints.add(new TriggerParams(0.0d, 0, 0.0));
		}

		if( isTriggerPulseOverlapForTheSamePort(newSampleEnvironment) ) {
			//must not allow trigger pulse overlapping on the same output port
			throw new IllegalStateException("Signals on the same port are not allowed to overlap in time.");
		}

		// Array used to track on/off status of each port
		boolean [] activePortArray = new boolean[ TriggerOutputPort.getTotalNumPorts() ];
		Arrays.fill( activePortArray, false );

		// Get List of times of all pulse edges from map
		List<Double> edgeTimes = new ArrayList<Double>( pulseEdgeTime2TriggerObj.keySet() );
		int edgeCount = 0;

		// For each pulse edge there may be several TriggerableObjects. Create *one* entry in triggerPoints list
		// per edge, using live port corresponding to currently 'on' set of live ports.
		// On/off status of each port with time is tracked using array of bools (activePortArray)
		for (Map.Entry<Double, List<TriggerableObject>> entry : pulseEdgeTime2TriggerObj.entrySet()) {
			double currentEdgeTime = entry.getKey();

			for (TriggerableObject triggerObjForTime : entry.getValue()) {
				double pulseStartTime = triggerObjForTime.getTriggerDelay();
				double pulseLength = triggerObjForTime.getTriggerPulseLength();
				// if (currentEdgeTime == pulseStartTime) { // Not a good idea for floating point... imh 21/9/2015
				if ( Math.abs(currentEdgeTime-pulseStartTime) < TFG_TIME_RESOLUTION ) {
					// TriggerableObject corresponding to start of pulse (switch port on)
					TriggerOutputPort triggerOutputPort = triggerObjForTime.getTriggerOutputPort(); // i.e. USR_OUT_0, USR_OUT_1 etc.
					activePortArray[ triggerOutputPort.getUsrPortNumber() ] = true;
				} else {
					// TriggerableObject corresponding to end of pulse (switch port off)
					TriggerOutputPort triggerOutputPort = triggerObjForTime.getTriggerOutputPort();
					activePortArray[ triggerOutputPort.getUsrPortNumber() ] = false;
				}
			}

			// set active port bit field from array of active ports.
			int activePortBitfield = 0;
			for( int i = 0; i<activePortArray.length; i++) {
				if ( activePortArray[i] == true ) {
					activePortBitfield +=  Math.pow(2, i);
				}
			}

			// Framelength is time between current and next edge - this will be different to total pulse length
			// on a port if several pulses on different ports overlap in time.
			double frameLength = 0.0; // if on last edge, everything is switched off and length = 0
			if ( edgeCount < edgeTimes.size() - 1 ) {
				frameLength = edgeTimes.get( edgeCount+1 ) - edgeTimes.get( edgeCount );
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
							.filter(param -> param.isOverlap(pulseTime) && param.getPort() > 0)
							.findFirst()
							.isPresent();
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

	private boolean isTriggerPulseOverlapForTheSamePort( List<TriggerableObject> triggerableObjList ) {
		// Make list of triggerable objects for each output port
		TreeMap<TriggerOutputPort, List<TriggerableObject>> outputPort2TriggerObj = new TreeMap<TriggerOutputPort, List<TriggerableObject>>();
		for (TriggerableObject triggerObjForPulse : triggerableObjList) {
			TriggerOutputPort outputPort = triggerObjForPulse.getTriggerOutputPort();
			if (outputPort2TriggerObj.containsKey(outputPort)) {
				// add triggerable to list of for this port
				outputPort2TriggerObj.get(outputPort).add(triggerObjForPulse);
			} else {
				// make new list for port and add triggerable object to it
				List<TriggerableObject> trigger = new ArrayList<TriggerableObject>();
				trigger.add(triggerObjForPulse);
				outputPort2TriggerObj.put(outputPort, trigger);
			}
		}

		boolean overlapping=false;
		for (Map.Entry<TriggerOutputPort, List<TriggerableObject>> entry : outputPort2TriggerObj.entrySet()) {
			// TriggerOutputPort outputPort = entry.getKey();
			List<TriggerableObject> triggerObjList = entry.getValue();
			Collections.sort(triggerObjList);
			for (int i=0; i<triggerObjList.size()-1; i++) {
				TriggerableObject triggerableObject = triggerObjList.get(i);
				TriggerableObject nextTriggerableObject = triggerObjList.get(i+1);
				overlapping = overlapping || overlap(triggerableObject.getTriggerDelay(), triggerableObject.getTriggerDelay()+triggerableObject.getTriggerPulseLength(),
						nextTriggerableObject.getTriggerDelay(),nextTriggerableObject.getTriggerDelay()+nextTriggerableObject.getTriggerPulseLength());
				if (overlapping) {
					TriggerOutputPort outputPort = entry.getKey();
					logger.warn("Triggers at {} and {} are overlapping on port {}.",triggerableObject.getTriggerDelay(), nextTriggerableObject.getTriggerDelay(),outputPort.getPortName());
					break;
				}
			}
		}
		return overlapping;
	}

	private static boolean overlap(double min1, double max1, double min2, double max2) {
		double start = Math.max(min1,min2);
		double end = Math.min(max1,max2);
		double d = end - start + TFG_TIME_RESOLUTION; //ensure minimum pulse separation - TFG2 time resolution
		if (d < 0.0) {
			return false;
		}
		return true;
	}

	//renamed TriggerPair to TriggerParams. imh 17/9/2015
	private static class TriggerParams implements Comparable<TriggerParams>{
		private double time;
		private int port;
		private double length;

		private int accumulationFrameNumber;
		private double accumulationTime;
		private double accumulationFrameStartTime;
		private double accumulationFrameTotalLength;
		private boolean triggerIsDuringAccumulation;

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

		public int getAccumulationFrameNumber() {
			return accumulationFrameNumber;
		}

		public void setAccumulationFrameNumber(int accumulationFrameNumber) {
			this.accumulationFrameNumber = accumulationFrameNumber;
		}

		public void setAccumulationTime(double accumulationLength ) {
			accumulationTime = accumulationLength;
		}
		public double getAccumulationLength() {
			return accumulationTime;
		}

		public double getAccumulationFrameStartTime() {
			return accumulationFrameStartTime;
		}

		public void setAccumulationFrameStartTime(double accumulationFrameStartTime) {
			this.accumulationFrameStartTime = accumulationFrameStartTime;
		}

		public void setAccumulationFrameLength(double accumulationFrameTotalLength) {
			this.accumulationFrameTotalLength = accumulationFrameTotalLength;

		}

		public double getAccumulationFrameLength() {
			return accumulationFrameTotalLength;
		}

		public double getTimeRelativeToAccumulationFrameStart() {
			return time - accumulationFrameStartTime;
		}

		public int getAccumulationFramePart() {
			double relTime = getTimeRelativeToAccumulationFrameStart();
			if ( relTime > accumulationFrameTotalLength ) {
				relTime = 0;
			}
			double diff = relTime-accumulationTime;
			if ( relTime > accumulationTime + TFG_TIME_RESOLUTION ) { //  && Math.abs(relTime-accumulationTime) > TFG_TIME_RESOLUTION  ) {
				return 1;
			} else {
				return 0;
			}
		}
		public double getTimeRelativeToAccumulationEnd() {
			return time - (accumulationFrameStartTime+accumulationTime);
		}

		public double getTimeFromAccumulationEnd() {
			double timeToNext = getTimeRelativeToAccumulationEnd();
			if ( timeToNext < 0 )
			{
				timeToNext = getTimeRelativeToAccumulationFrameStart() + (accumulationFrameTotalLength-accumulationTime);
			}
			return timeToNext;
		}

		public boolean getTriggerIsDuringAccumulation() {
			return triggerIsDuringAccumulation;
		}

		public void setTriggerIsDuringAccumulation(boolean triggerIsDuringAccumulation) {
			this.triggerIsDuringAccumulation = triggerIsDuringAccumulation;
		}

		/**
		 * @param testTime
		 * @return true it testTime occurs within pulse start and pulse start + pulse length
		 */
		public boolean isOverlap(double testTime) {
			return testTime> time && testTime < time + length;
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
