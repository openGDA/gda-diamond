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

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertThrows;
import static org.junit.Assert.assertTrue;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

import org.apache.commons.configuration.ConfigurationException;
import org.apache.commons.configuration.PropertiesConfiguration;
import org.junit.Before;
import org.junit.Test;
import org.mockito.ArgumentMatchers;
import org.mockito.Mockito;

import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.factory.FactoryException;
import gda.scan.ede.position.Location;

public class AlignmentStageScannableTest {

	private AlignmentStageScannable alignmentStageScn = new AlignmentStageScannable();
	private ScannableMotor xMotor;
	private ScannableMotor yMotor;

	@Before
	public void setup() {
		xMotor = Mockito.mock(ScannableMotor.class);
		yMotor = Mockito.mock(ScannableMotor.class);
		alignmentStageScn.setName("alignmentStageScn");
		alignmentStageScn.setxMotor(xMotor);
		alignmentStageScn.setyMotor(yMotor);
	}

	@Test(expected = FactoryException.class)
	public void testConfigureFailsWithMissingXMotor() throws FactoryException {
		alignmentStageScn.setxMotor(null);
		alignmentStageScn.configure();
	}

	@Test(expected = FactoryException.class)
	public void testConfigureFailWithMissingYMotor() throws FactoryException {
		alignmentStageScn.setyMotor(null);
		alignmentStageScn.configure();
	}

	/**
	 * Check configuration file has been written to var directory,
	 * @return PropertiesConfiguration containing the config loaded from file.
	 * @throws ConfigurationException
	 */
	private PropertiesConfiguration loadTestConfigFile() throws ConfigurationException {
		// Check config file has been written
		Path dir = Paths.get(LocalProperties.getVarDir(), "/" );
		File[] configFile = dir.toFile().listFiles(f -> f.getName().endsWith(".xml"));
		assertNotNull(configFile);
		assertTrue(configFile[0].isFile());

		// Load the config file and check the contents
		PropertiesConfiguration config = new PropertiesConfiguration();
		config.setDelimiterParsingDisabled(true);
		config.load(configFile[0]);

		return config;
	}

	/**
	 * Check to see if Locations stored in the {@link PropertiesConfiguration} match those in the {@link AlignmentStageScannable}
	 * @param scn AlignmentStageScannable object
	 * @param config PropertiesConfiguration
	 */
	private void testConfigurationValues(AlignmentStageScannable scn, PropertiesConfiguration config) {
		// Get the JSon Location values from the PropertiesConfiguration
		List<String> locationsFromStore = new ArrayList<>();
		config.getKeys().forEachRemaining(key -> locationsFromStore.add(config.getString(key)));

		// Get Json Location values from the scannable and test against values in AlignmentStageScannable
		List<String> locationJsonStrings = scn.getLocations().stream().map(l -> l.toJson()).collect(Collectors.toList());
		assertEquals(locationJsonStrings, locationsFromStore);
	}

	@Test
	public void testDefaultsSaveToFile() throws Exception {
		TestHelpers.setUpTest(AlignmentStageScannableTest.class, "testDefaultsSaveToFile", true);
		alignmentStageScn.configure();
		alignmentStageScn.saveConfiguration();

		PropertiesConfiguration config = loadTestConfigFile();
		testConfigurationValues(alignmentStageScn, config);
	}

	private List<Location> getLocations() {
		return Arrays.asList( Location.create("loc1", "Location 1", 1.0, 61.0),
				Location.create("loc2", "Location 2", 2.0, 71.0),
				Location.create("loc3", "Location 3", 3.0, 81.0),
				Location.create("loc4", "Location 4", 4.0, 91.0) );
	}

	@Test
	public void testConfigSaveToFile() throws Exception {
		TestHelpers.setUpTest(AlignmentStageScannableTest.class, "testConfigSaveToFile", true);
		alignmentStageScn.configure();
		alignmentStageScn.clearLocations();
		getLocations().forEach(alignmentStageScn::setLocation);
		alignmentStageScn.saveConfiguration();

		PropertiesConfiguration config = loadTestConfigFile();
		testConfigurationValues(alignmentStageScn, config);
	}

	@Test
	public void testMove() throws FactoryException, DeviceException {
		alignmentStageScn.configure();

		// Make the Location positions unique so mockito.verify can work properly
		Collection<Location> locations = alignmentStageScn.getLocations();
		AtomicInteger count = new AtomicInteger(0);
		locations.forEach(l -> {
			double c = count.getAndIncrement();
			l.setxPosition(c);
			l.setyPosition(c+0.5);
		});

		// Check the motor moves are made to correct locations
		for(Location loc : locations) {
			alignmentStageScn.moveTo(loc.getName());
			Mockito.verify(xMotor).asynchronousMoveTo(loc.getxPosition());
			Mockito.verify(yMotor).asynchronousMoveTo(loc.getyPosition());
			assertEquals(loc.getName(), alignmentStageScn.rawGetPosition());
		}
	}

	@Test
	public void testMoveFailsForUnknownPosition() throws FactoryException, DeviceException {
		alignmentStageScn.configure();
		assertThrows(DeviceException.class, () -> alignmentStageScn.moveTo("unknown position"));
		Mockito.verify(xMotor, Mockito.never()).asynchronousMoveTo(ArgumentMatchers.anyDouble());
		Mockito.verify(yMotor, Mockito.never()).asynchronousMoveTo(ArgumentMatchers.anyDouble());

	}

}
