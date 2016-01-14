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

import gda.device.DeviceException;

public interface EdeScanPosition {

	/** Move all scan position motors from their current to final position */
	public abstract void moveIntoPosition() throws DeviceException, InterruptedException;

	public abstract EdePositionType getType();

	/** Return estimate of the time needed to perform {@link #moveIntoPosition()} */
	public abstract double getTimeToMove();

}