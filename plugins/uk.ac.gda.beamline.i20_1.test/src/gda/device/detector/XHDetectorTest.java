/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package gda.device.detector;

import static org.junit.Assert.assertEquals;

import java.io.File;

import org.junit.Before;
import org.junit.Test;

import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.device.detector.xstrip.DummyXStripDAServer;
import gda.device.detector.xstrip.XhDetector;
import gda.device.detector.xstrip.XhDetectorData;
import gda.factory.FactoryException;
import gda.util.TestUtils;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

/**
 * Tests the commands sent to DAServer by the XHDetector class for a variety of experimental setups
 */
public class XHDetectorTest {

	private static XhDetector xh;
	private DummyXStripDAServer daserver;

	@Before
	public void createObject() throws FactoryException{
		final File scratchDir = TestUtils.createClassScratchDirectory(XHDetectorTest.class);
		LocalProperties.set(LocalProperties.GDA_VAR_DIR, scratchDir.getAbsolutePath());

		daserver = new DummyXStripDAServer();

		xh = new XhDetector();
		xh.setName("xh");
		xh.setDaServer(daserver);
		xh.setDetectorName("xh0");
		xh.setDetectorData(new XhDetectorData());
		xh.configure();
	}

	@Test
	public void testSimpleGroup() throws DeviceException{
		daserver.clearRecievedCommands();

		EdeScanParameters scan = new EdeScanParameters();
		scan.setUseFrameTime(true);

		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.1);
		group1.setTimePerFrame(1);
		scan.addGroup(group1);

		xh.prepareDetectorwithScanParameters(scan);

		String[] commands = daserver.getRecievedCommands();

