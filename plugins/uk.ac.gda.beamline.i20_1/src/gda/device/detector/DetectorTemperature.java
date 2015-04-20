/*-
 * Copyright © 2015 Diamond Light Source Ltd.
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

package gda.device.detector;

import gda.device.DeviceException;

import java.util.HashMap;

import org.eclipse.dawnsci.analysis.api.dataset.IDataset;

public interface DetectorTemperature {
	HashMap<String, Double> getTemperatures() throws DeviceException;
	/**
	 * Fetches the logged temperatures since the last time startTemperatureLogging called.
	 * <p>
	 * time is in epoch seconds.
	 *
	 * @return an array of Datasets: time, temp for sensor1, temp for sensor 2 etc.
	 * @throws DeviceException
	 */
	IDataset[][] fetchTemperatureData() throws DeviceException;

	public void startTemperatureLogging() throws DeviceException;

	public void stopTemperatureLogging() throws DeviceException;

	/**
	 * This will be a file of format LocalProperties.getVarDir() + getName() + "_temperatures_" + today's date + ".log";
	 *
	 * @return String - full path to the current fiel being written to.
	 */
	public String getTemperatureLogFile();

}
