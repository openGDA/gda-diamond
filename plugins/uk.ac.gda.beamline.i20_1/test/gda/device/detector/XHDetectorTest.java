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

import org.junit.Before;
import org.junit.Test;

import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

/**
 * Tests the commands sent to DAServer by the XHDetector class for a variety of experimental setups
 */
public class XHDetectorTest {
	
	private static XHDetector xh;
	private DummyXStripDAServer daserver;

	@Before
	public void createObject(){
		daserver = new DummyXStripDAServer();
		
		xh = new XHDetector();
		xh.setDaServer(daserver);
		xh.setDetectorName("xh0");
		xh.setReadoutStartupCommand("xstrip open-mca 'xh0'");
		xh.configure();
	}
	
	@Test
	public void testSimpleGroup(){
		daserver.clearRecievedCommands();
		
		EdeScanParameters scan = new EdeScanParameters();
		
		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.1);
		group1.setTimePerFrame(1);		
		scan.addGroup(group1);
		
		xh.loadParameters(scan);
		
		String[] commands = daserver.getRecievedCommands();
		
		//always clear out signals before setting anything up
		assertEquals("xstrip timing ext-output \"xh0\" -1 dc",commands[0]);
		assertEquals("xstrip timing setup-group \"xh0\" 0 1 0 5000000 frame-time 50000000 last",commands[1]);
	}
	
	@Test
	public void testDelays(){
		daserver.clearRecievedCommands();
		
		EdeScanParameters scan = new EdeScanParameters();
		
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
		
		xh.loadParameters(scan);
		
		String[] commands = daserver.getRecievedCommands();
		
		//always clear out signals before setting anything up
		assertEquals("xstrip timing ext-output \"xh0\" -1 dc",commands[0]);
		assertEquals("xstrip timing setup-group \"xh0\" 0 1 0 5000000 frame-time 50000000 frame-delay 250000000",commands[1]);
		assertEquals("xstrip timing setup-group \"xh0\" 1 2 0 5000000 frame-time 150000000 group-delay 3000000000 last",commands[2]);
	}
	
	@Test
	public void testInputs(){
		daserver.clearRecievedCommands();
		
		EdeScanParameters scan = new EdeScanParameters();
		
		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.1);
		group1.setTimePerFrame(1);	
		group1.setGroupTrig(true);
		group1.setGroupTrigLemo(5);
		scan.addGroup(group1);
		
		xh.loadParameters(scan);
		
		String[] commands = daserver.getRecievedCommands();
		
		//always clear out signals before setting anything up
		assertEquals("xstrip timing ext-output \"xh0\" -1 dc",commands[0]);
		assertEquals("xstrip timing setup-group \"xh0\" 0 1 0 5000000 frame-time 50000000 ext-trig-group trig-mux 5 last",commands[1]);
	}
	
	@Test
	public void testInputsFallingEdge(){
		daserver.clearRecievedCommands();
		
		EdeScanParameters scan = new EdeScanParameters();
		
		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.1);
		group1.setTimePerFrame(1);	
		group1.setGroupTrig(true);
		group1.setGroupTrigLemo(5);
		group1.setGroupTrigRisingEdge(false);
		scan.addGroup(group1);
		
		xh.loadParameters(scan);
		
		String[] commands = daserver.getRecievedCommands();
		
		//always clear out signals before setting anything up
		assertEquals("xstrip timing ext-output \"xh0\" -1 dc",commands[0]);
		assertEquals("xstrip timing setup-group \"xh0\" 0 1 0 5000000 frame-time 50000000 ext-trig-group trig-mux 5 trig-falling last",commands[1]);
	}

	
	@Test 
	public void testOutputs(){
		daserver.clearRecievedCommands();
		
		EdeScanParameters scan = new EdeScanParameters();
		scan.setOutputsChoice0(EdeScanParameters.TRIG_FRAME_BEFORE);
		
		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.1);
		group1.setTimePerFrame(1);	
		group1.setOutLemo0(true);
		scan.addGroup(group1);
		
		xh.loadParameters(scan);
		
		String[] commands = daserver.getRecievedCommands();
		
		//always clear out signals before setting anything up
		assertEquals("xstrip timing ext-output \"xh0\" -1 dc",commands[0]);
		assertEquals("xstrip timing ext-output \"xh0\" 0 frame-pre-delay",commands[1]);
		assertEquals("xstrip timing setup-group \"xh0\" 0 1 0 5000000 frame-time 50000000 lemo-out 1 last",commands[2]);
	}
	
	@Test 
	public void testOutputsDelay(){
		daserver.clearRecievedCommands();
		
		EdeScanParameters scan = new EdeScanParameters();
		scan.setOutputsChoice0(EdeScanParameters.TRIG_FRAME_BEFORE);
		scan.setOutputsWidth0(2);
		
		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.1);
		group1.setTimePerFrame(1);	
		group1.setOutLemo0(true);
		scan.addGroup(group1);
		
		xh.loadParameters(scan);
		
		String[] commands = daserver.getRecievedCommands();
		
		//always clear out signals before setting anything up
		assertEquals("xstrip timing ext-output \"xh0\" -1 dc",commands[0]);
		assertEquals("xstrip timing ext-output \"xh0\" 0 frame-pre-delay width 100000000",commands[1]);
		assertEquals("xstrip timing setup-group \"xh0\" 0 1 0 5000000 frame-time 50000000 lemo-out 1 last",commands[2]);
	}

	
	@Test
	public void testMixInputAndOuputs(){
		daserver.clearRecievedCommands();
		
		EdeScanParameters scan = new EdeScanParameters();
		scan.setOutputsChoice6(EdeScanParameters.TRIG_FRAME_BEFORE);
		
		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.000006);
		group1.setTimePerFrame(0.00001);	
		group1.setOutLemo6(true);
		group1.setGroupTrig(true);
		group1.setGroupTrigLemo(5);
		scan.addGroup(group1);
		
		xh.loadParameters(scan);
		
		String[] commands = daserver.getRecievedCommands();
		
		//always clear out signals before setting anything up
		assertEquals("xstrip timing ext-output \"xh0\" -1 dc",commands[0]);
		assertEquals("xstrip timing ext-output \"xh0\" 6 frame-pre-delay",commands[1]);
		assertEquals("xstrip timing setup-group \"xh0\" 0 1 0 300 frame-time 500 lemo-out 4096 ext-trig-group trig-mux 5 last",commands[2]);

	}
	
