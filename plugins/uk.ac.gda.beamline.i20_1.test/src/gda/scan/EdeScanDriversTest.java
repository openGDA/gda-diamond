/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package gda.scan;

import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.Vector;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Ignore;
import org.junit.Test;
import org.powermock.core.classloader.annotations.PowerMockIgnore;

import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.device.detector.xstrip.DummyXStripDAServer;
import gda.device.detector.xstrip.XhDetector;
import gda.device.detector.xstrip.XhDetectorData;
import gda.device.monitor.DummyMonitor;
import gda.device.scannable.AlignmentStageScannable;
import gda.device.scannable.AlignmentStageScannable.AlignmentStageDevice;
import gda.device.scannable.ScannableMotor;
import gda.factory.Factory;
import gda.factory.Finder;
import gda.scan.ede.drivers.LinearExperimentDriver;
import gda.scan.ede.drivers.SingleSpectrumDriver;
import uk.ac.gda.exafs.ui.data.TimingGroup;

@Ignore("2015/09/29 All tests in the class are currently ignored, so just ignore the entire class")
@PowerMockIgnore({"javax.management.*", "javax.xml.parsers.*", "org.apache.xerces.*" ,"com.sun.org.apache.xerces.internal.jaxp.*", "ch.qos.logback.*", "org.slf4j.*"})
public class EdeScanDriversTest extends EdeTestBase {
	private static DummyXStripDAServer daserver;
	private static XhDetector xh;
	private String testDir;
	private static ScannableMotor sample_x;
	private static ScannableMotor sample_y;
	private static ScannableMotor fastShutter_xMotor;
	private static ScannableMotor fastShutter_yMotor;
	private static AlignmentStageScannable alignment_stage;
	private static DummyMonitor topupMonitor;

	private static Map<String, Double> sampleStageMotorInPositions = new HashMap<String, Double>();
	private static Map<String, Double> sampleStageMotorOutPositions = new HashMap<String, Double>();

	@BeforeClass
	public static void startup() throws Exception {
		// dummy daserver
		daserver = new DummyXStripDAServer();
		// detector
		xh = new XhDetector();
		xh.setDaServer(daserver);
		xh.setName("xh");
		xh.setDetectorData(new XhDetectorData());
		xh.setDetectorName("xh0");
		xh.configure();

		sample_x = createMotor("sample_x");
		sample_y = createMotor("sample_y");
		fastShutter_xMotor = createMotor("fastShutter_xMotor");
		fastShutter_yMotor = createMotor("fastShutter_yMotor");

		sampleStageMotorInPositions.put(sample_x.getName(), 0.0);
		sampleStageMotorInPositions.put(sample_y.getName(), 0.0);
		sampleStageMotorOutPositions.put(sample_x.getName(), 1.0);
		sampleStageMotorOutPositions.put(sample_y.getName(), 1.0);

		alignment_stage = new AlignmentStageScannable(sample_x, sample_y, fastShutter_xMotor, fastShutter_yMotor);
		alignment_stage.setName("alignment_stage");

		// topup monitor
		topupMonitor = new DummyMonitor();
		topupMonitor.setName("topup");
		topupMonitor.setValue(120.0);

		final Factory factory = TestHelpers.createTestFactory();
		factory.addFindable(xh);
		factory.addFindable(alignment_stage);
		factory.addFindable(sample_x);
		factory.addFindable(sample_y);
		factory.addFindable(fastShutter_xMotor);
		factory.addFindable(fastShutter_yMotor);
		factory.addFindable(topupMonitor);
		Finder.addFactory(factory);
	}

	@AfterClass
	public static void tearDownClass() {
		// Remove factories from Finder so they do not affect other tests
		Finder.removeAllFactories();
	}

