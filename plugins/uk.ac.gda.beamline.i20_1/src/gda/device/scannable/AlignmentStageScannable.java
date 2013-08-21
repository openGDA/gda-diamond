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

import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.EnumPositionerStatus;
import gda.device.MotorStatus;
import gda.factory.FactoryException;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;

import org.apache.commons.configuration.ConfigurationException;
import org.apache.commons.configuration.PropertiesConfiguration;
import org.apache.commons.lang.ArrayUtils;
import org.python.core.PyException;
import org.python.core.PyString;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AlignmentStageScannable extends ScannableBase implements EnumPositioner {

	private static final Logger logger = LoggerFactory.getLogger(AlignmentStageScannable.class);
	private static final String Y_POSITION_PROPERTY_SUFFIX = "_yPosition";
	private static final String X_POSITION_PROPERTY_SUFFIX = "_xPosition";
	private static final String IS_RELATIVE_PROPERTY_SUFFIX = "_relative";
	private static final String FAST_SHUTTER_INBEAM_PROPERTY_PREFIX = "FastShutter_InBeam";
	private static final String FAST_SHUTTER_OUTBEAM_PROPERTY_PREFIX = "FastShutter_OutBeam";
	private static final String CONFIGURATION_FILE_SUFFIX = "_alignmentConfiguration.xml";
	private static final Devices PRIMARY_DEVICE = Devices.slits;

	public static enum Devices {
		/**
		 * Horizontal slits
		 */
		slits,
		/**
		 * x-ray eye
		 */
		eye,
		/**
		 * Reference foil
		 */
		foil,
		/**
		 * Hole, to be used on conjunction with a fast shutter in a separate location
		 */
		hole,
		/**
		 * Fast shutter. In fact this is downstream to the rest and used in conjunction with the hole.
		 */
		shutter;

		public static Devices getDevice(String name){
			for(Devices device : Devices.values()){
				if (name.equals(device.toString())){
					return device;
				}
			}
			return null;
		}
	}

	// motors
	private final ScannableMotor xMotor;
	private final ScannableMotor yMotor;
	private final ScannableMotor fastShutter_xMotor;
	private final ScannableMotor fastShutter_yMotor;

	// configuration objects
	private PropertiesConfiguration configuration;
	private final HashMap<Devices, AlignmentLocation> deviceLocations = new HashMap<Devices, AlignmentLocation>();
	private AlignmentLocation fastShutterInBeamLocation = new AlignmentLocation();
	private AlignmentLocation fastShutterOutBeamLocation = new AlignmentLocation();
	private AlignmentLocation lastDemandPosition = null;

	public AlignmentStageScannable(ScannableMotor xMotor, ScannableMotor yMotor, ScannableMotor fastShutter_xMotor,
			ScannableMotor fastShutter_yMotor) {
		this.xMotor = xMotor;
		this.yMotor = yMotor;
		this.fastShutter_xMotor = fastShutter_xMotor;
		this.fastShutter_yMotor = fastShutter_yMotor;
		this.setOutputFormat(new String[] { "%s" });
	}

	@Override
	public void configure() throws FactoryException {
		super.configure();
		try {
			loadConfiguration();
		} catch (IOException e) {
			throw new FactoryException("Error reading the persisted configuration file", e);
		}
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return xMotor.isBusy() || yMotor.isBusy();
	}

	@Override
	public String[] getPositions() throws DeviceException {
		String[] labels = new String[Devices.values().length];
		for (int index = 0; index < Devices.values().length; index++) {
			labels[index] = Devices.values()[index].toString();
		}
		return labels;
	}

	@Override
	public EnumPositionerStatus getStatus() throws DeviceException {
		if (isBusy()) {
			return EnumPositionerStatus.MOVING;
		} else if (xMotor.getMotor().getStatus() == MotorStatus.FAULT
				|| yMotor.getMotor().getStatus() == MotorStatus.FAULT
				|| fastShutter_xMotor.getMotor().getStatus() == MotorStatus.FAULT
				|| fastShutter_yMotor.getMotor().getStatus() == MotorStatus.FAULT) {
			return EnumPositionerStatus.ERROR;
		}
		return EnumPositionerStatus.IDLE;
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		if (checkPositionValid(position) == null) {
			// ignore case when string matching
			try {
				Devices enumval = Devices.valueOf(position.toString());
				switch (enumval) {
				case slits:
				case hole:
				case foil:
				case eye:
					moveToLocation(enumval, true);
					break;
				case shutter:
					moveToLocation(enumval, false);
					break;
				default:
					throw new DeviceException("Demand position " + position + " is not a valid position.");
				}
			} catch (DeviceException e) {
				lastDemandPosition = null;
				logger.error("Exception when moving " + getName() + ": " + e.getMessage(), e);
			}
		} else {
			throw new DeviceException(position + " is not an acceptable position value");
		}
	}

	private void moveToLocation(Devices enumval, Boolean moveShutterOutOfBeam) throws DeviceException {
		AlignmentLocation slitsLoc = deviceLocations.get(enumval);
		Double newX = slitsLoc.xPosition;
		Double newY = slitsLoc.xPosition;
		if (slitsLoc.isRelative) {
			newX += getPrimaryXPosition();
			newY += getPrimaryYPosition();
		}
		xMotor.asynchronousMoveTo(newX);
		yMotor.asynchronousMoveTo(newY);
		if (moveShutterOutOfBeam) {
			fastShutter_xMotor.asynchronousMoveTo(fastShutterOutBeamLocation.xPosition);
			fastShutter_yMotor.asynchronousMoveTo(fastShutterOutBeamLocation.yPosition);
		} else {
			fastShutter_xMotor.asynchronousMoveTo(fastShutterInBeamLocation.xPosition);
			fastShutter_yMotor.asynchronousMoveTo(fastShutterInBeamLocation.yPosition);
		}
		lastDemandPosition = slitsLoc;
	}

	private Double getPrimaryXPosition() {
		AlignmentLocation primaryLoc = deviceLocations.get(PRIMARY_DEVICE);
		return primaryLoc.xPosition;
	}

	private Double getPrimaryYPosition() {
		AlignmentLocation primaryLoc = deviceLocations.get(PRIMARY_DEVICE);
		return primaryLoc.yPosition;
	}

	@Override
	public Object rawGetPosition() throws DeviceException {

		if (lastDemandPosition == null) {
			return "unknown";
		}
		return lastDemandPosition.label;
	}

	@Override
	public String checkPositionValid(Object position) throws DeviceException {
		if (position instanceof String || position instanceof PyString) {
			String pos = position.toString();
			if (ArrayUtils.contains(getPositions(), pos)) {
				return null;
			}
			return "position not in the list of acceptable positions";
		}
		return "position not a string";
	}

	@Override
	public String toFormattedString() {
		try {

			// get the current position as an array of doubles
			Object position = getPosition();

			// if position is null then simply return the name
			if (position == null) {
				logger.warn("getPosition() from " + getName() + " returns NULL.");
				return getName() + " : Unknown";
			}
			String rr = createFormattedListAcceptablePositions();

			return getName() + " : " + position.toString() + " " + rr;

		} catch (PyException e) {
			logger.info(getName() + ": jython exception while getting position. " + e.toString());
			return getName() + " : NOT AVAILABLE";
		} catch (Exception e) {
			logger.info(getName() + ": exception while getting position. " + e.getMessage() + "; " + e.getCause(), e);
			return getName() + " : NOT AVAILABLE";
		}
	}

	private void saveDeviceFromCurrentMotorPositions(String positionName, Boolean storeAsRelative)
			throws ConfigurationException, DeviceException, IOException {
		if (checkPositionValid(positionName) == null) {
			AlignmentLocation loc = deviceLocations.get(Devices.valueOf(positionName));
			Double xMotorPos = (Double) xMotor.getPosition();
			Double yMotorPos = (Double) yMotor.getPosition();
			if (storeAsRelative && loc.label.compareTo(PRIMARY_DEVICE.name()) == 0) {
				throw new DeviceException("Trying to svae primary location as relative!!");
			} else if (!storeAsRelative) {
				loc.isRelative = false;
				loc.xPosition = xMotorPos;
				loc.yPosition = yMotorPos;
			} else {
				loc.isRelative = true;
				loc.xPosition = xMotorPos - getPrimaryXPosition();
				loc.yPosition = yMotorPos - getPrimaryYPosition();
			}
			saveConfiguration();
		}
	}

	public void saveDeviceFromCurrentMotorPositions(String positionName) throws ConfigurationException,
	DeviceException, IOException {
		saveDeviceFromCurrentMotorPositions(positionName, positionName.compareTo(PRIMARY_DEVICE.name()) != 0);
	}

	private String createFormattedListAcceptablePositions() throws DeviceException {
		String[] posLables = getPositions();
		String rr = "(";
		for (String s : posLables) {
			rr += "'" + s + "' ";
		}
		rr = rr.trim() + ")";
		return rr;
	}

	/**
	 * Reload the positions from the file.
	 * 
	 * @throws IOException
	 */
	public void loadConfiguration() throws IOException {
		openConfigurationFile();

		AlignmentLocation newLocation1 = new AlignmentLocation();
		newLocation1.label = FAST_SHUTTER_INBEAM_PROPERTY_PREFIX;
		newLocation1.xPosition = configuration.getDouble(FAST_SHUTTER_INBEAM_PROPERTY_PREFIX
				+ X_POSITION_PROPERTY_SUFFIX, 0.0);
		newLocation1.yPosition = configuration.getDouble(FAST_SHUTTER_INBEAM_PROPERTY_PREFIX
				+ Y_POSITION_PROPERTY_SUFFIX, 0.0);
		newLocation1.isRelative = false;
		fastShutterInBeamLocation = newLocation1;

		AlignmentLocation newLocation2 = new AlignmentLocation();
		newLocation2.label = FAST_SHUTTER_OUTBEAM_PROPERTY_PREFIX;
		newLocation2.xPosition = configuration.getDouble(FAST_SHUTTER_OUTBEAM_PROPERTY_PREFIX
				+ X_POSITION_PROPERTY_SUFFIX, 0.0);
		newLocation2.yPosition = configuration.getDouble(FAST_SHUTTER_OUTBEAM_PROPERTY_PREFIX
				+ Y_POSITION_PROPERTY_SUFFIX, 0.0);
		newLocation2.isRelative = false;
		fastShutterOutBeamLocation = newLocation2;

		for (Devices dev : Devices.values()) {
			AlignmentLocation loc = new AlignmentLocation();
			if (deviceLocations.containsKey(dev.toString())
					&& configuration.containsKey(dev.toString() + X_POSITION_PROPERTY_SUFFIX)) {
				loc.label = dev.toString();
				loc.xPosition = configuration.getDouble(loc.label + X_POSITION_PROPERTY_SUFFIX);
				loc.yPosition = configuration.getDouble(loc.label + Y_POSITION_PROPERTY_SUFFIX);
				loc.isRelative = configuration.getBoolean(loc.label + IS_RELATIVE_PROPERTY_SUFFIX);
			} else {
				loc.label = dev.toString();
				loc.xPosition = 0.0;
				loc.yPosition = 0.0;
				loc.isRelative = loc.label.compareTo(PRIMARY_DEVICE.toString()) == 0 ? false : true;
			}
			deviceLocations.put(dev, loc);
		}

		logger.info("Configuration file loaded.");
	}

	private void openConfigurationFile() throws IOException {
		String propertiesFileName = getFileName();
		File test = new File(propertiesFileName);
		if (!test.exists()) {
			try {
				test.createNewFile();
			} catch (IOException e) {
				throw e;
			}
		}
		try {
			configuration = new PropertiesConfiguration(propertiesFileName);
			logger.info("Configuration file " + propertiesFileName + " opened.");
		} catch (ConfigurationException e) {
			throw new IOException("ConfigurationException trying to open file: " + e.toString(), e);
		}
	}

	private void saveConfiguration() throws ConfigurationException, IOException {

		if (configuration == null) {
			openConfigurationFile();
		}

		for (AlignmentLocation loc : deviceLocations.values()) {
			configuration.setProperty(loc.label + X_POSITION_PROPERTY_SUFFIX, loc.xPosition);
			configuration.setProperty(loc.label + Y_POSITION_PROPERTY_SUFFIX, loc.yPosition);
			configuration.setProperty(loc.label + IS_RELATIVE_PROPERTY_SUFFIX, loc.isRelative);
		}

		configuration.setProperty(fastShutterInBeamLocation.label + X_POSITION_PROPERTY_SUFFIX,
				fastShutterInBeamLocation.xPosition);
		configuration.setProperty(fastShutterInBeamLocation.label + Y_POSITION_PROPERTY_SUFFIX,
				fastShutterInBeamLocation.yPosition);
		configuration.setProperty(fastShutterOutBeamLocation.label + X_POSITION_PROPERTY_SUFFIX,
				fastShutterOutBeamLocation.xPosition);
		configuration.setProperty(fastShutterOutBeamLocation.label + Y_POSITION_PROPERTY_SUFFIX,
				fastShutterOutBeamLocation.yPosition);

		configuration.save();

		logger.info("Configuration file saved.");
	}

	private String getFileName() {
		String propertiesFileName = LocalProperties.getVarDir() + getName() + CONFIGURATION_FILE_SUFFIX;
		return propertiesFileName;
	}

	public ScannableMotor getxMotor() {
		return xMotor;
	}

	public ScannableMotor getyMotor() {
		return yMotor;
	}

	public ScannableMotor getFastShutter_xMotor() {
		return fastShutter_xMotor;
	}

	public ScannableMotor getFastShutter_yMotor() {
		return fastShutter_yMotor;
	}
}

class AlignmentLocation {
	Double xPosition;
	Double yPosition;
	String label;
	Boolean isRelative;
}
