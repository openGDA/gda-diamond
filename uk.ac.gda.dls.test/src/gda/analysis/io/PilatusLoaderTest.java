/*-
 * Copyright © 2009 Diamond Light Source Ltd., Science and Technology
 * Facilities Council
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

package gda.analysis.io;

import static org.junit.Assume.assumeNotNull;

import java.io.File;

import org.junit.BeforeClass;
import org.junit.Test;

import gda.util.TestUtils;

/**
 * PilatusLoaderTest Class
 */
public class PilatusLoaderTest {
	static String TestFileFolder;
	@BeforeClass
	static public void setUpClass() {
		TestFileFolder = TestUtils.getGDALargeTestFilesLocation();
		assumeNotNull(TestFileFolder); // Skip test if property not set
		TestFileFolder += "PilatusTiffLoaderTest/";
	}

	/**
	 * Testing loading a file into a sfh
	 *
	 * @throws Exception if the file couldn't be loaded
	 */
	@SuppressWarnings("deprecation")
	@Test
	public void testLoadFile1x1() throws Exception {
		// PilatusLoader.java references /dls_sw/apps/PilatusReader/
		if (!new File("/dls_sw/apps/PilatusReader/").isDirectory()) {
			System.out.println("Skipped JUnit test " + this.getClass().getCanonicalName() + ".testLoadFile1x1 (since PilatusLoader.java references /dls_sw/apps/PilatusReader/)");
			return;
		}
		if (!new File("/usr/lib/libtiff.so.3").isFile()) {  // we required the 32-bit version of libtiff to be installed
			System.out.println("Skipped JUnit test " + this.getClass().getCanonicalName() + ".testLoadFile1x1 (since PilatusLoader.java references /usr/lib/libtiff.so.3)");
			return;
		}
		new PilatusLoader(TestFileFolder + "fcell_H_8GPa_20keV_18000s_0173.tif").loadFile();
	}
}
