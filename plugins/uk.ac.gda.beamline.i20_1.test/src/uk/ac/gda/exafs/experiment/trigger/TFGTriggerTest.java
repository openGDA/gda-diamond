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

import static org.junit.Assert.assertTrue;

import java.util.List;

import gda.device.detector.EdeDetector;
import gda.device.detector.frelon.EdeFrelon;
import gda.device.detector.frelon.FrelonCcdDetectorData;
import gda.device.detector.xstrip.XhDetector;

import org.junit.Ignore;
import org.junit.Test;

import uk.ac.gda.exafs.experiment.trigger.TriggerableObject.TriggerOutputPort;

public class TFGTriggerTest {

	private void setupDetectorDataCollection( TFGTrigger tfgTrigger ) {
		// Set data collection duration, number of frames
		tfgTrigger.getDetectorDataCollection().setTriggerDelay(0.1); //start time
		tfgTrigger.getDetectorDataCollection().setTriggerPulseLength(0.001);
		tfgTrigger.getDetectorDataCollection().setNumberOfFrames(5);
		tfgTrigger.getDetectorDataCollection().setCollectionDuration(0.50688);

		EdeFrelon frelonDetector = (EdeFrelon) tfgTrigger.getDetector();
		FrelonCcdDetectorData detectorSettings = new FrelonCcdDetectorData();
		detectorSettings.setAccumulationMaximumExposureTime(0.001);
		frelonDetector.setDetectorData( detectorSettings );
	}

	@Test
	public void testNoPulses() {
		// Test TFG triggering commands produced for Frelon
		// No user-added pulses - i.e. trigger to start data collection trigger only.

		TFGTrigger tfgTrigger = new TFGTrigger();
		EdeDetector detector = new EdeFrelon();
		tfgTrigger.setDetector(detector);
		detector.setName("frelon");

		detector.setNumberScansInFrame( 66 ); //number of scans per frame of Frelon

		// data collection duration, number of frames
		setupDetectorDataCollection(tfgTrigger);

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");

		assertTrue("TFGTrigger testPulseOverlapCollectionStart - single 2 frame long pulse overlapping with collection start",
				command.equals("tfg setup-groups\n"+
								"1 0.100000 0.0 0 0 0 0\n"+
								"1 0.001000 0.0 2 0 0 0\n"+
								"330 0 0.000001 0 0 0 9\n"+
								"1 0.000536 0.0 0 0 0 0\n"+
								"-1 0 0 0 0 0 0") );

	}

	@Test
	public void testPulseOverlapCollectionStart() {
		// Test TFG triggering commands produced for Frelon
		// Pulse overlapping with collection start trigger. imh 21/9/2015

		TFGTrigger tfgTrigger = new TFGTrigger();
		EdeDetector detector = new EdeFrelon();
		tfgTrigger.setDetector(detector);
		detector.setName("frelon");

		detector.setNumberScansInFrame( 66 ); //number of scans per frame of Frelon

		// data collection duration, number of frames
		setupDetectorDataCollection(tfgTrigger);

		DetectorDataCollection detDataCollection = 	tfgTrigger.getDetectorDataCollection();
		int totalNumFrames = detDataCollection.getNumberOfFrames()*tfgTrigger.getDetector().getNumberScansInFrame();
		double timePerFrame = detDataCollection.getCollectionDuration()/totalNumFrames;

		// Pulse begins just before data collection trigger, and overlaps the first two count signals
		TriggerableObject trigger1 = tfgTrigger.createNewSampleEnvEntry( 0.0995, 2*timePerFrame, TriggerOutputPort.USR_OUT_2 );

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");

		assertTrue("TFGTrigger testPulseOverlapCollectionStart - single 2 frame long pulse overlapping with collection start",
				command.equals("tfg setup-groups\n" +
						"1 0.099500 0.0 0 0 0 0\n" +
						"1 0.000500 0.0 4 0 0 0\n" +
						"1 0.001000 0.0 6 0 0 0\n" +
						"1 0.001572 0.0 4 0 0 0\n" +
						"328 0 0.000001 0 0 0 9\n" +
						"1 0.000536 0.0 0 0 0 0\n" +
						"-1 0 0 0 0 0 0") );

	}

