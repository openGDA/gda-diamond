/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;

import org.eclipse.january.dataset.IDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.detector.DAServer;
import gda.device.detector.DetectorTemperature;
import gda.jython.InterfaceProvider;
import uk.ac.gda.exafs.detectortemperature.XCHIPTemperatureLogParser;


public class XhDetectorTemperature implements DetectorTemperature {

	private static final Logger logger = LoggerFactory.getLogger(XhDetectorTemperature.class);

	private static final String SENSOR0NAME = "Peltier Hotplate";
	private static final String SENSOR1NAME = "Peltier Coldplate";
	private static final String SENSOR2NAME = "PCB power supply";
	private static final String SENSOR3NAME = "PCB control";

	private String temperatureLogFilename;

	private final DAServer daServer;
	private final String name;

	public XhDetectorTemperature(DAServer daServer, String name) {
		this.daServer = daServer;
		this.name = name;
	}

	@Override
	public HashMap<String, Double> getTemperatures() throws DeviceException {
		openTCSocket();

		HashMap<String, Double> temps = new HashMap<String, Double>();
		Double sensor0Temp = Double.parseDouble(daServer.sendCommand("xstrip tc get \"" + name + "\" ch 0 t")
				.toString());
		temps.put(SENSOR0NAME, sensor0Temp);
		Double sensor1Temp = Double.parseDouble(daServer.sendCommand("xstrip tc get \"" + name + "\" ch 1 t")
				.toString());
		temps.put(SENSOR1NAME, sensor1Temp);
		Double sensor2Temp = Double.parseDouble(daServer.sendCommand("xstrip tc get \"" + name + "\" ch 2 t")
				.toString());
		temps.put(SENSOR2NAME, sensor2Temp);
		Double sensor3Temp = Double.parseDouble(daServer.sendCommand("xstrip tc get \"" + name + "\" ch 3 t")
				.toString());
		temps.put(SENSOR3NAME, sensor3Temp);
		return temps;
	}

	private void openTCSocket() throws DeviceException {
		int tcIsOpen = (int) daServer.sendCommand("xstrip tc print \"" + name + "\"");
		if (tcIsOpen == -1) {
			daServer.sendCommand("xstrip tc open \"" + name + "\"");
			tcIsOpen = (int) daServer.sendCommand("xstrip tc print \"" + name + "\"");
			if (tcIsOpen == -1) {
				throw new DeviceException(
						"Could not open temperature controller to find out current temperature values");
			}
		}
	}

	@Override
	public IDataset[][] fetchTemperatureData() {
		return new XCHIPTemperatureLogParser(temperatureLogFilename).getTemperatures();
	}

	@Override
	public String getTemperatureLogFile() {
		return temperatureLogFilename;
	}

	@Override
	public void startTemperatureLogging() throws DeviceException {
		// derive the filename
		DateFormat dateFormat = new SimpleDateFormat("yyyy_MM_dd_HH_mm_ss");
		Date date = new Date();
		temperatureLogFilename = InterfaceProvider.getPathConstructor().createFromDefaultProperty() + "spool/" + name + "_temperatures_"
				+ dateFormat.format(date) + ".log";

		// tell the detector to start temp logging to the filename
		int result = (int) daServer.sendCommand("xstrip tc set \"xh0\" autoinc -1 logt '" + temperatureLogFilename +"'");
		if (result == -1) {
			throw new DeviceException("Failed to start logging " + name + " tempratures to " + temperatureLogFilename);
		}

		logger.info(name + " temperatures now being logged to " + temperatureLogFilename);

	}

	@Override
	public void stopTemperatureLogging() throws DeviceException {
		// tell the detector to start temp logging to the filename
		int result = (int) daServer.sendCommand("xstrip tc set \""+ name +"\" autoinc 0");
		if (result == -1) {
			throw new DeviceException("Failed to start logging " + name + " tempratures to " + temperatureLogFilename);
		}

		logger.info(name + " temperature logging stopped.");

	}
}
