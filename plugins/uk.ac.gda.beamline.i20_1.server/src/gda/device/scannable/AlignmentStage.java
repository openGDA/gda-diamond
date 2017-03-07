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
import gda.device.Scannable;
import gda.device.scannable.AlignmentStageScannable.AlignmentStageDevice;
import gda.device.scannable.AlignmentStageScannable.FastShutter;

import java.io.IOException;

import org.apache.commons.configuration.ConfigurationException;

public interface AlignmentStage extends Scannable {
	public AlignmentStageDevice getAlignmentStageDevice(String name);
	public FastShutter getFastShutter();
	void saveDeviceFromCurrentMotorPositions(Object positionName) throws ConfigurationException, DeviceException,
	IOException;
}
