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

import static org.junit.Assert.assertEquals;
import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.device.MotorException;
import gda.device.detector.DummyXStripDAServer;
import gda.device.detector.StepScanXHDetector;
import gda.device.detector.XHDetector;
import gda.device.motor.DummyMotor;
import gda.device.scannable.ScannableMotor;
import gda.factory.FactoryException;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.List;

import org.junit.Test;

import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public class EdeScanTest {

	private DummyXStripDAServer daserver;
	private XHDetector xh;
	private String testDir;


	public void setup(String testName) throws Exception {
		/*String testFolder = */TestHelpers.setUpTest(EdeScanTest.class, testName, true);
		LocalProperties.setScanSetsScanNumber(true);
		LocalProperties.set("gda.scan.sets.scannumber", "true");
		LocalProperties.set("gda.scanbase.firstScanNumber", "-1");
		LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, "NexusDataWriter");
		LocalProperties.set("gda.nexus.createSRS", "false");
		testDir = LocalProperties.getBaseDataDir();
		
		// dummy daserver
		daserver = new DummyXStripDAServer();
		// detector
		xh = new XHDetector();
		xh.setDaServer(daserver);
		xh.setName("xh");
		xh.setDetectorName("xh0");
		xh.configure();
	}

	@Test
	public void testRunScan() throws Exception {
		setup("testRunScan");
		EdeScanParameters scanParams = new EdeScanParameters();
		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(2);
		group1.setTimePerScan(0.005);
		group1.setTimePerFrame(0.02);
		scanParams.addGroup(group1);

		ScannableMotor xScannable = createMotor("xScannable");
		ScannableMotor yScannable = createMotor("yScannable");

		LocalProperties.set("gda.nexus.createSRS", "true");
		EdeScanPosition inBeam = new EdeScanPosition(EdePositionType.INBEAM, 1d, 1d, xScannable, yScannable);
		// EdeScanPosition outBeam = new EdeScanPosition(EdePositionType.OUTBEAM,0d,0d,"xScannable","yScannable");

		EdeScan theScan = new EdeScan(scanParams, inBeam, EdeScanType.LIGHT, xh);
		theScan.runScan();

		List<ScanDataPoint> data = theScan.getData();

		assertEquals(2, data.size());

		// test the SRS file to see if the number of columns is correct
		FileReader asciiFile = new FileReader(testDir + File.separator + "1.dat");
		BufferedReader reader = null;
		try {
			reader = new BufferedReader(asciiFile);
			reader.readLine(); // &SRS
			reader.readLine(); // &END
			reader.readLine(); // header line
			String dataString = reader.readLine(); // first data point
			String[] dataParts = dataString.split("\t");
			assertEquals(7, dataParts.length);
		} finally {
			if (reader != null) {
				reader.close();
			}
		}

	}
	
	@Test
	public void testRunExperimentSameParameters() throws Exception {
		setup("testRunExperimentSameParameters");
		EdeScanParameters scanParams = new EdeScanParameters();
		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.005);
		group1.setTimePerFrame(0.02);
		scanParams.addGroup(group1);

		ScannableMotor xScannable = createMotor("xScannable");
		ScannableMotor yScannable = createMotor("yScannable");

		EdeScanPosition inBeam = new EdeScanPosition(EdePositionType.INBEAM, 1d, 1d, xScannable, yScannable);
		EdeScanPosition outBeam = new EdeScanPosition(EdePositionType.OUTBEAM,0d,0d,xScannable,yScannable);

		EdeSingleExperiment theExperiment = new EdeSingleExperiment(scanParams, inBeam, outBeam, xh);
		theExperiment.runExperiment();


		testEDEFormatAsciiFile(3);
	}

	@Test
	public void testRunExperimentDifferentParameters() throws Exception {
		setup("testRunExperimentDifferentParameters");
		EdeScanParameters i0Params = new EdeScanParameters();
		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.005);
		group1.setTimePerFrame(0.02);
		i0Params.addGroup(group1);

		EdeScanParameters itParams = new EdeScanParameters();
		TimingGroup group2 = new TimingGroup();
		group2.setLabel("group1");
		group2.setNumberOfFrames(1);
		group2.setTimePerScan(0.05);
		group2.setTimePerFrame(0.02);
		itParams.addGroup(group2);

		ScannableMotor xScannable = createMotor("xScannable");
		ScannableMotor yScannable = createMotor("yScannable");

		EdeScanPosition inBeam = new EdeScanPosition(EdePositionType.INBEAM, 1d, 1d, xScannable, yScannable);
		EdeScanPosition outBeam = new EdeScanPosition(EdePositionType.OUTBEAM,0d,0d,xScannable,yScannable);

		EdeSingleExperiment theExperiment = new EdeSingleExperiment(i0Params, itParams, inBeam, outBeam, xh);
		theExperiment.runExperiment();


		testEDEFormatAsciiFile(4);
	}

	private void testEDEFormatAsciiFile(int fileNumber) throws FileNotFoundException, IOException {
		FileReader asciiFile = new FileReader(testDir + File.separator + fileNumber + ".txt");
		BufferedReader reader = null;
		try {
			reader = new BufferedReader(asciiFile);
			reader.readLine(); // header line
			String dataString = reader.readLine(); // first data point
			String[] dataParts = dataString.split("\t");
			assertEquals(9, dataParts.length);
		} finally {
			if (reader != null) {
				reader.close();
			}
		}
	}
	
	@Test
	public void testExperimentUsingStepScan() throws Exception{
		setup("testExperimentUsingStepScan");
		LocalProperties.set("gda.nexus.createSRS", "true");
		ScannableMotor xScannable = createMotor("xScannable");
		StepScanXHDetector ssxh = new StepScanXHDetector();
		ssxh.setXh(xh);
		new ConcurrentScan(
				new Object[] { xScannable, 0., 1., 1., ssxh, 0.2 })
				.runScan();
		
		// test the SRS file to see if the number of columns is correct
		FileReader asciiFile = new FileReader(testDir + File.separator + "1.dat");
		BufferedReader reader = null;
		try {
			reader = new BufferedReader(asciiFile);
			reader.readLine(); // &SRS
			reader.readLine(); // &END
			reader.readLine(); // header line
			String dataString = reader.readLine(); // first data point
			String[] dataParts = dataString.split("\t");
			assertEquals(6, dataParts.length);
		} finally {
			if (reader != null) {
				reader.close();
			}
		}

	}

	@Test
	public void testExperimentUsingEdeScanParametersStaticMethods() throws Exception{
		setup("testExperimentUsingEdeScanParametersStaticMethods");
		
		EdeScanParameters itparams = EdeScanParameters.createSingleFrameScan(0.2);
		
		ScannableMotor xScannable = createMotor("xScannable");
		ScannableMotor yScannable = createMotor("yScannable");

		EdeScanPosition inBeam = new EdeScanPosition(EdePositionType.INBEAM, 1d, 1d, xScannable, yScannable);
		EdeScanPosition outBeam = new EdeScanPosition(EdePositionType.OUTBEAM,0d,0d,xScannable,yScannable);

		EdeSingleExperiment theExperiment = new EdeSingleExperiment(itparams, inBeam, outBeam, xh);
		theExperiment.runExperiment();
		
		testEDEFormatAsciiFile(3);
	}

	private ScannableMotor createMotor(String name) throws MotorException, FactoryException {
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
