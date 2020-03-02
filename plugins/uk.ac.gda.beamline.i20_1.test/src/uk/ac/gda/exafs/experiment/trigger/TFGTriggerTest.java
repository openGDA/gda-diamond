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

import static org.junit.Assert.assertEquals;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.apache.commons.math3.util.Pair;
import org.junit.Before;
import org.junit.Test;

import gda.device.detector.EdeDetector;
import gda.device.detector.frelon.EdeFrelon;
import gda.device.detector.frelon.FrelonCcdDetectorData;
import gda.device.detector.xstrip.XhDetector;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject.TriggerOutputPort;

public class TFGTriggerTest {

	private TFGTrigger tfgTrigger;
	private EdeDetector detector;

	private double collectionDuration = 0.50688;
	private double detectorTriggerPulseLength = 0.001;
	private double detectorTriggerStartTime = 0.1;
	private int numberOfFrames = 5;
	private int numberOfScansPerFrame = 66;

	@Before
	public void setup() {
		tfgTrigger = new TFGTrigger();
	}

	private void setupDetectorDataCollection() {
		// Set data collection duration, number of frames
		tfgTrigger.getDetectorDataCollection().setTriggerDelay(detectorTriggerStartTime); //start time
		tfgTrigger.getDetectorDataCollection().setTriggerPulseLength(detectorTriggerPulseLength);
		tfgTrigger.getDetectorDataCollection().setNumberOfFrames(numberOfFrames);
		tfgTrigger.getDetectorDataCollection().setCollectionDuration(collectionDuration);
		tfgTrigger.setUseCountFrameScalers(false);

		if (detector instanceof EdeFrelon) {
			EdeFrelon frelonDetector = (EdeFrelon) detector;
			FrelonCcdDetectorData detectorSettings = new FrelonCcdDetectorData();
			detectorSettings.setAccumulationMaximumExposureTime(0.001);
			frelonDetector.setDetectorData( detectorSettings );

		}
	}

	public void setupFrelon() {
		detector = new EdeFrelon();
		detector.setName("frelon");
		detector.setNumberScansInFrame( numberOfScansPerFrame ); //number of scans per frame of Frelon
		tfgTrigger.setDetector(detector);
		tfgTrigger.setTriggerOnRisingEdge(true);
	}

	public void setupXh() {
		detector = new XhDetector();
		detector.setName("xh");
		tfgTrigger.setDetector(detector);
		tfgTrigger.setTriggerOnRisingEdge(true);
	}

	@Test
	public void testNoPulses() {
		// Test TFG triggering commands produced for Frelon
		// No user-added pulses - i.e. trigger to start data collection trigger only.

		setupFrelon();

		// data collection duration, number of frames
		setupDetectorDataCollection();

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");

		compareCommands("tfg setup-groups\n"+
								"1 0.100000 0.0 0 0 0 0\n"+
								"1 0.001000 0.0 2 0 0 0\n"+
								"330 0 0.000001 0 0 0 9\n"+
								"1 0.000536 0.0 0 0 0 0\n"+
								"-1 0 0 0 0 0 0", command);

	}

	@Test
	public void testPulseOverlapCollectionStart() {
		// Test TFG triggering commands produced for Frelon
		// Pulse overlapping with collection start trigger. imh 21/9/2015

		setupFrelon();

		// data collection duration, number of frames
		setupDetectorDataCollection();

		DetectorDataCollection detDataCollection = 	tfgTrigger.getDetectorDataCollection();
		int totalNumFrames = detDataCollection.getNumberOfFrames()*tfgTrigger.getDetector().getNumberScansInFrame();
		double timePerFrame = detDataCollection.getCollectionDuration()/totalNumFrames;

		// Pulse begins just before data collection trigger, and overlaps the first two count signals
		TriggerableObject trigger1 = TriggerableObject.createNewSampleEnvEntry( 0.0995, 2*timePerFrame, TriggerOutputPort.USR_OUT_2 );

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");

		compareCommands("tfg setup-groups\n" +
						"1 0.099500 0.0 0 0 0 0\n" +
						"1 0.000500 0.0 4 0 0 0\n" +
						"1 0.001000 0.0 6 0 0 0\n" +
						"1 0.001572 0.0 4 0 0 0\n" +
						"328 0 0.000001 0 0 0 9\n" +
						"1 0.000536 0.0 0 0 0 0\n" +
						"-1 0 0 0 0 0 0", command);

	}

