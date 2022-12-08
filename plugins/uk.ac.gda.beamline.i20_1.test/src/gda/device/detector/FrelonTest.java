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
	private static final String ROI_BINNING = "roiVerticalBinning";
	private static final String ROI_START = "roiVerticalStart";
	private static final String READOUT_TIME = "accumulationReadoutTime";

	private static class EdeFrelonForTest extends EdeFrelon {
		public EdeFrelonForTest() {
			super();
			super.setAccumulationReadoutTime(0.987e-3);
		}
		public void loadSettings() {
			loadSettingsFromStore();
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
	public void readSettings() throws Exception {
		TestHelpers.setUpTest(FrelonTest.class, "readRoiSettings", true);

		// Make new configuration file for Frelon to read from :
		FileConfiguration fileConfig = getSettings();

		assertTrue(fileConfig.isEmpty());
		fileConfig.addProperty(ROI_BINNING, "11");
		fileConfig.addProperty(ROI_START, "1024");
		fileConfig.addProperty(READOUT_TIME, "0.534e-3");
		fileConfig.save();

		frelon.loadSettings();
		assertEquals(11, frelon.getRoiVerticalBinning());
		assertEquals(1024, frelon.getRoiVerticalStart());
		assertEquals(0.534e-3, frelon.getAccumulationReadoutTime(), 1e-6);

	}

	@Test
	public void saveSettings() throws Exception {
		TestHelpers.setUpTest(FrelonTest.class, "saveRoiSettings", true);
		// change roi settings (these are persisted immediately)
		frelon.setRoiVerticalBinning(64);
		frelon.setRoiVerticalStart(1234);
		frelon.setAccumulationReadoutTime(0.9e-3);

		// Check the settings in configuration file written by frelon :
		FileConfiguration fileConfig = getSettings();

		assertEquals(frelon.getRoiVerticalBinning(), fileConfig.getProperty(ROI_BINNING));
		assertEquals(frelon.getRoiVerticalStart(), fileConfig.getProperty(ROI_START));
		assertEquals(frelon.getAccumulationReadoutTime(), Double.parseDouble(fileConfig.getProperty(READOUT_TIME).toString()), 1e-6);

	}

	@Test
	public void createNewSettings() throws Exception {
		TestHelpers.setUpTest(FrelonTest.class, "createNewSettings", true);
		int binning = frelon.getRoiVerticalBinning();
		int start = frelon.getRoiVerticalStart();
		double readoutTime = frelon.getAccumulationReadoutTime();

		// Check file doesn't exist
		File f = Paths.get(LocalProperties.getVarDir(), "FrelonRoiSettings").toFile();
		assertFalse(f.exists());

		// loadSettings create new file with current binning and start values if one doesn't exist already
		frelon.loadSettings();

		FileConfiguration fileConfig = getSettings();
		assertEquals(binning, fileConfig.getProperty(ROI_BINNING));
		assertEquals(start, fileConfig.getProperty(ROI_START));
		assertEquals(readoutTime, Double.parseDouble(fileConfig.getProperty(READOUT_TIME).toString()), 1e-6);

	}

}
