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

import java.io.IOException;
import java.util.List;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.scan.ede.position.Location;

public interface AlignmentStage extends Scannable {

	List<Location> getLocations();

	Location getLocation(String name);

	boolean hasLocation(String name);

	void setLocation(Location loc);

	void clearLocations();

	void moveToLocation(Location location) throws DeviceException;

	void saveConfiguration() throws IOException;

	/**
	 * Reload the positions from the file.
	 *
	 * @throws IOException
	 */
	void loadConfiguration() throws IOException;

}
