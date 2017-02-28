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

package gda.device.detector.xstrip;

import gda.device.DeviceException;

import java.util.HashMap;

import org.eclipse.dawnsci.analysis.api.dataset.IDataset;

/**
 * Sub-interface for functionality specifically relating the XH and XStrip detectors.
 * <p>
 * XCHIP relates to the common electronics of those two read heads.
 */
public interface XCHIPDetector extends StripDetector {


	@Override
	HashMap<String, Double> getTemperatures() throws DeviceException;

	/**
	 * Given, in seconds, the frame time and the scan time, returns back the number of scans which would be fitted into
	 * the frame.
	 * <p>
	 * As the rules for this are complicated and potentially variable depending on settings inside da.server, the logic
	 * is held within da.server and so this value must be fetched from da.server every time.
	 *
	 * @param frameTime
	 * @param scanTime
	 * @param numberOfFrames
	 * @return int the number of scans which would fit into the given frame
	 * @throws DeviceException
	 */
	@Override
	int getNumberScansInFrame(double frameTime, double scanTime, int numberOfFrames) throws DeviceException;

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