	@Test
	public void testPulsesDuringCollection() {
		// Test TFG triggering commands produced for Frelon
		// Long and short pulse during data collection. imh 21/9/2015

		TFGTrigger tfgTrigger = new TFGTrigger();
		EdeDetector detector = new EdeFrelon();
		tfgTrigger.setDetector(detector);
		detector.setName("frelon");

		detector.setNumberScansInFrame( 66 ); //number of scans per frame of Frelon

		// data collection duration, number of frames
		setupDetectorDataCollection(tfgTrigger);

		DetectorDataCollection detDataCollection = 	tfgTrigger.getDetectorDataCollection();
		int totalNumFrames = detDataCollection.getNumberOfFrames()*tfgTrigger.getDetector().getNumberScansInFrame();
		double timePerFrame = detDataCollection.getCollectionDuration()/totalNumFrames;

		// Long and short pulse during data collection should be handled correctly.
		// The number of pulses not counted whilst long pulse is 'on' is now subtracted from total to count.
		// (time per frame of camera = 0.001536 secs)
		// 1st pulse begins after 0.1 + 0.01 + 130*frames0.001536 secs, and is 'on' for 6 frames
		TriggerableObject trigger1 = tfgTrigger.createNewSampleEnvEntry( 0.3, 0.010, TriggerOutputPort.USR_OUT_2 );
		// There are *58* frames (58*0.001536sec) between end of first and start of second pulse
		TriggerableObject trigger2 = tfgTrigger.createNewSampleEnvEntry( 0.4, 0.001, TriggerOutputPort.USR_OUT_2 ); // On for < 1 frame

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");

		assertTrue("TFGTrigger testPulsesDuringCollection - two pulses (long and short) during data collection",
				command.equals("tfg setup-groups\n"+
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
						"-1 0 0 0 0 0 0") );

	}


	@Test
	public void testOverlappingPulsesDuringCollection() {
		// Test TFG triggering commands produced for Frelon
		// Overlapping pulses during data collection. imh 21/9/2015

		TFGTrigger tfgTrigger = new TFGTrigger();
		EdeDetector detector = new EdeFrelon();
		tfgTrigger.setDetector(detector);
		detector.setName("frelon");

		detector.setNumberScansInFrame( 66 ); //number of scans per frame of Frelon

		// data collection duration, number of frames
		setupDetectorDataCollection(tfgTrigger);

		DetectorDataCollection detDataCollection = 	tfgTrigger.getDetectorDataCollection();
		int totalNumFrames = detDataCollection.getNumberOfFrames()*tfgTrigger.getDetector().getNumberScansInFrame();
		double timePerFrame = detDataCollection.getCollectionDuration()/totalNumFrames;

		// 1st pulse begins after 0.1 + 0.01 + 130*frames0.001536 secs, and is 'on' for 6 frames
		TriggerableObject trigger1 = tfgTrigger.createNewSampleEnvEntry( 0.300, 0.010, TriggerOutputPort.USR_OUT_2 );

		// 2nd pulse overlaps with first, extend beyond first by 3 frames (i.e. 330 - 130 - 9 = *191* frames left count after pulse)
		TriggerableObject trigger2 = tfgTrigger.createNewSampleEnvEntry( 0.305, 0.010, TriggerOutputPort.USR_OUT_3 );

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");

		assertTrue("TFGTrigger testOverlappingPulsesDuringCollection - 2 overlapping pulses (6 frames long each) during data collection",
				command.equals("tfg setup-groups\n"+
						"1 0.100000 0.0 0 0 0 0\n"+
						"1 0.001000 0.0 2 0 0 0\n"+
						"130 0 0.000001 0 0 0 9\n"+
						"1 0.000856 0.0 0 0 0 0\n"+
						"1 0.005000 0.0 4 0 0 0\n"+
						"1 0.005000 0.0 12 0 0 0\n"+
						"1 0.005000 0.0 8 0 0 0\n"+
						"190 0 0.000001 0 0 0 9\n"+
						"1 0.000536 0.0 0 0 0 0\n"+
						"-1 0 0 0 0 0 0") );

	}