	@Test
	public void testPulsesDuringCollection() {
		// Test TFG triggering commands produced for Frelon
		// Long and short pulse during data collection. imh 21/9/2015

		setupFrelon();

		// data collection duration, number of frames
		setupDetectorDataCollection();

		DetectorDataCollection detDataCollection = 	tfgTrigger.getDetectorDataCollection();
		int totalNumFrames = detDataCollection.getNumberOfFrames()*tfgTrigger.getDetector().getNumberScansInFrame();
		double timePerFrame = detDataCollection.getCollectionDuration()/totalNumFrames;

		// Long and short pulse during data collection should be handled correctly.
		// The number of pulses not counted whilst long pulse is 'on' is now subtracted from total to count.
		// (time per frame of camera = 0.001536 secs)
		// 1st pulse begins after 0.1 + 0.01 + 130*frames0.001536 secs, and is 'on' for 6 frames
		TriggerableObject trigger1 = TriggerableObject.createNewSampleEnvEntry( 0.3, 0.010, TriggerOutputPort.USR_OUT_2 );
		// There are *58* frames (58*0.001536sec) between end of first and start of second pulse
		TriggerableObject trigger2 = TriggerableObject.createNewSampleEnvEntry( 0.4, 0.001, TriggerOutputPort.USR_OUT_2 ); // On for < 1 frame

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");

		compareCommands("tfg setup-groups\n"+
						"1 0.100000 0.0 0 0 0 0\n"+
						"1 0.001000 0.0 2 0 0 0\n"+
						"130 0 0.000001 0 0 0 9\n"+
						"1 0.000856 0.0 0 0 0 0\n"+
						"1 0.010000 0.0 4 0 0 0\n"+
						"58 0 0.000001 0 0 0 9\n"+
						"1 0.001016 0.0 0 0 0 0\n"+
						"1 0.001000 0.0 4 0 0 0\n"+
						"134 0 0.000001 0 0 0 9\n"+
						"1 0.000536 0.0 0 0 0 0\n"+
						"-1 0 0 0 0 0 0", command);

	}


	@Test
	public void testOverlappingPulsesDuringCollection() {
		// Test TFG triggering commands produced for Frelon
		// Overlapping pulses during data collection. imh 21/9/2015

		setupFrelon();

		// data collection duration, number of frames
		setupDetectorDataCollection();

		DetectorDataCollection detDataCollection = 	tfgTrigger.getDetectorDataCollection();
		int totalNumFrames = detDataCollection.getNumberOfFrames()*tfgTrigger.getDetector().getNumberScansInFrame();
		double timePerFrame = detDataCollection.getCollectionDuration()/totalNumFrames;

		// 1st pulse begins after 0.1 + 0.01 + 130*frames0.001536 secs, and is 'on' for 6 frames
		TriggerableObject trigger1 = TriggerableObject.createNewSampleEnvEntry( 0.300, 0.010, TriggerOutputPort.USR_OUT_2 );

		// 2nd pulse overlaps with first, extend beyond first by 3 frames (i.e. 330 - 130 - 9 = *191* frames left count after pulse)
		TriggerableObject trigger2 = TriggerableObject.createNewSampleEnvEntry( 0.305, 0.010, TriggerOutputPort.USR_OUT_3 );

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");

		compareCommands("tfg setup-groups\n"+
						"1 0.100000 0.0 0 0 0 0\n"+
						"1 0.001000 0.0 2 0 0 0\n"+
						"130 0 0.000001 0 0 0 9\n"+
						"1 0.000856 0.0 0 0 0 0\n"+
						"1 0.005000 0.0 4 0 0 0\n"+
						"1 0.005000 0.0 12 0 0 0\n"+
						"1 0.005000 0.0 8 0 0 0\n"+
						"190 0 0.000001 0 0 0 9\n"+
						"1 0.000536 0.0 0 0 0 0\n"+
						"-1 0 0 0 0 0 0", command);

	}

