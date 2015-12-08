/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package gda.util;

import static org.junit.Assert.assertTrue;

import java.io.File;

import org.junit.BeforeClass;
import org.junit.Ignore;
import org.junit.Test;

/**
 * test class for NexusConverter
 *
 * Before to set the java.library.path before running.
 */
public class NexusConverterTest {
	final static String testScratchDirectoryName =
		TestUtils.generateDirectorynameFromClassname(NexusConverterTest.class.getCanonicalName());
	/**
	 *
	 * @throws Exception
	 */
	@BeforeClass
	public static void beforeClass() throws Exception{
		TestUtils.makeScratchDirectory(testScratchDirectoryName);
	}

	/**
	 * test for file existence
	 */
	@Ignore("2015/12/8 - this seems to required the SWMR read flag to be set to read past the super block whereas the next test does not!!!")
	// Passed problem up to the HDF group
	@Test
	public void testConvert1() throws Exception {
		final File nexus = new File("testfiles/gda/util/NexusConverterTest/i20_4720.nxs");
		final File ascii = new File(new File(testScratchDirectoryName), "i20_4720.dat");
		NexusConverter.convert(nexus, ascii);
		// TODO: test the contents of the file
		assertTrue(new File(testScratchDirectoryName + File.separator + "i20_4720.dat").exists());
	}

	/**
	 * test for file existence
	 */
	@Test
	public void testConvert2() throws Exception {
		final File nexus = new File("testfiles/gda/util/NexusConverterTest/i20_4723.nxs");
		final File ascii = new File(new File(testScratchDirectoryName) , "i20_4723.dat");
		NexusConverter.convert(nexus, ascii);
		// TODO: test the contents of the file
		assertTrue(new File(testScratchDirectoryName + File.separator + "i20_4723.dat").exists());
	}
}