	@Test
	public void testLongPulseDuringCollection() {
		// Test TFG triggering commands produced for Frelon

		TFGTrigger tfgTrigger = new TFGTrigger();
		EdeDetector detector = new EdeFrelon();
		tfgTrigger.setDetector(detector);
		detector.setName("frelon");

		detector.setNumberScansInFrame( 66 ); //number of scans per frame of Frelon

		// data collection duration, number of frames
		setupDetectorDataCollection(tfgTrigger);

		// Single long pulse during data collection (pulse length covers 6 accumulation signals of camera
		TriggerableObject trigger1 = tfgTrigger.createNewSampleEnvEntry( 0.3, 0.01, TriggerOutputPort.USR_OUT_2 ); // < covers 6 frames

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");

		assertTrue("TFGTrigger testLongPulseDuringCollection - single long (6 frame) pulse during data collection",
				command.equals("tfg setup-groups\n"+
						"1 0.100000 0.0 0 0 0 0\n"+
						"1 0.001000 0.0 2 0 0 0\n"+
						"130 0 0.000001 0 0 0 9\n"+
						"1 0.000856 0.0 0 0 0 0\n"+
						"1 0.010000 0.0 4 0 0 0\n"+
						"193 0 0.000001 0 0 0 9\n"+
						"1 0.000536 0.0 0 0 0 0\n"+
						"-1 0 0 0 0 0 0") );

	}


	@Test
	public void testPulseDuringCollectionTopupTriggeredStart() {
		// Test TFG triggering commands produced for Frelon

		TFGTrigger tfgTrigger = new TFGTrigger();
		EdeDetector detector = new EdeFrelon();
		tfgTrigger.setDetector(detector);
		detector.setName("frelon");

		detector.setNumberScansInFrame( 66 ); //number of scans per frame of Frelon

		// data collection duration, number of frames
		setupDetectorDataCollection(tfgTrigger);

		TriggerableObject trigger1 = tfgTrigger.createNewSampleEnvEntry( 0.05, 0.01, TriggerOutputPort.USR_OUT_2 ); // Pulse on Port 2 before data collection
		TriggerableObject trigger2 = tfgTrigger.createNewSampleEnvEntry( 0.3, 0.01, TriggerOutputPort.USR_OUT_3 ); // Pulse on Port 3 during collection (covers 6 frames)

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, true); // start experiment from topup trigger
		System.out.print(command+"\n");