//	@Test
//	public void testVaryingSectorNumbers(){
//		daserver.clearRecievedCommands();
//		daserver.setReadoutMode(MODE.FLAT);
//		
//		try {
//			// default is 4
//			assertEquals(4,xh.getNumberOfSectors());
//			assertEquals(4,xh.getAttribute(XHDetector.ATTR_NUMBERSECTORS));
//			assertEquals("sector4", xh.getExtraNames()[5]);
//			assertEquals(6,xh.getOutputFormat().length);
//			NXDetectorData data = (NXDetectorData) xh.readout();
//			Double[] sectorVals = data.getDoubleVals();
//			assertEquals(6,sectorVals.length);
//			assertTrue(256.0 == sectorVals[2]);
//			assertTrue(256.0 == sectorVals[5]);
//			
//			//same tests at 6 sectors
//			xh.setNumberOfSectors(6);
//			assertEquals(6,xh.getNumberOfSectors());
//			assertEquals(6,xh.getAttribute(XHDetector.ATTR_NUMBERSECTORS));
//			assertEquals("sector4", xh.getExtraNames()[5]);
//			assertEquals(8,xh.getOutputFormat().length);
//			data = (NXDetectorData) xh.readout();
//			sectorVals = data.getDoubleVals();
//			assertEquals(8,sectorVals.length);
//			assertTrue(170 == sectorVals[2]);
//			assertTrue(170 == sectorVals[6]);
//			
//			
//			// same test at 10 sectors
//			xh.setAttribute(XHDetector.ATTR_NUMBERSECTORS, 10);
//			assertEquals(10,xh.getNumberOfSectors());
//			assertEquals(10,xh.getAttribute(XHDetector.ATTR_NUMBERSECTORS));
//			assertEquals("sector4", xh.getExtraNames()[5]);
//			assertEquals(12,xh.getOutputFormat().length);
//			data = (NXDetectorData) xh.readout();
//			sectorVals = data.getDoubleVals();
//			assertEquals(12,sectorVals.length);
//			assertTrue(102.0 == sectorVals[2]);
//			assertTrue(102.0 == sectorVals[9]);
//		} catch (DeviceException e) {
//			fail(e.getMessage());
//		} finally {
//			daserver.setReadoutMode(MODE.STEP);
//		}
//	}
}