	public void setup(String testName) throws Exception {
		/* String testFolder = */TestHelpers.setUpTest(EdeScanTest.class, testName, true);
		LocalProperties.setScanSetsScanNumber(true);
		LocalProperties.set("gda.scan.sets.scannumber", "true");
		LocalProperties.set("gda.scanbase.firstScanNumber", "-1");
		LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, "NexusDataWriter");
		LocalProperties.set("gda.nexus.createSRS", "false");
		testDir = LocalProperties.getBaseDataDir();

		// need the var dir to be created for this test in order to calibrate the alignment stage and store the
		// calibration. It cannot be used until this is done so.
		LocalProperties.set(LocalProperties.GDA_VAR_DIR, testDir);
		File test = new File(testDir);
		if (!test.exists()) {
			test.mkdir();
		}

		for (AlignmentStageDevice device : AlignmentStageScannable.AlignmentStageDevice.values()) {
			alignment_stage.saveDeviceFromCurrentMotorPositions(device.toString());
		}

	}

	// FIXME This is not testing anything?
	// Ignore as SingleSpectrumDriver is deprecated
	@Test
	@Ignore
	public void testDriveSingleSpectrumScan_motorpositions() throws Exception {
		setup("testDriveSingleSpectrumScan_motorpositions");

		SingleSpectrumDriver driver = new SingleSpectrumDriver("xh", "topup", 0.1, 2, 0.2, 1, createShutter2());
		driver.setInBeamPosition(sampleStageMotorInPositions);
		driver.setOutBeamPosition(sampleStageMotorOutPositions);

		String filename = driver.doCollection();
		System.out.println(filename);
	}

	// FIXME This is not testing anything?
//	@Test  //TODO wait until Phyo has completed alignment stage refactoring
	public void testDriveSingleSpectrumScan_alignmentstagepositions() throws Exception {
		setup("testDriveSingleSpectrumScan_alignmentstagepositions");

		SingleSpectrumDriver driver = new SingleSpectrumDriver("xh", "topup", 0.1, 2, 0.2, 1, createShutter2());
		driver.setInBeamPosition(sampleStageMotorInPositions);
		driver.setOutBeamPosition(sampleStageMotorOutPositions);

		String filename = driver.doCollection();
		System.out.println(filename);

	}

//	@Test  //TODO wait until Phyo has completed alignment stage refactoring
	public void testDriveSingleSpectrumScan_mixedpositions() throws Exception {
		setup("testDriveSingleSpectrumScan_mixedpositions");

		SingleSpectrumDriver driver = new SingleSpectrumDriver("xh", "topup", 0.1, 2, 0.2, 1, createShutter2());
		driver.setInBeamPosition(sampleStageMotorInPositions);
		driver.setOutBeamPosition(sampleStageMotorOutPositions);

		String filename = driver.doCollection();
		System.out.println(filename);

	}

	// Ignored because LinearExperimentDriver is deprecated
	@Ignore @Test
	public void testDriveLinearSpectrumScan_motorpositions() throws Exception {
		setup("testDriveLinearSpectrumScan_motorpositions");

		Vector<TimingGroup> groups = new Vector<TimingGroup>();

		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(10);
		group1.setTimePerScan(0.005);
		group1.setNumberOfScansPerFrame(5);
		groups.add(group1);

		TimingGroup group2 = new TimingGroup();
		group2.setLabel("group2");
		group2.setNumberOfFrames(10);
		group2.setTimePerScan(0.05);
		group2.setNumberOfScansPerFrame(5);
		groups.add(group2);

		TimingGroup group3 = new TimingGroup();
		group3.setLabel("group3");
		group3.setNumberOfFrames(5);
		group3.setTimePerScan(0.01);
		group3.setNumberOfScansPerFrame(5);
		groups.add(group3);


		LinearExperimentDriver driver = new LinearExperimentDriver("xh", "topup", groups, createShutter2());
		driver.setInBeamPosition(sampleStageMotorInPositions);
		driver.setOutBeamPosition(sampleStageMotorOutPositions);

		String filename = driver.doCollection();
		System.out.println(filename);
	}

}