		assertTrue("TFGTrigger testPulseDuringCollectionTopupTriggeredStart - topup trigger start, with pulse before and during (6 frame long) data collection",
				command.equals("tfg setup-groups\n" +
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
						"-1 0 0 0 0 0 0") );

	}


	@Test
	public void test2PulsesBeforeCollection( ) {
		// Test TFG triggering commands produced for Frelon

		TFGTrigger tfgTrigger = new TFGTrigger();
		EdeDetector detector = new EdeFrelon();
		tfgTrigger.setDetector(detector);
		detector.setName("frelon");

		detector.setNumberScansInFrame( 66 ); //number of scans per frame of Frelon

		// data collection duration, number of frames
		setupDetectorDataCollection(tfgTrigger);

		// Two pulses, both before data collection, with different starting time and lengths
		TriggerableObject trigger1 = tfgTrigger.createNewSampleEnvEntry( 0.02, 0.04, TriggerOutputPort.USR_OUT_2 );
		TriggerableObject trigger2 = tfgTrigger.createNewSampleEnvEntry( 0.04, 0.02, TriggerOutputPort.USR_OUT_3 );

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");

		assertTrue("TFGTrigger test2PulsesBeforeCollection - 2 pulses before data collection (different start, same end)",
				command.equals(	"tfg setup-groups\n"+
						"1 0.020000 0.0 0 0 0 0\n"+
						"1 0.020000 0.0 4 0 0 0\n"+
						"1 0.020000 0.0 12 0 0 0\n"+
						"1 0.040000 0.0 0 0 0 0\n"+
						"1 0.001000 0.0 2 0 0 0\n"+
						"330 0 0.000001 0 0 0 9\n"+
						"1 0.000536 0.0 0 0 0 0\n"+
						"-1 0 0 0 0 0 0") );

	}


	@Test
	public void test2PulsesAfterCollection( ) {
		// Test TFG triggering commands produced for Frelon

		TFGTrigger tfgTrigger = new TFGTrigger();
		EdeDetector detector = new EdeFrelon();
		tfgTrigger.setDetector(detector);
		detector.setName("frelon");

		detector.setNumberScansInFrame( 66 ); //number of scans per frame of Frelon

		// data collection duration, number of frames
		setupDetectorDataCollection(tfgTrigger);

		// Two pulses, both after data collection, with same starting time and different lengths
		TriggerableObject trigger1 = tfgTrigger.createNewSampleEnvEntry( 0.7, 0.10, TriggerOutputPort.USR_OUT_2 );
		TriggerableObject trigger2 = tfgTrigger.createNewSampleEnvEntry( 0.7, 0.05, TriggerOutputPort.USR_OUT_3 );

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");
		assertTrue("TFGTrigger test2PulsesAfterCollection - 2 pulses after data collection (same start, different lengths)",
				command.equals("tfg setup-groups\n" +
							"1 0.100000 0.0 0 0 0 0\n" +
							"1 0.001000 0.0 2 0 0 0\n" +
							"330 0 0.000001 0 0 0 9\n" +
							"1 0.093656 0.0 0 0 0 0\n" +
							"1 0.050000 0.0 12 0 0 0\n" +
							"1 0.050000 0.0 4 0 0 0\n" +
							"-1 0 0 0 0 0 0") );
	}


	@Test
	public void test3OverlappingPulses( ) {
		// Test TFG triggering commands produced for Frelon

		TFGTrigger tfgTrigger = new TFGTrigger();
		EdeDetector detector = new EdeFrelon();
		tfgTrigger.setDetector(detector);
		detector.setName("frelon");

		detector.setNumberScansInFrame( 66 ); //number of scans per frame of Frelon

		// data collection duration, number of frames
		setupDetectorDataCollection(tfgTrigger);

		// 3 partially overlapping pulses, all after data collection
		TriggerableObject trigger1 = tfgTrigger.createNewSampleEnvEntry( 0.70, 0.10, TriggerOutputPort.USR_OUT_2 );
		TriggerableObject trigger2 = tfgTrigger.createNewSampleEnvEntry( 0.70, 0.05, TriggerOutputPort.USR_OUT_3 );
		TriggerableObject trigger3 = tfgTrigger.createNewSampleEnvEntry( 0.73, 0.10, TriggerOutputPort.USR_OUT_4 );


		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );
		triggerList.add( trigger3 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");
		assertTrue("TFGTrigger test3OverlappingPulses - 3 partially overlapping pulses after data collection",
				command.equals("tfg setup-groups\n"+
								"1 0.100000 0.0 0 0 0 0\n"+
								"1 0.001000 0.0 2 0 0 0\n"+
								"330 0 0.000001 0 0 0 9\n"+
								"1 0.093656 0.0 0 0 0 0\n"+
								"1 0.030000 0.0 12 0 0 0\n"+
								"1 0.020000 0.0 28 0 0 0\n"+
								"1 0.050000 0.0 20 0 0 0\n"+
								"1 0.030000 0.0 16 0 0 0\n"+
								"-1 0 0 0 0 0 0") );

	}


	@Test
	public void test4OverlappingPulses( ) {
		// Test TFG triggering commands produced for Frelon

		TFGTrigger tfgTrigger = new TFGTrigger();
		EdeDetector detector = new EdeFrelon();
		tfgTrigger.setDetector(detector);
		detector.setName("frelon");

		detector.setNumberScansInFrame( 66 ); //number of scans per frame of Frelon

		// data collection duration, number of frames
		setupDetectorDataCollection(tfgTrigger);

		// 3 partially overlapping pulses, all after data collection
		TriggerableObject trigger1 = tfgTrigger.createNewSampleEnvEntry( 0.70, 0.10, TriggerOutputPort.USR_OUT_2 );
		TriggerableObject trigger2 = tfgTrigger.createNewSampleEnvEntry( 0.72, 0.10, TriggerOutputPort.USR_OUT_3 );
		TriggerableObject trigger3 = tfgTrigger.createNewSampleEnvEntry( 0.74, 0.10, TriggerOutputPort.USR_OUT_4 );
		TriggerableObject trigger4 = tfgTrigger.createNewSampleEnvEntry( 0.76, 0.10, TriggerOutputPort.USR_OUT_5 );

		List<TriggerableObject> triggerList = tfgTrigger.getSampleEnvironment();
		triggerList.add( trigger1 );
		triggerList.add( trigger2 );
		triggerList.add( trigger3 );
		triggerList.add( trigger4 );

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command+"\n");
		assertTrue("TFGTrigger test4OverlappingPulses - 4 partially overlapping pulses after data collection",
				command.equals("tfg setup-groups\n"+
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
						"-1 0 0 0 0 0 0" ) );

	}


	//TODO taking out this test as it is test the wrong thing and cannot cover script run yet.
	@Ignore("taking out this test as it is test the wrong thing and cannot cover script run yet.")
	@Test
	public void testGetTfgSetupGroupCommandParameters() throws Exception {

		TFGTrigger tfgTrigger = new TFGTrigger();
		EdeDetector detector = new XhDetector();
		detector.setName("xh");
		tfgTrigger.setDetector(detector);


		tfgTrigger.getDetectorDataCollection().setTriggerDelay(4.0d);
		tfgTrigger.getDetectorDataCollection().setTriggerPulseLength(0.1d);
		tfgTrigger.getDetectorDataCollection().setNumberOfFrames(20);
		tfgTrigger.getDetectorDataCollection().setCollectionDuration(10.0d);

		TriggerableObject testObj = tfgTrigger.createNewSampleEnvEntry();
		testObj.setTriggerDelay(0.5d);
		testObj.setTriggerPulseLength(0.1d);
		tfgTrigger.getSampleEnvironment().add(testObj);

		testObj = tfgTrigger.createNewSampleEnvEntry();
		testObj.setTriggerDelay(0.8d);
		testObj.setTriggerPulseLength(20d);
		tfgTrigger.getSampleEnvironment().add(testObj);

		String command = tfgTrigger.getTfgSetupGroupCommandParameters(1, false);
		System.out.print(command);
		assertTrue(command.equals("tfg setup-groups\n" +
				"1 0.500000 0.0 0 0 0 0\n" +
				"1 0.100000 0.0 4 0 0 0\n" +
				"1 0.200000 0.0 0 0 0 0\n" +
				"1 3.200000 0.0 8 0 0 0\n" +
				"1 0.100000 0.0 10 0 0 0\n" +
				"20 0 0.000001 0 8 0 9\n" +
				"1 7.300000 0.0 8 0 0 0\n" +
				"-1 0 0 0 0 0 0"));
	}
}

