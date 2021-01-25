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

import java.util.List;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.robot.SamplePlateMoverBase.MotorSequence;

public interface SamplePlateMover extends Scannable {

	/** Pick up new sample plate
	 * @param samplePlateName
	 * @throws DeviceException
	 */
	void loadPlate(String samplePlateName) throws DeviceException;

	/** Unload the currently held sample plate
	 * @throws DeviceException
	 */
	void unloadPlate() throws DeviceException;

	/** Move sample plate to the in beam position
	 * @throws DeviceException
	 */
	void moveToBeam() throws DeviceException;

	/** Perform sequence of moves (load, unload sample plate, move into beam)
	 * @throws DeviceException
	 */
	void performMotion(MotorSequence motion, String c) throws DeviceException;

	/**
	 * @return List of names of all sample plates (i.e. 'positions' that can be moved to)
	 */
	List<String> getPlateNames();

	/**
	 *
	 * @return Name of the currently held plate
	 */
	String getCurrentPlate();

}
