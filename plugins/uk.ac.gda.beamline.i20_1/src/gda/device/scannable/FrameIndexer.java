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

package gda.device.scannable;

import gda.device.DeviceException;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.position.EdePositionType;

/**
 * This should be used within EdeScans to describe every spectrum collected.
 * <p>
 * It should say if the spectrum is light/dark, I0/It, and list the timing group and frame.
 * <p>
 * This intentionally does not cover repetitions in cyclic experiment at this stage.
 */
public class FrameIndexer extends ScannableBase {

	public static Integer[] generateIndex(EdeScanType scantype, EdePositionType positionsType, int repetitionNumber,
			int timingGroup, int frameNumber) {
		Integer[] position = new Integer[5];
		position[0] = scantype == EdeScanType.DARK ? 1 : 0;
		position[1] = positionsType == EdePositionType.INBEAM ? 1 : 0;
		position[2] = repetitionNumber;
		position[3] = timingGroup;
		position[4] = frameNumber;
		return position;
	}

	private final int repetitionNumber;
	private int frameNumber;
	private int timingGroup;
	private final EdeScanType scantype;
	private final EdePositionType positionsType;

	public FrameIndexer(EdeScanType scanType, EdePositionType type, Integer repetitionNumber) {
		inputNames = new String[] {};
		extraNames = new String[] { "Dark", "It", "Repetition", "Group", "Frame" };
		outputFormat = new String[] { "%1d", "%1d", "%d", "%d", "%d" };
		scantype = scanType;
		positionsType = type;
		this.repetitionNumber = repetitionNumber;
	}

	public void setGroup(Integer groupNum) {
		timingGroup = groupNum;
	}

	public void setFrame(Integer frameNum) {
		frameNumber = frameNum;
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		// no inputs for this object so this method should not do anything.
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		return generateIndex(scantype, positionsType, repetitionNumber, timingGroup, frameNumber);
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

}
