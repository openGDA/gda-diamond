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

import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.device.MotorException;
import gda.device.detector.DummyXStripDAServer;
import gda.device.detector.XHDetector;
import gda.device.motor.DummyMotor;
import gda.device.scannable.AlignmentStageScannable;
import gda.device.scannable.AlignmentStageScannable.Devices;
import gda.device.scannable.ScannableMotor;
import gda.factory.FactoryException;
import gda.factory.Finder;
import gda.factory.ObjectFactory;
import gda.scan.ede.drivers.SingleSpectrumDriver;

import java.io.File;

import org.junit.BeforeClass;
import org.junit.Test;

public class EdeScanDriversTest {
	private static DummyXStripDAServer daserver;
	private static XHDetector xh;
	private String testDir;
	private static ScannableMotor sample_x;
	private static ScannableMotor sample_y;
	private static ScannableMotor fastShutter_xMotor;
	private static ScannableMotor fastShutter_yMotor;
	private static AlignmentStageScannable alignment_stage;

	@BeforeClass
	public static void startup() throws FactoryException, DeviceException {
		// dummy daserver
		daserver = new DummyXStripDAServer();
		// detector
		xh = new XHDetector();
		xh.setDaServer(daserver);
		xh.setName("xh");
		xh.setDetectorName("xh0");
		xh.configure();

		sample_x = createMotor("sample_x");
		sample_y = createMotor("sample_y");
		fastShutter_xMotor = createMotor("fastShutter_xMotor");
		fastShutter_yMotor = createMotor("fastShutter_yMotor");

		alignment_stage = new AlignmentStageScannable(sample_x, sample_y, fastShutter_xMotor, fastShutter_yMotor);
		alignment_stage.setName("alignment_stage");

		ObjectFactory factory = new ObjectFactory();
		factory.addFindable(xh);
		factory.addFindable(alignment_stage);
		factory.addFindable(sample_x);
		factory.addFindable(sample_y);
		factory.addFindable(fastShutter_xMotor);
		factory.addFindable(fastShutter_yMotor);
		Finder.getInstance().addFactory(factory);
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

		for (Devices device : AlignmentStageScannable.Devices.values()) {
			alignment_stage.saveDeviceFromCurrentMotorPositions(device.toString());
		}

	}

	@Test
	public void testDriveSingleSpectrumScan_motorpositions() throws Exception {
		setup("testDriveSingleSpectrumScan_motorpositions");

		SingleSpectrumDriver driver = new SingleSpectrumDriver("xh", 0.1, 2, 0.2, 1);
		driver.setInBeamPosition(0.0, 0.0);
		driver.setOutBeamPosition(0.1, 0.1);

		String filename = driver.doCollection();
		System.out.println(filename);
	}

//	@Test  TODO wait until Phyo has completed alignment stage refactoring
	public void testDriveSingleSpectrumScan_alignmentstagepositions() throws Exception {
		setup("testDriveSingleSpectrumScan_alignmentstagepositions");

		SingleSpectrumDriver driver = new SingleSpectrumDriver("xh", 0.1, 2, 0.2, 1);
		driver.setInBeamPosition("hole", null);
		driver.setOutBeamPosition("foil", null);

		String filename = driver.doCollection();
		System.out.println(filename);

	}

//	@Test  TODO wait until Phyo has completed alignment stage refactoring
	public void testDriveSingleSpectrumScan_mixedpositions() throws Exception {
		setup("testDriveSingleSpectrumScan_mixedpositions");

		SingleSpectrumDriver driver = new SingleSpectrumDriver("xh", 0.1, 2, 0.2, 1);
		driver.setInBeamPosition(0.0, 0.0);
		driver.setOutBeamPosition("foil", null);

		String filename = driver.doCollection();
		System.out.println(filename);

	}

	private static ScannableMotor createMotor(String name) throws MotorException, FactoryException {
		DummyMotor xMotor = new DummyMotor();
		xMotor.setSpeed(5000);
		xMotor.configure();
		ScannableMotor xScannable = new ScannableMotor();
		xScannable.setMotor(xMotor);
		xScannable.setName(name);
		xScannable.configure();
		return xScannable;
	}
}
