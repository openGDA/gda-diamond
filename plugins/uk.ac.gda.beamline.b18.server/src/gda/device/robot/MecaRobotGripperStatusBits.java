/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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
 * Meca 'gripper status' bits
 */
public enum MecaRobotGripperStatusBits {
	Detected("Enabled", 0),
	Homed("Homed", 1),
	Holding_Part("Holding part", 2),
	Limit_Reached("Limit reached", 3),
	Error("Error", 4),
	Overload("Overload", 5);

	private final String name;
	private final int bit;
	private MecaRobotGripperStatusBits(String name, int bit) {
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