	@Test
	public void testLongPulseDuringCollection() {
		// Test TFG triggering commands produced for Frelon

		setupFrelon();

		// data collection duration, number of frames
		setupDetectorDataCollection();

		// Single long pulse during data collection (pulse length covers 6 accumulation signals of camera
		TriggerableObject trigger1 = TriggerableObject.createNewSampleEnvEntry( 0.3, 0.01, TriggerOutputPort.USR_OUT_2 ); // < covers 6 frames

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");

		compareCommands("tfg setup-groups\n"+
						"1 0.100000 0.0 0 0 0 0\n"+
						"1 0.001000 0.0 2 0 0 0\n"+
						"130 0 0.000001 0 0 0 9\n"+
						"1 0.000856 0.0 0 0 0 0\n"+
						"1 0.010000 0.0 4 0 0 0\n"+
						"193 0 0.000001 0 0 0 9\n"+
						"1 0.000536 0.0 0 0 0 0\n"+
						"-1 0 0 0 0 0 0", command);

	}


	@Test
	public void testPulseDuringCollectionTopupTriggeredStart() {
		// Test TFG triggering commands produced for Frelon

		setupFrelon();

		// data collection duration, number of frames
		setupDetectorDataCollection();

		TriggerableObject trigger1 = TriggerableObject.createNewSampleEnvEntry( 0.05, 0.01, TriggerOutputPort.USR_OUT_2 ); // Pulse on Port 2 before data collection
		TriggerableObject trigger2 = TriggerableObject.createNewSampleEnvEntry( 0.3, 0.01, TriggerOutputPort.USR_OUT_3 ); // Pulse on Port 3 during collection (covers 6 frames)

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, true); // start experiment from topup trigger
		System.out.print(command+"\n");

