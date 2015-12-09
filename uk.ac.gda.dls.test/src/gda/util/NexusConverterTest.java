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

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import java.io.File;

import org.junit.BeforeClass;
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
	 * Test conversion fails when given corrupted nexus file
	 *
	 * The nexus file under test has had its End Of Allocation marker corrupted, indicating the file
	 * is larger than it really is.
	 */
	@Test
	public void testConversionFailureWithCorruptedNexus() {
		final File nexus = new File("testfiles/gda/util/NexusConverterTest/corrupted_superblock.nxs");
		final File ascii = new File(new File(testScratchDirectoryName), "corrupted_superblock.dat");
		try {
			NexusConverter.convert(nexus, ascii);
			fail("Conversion should fail when given a corrupted nexus file.");
		} catch (Exception e) {
			assertFalse(ascii.exists());
		}
	}

	/**
	 * test for file existence
	 */
	@Test
	public void testConversion() throws Exception {
		final File nexus = new File("testfiles/gda/util/NexusConverterTest/i20_4723.nxs");
		final File ascii = new File(new File(testScratchDirectoryName) , "i20_4723.dat");
		NexusConverter.convert(nexus, ascii);
		// TODO: test the contents of the file
		assertTrue(new File(testScratchDirectoryName + File.separator + "i20_4723.dat").exists());
	}
}