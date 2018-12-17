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

package uk.ac.gda.exafs.beans;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.util.List;

import org.eclipse.core.runtime.content.IContentDescriber;
import org.junit.BeforeClass;
import org.junit.Test;

import gda.exafs.validation.I20Validator;
import gda.util.TestUtils;
import uk.ac.gda.beans.exafs.i20.I20SampleParameters;
import uk.ac.gda.beans.validation.InvalidBeanMessage;
import uk.ac.gda.exafs.ui.describers.I20SampleDescriber;
import uk.ac.gda.util.beans.xml.XMLHelpers;

/**
 * class to hold I20 sample parameters
 */

public class I20SampleParametersTest {
	private static final String testScratchDirectoryName =
		TestUtils.generateDirectorynameFromClassname(I20SampleParametersTest.class.getCanonicalName());

	// Class to allow access to protected methods in validator
	private class I20ValidatorForTest extends I20Validator {
		public List<InvalidBeanMessage> validateI20SampleParametersForTest(I20SampleParameters s) {
			return validateISampleParameters(s);
		}
	}

	public static I20SampleParameters createFromXML(String filename) throws Exception {
		return XMLHelpers.createFromXML(I20SampleParameters.mappingURL, I20SampleParameters.class, I20SampleParameters.schemaURL,
				filename);
	}

	public static void writeToXML(I20SampleParameters sampleParameters, String filename) throws Exception {
		XMLHelpers.writeToXML(I20SampleParameters.mappingURL, sampleParameters, filename);
	}

	@BeforeClass
	public static void beforeClass() throws Exception{
		TestUtils.makeScratchDirectory(testScratchDirectoryName);
	}

	@Test
	public void testDescriber() {
		try {
			InputStream contents = new FileInputStream(new File("testfiles/uk/ac/gda/exafs/beans/I20SampleParametersTest/SampleParameters_withCryostat.xml"));
			I20SampleDescriber describer = new I20SampleDescriber();
			assertEquals(IContentDescriber.VALID, describer.describe(contents, null));
		} catch (Exception e) {
			fail(e.getMessage());
		}
	}


	/**
	 * test for file not existing
	 */
	@Test
	public void testCreateFromXML_FileDoesNotExist() {
		try {
			createFromXML("testfiles/uk/ac/gda/exafs/beans/I20SampleParametersTest/DoesNotExist");
			fail("File does not exist");
		} catch (Exception ex) {
			if (!(ex instanceof FileNotFoundException)) {
				fail("Invalid exception thrown - " + ex.getMessage());
			}
		}
	}
}
