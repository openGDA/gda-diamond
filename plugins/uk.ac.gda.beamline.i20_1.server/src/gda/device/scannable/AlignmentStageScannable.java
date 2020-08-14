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

import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;

import org.apache.commons.configuration.ConfigurationException;
import org.apache.commons.configuration.PropertiesConfiguration;
import org.python.core.PyString;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.gson.Gson;

import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.EnumPositionerStatus;
import gda.device.MotorStatus;
import gda.device.Scannable;
import gda.factory.FactoryException;
import uk.ac.gda.api.remoting.ServiceInterface;
import uk.ac.gda.beans.ObservableModel;

@ServiceInterface(AlignmentStage.class)
public class AlignmentStageScannable extends ScannableBase implements EnumPositioner, AlignmentStage {

	private static final Logger logger = LoggerFactory.getLogger(AlignmentStageScannable.class);
	private static final String CONFIGURATION_FILE_SUFFIX = "_alignmentConfiguration.xml";
	//	private static final AlignmentStageDevice PRIMARY_DEVICE = AlignmentStageDevice.slits;
	private static final Gson GSON = new Gson();

	public static class Location extends ObservableModel {
		public static final String X_POS_PROP_NAME = "xPosition";
		private double xPosition = 0.0;
		public static final String Y_POS_PROP_NAME = "yPosition";
		private double yPosition = 0.0;
		public static final String RELATIVE_PROP_NAME = "relative";
		private boolean relative;

		public double getxPosition() {
			return xPosition;
		}
		public void setxPosition(double value) {
			this.firePropertyChange(X_POS_PROP_NAME, xPosition, xPosition = value);
		}
		public double getyPosition() {
			return yPosition;
		}
		public void setyPosition(double value) {
			this.firePropertyChange(Y_POS_PROP_NAME, yPosition, yPosition = value);
		}
		public boolean isRelative() {
			return relative;
		}
		public void setRelative(boolean value) {
			this.firePropertyChange(Y_POS_PROP_NAME, relative, relative = value);
		}
	}

	public enum FastShutter {
		FIRST_SHUTTER_INSTANCE;

		private Location inLocation = new Location();
		private Location outLocation = new Location();

		public void save(PropertiesConfiguration configuration) {
			configuration.setProperty(this.name(), GSON.toJson(new Location[]{inLocation, outLocation}));
		}

		public void load(PropertiesConfiguration configuration) {
			if (configuration.containsKey(this.name())) {
				Location[] location = GSON.fromJson(configuration.getString(this.name()), Location[].class);
				inLocation = location[0];
				outLocation = location[1];
			}
		}

		public Location getInLocation() {
			return inLocation;
		}

		public Location getOutLocation() {
			return outLocation;
		}
	}

	public static enum AlignmentStageDevice {
		slits(false), // Horizontal slits
		eye, // x-ray eye
		foil, // Reference foil
		hole, // Hole, to be used on conjunction with a fast shutter in a separate location
		shutter, // Fast shutter. In fact this is downstream to the rest and used in conjunction with the hole.
		laser, // Laser.
		hole2; // Hole2

		private Location location;

		public Location getLocation() {
			return location;
		}

		private AlignmentStageDevice( boolean isRelative ) {
			location = new Location();
			location.setRelative( isRelative );
		}

		private AlignmentStageDevice() {
			location = new Location();
			location.setRelative( true );
			// location.setRelative((this != PRIMARY_DEVICE));
		}

		public void save(PropertiesConfiguration configuration) {
			StringBuilder json = new StringBuilder();
			GSON.toJson(location, json);
			configuration.setProperty(this.name(), json.toString());
		}

		public void load(PropertiesConfiguration configuration) {
			if (configuration.containsKey(this.name())) {
				location = GSON.fromJson((String) configuration.getProperty(this.name()), Location.class);
			}
		}

		public void moveLocation(
				Scannable xMotor,
				Scannable yMotor,
				Scannable fastShutter_xMotor,
				Scannable fastShutter_yMotor) throws DeviceException {

			//				ScannableMotor xMotor,
			//				ScannableMotor yMotor,
			//				ScannableMotor fastShutter_xMotor,
			//				ScannableMotor fastShutter_yMotor) throws DeviceException {
			// Just move to given position.
			xMotor.asynchronousMoveTo(location.xPosition);
			yMotor.asynchronousMoveTo(location.yPosition);
			/*
			if (this == PRIMARY_DEVICE) {
				xMotor.asynchronousMoveTo(location.xPosition);
				yMotor.asynchronousMoveTo(location.yPosition);
			}
			else {
				xMotor.asynchronousMoveTo(location.xPosition + PRIMARY_DEVICE.location.xPosition);
				yMotor.asynchronousMoveTo(location.yPosition + PRIMARY_DEVICE.location.yPosition);
			}
			if (this == AlignmentStageDevice.hole) {
				fastShutter_xMotor.asynchronousMoveTo(FastShutter.FIRST_SHUTTER_INSTANCE.outLocation.xPosition);
				fastShutter_yMotor.asynchronousMoveTo(FastShutter.FIRST_SHUTTER_INSTANCE.outLocation.yPosition);

			} else
			 */
			if (this == AlignmentStageDevice.shutter) {
				fastShutter_xMotor.asynchronousMoveTo(FastShutter.FIRST_SHUTTER_INSTANCE.inLocation.xPosition);
				fastShutter_yMotor.asynchronousMoveTo(FastShutter.FIRST_SHUTTER_INSTANCE.inLocation.yPosition);
			}
		}
	}
	private static final AlignmentStageDevice PRIMARY_DEVICE = AlignmentStageDevice.slits;

