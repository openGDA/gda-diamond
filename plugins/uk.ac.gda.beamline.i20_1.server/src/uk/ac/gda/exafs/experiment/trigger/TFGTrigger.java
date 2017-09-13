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
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

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
		return getTfgSetupGroupsCommandParameters4Frelon_new(numberOfCycles, shouldStartOnTopupSignal);
	}

	public String getTfgSetupGrupsCommandParameters4XH(int numberOfCycles, boolean shouldStartOnTopupSignal) {
		// using TFG setup GUI for XH detector
		StringBuilder tfgCommand = new StringBuilder();
		List<TriggerParams> triggerPoints = processTimes(); //ensure there is at least one trigger point at time start point (0.0d,0,0)
		Collections.sort(triggerPoints);

		tfgCommand.append("tfg setup-groups");
		if (numberOfCycles > 1) {
			tfgCommand.append(" cycles ");
			tfgCommand.append(numberOfCycles);
		}
		tfgCommand.append("\n");
		if (shouldStartOnTopupSignal) {
			//ttl0 - TTL Trigger LEMO0 is used for waiting topup signal
			// tfgCommand.append(String.format("1 %f 0 0 0 8 0\n", MIN_DEAD_TIME));
			// trigger on falling edge of port 0 (OR with 32 for falling edge) = 8|32 = 40
			tfgCommand.append(String.format("1 %f 0 0 0 %d 0\n", MIN_DEAD_TIME, 40 ));
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
				TriggerParams thisPoint = triggerPoints.get(i);
				TriggerParams nextPoint = triggerPoints.get(i + 1);
				if (nextPoint.getTime() >= iTcollectionStartTime && nextPoint.getTime() < iTcollectionEndTime) {
					// external triggers fall inside data collection time - split frames collected in chunks between trigger points
					if (!beginningFramesAdded) {
						//wait frame before collection starts
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", (iTcollectionStartTime - thisPoint.getTime()), thisPoint.getPort()));
					}

					//sample environment trigger
					tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", thisPoint.getLength(), detectorDataCollection.getTriggerOutputPort().getUsrPort() + thisPoint.getPort()));

					int numberOfFramesBetweenAdjacentPoints=0;
					if (!beginningFramesAdded) {
						numberOfFramesBetweenAdjacentPoints=(int) ((nextPoint.getTime()-iTcollectionStartTime)/singleFrameTime);
					} else {
						numberOfFramesBetweenAdjacentPoints=(int) ((nextPoint.getTime()-thisPoint.getTime())/singleFrameTime);
					}
					if ((totalnumberFramesSoFar+numberOfFramesBetweenAdjacentPoints)<numberOfFrames) {
						tfgCommand.append(String.format("%d 0 %f 0 %d 0 9\n", numberOfFramesBetweenAdjacentPoints, MIN_LIVE_TIME, thisPoint.getPort())); // Review if this is dead or live port
					}
					totalnumberFramesSoFar += numberOfFramesBetweenAdjacentPoints;
					beginningFramesAdded=true;
					if (i+1==triggerPoints.size()-1) {
						//nextPoint is the last trigger point before iTCollectionEndTime
						if (totalnumberFramesSoFar<numberOfFrames) {
							//add last few frames in data acquisition before iTCollectionEndTime
							int numberOfFramesLeft = numberOfFrames-totalnumberFramesSoFar;
							tfgCommand.append(String.format("%d 0 %f 0 %d 0 9\n", numberOfFramesLeft, MIN_LIVE_TIME, thisPoint.getPort())); // Review if this is dead or live port
							totalnumberFramesSoFar += numberOfFramesLeft;
						}
						// at end of data collection, external TFG2 must wait for a single frame to allow detector collection to complete.
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", singleFrameTime, thisPoint.getPort()));
						itCollectionAdded=true;
					}
				} else if (nextPoint.getTime() >= iTcollectionEndTime  && !itCollectionAdded) {
					//external triggers at and after data collection end time
					if (beginningFramesAdded) {
						//finish what already started by previous trigger points
						if (totalnumberFramesSoFar<numberOfFrames) {
							//add last few frames in data acquisition before iTCollectionEndTime
							int numberOfFramesLeft = numberOfFrames-totalnumberFramesSoFar;
							tfgCommand.append(String.format("%d 0 %f 0 %d 0 9\n", numberOfFramesLeft, MIN_LIVE_TIME, thisPoint.getPort())); // Review if this is dead or live port
							totalnumberFramesSoFar += numberOfFramesLeft;
						}
					} else {
						//No external trigger falls inside data collection time
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", (iTcollectionStartTime - thisPoint.getTime()), thisPoint.getPort()));
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", detectorDataCollection.getTriggerPulseLength(), detectorDataCollection.getTriggerOutputPort().getUsrPort() + thisPoint.getPort()));
						tfgCommand.append(String.format("%d 0 %f 0 %d 0 9\n", detectorDataCollection.getNumberOfFrames(), MIN_LIVE_TIME, thisPoint.getPort())); // Review if this is dead or live port
					}
					if (nextPoint.getTime() == iTcollectionEndTime) {
						// at end of data collection wait for at least a single frame to allow detector collection to complete.
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", singleFrameTime, thisPoint.getPort()));
					} else {
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", singleFrameTime + nextPoint.getTime()	- iTcollectionEndTime, thisPoint.getPort())); // Review if this is dead or live port
					}
					itCollectionAdded = true;
				} else {
					//external triggers fall before data collection start time
					if (thisPoint.getTime() != iTcollectionStartTime && thisPoint.getTime() != iTcollectionEndTime) {
						tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", nextPoint.getTime() - thisPoint.getTime(), thisPoint.getPort()));
					}
				}
			}
		}
		if (!itCollectionAdded) {
			//No external trigger after data collection start time
			if (!triggerPoints.isEmpty()) {
				tfgCommand.append(String.format("1 %f 0.0 %d 0 0 0\n", (iTcollectionStartTime - triggerPoints.get(triggerPoints.size() -1).getTime()), 0));
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

	public String getTfgSetupGroupsCommandParameters4Frelon_new(int numberOfCycles, boolean shouldStartOnTopupSignal) {
		// using TFG setup GUI for Frelon - completely re-written version. imh 29Sept2015

		StringBuilder tfgCommand = new StringBuilder();
		List<TriggerParams> triggerPoints = processTimesFrelon( true ); // also includes trigger to start camera
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

		double iTcollectionEndTime = detectorDataCollection.getTotalDelay();
		double iTcollectionStartTime = detectorDataCollection.getTriggerDelay();
		double collectionDuration = detectorDataCollection.getCollectionDuration();

		int totalNumberOfFrames = getTotalNumberOfFrames();
		double singleFrameLength=collectionDuration/totalNumberOfFrames;
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

	public String getTfgSetupGroupsCommandParameters4Frelon(int numberOfCycles, boolean shouldStartOnTopupSignal) {
		// using TFG setup GUI for XH detector
		StringBuilder tfgCommand = new StringBuilder();
		List<TriggerParams> triggerPoints = processTimesFrelon( true ); // also includes trigger to start camera
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
		//		double timePerSpectrum = collectionDuration/(detectorDataCollection.getNumberOfFrames()-1);
		//		iTcollectionEndTime += timePerSpectrum;
		//		collectionDuration += timePerSpectrum;

		int totalNumberOfFrames = detectorDataCollection.getNumberOfFrames()*getDetector().getNumberScansInFrame();
		double singleFrameLength=collectionDuration/totalNumberOfFrames;
		boolean itCollectionAdded = false;
		boolean beginningFramesAdded=false;
		int totalnumberFramesSoFar=0;


		boolean adjustToExactStartTime = false;
		int numberOfCollectionFramesToNotCount = 0;
		double currentAbsoluteTime = 0.0;

		// Set accumulation and accumulation readout time (per frame) .
		// (Total frame time = accumulation time + accumulation readout time)
		double accumulationTime = singleFrameLength;
		FrelonCcdDetectorData detectorSettings = (FrelonCcdDetectorData) getDetector().getDetectorData();
		if ( detectorSettings != null ) {
			accumulationTime = detectorSettings.getAccumulationMaximumExposureTime();
			// ExperimentUnit.MILLI_SEC.convertTo(accumulationTimeMilliSec, ExperimentUnit.SEC );
		}
		double accumulationReadoutTime = singleFrameLength - accumulationTime;


		// NBCounting current occurs on rising edge of accumulation readout signal; middle of frame

		for (int i = 0; i < triggerPoints.size()-1; i++) {
			TriggerParams thisPoint = triggerPoints.get(i);
			TriggerParams nextPoint = triggerPoints.get(i + 1);

			if ( thisPoint.getTime() <= iTcollectionStartTime )	{
				// Triggerpoints before data collection ...
				tfgCommand.append( getWaitForTimeString(thisPoint.getLength(), thisPoint.getPort() ) );
				currentAbsoluteTime += thisPoint.getLength();
			} else if (thisPoint.getTime() > iTcollectionStartTime &&
					thisPoint.getTime() < iTcollectionEndTime) {

				//Triggerpoints during data collection ...

				// Number of 'count' signals that occur between next 2 triggerpoints
				int numberCountSignalsBetweenAdjacentPoints = nextPoint.getAccumulationFrameNumber()-thisPoint.getAccumulationFrameNumber();
				if ( thisPoint.getAccumulationFramePart()>0 ) { // start triggerpoint happens *after* count signal
					numberCountSignalsBetweenAdjacentPoints--;
				}
				if ( nextPoint.getAccumulationFramePart()>0 ) { // end triggerpoint *after* count
					numberCountSignalsBetweenAdjacentPoints++;
				}

				// Determine number of frames to count, so that next trigger starts at correct time
				boolean countFrames = false;
				if ((totalnumberFramesSoFar+numberCountSignalsBetweenAdjacentPoints)<=totalNumberOfFrames
						&& numberCountSignalsBetweenAdjacentPoints>0 ) {
					// 'count' frames at beginning of data accumulation (to get to start of first pulse) ,
					// and also in for *gaps between pulses* within data accumulation.
					if ( !beginningFramesAdded || thisPoint.getPort() == 0 ) {
						countFrames = true;
					}
				}

				if ( countFrames ) {
					tfgCommand.append( getCountFrameString(numberCountSignalsBetweenAdjacentPoints, 0 ) );
				}

				// Only do this if there is port output (i.e. since port=0 means wait, which now corresponds to count frames
				if ( thisPoint.getPort() != 0 ) {
					//add extra wait to get trigger to start at exact user specified time within data collection

					double timeToNextPulse = nextPoint.getTimeFromAccumulationEnd();
					if ( adjustToExactStartTime && timeToNextPulse > 0 ) {
						tfgCommand.append( getWaitForTimeString(timeToNextPulse, 0) );
					}

					tfgCommand.append( getWaitForTimeString(thisPoint.getLength(), thisPoint.getPort()) );
					double pulseOverlapStart = Math.max( thisPoint.getTime(), iTcollectionStartTime );
					double pulseOverlapEnd = Math.min( thisPoint.getTime() + thisPoint.getLength() , iTcollectionEndTime );
					numberOfCollectionFramesToNotCount += (pulseOverlapEnd - pulseOverlapStart)/singleFrameLength;
					currentAbsoluteTime += timeToNextPulse + thisPoint.getLength();
				}
				totalnumberFramesSoFar += numberCountSignalsBetweenAdjacentPoints;
				beginningFramesAdded=true;
			} else if (thisPoint.getTime() > iTcollectionEndTime ) {
				// External triggers after data collection end time ...
				if (beginningFramesAdded && !itCollectionAdded ) {
					// For first trigger point after data collection...
					// Count any leftover frames not already counted from data collection
					int numberOfFramesLeft = totalNumberOfFrames-totalnumberFramesSoFar;
					numberOfFramesLeft -= numberOfCollectionFramesToNotCount;
					if ( numberOfFramesLeft > 0 ) {
						tfgCommand.append( getCountFrameString(numberOfFramesLeft, 0) );
						tfgCommand.append( getWaitForTimeString(accumulationReadoutTime, 0) );
						currentAbsoluteTime += numberOfFramesLeft*singleFrameLength;
					}
					// Place gap between end of data collection so trigger starts at correct time
					// Port of last trigger point
					int lastTriggerPort = triggerPoints.get(i-1).getPort();
					// double waitTime = thisPoint.getTime() - (iTcollectionEndTime + accumulationReadoutTime);
					double waitTime = thisPoint.getTime() - currentAbsoluteTime;
					if ( waitTime > 0 ) {
						tfgCommand.append( getWaitForTimeString(waitTime, lastTriggerPort ) );
					}
					totalnumberFramesSoFar += numberOfFramesLeft;
				}
				tfgCommand.append( getWaitForTimeString(thisPoint.getLength(), thisPoint.getPort() ) );
				itCollectionAdded = true;
			}

			// On last iteration, process final trigger point
			if (i==triggerPoints.size()-2) {
				//if nextPoint is the last trigger point before iTCollectionEndTime
				int numberOfFramesLeft = totalNumberOfFrames-totalnumberFramesSoFar;
				numberOfFramesLeft -= numberOfCollectionFramesToNotCount;
				if ( numberOfFramesLeft>0 ) {
					//add last few frames in data acquisition before iTCollectionEndTime

					// tfgCommand.append(String.format("%d 0 %f 0 0 0 9\n", numberOfFramesLeft, MIN_LIVE_TIME)); // Review if this is dead or live port
					tfgCommand.append( getCountFrameString(numberOfFramesLeft, 0) );
					tfgCommand.append( getWaitForTimeString(accumulationReadoutTime, 0) );
					totalnumberFramesSoFar += numberOfFramesLeft;
				}

				itCollectionAdded=true;
			}
		}

		// Add data collection, after adding all trigger points
		if (!itCollectionAdded) {
			//tfgCommand.append(String.format("%d 0 %f 0 0 0 9\n", detectorDataCollection.getNumberOfFrames()*getDetector().getNumberScansInFrame(), MIN_LIVE_TIME, detectorDataCollection.getTriggerOutputPort().getUsrPort())); // Review if this is dead or live port
			tfgCommand.append( getCountFrameString(totalNumberOfFrames, 0) );

			// at end of data collection external TFG2 must wait for a single accumulation readout to allow detector collection to complete.
			tfgCommand.append( getWaitForTimeString(accumulationReadoutTime, 0) );
		}
		tfgCommand.append("-1 0 0 0 0 0 0");
		//		String tfgCommand=InterfaceProvider.getCommandRunner().evaluateCommand("getCommands4ExternalTFG()");
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
	 * Set list of trigger parameters for Frelon. Derived from processTimes function (originally written for XH).
	 * Works correctly for multiple overlapping pulses on different ports.
	 * @since 18/9/2015
	 * @param addDetectorTriggerToSampleEnvironment
	 * @return
	 */
	private List<TriggerParams> processTimesFrelon( boolean addDetectorTriggerToSampleEnvironment ) {

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

	private List<TriggerParams> processTimes() {
		TreeMap<Double, List<TriggerableObject>> pulseEdgeTime2TriggerObj = new TreeMap<Double, List<TriggerableObject>>();
		List<TriggerParams> triggerPoints = new ArrayList<TriggerParams>();
		if (sampleEnvironment.isEmpty()) {
			return triggerPoints;
		}

		// Make map of pulse edge times and list of triggerable objects that start/end at those times
		// (TreeMap automatically sorts into ascending key order).
		for (TriggerableObject triggerObjForPulse : sampleEnvironment) {
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

		if (pulseEdgeTime2TriggerObj.firstKey() > 0d) {
			//define the time zero trigger point - note this is not a trigger.
			triggerPoints.add(new TriggerParams(0.0d, 0, 0.0));
		}

		if(isTriggerPulseOverlapForTheSamePort(sampleEnvironment)) {
			//must not allow trigger pulse overlapping on the same output port
			throw new IllegalStateException("Signals on the same port are not allowed to overlap in time.");
		}


		// Map from TriggerOutputPort (USR_OUT_0, USR_OUT_1, etc) to port on/off status
		HashMap<TriggerOutputPort, Integer> outputPort2LivePortIndex = new HashMap<TriggerOutputPort, Integer>();
		// double currentTime=0.0;

		int currentLivePort = 0;
		for (Map.Entry<Double, List<TriggerableObject>> entry : pulseEdgeTime2TriggerObj.entrySet()) {
			double currentEdgeTime = entry.getKey();

			// For each pulse edge there may be several TriggerableObjects. But should only create *one* entry in triggerPoints list
			// per edge, using live port corresponding to currently 'on' set of live ports.
			// Current implementation adds 1 entry in list per port pulse edge, last entry per time has merged active port number.
			// imh 17/9/2015

			for (TriggerableObject triggerObjForTime : entry.getValue()) {
				double pulseStartTime = triggerObjForTime.getTriggerDelay();
				double pulseLength = triggerObjForTime.getTriggerPulseLength();
				if (currentEdgeTime == pulseStartTime) {
					// TriggerableObject corresponding to start of pulse (switch port on)
					TriggerOutputPort triggerOutputPort = triggerObjForTime.getTriggerOutputPort(); // i.e. USR_OUT_0, USR_OUT_1 etc.
					if (outputPort2LivePortIndex.containsKey(triggerOutputPort)) {
						// port already on?
						currentLivePort = outputPort2LivePortIndex.get(triggerOutputPort);
					} else {
						// add new port to current set of live ports
						currentLivePort += triggerObjForTime.getTriggerOutputPort().getUsrPort();
						outputPort2LivePortIndex.put(triggerOutputPort, currentLivePort);
					}
					triggerPoints.add(new TriggerParams(currentEdgeTime, currentLivePort, pulseLength));
				} else {
					// TriggerableObject corresponding to end of pulse (switch port off)
					TriggerOutputPort triggerOutputPort = triggerObjForTime.getTriggerOutputPort();

					if (outputPort2LivePortIndex.containsKey(triggerOutputPort)) {
						// remove port from current 'set' of live ports (should be XORed not subtracted?)
						currentLivePort = outputPort2LivePortIndex.get(triggerOutputPort);
						currentLivePort -= triggerObjForTime.getTriggerOutputPort().getUsrPort();
						outputPort2LivePortIndex.remove(triggerOutputPort);
					} else {
						logger.error("Cannot find {} for the end pulse {}.",triggerOutputPort.getPortName(), pulseStartTime+triggerObjForTime.getTriggerPulseLength());
					}
					triggerPoints.add(new TriggerParams(currentEdgeTime, currentLivePort, 0.0));
				}
			}
		}
		return triggerPoints;
	}

	private boolean isTriggerPulseOverlapForTheSamePort( List<TriggerableObject> triggerableObjList ) {
		// boolean overlapping=false;
		// TreeMap<TriggerOutputPort, List<TriggerableObject>> triggerTimesAndSamEnv = new TreeMap<TriggerOutputPort, List<TriggerableObject>>();

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
	private boolean overlap(double min1, double max1, double min2, double max2) {
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