		//always clear out signals before setting anything up
		assertEquals("xstrip timing ext-output \"xh0\" -1 dc",commands[1]);
		assertEquals("xstrip timing setup-group \"xh0\" 0 1 0 5000000 frame-time 50000000 last",commands[10]);
	}

	@Test
	public void testDelays() throws DeviceException{
		daserver.clearRecievedCommands();

		EdeScanParameters scan = new EdeScanParameters();
		scan.setUseFrameTime(true);

		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.1);
		group1.setTimePerFrame(1);
		group1.setDelayBetweenFrames(5);
		scan.addGroup(group1);

		TimingGroup group2 = new TimingGroup();
		group2.setLabel("group2");
		group2.setNumberOfFrames(2);
		group2.setTimePerScan(0.1);
		group2.setTimePerFrame(3);
		group2.setPreceedingTimeDelay(60);
		scan.addGroup(group2);

		xh.prepareDetectorwithScanParameters(scan);

		String[] commands = daserver.getRecievedCommands();

		//always clear out signals before setting anything up
		assertEquals("xstrip timing ext-output \"xh0\" -1 dc",commands[1]);
		assertEquals("xstrip timing setup-group \"xh0\" 0 1 0 5000000 frame-time 50000000 frame-delay 250000000",commands[10]);
		assertEquals("xstrip timing setup-group \"xh0\" 1 2 0 5000000 frame-time 150000000 group-delay 3000000000 last",commands[19]);
	}

	@Test
	public void testInputs() throws DeviceException{
		daserver.clearRecievedCommands();

		EdeScanParameters scan = new EdeScanParameters();
		scan.setUseFrameTime(true);

		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.1);
		group1.setTimePerFrame(1);
		group1.setGroupTrig(true);
		group1.setGroupTrigLemo(5);
		group1.setGroupTrigRisingEdge(false);
		scan.addGroup(group1);

		xh.prepareDetectorwithScanParameters(scan);

		String[] commands = daserver.getRecievedCommands();

		//always clear out signals before setting anything up
		assertEquals("xstrip timing ext-output \"xh0\" -1 dc",commands[1]);
		assertEquals("xstrip timing setup-group \"xh0\" 0 1 0 5000000 frame-time 50000000 ext-trig-group trig-mux 5 trig-falling last",commands[10]);
	}

	@Test
	public void testInputsFallingEdge() throws DeviceException{
		daserver.clearRecievedCommands();

		EdeScanParameters scan = new EdeScanParameters();
		scan.setUseFrameTime(true);

		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.1);
		group1.setTimePerFrame(1);
		group1.setGroupTrig(true);
		group1.setGroupTrigLemo(5);
		group1.setGroupTrigRisingEdge(false);
		scan.addGroup(group1);

		xh.prepareDetectorwithScanParameters(scan);

		String[] commands = daserver.getRecievedCommands();

		//always clear out signals before setting anything up
		assertEquals("xstrip timing ext-output \"xh0\" -1 dc",commands[1]);
		assertEquals("xstrip timing setup-group \"xh0\" 0 1 0 5000000 frame-time 50000000 ext-trig-group trig-mux 5 trig-falling last",commands[10]);
	}


	@Test
	public void testOutputs() throws DeviceException{
		daserver.clearRecievedCommands();

		EdeScanParameters scan = new EdeScanParameters();
		scan.setUseFrameTime(true);
		scan.setOutputsChoice0(EdeScanParameters.TRIG_FRAME_BEFORE);

		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.1);
		group1.setTimePerFrame(1);
		group1.setOutLemo0(true);
		scan.addGroup(group1);

		xh.prepareDetectorwithScanParameters(scan);

		String[] commands = daserver.getRecievedCommands();

		//always clear out signals before setting anything up
		assertEquals("xstrip timing ext-output \"xh0\" -1 dc",commands[1]);
		assertEquals("xstrip timing ext-output \"xh0\" 0 frame-pre-delay",commands[2]);
		assertEquals("xstrip timing setup-group \"xh0\" 0 1 0 5000000 frame-time 50000000 lemo-out 1 last",commands[11]);
	}

	@Test
	public void testOutputsDelay() throws DeviceException{
		daserver.clearRecievedCommands();

		EdeScanParameters scan = new EdeScanParameters();
		scan.setUseFrameTime(true);
		scan.setOutputsChoice0(EdeScanParameters.TRIG_FRAME_BEFORE);
		scan.setOutputsWidth0(2);

		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.1);
		group1.setTimePerFrame(1);
		group1.setOutLemo0(true);
		scan.addGroup(group1);

		xh.prepareDetectorwithScanParameters(scan);

		String[] commands = daserver.getRecievedCommands();

		//always clear out signals before setting anything up
		assertEquals("xstrip timing ext-output \"xh0\" -1 dc",commands[1]);
		assertEquals("xstrip timing ext-output \"xh0\" 0 frame-pre-delay width 100000000",commands[2]);
		assertEquals("xstrip timing setup-group \"xh0\" 0 1 0 5000000 frame-time 50000000 lemo-out 1 last",commands[11]);
	}


	@Test
	public void testMixInputAndOuputs() throws DeviceException{
		daserver.clearRecievedCommands();

		EdeScanParameters scan = new EdeScanParameters();
		scan.setUseFrameTime(true);
		scan.setOutputsChoice6(EdeScanParameters.TRIG_FRAME_BEFORE);

		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.000006);
		group1.setTimePerFrame(0.00001);
		group1.setOutLemo6(true);
		group1.setGroupTrig(true);
		group1.setGroupTrigLemo(5);
		group1.setGroupTrigRisingEdge(false);
		scan.addGroup(group1);

		xh.prepareDetectorwithScanParameters(scan);

		String[] commands = daserver.getRecievedCommands();

		//always clear out signals before setting anything up
		assertEquals("xstrip timing ext-output \"xh0\" -1 dc",commands[1]);
		assertEquals("xstrip timing ext-output \"xh0\" 6 frame-pre-delay",commands[2]);
		assertEquals("xstrip timing setup-group \"xh0\" 0 1 0 300 frame-time 500 lemo-out 4096 ext-trig-group trig-mux 5 trig-falling last",commands[11]);
	}

	@Test
	public void testBiasControl() throws DeviceException {
		daserver.clearRecievedCommands();

		assertEquals(new Double(0.0),xh.getBias());
		xh.setBias(4.5);
		assertEquals(new Double(4.5),xh.getBias());
	}
}