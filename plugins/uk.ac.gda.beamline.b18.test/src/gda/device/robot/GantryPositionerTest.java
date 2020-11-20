/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

package gda.device.robot;

import static org.junit.Assert.assertEquals;

import java.util.Arrays;

import org.junit.Before;
import org.junit.Test;
import org.mockito.InOrder;
import org.mockito.Mockito;

import gda.MockFactory;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.enumpositioner.ValvePosition;
import gda.device.robot.SamplePlateMoverBase.GripperState;
import gda.factory.FactoryException;
import gda.jython.InterfaceProvider;
import gda.jython.MockJythonServerFacade;

public class GantryPositionerTest {

	private GantryPositioner positioner;
	private Scannable horizScannable;
	private Scannable vertScannable;
	private Scannable gripper;
	private Scannable gripperAngle;

//	private DummyEnumPositioner gripper;
	@Before
	public void setup() throws DeviceException, FactoryException {
		InterfaceProvider.setTerminalPrinterForTesting(new MockJythonServerFacade());

		horizScannable = MockFactory.createMockScannable("horizScannable");
		vertScannable = MockFactory.createMockScannable("vertScannable");
		gripper = MockFactory.createMockScannable("gripper");
		gripperAngle = MockFactory.createMockScannable("gripperAngle");

		positioner = new GantryPositioner();
		positioner.setName("positioner");
		positioner.setHorizScannable(horizScannable);
		positioner.setVertScannable(vertScannable);
		positioner.setGripperScannable(gripper);
		positioner.setGripperAngleScannable(gripperAngle);
		positioner.setOutputFormat(new String[] {"%.1f", "%.1f"});
		positioner.setInputNames(new String[] {"horizScannable", "vertScannable"});
		positioner.setVerifyMove(false);

		positioner.setGripperPosition(GripperState.OPEN, ValvePosition.OPEN);
		positioner.setGripperPosition(GripperState.CLOSE, ValvePosition.CLOSE);

		positioner.setSafeHeight(100);
		positioner.setLoadHeight(50);
		positioner.setBeamHorizontalPosition(20.0);
		positioner.setPlatePosition("A", 1.0);
		positioner.setPlatePosition("B", 2.0);
		positioner.setPlatePosition("C", 2.0);
		positioner.setMoveTolerance(10000);
		positioner.setGripperBeamAngle(1.0);
		positioner.setGripperLoadAngle(91.0);

		positioner.configure();

		// Expected interactions from 'configure'
		Arrays.asList(horizScannable,vertScannable, gripper, gripperAngle).forEach( m -> {
			Mockito.verify(m).getOutputFormat();
			Mockito.verify(m).getName();
		});
	}

	@Test
	public void testPickupPlate() throws DeviceException {
		positioner.loadPlate("A");
		InOrder inorder = Mockito.inOrder(horizScannable, vertScannable, gripperAngle, gripper);
		inorder.verify(vertScannable).moveTo(positioner.getSafeHeight());
		inorder.verify(horizScannable).moveTo(positioner.getPlatePosition("A"));
		inorder.verify(gripperAngle).moveTo(positioner.getGripperLoadAngle());
		inorder.verify(gripper).moveTo(ValvePosition.OPEN);
		inorder.verify(vertScannable).moveTo(positioner.getLoadHeight());
		inorder.verify(gripper).moveTo(ValvePosition.CLOSE);
		assertEquals("A", positioner.getCurrentPlate());
	}

	@Test
	public void testPickupUnknownPlate() throws DeviceException {
		positioner.loadPlate("Z");
		Mockito.verifyNoMoreInteractions(horizScannable, vertScannable, gripperAngle, gripper);
	}

	@Test
	public void testPutdownPlate() throws DeviceException {
		positioner.setCurrentPlate("A");
		positioner.unloadPlate();
		InOrder inorder = Mockito.inOrder(horizScannable, vertScannable, gripperAngle, gripper);

		// Unload currently held sample
		inorder.verify(vertScannable).moveTo(positioner.getSafeHeight());
		inorder.verify(horizScannable).moveTo(positioner.getPlatePosition("A"));
		inorder.verify(gripperAngle).moveTo(positioner.getGripperLoadAngle());
		inorder.verify(vertScannable).moveTo(positioner.getLoadHeight());
		inorder.verify(gripper).moveTo(ValvePosition.OPEN);
		assertEquals("", positioner.getCurrentPlate());
	}

	@Test
	public void testPickupPlateWhenOneAlreadyHeld() throws DeviceException {
		positioner.setCurrentPlate("A");
		positioner.loadPlate("B");
		InOrder inorder = Mockito.inOrder(horizScannable, vertScannable,  gripperAngle, gripper);

		// First unload currently held sample
		inorder.verify(vertScannable).moveTo(positioner.getSafeHeight());
		inorder.verify(horizScannable).moveTo(positioner.getPlatePosition("A"));
		inorder.verify(gripperAngle).moveTo(positioner.getGripperLoadAngle());
		inorder.verify(vertScannable).moveTo(positioner.getLoadHeight());
		inorder.verify(gripper).moveTo(ValvePosition.OPEN);

		// Load the new one
		inorder.verify(vertScannable).moveTo(positioner.getSafeHeight());
		inorder.verify(horizScannable).moveTo(positioner.getPlatePosition("B"));
		inorder.verify(gripperAngle).moveTo(positioner.getGripperLoadAngle());
		inorder.verify(gripper).moveTo(ValvePosition.OPEN);
		inorder.verify(vertScannable).moveTo(positioner.getLoadHeight());
		inorder.verify(gripper).moveTo(ValvePosition.CLOSE);

		assertEquals("B", positioner.getCurrentPlate());
	}

	@Test
	public void moveIntoBeam() throws DeviceException {
		positioner.moveToBeam();

		InOrder inorder = Mockito.inOrder(horizScannable, vertScannable, gripperAngle, gripper);
		inorder.verify(vertScannable).moveTo(positioner.getSafeHeight());
		inorder.verify(horizScannable).moveTo(positioner.getBeamHorizontalPosition());
		inorder.verify(gripperAngle).moveTo(positioner.getGripperBeamAngle());
	}
}
