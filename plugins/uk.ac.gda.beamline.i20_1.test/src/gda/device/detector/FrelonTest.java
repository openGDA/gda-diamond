/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.io.File;
import java.io.IOException;
import java.nio.file.Paths;

import org.apache.commons.configuration.ConfigurationException;
import org.apache.commons.configuration.FileConfiguration;
import org.junit.Before;
import org.junit.Test;

import gda.TestHelpers;
import gda.configuration.properties.LocalProperties;
import gda.device.detector.frelon.EdeFrelon;
import uk.ac.diamond.daq.persistence.jythonshelf.LocalParameters;

public class FrelonTest {

	private EdeFrelonForTest frelon;

	private static class EdeFrelonForTest extends EdeFrelon {
		public void loadRoiSettings() {
			loadRoiSettingsFromStore();
		}
	}

	@Before
	public void setup() {
		frelon = new EdeFrelonForTest();
	}

	private FileConfiguration getSettings() throws ConfigurationException, IOException {
		return LocalParameters.getXMLConfiguration("FrelonRoiSettings");
	}

	@Test
	public void readRoiSettings() throws Exception {
		TestHelpers.setUpTest(FrelonTest.class, "readRoiSettings", true);

		// Make new configuration file for Frelon to read from :
		FileConfiguration fileConfig = getSettings();

		assertTrue(fileConfig.isEmpty());
		fileConfig.addProperty("roiVerticalBinning", "11");
		fileConfig.addProperty("roiVerticalStart", "1024");
		fileConfig.save();

		frelon.loadRoiSettings();
		assertEquals(11, frelon.getRoiVerticalBinning());
		assertEquals(1024, frelon.getRoiVerticalStart());
	}

	@Test
	public void saveRoiSettings() throws Exception {
		TestHelpers.setUpTest(FrelonTest.class, "saveRoiSettings", true);
		// change roi settings (these are persisted immediately)
		frelon.setRoiVerticalBinning(64);
		frelon.setRoiVerticalStart(1234);

		// Check the settings in configuration file written by frelon :
		FileConfiguration fileConfig = getSettings();

		assertEquals(frelon.getRoiVerticalBinning(), fileConfig.getProperty("roiVerticalBinning"));
		assertEquals(frelon.getRoiVerticalStart(), fileConfig.getProperty("roiVerticalStart"));
	}

	@Test
	public void createRoiDefaultSettings() throws Exception {
		TestHelpers.setUpTest(FrelonTest.class, "createRoiDefaultSettings", true);
		int binning = frelon.getRoiVerticalBinning();
		int start = frelon.getRoiVerticalStart();

		// Check file doesn't exist
		File f = Paths.get(LocalProperties.getVarDir(), "FrelonRoiSettings").toFile();
		assertFalse(f.exists());

		// loadSettings create new file with current binning and start values if one doesn't exist already
		frelon.loadRoiSettings();

		FileConfiguration fileConfig = getSettings();
		assertEquals(binning, fileConfig.getProperty("roiVerticalBinning"));
		assertEquals(start, fileConfig.getProperty("roiVerticalStart"));
	}

}
