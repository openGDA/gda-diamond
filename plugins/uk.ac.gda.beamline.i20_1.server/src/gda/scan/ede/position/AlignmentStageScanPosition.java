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

package gda.scan.ede.position;

import org.dawnsci.ede.herebedragons.EdePositionType;

import gda.device.DeviceException;
import gda.device.scannable.AlignmentStageScannable;
import gda.device.scannable.AlignmentStageScannable.AlignmentStageDevice;

/**
 * Define the position for a scan using the alignment stage instead of motor positions.
 */
public class AlignmentStageScanPosition implements EdeScanPosition {

	private final EdePositionType type;
	private final AlignmentStageScannable.AlignmentStageDevice device;
	private final AlignmentStageScannable theScannable;

	public AlignmentStageScanPosition(EdePositionType type, AlignmentStageDevice device, AlignmentStageScannable theScannable) {
		this.type = type;
		this.device = device;
		this.theScannable = theScannable;
	}

	@Override
	public void moveIntoPosition() throws DeviceException, InterruptedException {
		theScannable.moveTo(device);
	}

	@Override
	public EdePositionType getType() {
		return type;
	}

	@Override
	public double getTimeToMove() {
		return 0;
	}

}
