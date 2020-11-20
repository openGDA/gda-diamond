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

import gda.device.DeviceException;
import gda.device.robot.SamplePlateMoverBase.MotorSequence;

public interface SamplePlateMover {

	/** Pick up new sample plate **/
	void loadPlate(String samplePlateName) throws DeviceException;

	/** Unload the currently held sample plate */
	void unloadPlate() throws DeviceException;

	/** Move sample plate to the in beam position */
	void moveToBeam() throws DeviceException;

	/** Perform sequance of moves (load, unload sample plate, move into beam) **/
	void performMotion(MotorSequence motion, String c);

}
