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
	@Test
	public void testConvert1() throws Exception {
		try {
			final File nexus = new File("testfiles/gda/util/NexusConverterTest/i20_4720.nxs");
			final File ascii = new File(new File(testScratchDirectoryName) , "i20_4720.dat");
			NexusConverter.convert(nexus, ascii);
		} catch (Exception expected) {
			return;
		}
		throw new Exception("Invalid file did not produce error.");
	}
	/**
	 * test for file existence
	 */
	@Test
	@Ignore("2012/09/18 - crashes in native code on RH5-64")
	public void testConvert2() throws Exception {
		final File nexus = new File("testfiles/gda/util/NexusConverterTest/i20_4723.nxs");
		final File ascii = new File(new File(testScratchDirectoryName) , "i20_4723.dat");
		NexusConverter.convert(nexus, ascii);
	}
}