	// motors
	private final ScannableMotor xMotor;
	private final ScannableMotor yMotor;
	private final ScannableMotor fastShutter_xMotor;
	private final ScannableMotor fastShutter_yMotor;

	// configuration objects
	private PropertiesConfiguration configuration;
	private AlignmentStageDevice lastDemandPosition = null;

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
		if (isConfigured()) {
			return;
		}
		super.configure();
		try {
			loadConfiguration();
		} catch (IOException e) {
			throw new FactoryException("Error reading the persisted configuration file", e);
		}
		setConfigured(true);
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return xMotor.isBusy() || yMotor.isBusy();
	}

	@Override
	public String[] getPositions() throws DeviceException {
		String[] labels = new String[AlignmentStageDevice.values().length];
		for (int index = 0; index < AlignmentStageDevice.values().length; index++) {
			labels[index] = AlignmentStageDevice.values()[index].toString();
		}
		return labels;
	}

	@Override
	public List<String> getPositionsList() throws DeviceException {
		return Arrays.asList(getPositions());
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

	/**
	 * Simple implementation to check whether device is in position.<br>
	 * If there is a PV that indicates this, use that instead.
	 */
	@Override
	public boolean isInPos() throws DeviceException {
		logger.debug("Default isInPos() called");
		return getStatus() == EnumPositionerStatus.IDLE;
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		if (checkPositionValid(position) == null) {
			AlignmentStageDevice device = AlignmentStageDevice.valueOf(position.toString());
			device.moveLocation(xMotor, yMotor, fastShutter_xMotor, fastShutter_yMotor);
			lastDemandPosition = device;
		} else {
			throw new DeviceException(position + " is not an acceptable position value");
		}
	}

	@Override
	public Object rawGetPosition() throws DeviceException {

		if (lastDemandPosition == null) {
			return "unknown";
		}
		return lastDemandPosition.name();
	}

	@Override
	public String checkPositionValid(Object position) throws DeviceException {
		if (position instanceof String || position instanceof PyString) {
			String deviceName = position.toString();
			try {
				AlignmentStageDevice.valueOf(deviceName);
			} catch (Exception e) {
				return "position not in the list of acceptable positions";
			}
		}
		return "position not a string";
	}

	@Override
	public String toFormattedString() {
		try {
			// get the current position as an array of doubles
			final Object position = getPosition();

			// if position is null then simply return the name
			if (position == null) {
				logger.warn("getPosition() from {} returns NULL.", getName());
				return valueUnavailableString();
			} else {
				final String rr = createFormattedListAcceptablePositions();
				return String.format("%s : %s %s", getName(), position, rr);
			}
		} catch (Exception e) {
			logger.warn("{} : exception while getting position", getName(), e);
			return valueUnavailableString();
		}
	}

	@Override
	public void saveDeviceFromCurrentMotorPositions(Object positionName) throws ConfigurationException,
	DeviceException, IOException {
		if (checkPositionValid(positionName) == null) {
			double xMotorPos = (double) xMotor.getPosition();
			double yMotorPos = (double) yMotor.getPosition();
			AlignmentStageDevice device = AlignmentStageDevice.valueOf((String) positionName);
			if (device == PRIMARY_DEVICE) {
				device.getLocation().xPosition = xMotorPos;
				device.getLocation().yPosition = yMotorPos;
				device.getLocation().setRelative(false);
			} else {
				device.getLocation().setRelative(true);
				device.getLocation().xPosition = xMotorPos - PRIMARY_DEVICE.getLocation().xPosition;
				device.getLocation().yPosition = yMotorPos - PRIMARY_DEVICE.getLocation().yPosition;
			}
			saveConfiguration();
		}
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
		FastShutter.FIRST_SHUTTER_INSTANCE.load(configuration);
		for (AlignmentStageDevice dev : AlignmentStageDevice.values()) {
			dev.load(configuration);
		}
		logger.info("Configuration file loaded.");
	}

	private void openConfigurationFile() throws IOException {
		if (configuration != null) {
			return;
		}
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
			configuration = new PropertiesConfiguration();
			configuration.setDelimiterParsingDisabled(true);
			configuration.load(propertiesFileName);
			logger.info("Configuration file " + propertiesFileName + " opened.");
		} catch (ConfigurationException e) {
			throw new IOException("ConfigurationException trying to open file: " + e.toString(), e);
		}
	}

	private void saveConfiguration() throws ConfigurationException, IOException {
		openConfigurationFile();
		for (AlignmentStageDevice device : AlignmentStageDevice.values()) {
			device.save(configuration);
		}
		FastShutter.FIRST_SHUTTER_INSTANCE.save(configuration);
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

	@Override
	public AlignmentStageDevice getAlignmentStageDevice(String name) {
		return AlignmentStageDevice.valueOf(name);
	}

	@Override
	public FastShutter getFastShutter() {
		return FastShutter.FIRST_SHUTTER_INSTANCE;
	}
}
