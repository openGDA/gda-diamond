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
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.apache.commons.configuration.ConfigurationException;
import org.apache.commons.configuration.PropertiesConfiguration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.EnumPositionerStatus;
import gda.device.MotorStatus;
import gda.factory.FactoryException;
import gda.scan.ede.position.Location;
import uk.ac.gda.api.remoting.ServiceInterface;

@ServiceInterface(AlignmentStage.class)
public class AlignmentStageScannable extends ScannableBase implements EnumPositioner, AlignmentStage {

	private static final Logger logger = LoggerFactory.getLogger(AlignmentStageScannable.class);
	private static final String CONFIGURATION_FILE_SUFFIX = "_alignmentConfiguration.xml";

	// motors
	private ScannableMotor xMotor;
	private ScannableMotor yMotor;

	private List<Location> devicePositions = new ArrayList<>();
	private List<Location> defaultLocations = new ArrayList<>();

	private String lastDemandPosition = "";

	public AlignmentStageScannable() {
	}

	public AlignmentStageScannable(ScannableMotor xMotor, ScannableMotor yMotor) {
		this.xMotor = xMotor;
		this.yMotor = yMotor;
	}

	@Override
	public void configure() throws FactoryException {
		if (isConfigured()) {
			return;
		}
		Optional.ofNullable(xMotor).orElseThrow(() -> new FactoryException("xMotor has not been set"));
		Optional.ofNullable(yMotor).orElseThrow(() -> new FactoryException("yMotor has not been set"));

		this.setOutputFormat(new String[] { "%s" });

		super.configure();
		try {
			loadConfiguration();
			if (getLocations().isEmpty()) {
				logger.info("No locations found in configuration store - setting the defaults");
				if (defaultLocations.isEmpty()) {
					setDefaultLocations(createDefaultLocations());
				}
				defaultLocations.stream().forEach(this::setLocation);

			}
		} catch (IOException e) {
			throw new FactoryException("Error reading the persisted configuration file", e);
		}
		setConfigured(true);
	}


	@Override
	public Location getLocation(String name) {
		return devicePositions
				.stream()
				.filter(loc -> loc.getName().equals(name))
				.findFirst()
				.orElse(null);
	}

	@Override
	public boolean hasLocation(String name) {
		return getLocation(name) != null;
	}

	@Override
	public void setLocation(Location location) {
		devicePositions.add(location);
	}

	@Override
	public List<Location> getLocations() {
		return devicePositions;
	}

	@Override
	public void clearLocations() {
		devicePositions.clear();
	}

	@Override
	public void moveToLocation(Location location) throws DeviceException {
		logger.info("Moving to {} location ({}, {})", location.getName(), location.getxPosition(), location.getyPosition());
		yMotor.asynchronousMoveTo(location.getyPosition());
		xMotor.asynchronousMoveTo(location.getxPosition());
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return xMotor.isBusy() || yMotor.isBusy();
	}

	@Override
	public String[] getPositions() throws DeviceException {
		return getLocations()
				.stream()
				.map(Location::getName)
				.toArray(String[]::new);
	}

	@Override
	public List<String> getPositionsList() throws DeviceException {
		return getLocations()
				.stream()
				.map(Location::getName)
				.collect(Collectors.toList());
	}

	@Override
	public EnumPositionerStatus getStatus() throws DeviceException {
		if (isBusy()) {
			return EnumPositionerStatus.MOVING;
		} else if (xMotor.getMotor().getStatus() == MotorStatus.FAULT
				|| yMotor.getMotor().getStatus() == MotorStatus.FAULT) {
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
		if (!hasLocation(position.toString())) {
			throw new DeviceException(position + " is not an acceptable position value");
		}
		Location location = getLocation(position.toString());
		moveToLocation(location);
		lastDemandPosition = position.toString();
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		if (lastDemandPosition == null) {
			return "unknown";
		}
		return lastDemandPosition;
	}

	@Override
	public void stop() throws DeviceException {
		xMotor.stop();
		yMotor.stop();
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

	private String createFormattedListAcceptablePositions() throws DeviceException {
		return getLocations()
			.stream()
			.map(loc -> "'"+loc.getName()+"'")
			.collect(Collectors.joining(" ", "(", ")"));
	}

	private PropertiesConfiguration openConfigurationFile() throws IOException {
		Path propertiesFileName = getFilePath();
		if (!Files.isRegularFile(propertiesFileName)) {
			logger.info("Configuration file not found - creating new empty one");
			if(!propertiesFileName.getParent().toFile().exists()) {
				propertiesFileName.getParent().toFile().mkdirs();
			}
			Files.createFile(propertiesFileName);
		}
		PropertiesConfiguration configuration = new PropertiesConfiguration();
		configuration.setDelimiterParsingDisabled(true);
		logger.info("Configuration file {} ready to open", propertiesFileName);
		return configuration;

	}

	@Override
	public void saveConfiguration() throws IOException {
		PropertiesConfiguration configuration = openConfigurationFile();
		configuration.clear();
		getLocations().forEach(l -> l.save(configuration));

		try {
			configuration.save(getFilePath().toFile());
		} catch (ConfigurationException e) {
			throw new IOException("Problem saving AlignmentStageScannable configuration to "+getFilePath().toString(), e);
		}
		logger.info("Configuration file saved to {}", getFilePath());
	}

	/**
	 * Reload the positions from the file.
	 *
	 * @throws IOException
	 */
	@Override
	public void loadConfiguration() throws IOException {
		PropertiesConfiguration configuration = openConfigurationFile();
		try {
			configuration.load(getFilePath().toFile());
		} catch (ConfigurationException e) {
			throw new IOException("ConfigurationException trying to open file:  " + e.toString(), e);
		}
		clearLocations();
		Iterator<String> keys = configuration.getKeys();
		keys.forEachRemaining(k -> setLocation(Location.fromJson(configuration.getString(k))));
		logger.info("Configuration file loaded.");
	}

	private Path getFilePath() {
		return Paths.get(LocalProperties.getVarDir(), getName() + CONFIGURATION_FILE_SUFFIX);
	}


	private enum DefaultLocation {
		EYE("eye", "X-ray eye"),
		SLITS("slits", "Slits"),
		FOIL("foil", "Foils"),
		HOLE("hole", "Hole"),
		HOLE2("hole2", "Hole2"),
		LASER("laser", "Laser");

		private final Location loc;
		private DefaultLocation(String name, String label) {
			loc = new Location(name, label);
		}
		public Location getLocation() {
			return loc;
		}
	}

	public List<Location> createDefaultLocations() {
		return Stream.of(DefaultLocation.values())
			.map(DefaultLocation::getLocation)
			.collect(Collectors.toList());
	}

	public List<Location> getDefaultLocations() {
		return defaultLocations;
	}

	public void setDefaultLocations(List<Location> defaultLocations) {
		if (defaultLocations == null) {
			return;
		}
		this.defaultLocations = new ArrayList<>(defaultLocations);
	}

	public void setxMotor(ScannableMotor xMotor) {
		this.xMotor = xMotor;
	}

	public void setyMotor(ScannableMotor yMotor) {
		this.yMotor = yMotor;
	}

	public ScannableMotor getxMotor() {
		return xMotor;
	}

	public ScannableMotor getyMotor() {
		return yMotor;
	}
}