		compareCommands("tfg setup-groups\n" +
						"1 0.000001 0 0 0 40 0\n" +
						"1 0.050000 0.0 0 0 0 0\n" +
						"1 0.010000 0.0 4 0 0 0\n" +
						"1 0.040000 0.0 0 0 0 0\n" +
						"1 0.001000 0.0 2 0 0 0\n" +
						"130 0 0.000001 0 0 0 9\n" +
						"1 0.000856 0.0 0 0 0 0\n" +
						"1 0.010000 0.0 8 0 0 0\n" +
						"193 0 0.000001 0 0 0 9\n" +
						"1 0.000536 0.0 0 0 0 0\n" +
						"-1 0 0 0 0 0 0", command);

	}


	@Test
	public void test2PulsesBeforeCollection( ) {
		// Test TFG triggering commands produced for Frelon

		setupFrelon();

		// data collection duration, number of frames
		setupDetectorDataCollection();

		// Two pulses, both before data collection, with different starting time and lengths
		TriggerableObject trigger1 = TriggerableObject.createNewSampleEnvEntry( 0.02, 0.04, TriggerOutputPort.USR_OUT_2 );
		TriggerableObject trigger2 = TriggerableObject.createNewSampleEnvEntry( 0.04, 0.02, TriggerOutputPort.USR_OUT_3 );

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");

		compareCommands("tfg setup-groups\n"+
						"1 0.020000 0.0 0 0 0 0\n"+
						"1 0.020000 0.0 4 0 0 0\n"+
						"1 0.020000 0.0 12 0 0 0\n"+
						"1 0.040000 0.0 0 0 0 0\n"+
						"1 0.001000 0.0 2 0 0 0\n"+
						"330 0 0.000001 0 0 0 9\n"+
						"1 0.000536 0.0 0 0 0 0\n"+
						"-1 0 0 0 0 0 0", command);

	}


	@Test
	public void test2PulsesAfterCollection( ) {
		// Test TFG triggering commands produced for Frelon

		setupFrelon();

		// data collection duration, number of frames
		setupDetectorDataCollection();

		// Two pulses, both after data collection, with same starting time and different lengths
		TriggerableObject trigger1 = TriggerableObject.createNewSampleEnvEntry( 0.7, 0.10, TriggerOutputPort.USR_OUT_2 );
		TriggerableObject trigger2 = TriggerableObject.createNewSampleEnvEntry( 0.7, 0.05, TriggerOutputPort.USR_OUT_3 );

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");
		compareCommands("tfg setup-groups\n" +
							"1 0.100000 0.0 0 0 0 0\n" +
							"1 0.001000 0.0 2 0 0 0\n" +
							"330 0 0.000001 0 0 0 9\n" +
							"1 0.093656 0.0 0 0 0 0\n" +
							"1 0.050000 0.0 12 0 0 0\n" +
							"1 0.050000 0.0 4 0 0 0\n" +
							"-1 0 0 0 0 0 0", command);
	}


	@Test
	public void test3OverlappingPulses( ) {
		// Test TFG triggering commands produced for Frelon

		setupFrelon();

		// data collection duration, number of frames
		setupDetectorDataCollection();

		// 3 partially overlapping pulses, all after data collection
		TriggerableObject trigger1 = TriggerableObject.createNewSampleEnvEntry( 0.70, 0.10, TriggerOutputPort.USR_OUT_2 );
		TriggerableObject trigger2 = TriggerableObject.createNewSampleEnvEntry( 0.70, 0.05, TriggerOutputPort.USR_OUT_3 );
		TriggerableObject trigger3 = TriggerableObject.createNewSampleEnvEntry( 0.73, 0.10, TriggerOutputPort.USR_OUT_4 );


		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );
		triggerList.add( trigger3 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");
		compareCommands("tfg setup-groups\n"+
								"1 0.100000 0.0 0 0 0 0\n"+
								"1 0.001000 0.0 2 0 0 0\n"+
								"330 0 0.000001 0 0 0 9\n"+
								"1 0.093656 0.0 0 0 0 0\n"+
								"1 0.030000 0.0 12 0 0 0\n"+
								"1 0.020000 0.0 28 0 0 0\n"+
								"1 0.050000 0.0 20 0 0 0\n"+
								"1 0.030000 0.0 16 0 0 0\n"+
								"-1 0 0 0 0 0 0", command);

	}


	@Test
	public void test4OverlappingPulses( ) {
		// Test TFG triggering commands produced for Frelon

		setupFrelon();

		// data collection duration, number of frames
		setupDetectorDataCollection();

		// 3 partially overlapping pulses, all after data collection
		TriggerableObject trigger1 = TriggerableObject.createNewSampleEnvEntry( 0.70, 0.10, TriggerOutputPort.USR_OUT_2 );
		TriggerableObject trigger2 = TriggerableObject.createNewSampleEnvEntry( 0.72, 0.10, TriggerOutputPort.USR_OUT_3 );
		TriggerableObject trigger3 = TriggerableObject.createNewSampleEnvEntry( 0.74, 0.10, TriggerOutputPort.USR_OUT_4 );
		TriggerableObject trigger4 = TriggerableObject.createNewSampleEnvEntry( 0.76, 0.10, TriggerOutputPort.USR_OUT_5 );

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );
		triggerList.add( trigger3 );
		triggerList.add( trigger4 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");
		compareCommands("tfg setup-groups\n"+
						"1 0.100000 0.0 0 0 0 0\n"+
						"1 0.001000 0.0 2 0 0 0\n"+
						"330 0 0.000001 0 0 0 9\n"+
						"1 0.093656 0.0 0 0 0 0\n"+   // Wait here is : singleFrameTime + nextPoint.time - iTcollectionEndTime ends up at t=0.702536, NOT 0.7sec!
						"1 0.020000 0.0 4 0 0 0\n"+
						"1 0.020000 0.0 12 0 0 0\n"+
						"1 0.020000 0.0 28 0 0 0\n"+
						"1 0.040000 0.0 60 0 0 0\n"+
						"1 0.020000 0.0 56 0 0 0\n"+
						"1 0.020000 0.0 48 0 0 0\n"+
						"1 0.020000 0.0 32 0 0 0\n"+
						"-1 0 0 0 0 0 0", command);
	}

	@Test
	public void testXhNoPulses() throws Exception {

		setupXh();
		setupDetectorDataCollection();

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command);
		compareCommands("tfg setup-groups\n"+
				"1 0.100000 0.0 0 0 0 0\n"+
				"1 0.001000 0.0 2 0 0 0\n"+
				"4 0 0.000001 0 0 0 9\n"+
				"1 0.101376 0.0 0 0 0 0\n"+ // wait for final spectrum to finish
				"-1 0 0 0 0 0 0", command);
	}

	@Test
	public void testXhPulseOverlapCollectionStart() throws Exception {

		setupXh();
		setupDetectorDataCollection();

		// Pulse begins just before data collection trigger, and overlaps the first two spectra
		double timePerSpectrum = collectionDuration/numberOfFrames;
		TriggerableObject trigger1 = TriggerableObject.createNewSampleEnvEntry( 0.0995, 2*timePerSpectrum, TriggerOutputPort.USR_OUT_2 );

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command);
		compareCommands("tfg setup-groups\n"+
					"1 0.099500 0.0 0 0 0 0\n"+
					"1 0.000500 0.0 4 0 0 0\n"+
					"1 0.001000 0.0 6 0 0 0\n"+
					"1 0.201252 0.0 4 0 0 0\n"+
					"3 0 0.000001 0 0 0 9\n"+
					"1 0.101376 0.0 0 0 0 0\n"+
					"-1 0 0 0 0 0 0", command);
	}

	private List<Double> getArray(String values) {
		String[] splitString = values.split("\\s+");
		List<Double> splitStringValues = new ArrayList<>();
		for(String str : splitString) {
			splitStringValues.add(Double.parseDouble(str));
		}
		return splitStringValues;
	}

	private void compareCommands(String expected, String actual) {
		String[] exp = expected.split("\n");
		String[] act = actual.split("\n");
		assertEquals(exp.length, act.length);
		assertEquals(exp[0], act[0]); // first line is just text, so should match
		for(int i=1; i<exp.length; i++) {
			assertEquals("Line "+i+" of trigger command is incorrect", getArray(exp[i]), getArray(act[i]));
		}
	}

	@Test
	public void testXhPulsesDuringCollection() {

		collectionDuration = 0.5;
		numberOfFrames = 5;

		setupXh();
		setupDetectorDataCollection();

		// 1st pulse begins after 0.002 seconds after start of 3rd spectrum,
		TriggerableObject trigger1 = TriggerableObject.createNewSampleEnvEntry(0.302, 0.010, TriggerOutputPort.USR_OUT_2);

		// 1st pulse begins after 0.001 seconds after start of 4th spectrum,
		TriggerableObject trigger2 = TriggerableObject.createNewSampleEnvEntry(0.401, 0.010, TriggerOutputPort.USR_OUT_3);

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");
		compareCommands("tfg setup-groups\n"+
					"1 0.100 0.000000 0 0 0 0\n"+
					"1 0.001 0.000000 2 0 0 0\n"+
					"2 0.000 0.000001 0 0 0 9\n"+
					"1 0.002 0.000000 0 0 0 0\n"+
					"1 0.010 0.000000 4 0 0 0\n"+
					"1 0.000 0.000001 0 0 0 9\n"+
					"1 0.001 0.000000 0 0 0 0\n"+
					"1 0.010 0.000000 8 0 0 0\n"+
					"1 0.000 0.000001 0 0 0 9\n"+
					"1 0.100 0.000000 0 0 0 0\n"+
					"-1 0 0 0 0 0 0", command);

	}


	@Test
	public void testXhPulsesDuringCollection2() {

		collectionDuration = 0.5;
		numberOfFrames = 5;
		detectorTriggerStartTime = 0;

		setupXh();
		setupDetectorDataCollection();

		// 1st pulse begins after 0.05 seconds after start of 1st spectrum (i.e. start of data collection trigger),
		TriggerableObject trigger1 = TriggerableObject.createNewSampleEnvEntry(0.05, 0.001, TriggerOutputPort.USR_OUT_2);

		// 2nd pulse begins after 0.05 seconds after start of 2nd spectrum,
		TriggerableObject trigger2 = TriggerableObject.createNewSampleEnvEntry(0.15, 0.001, TriggerOutputPort.USR_OUT_2);
		// 3nd pulse starts same time as second, but is twice as long
		TriggerableObject trigger3 = TriggerableObject.createNewSampleEnvEntry(0.15, 0.002, TriggerOutputPort.USR_OUT_3);

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );
		triggerList.add( trigger3 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");
		compareCommands("tfg setup-groups\n"+
					"1 0.001 0.000000 2 0 0 0\n"+
					"1 0.049 0.000000 0 0 0 0\n"+
					"1 0.001 0.000000 4 0 0 0\n"+
					"1 0.000 0.000001 0 0 0 9\n"+
					"1 0.050 0.000000 0 0 0 0\n"+
					"1 0.001 0.000000 12 0 0 0\n"+
					"1 0.001 0.000000 8 0 0 0\n"+
					"3 0.000 0.000001 0 0 0 9\n"+
					"1 0.100 0.000000 0 0 0 0\n" +
					"-1 0 0 0 0 0 0", command);

	}

	@Test
	public void testScalerFramesNoTfgOutput() {
		setupFrelon();
		numberOfFrames = 100;

		setupDetectorDataCollection();

		Map<Integer, Pair<Integer, Integer>> scalerFramesForSpectra = tfgTrigger.getFramesForSpectra();
		for(int i=0; i<numberOfFrames; i++) {
			int firstFrame = numberOfScansPerFrame*i;
			assertEquals(scalerFramesForSpectra.get(i), Pair.create(firstFrame, firstFrame+numberOfScansPerFrame));
		}
	}

	@Test
	public void testScalerFramesHalfSpectrumOverlap() {
		setupFrelon();

		setupDetectorDataCollection();

		double timePerSpectrum = collectionDuration/numberOfFrames;
		double timePerAccumulation = timePerSpectrum/numberOfScansPerFrame;

		// Setup trigger to overlap with first 10 frames of 2nd spectrum
		double pulseStart = detectorTriggerStartTime+detectorTriggerPulseLength+timePerSpectrum;
		int numOverlapFrames = 10;
		TriggerableObject trigger1 = TriggerableObject.createNewSampleEnvEntry(pulseStart, timePerAccumulation*numOverlapFrames, TriggerOutputPort.USR_OUT_2);

		tfgTrigger.getSampleEnvironment().add(trigger1);

		Map<Integer, Pair<Integer, Integer>> scalerFramesForSpectra = tfgTrigger.getFramesForSpectra();
		assertEquals(Pair.create(0, numberOfScansPerFrame), scalerFramesForSpectra.get(0));

		// This spectrum should have full number of frames - 10
		int expectedLastScalerFrame = 2 * numberOfScansPerFrame - numOverlapFrames + 1;
		assertEquals(Pair.create(numberOfScansPerFrame, expectedLastScalerFrame), scalerFramesForSpectra.get(1));

		// The remaining spectra should all have full number of frames
		assertEquals(Pair.create(expectedLastScalerFrame, expectedLastScalerFrame+numberOfScansPerFrame), scalerFramesForSpectra.get(2));
		assertEquals(Pair.create(expectedLastScalerFrame+numberOfScansPerFrame,  expectedLastScalerFrame+2*numberOfScansPerFrame), scalerFramesForSpectra.get(3));
		assertEquals(Pair.create(expectedLastScalerFrame+numberOfScansPerFrame*2, expectedLastScalerFrame+numberOfScansPerFrame*3), scalerFramesForSpectra.get(4));
	}

	@Test
	public void testScalerFramesTwoHalfSpectrumOverlap() {
		setupFrelon();

		setupDetectorDataCollection();

		double timePerSpectrum = collectionDuration/numberOfFrames;
		double timePerAccumulation = timePerSpectrum/numberOfScansPerFrame;

		// Setup trigger to overlap with end of 2nd and start of 3rd spectrum
		int halfFrame = (int) (numberOfScansPerFrame*0.5);
		double pulseStart = detectorTriggerStartTime + detectorTriggerPulseLength + timePerSpectrum	+ timePerAccumulation * 33;
		int numOverlapFrames = numberOfScansPerFrame;
		TriggerableObject trigger1 = TriggerableObject.createNewSampleEnvEntry(pulseStart, timePerAccumulation*numOverlapFrames, TriggerOutputPort.USR_OUT_2);

		tfgTrigger.getSampleEnvironment().add(trigger1);

		Map<Integer, Pair<Integer, Integer>> scalerFramesForSpectra = tfgTrigger.getFramesForSpectra();
		assertEquals(Pair.create(0, numberOfScansPerFrame), scalerFramesForSpectra.get(0));

		// These two spectra should have half the frames due to overlap with Tfg output :
		int expectedLastScalerFrame = numberOfScansPerFrame + halfFrame + 1;
		assertEquals(Pair.create(numberOfScansPerFrame, expectedLastScalerFrame), scalerFramesForSpectra.get(1));
		assertEquals(Pair.create(expectedLastScalerFrame, expectedLastScalerFrame + halfFrame),	scalerFramesForSpectra.get(2));

		// Remaining spectra should have full number of frames :
		int fullFrameStart = expectedLastScalerFrame+halfFrame;
		assertEquals(Pair.create(fullFrameStart, fullFrameStart+numberOfScansPerFrame), scalerFramesForSpectra.get(3));
		assertEquals(Pair.create(fullFrameStart+numberOfScansPerFrame, fullFrameStart+2*numberOfScansPerFrame), scalerFramesForSpectra.get(4));
	}

	@Test
	public void testScalerFramesSeveralSpectrumOverlap() {
		setupFrelon();

		numberOfFrames = 1000;

		setupDetectorDataCollection();

		double timePerSpectrum = collectionDuration/numberOfFrames;
		double timePerAccumulation = timePerSpectrum/numberOfScansPerFrame;

		// Setup triggers to overlap with end of 2nd, all of 3rd and start of 4th spectrum
		int numOverlapFrames = 2*numberOfScansPerFrame;
		int halfFrame = (int) (numberOfScansPerFrame*0.5);
		double pulseStart = detectorTriggerStartTime+detectorTriggerPulseLength+timePerSpectrum + timePerAccumulation*halfFrame;
		double pulseLength = timePerAccumulation*(numOverlapFrames - 0.5); // extra half frame to avoid rounding error

		TriggerableObject trigger1 = TriggerableObject.createNewSampleEnvEntry(pulseStart, pulseLength, TriggerOutputPort.USR_OUT_2);

		tfgTrigger.getSampleEnvironment().add(trigger1);

		Map<Integer, Pair<Integer, Integer>> scalerFramesForSpectra = tfgTrigger.getFramesForSpectra();
		assertEquals(scalerFramesForSpectra.get(0), Pair.create(0, numberOfScansPerFrame));

		// This spectra should have half the frames due to overlap with Tfg output :
		int expectedLastScalerFrame = numberOfScansPerFrame + halfFrame + 1;
		assertEquals(Pair.create(numberOfScansPerFrame, expectedLastScalerFrame), scalerFramesForSpectra.get(1));
		// No frames for this one - overlapped completely by output signal
		assertEquals(Pair.create(expectedLastScalerFrame, expectedLastScalerFrame), scalerFramesForSpectra.get(2));
		// This should have half the frames
		assertEquals(Pair.create(expectedLastScalerFrame, expectedLastScalerFrame + halfFrame),	scalerFramesForSpectra.get(3));

		// Remaining spectra should have full number of frames :
		int fullFrameStart = expectedLastScalerFrame+halfFrame;
		assertEquals(Pair.create(fullFrameStart, fullFrameStart+numberOfScansPerFrame), scalerFramesForSpectra.get(4));
	}
}

