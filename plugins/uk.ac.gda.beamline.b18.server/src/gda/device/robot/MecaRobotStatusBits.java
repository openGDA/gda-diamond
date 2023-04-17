/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

/**
 * Meca 'robot status' bits
 */
public enum MecaRobotStatusBits {
	Activated("Activated", 0),
	Homed("Homed", 1),
	Simulation_Mode("Simulation Mode", 2),
	Error("Error", 3),
	Paused("Paused", 4),
	End_of_Block("End of Block", 5),
	End_of_Movement("End of Movement", 6);

	private final String name;
	private final int bit;
	private MecaRobotStatusBits(String name, int bit) {
		this.name = name;
		this.bit = bit;
	}
	public String getDescription() {
		return name;
	}
	public int getBit() {
		return bit;
	}
	public boolean bitIsSet(int word) {
		return (word & (int)Math.pow(2, bit)) > 0;
	}
	@Override
	public String toString() {
		return name;
	}

}
