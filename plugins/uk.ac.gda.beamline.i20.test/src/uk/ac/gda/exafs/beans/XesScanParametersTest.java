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

package uk.ac.gda.exafs.beans;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.util.List;

import org.eclipse.core.runtime.content.IContentDescriber;
import org.junit.BeforeClass;
import org.junit.Test;

import gda.exafs.validation.I20Validator;
import gda.util.TestUtils;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.validation.InvalidBeanMessage;
import uk.ac.gda.exafs.ui.describers.XesScanParametersDescriber;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class XesScanParametersTest {

	final static String testScratchDirectoryName =
		TestUtils.generateDirectorynameFromClassname(XesScanParametersTest.class.getCanonicalName());

	public static XesScanParameters createFromXML(String filename) throws Exception {
		return (XesScanParameters) XMLHelpers.createFromXML(XesScanParameters.mappingURL, XesScanParameters.class,
				XesScanParameters.schemaURL, filename);
	}

	public static void writeToXML(XesScanParameters params, String filename) throws Exception {
		XMLHelpers.writeToXML(XesScanParameters.mappingURL, params, filename);
	}

	public static DetectorParameters createDetectorsFromXML(String filename) throws Exception {
		return (DetectorParameters) XMLHelpers.createFromXML(DetectorParameters.mappingURL, DetectorParameters.class,
				DetectorParameters.schemaUrl, filename);
	}

	public static void writeDetectorsToXML(DetectorParameters sampleParameters, String filename) throws Exception {
		XMLHelpers.writeToXML(DetectorParameters.mappingURL, sampleParameters, filename);
	}

	@BeforeClass
	public static void beforeClass() throws Exception{
		TestUtils.makeScratchDirectory(testScratchDirectoryName);
	}

	@Test
	public void testDescriber() {
		try {
			InputStream contents = new FileInputStream(new File("testfiles/uk/ac/gda/exafs/beans/XesScanParametersTest/XES_Parameters.xml"));
			XesScanParametersDescriber describer = new XesScanParametersDescriber();
			assertEquals(IContentDescriber.VALID, describer.describe(contents, null));
		} catch (Exception e) {
			fail(e.getMessage());
		}
	}


	/**
	 * Got broken at one point so have simple test for it.
	 */
	@Test
	public void testCreateFromXMLWithClass() throws Exception {
		final File testFile = new File("testfiles/uk/ac/gda/exafs/beans/XesScanParametersTest/XES_Parameters.xml");
		final XesScanParameters s = (XesScanParameters)XMLHelpers.createFromXML(XesScanParameters.mappingURL,
									XesScanParameters.class,
									XesScanParameters.schemaURL,
									testFile);
		System.out.println(s);
	}

	/**
	 * Test method for {@link uk.ac.gda.beans.exafs.XasScanParameters#createFromXML(java.lang.String)}.
	 * @throws Exception
	 */
	@Test
	public void testCreateFromXML()  throws Exception{
		XesScanParameters sp = new XesScanParameters();
		sp.setScanType(1);
		sp.setMonoEnergy(15000d);
		sp.setXesInitialEnergy(15000d);
		sp.setXesFinalEnergy(16000d);
		sp.setXesStepSize(1d);
		sp.setXesIntegrationTime(1d);
		sp.setAdditionalCrystal0(false);
		sp.setAdditionalCrystal1(false);
		sp.setAdditionalCrystal2(false);
		sp.setAdditionalCrystal3(false);

		XesScanParameters s = createFromXML("testfiles/uk/ac/gda/exafs/beans/XesScanParametersTest/XES_Parameters.xml");
		DetectorParameters d = createDetectorsFromXML("testfiles/uk/ac/gda/exafs/beans/XesScanParametersTest/DetectorParameters_withXES.xml");
		List<InvalidBeanMessage> errors = new I20Validator().validateXesScanParameters(s,d);
		if (errors.size() > 0){
			fail(errors.get(0).getPrimaryMessage());
		}
		if (!sp.equals(s)) {
			fail("Values read are incorrect - " + s.toString());
		}
	}

	/**
	 * Test method for {@link uk.ac.gda.beans.exafs.XasScanParameters#writeToXML(uk.ac.gda.beans.exafs.XasScanParameters, java.lang.String)}.
	 * @throws Exception
	 */
	@Test
	public void testWriteToXML()  throws Exception{
		XesScanParameters sp = new XesScanParameters();
		sp.setScanType(1);
		sp.setMonoEnergy(15000d);
		sp.setXesInitialEnergy(15000d);
		sp.setXesFinalEnergy(16000d);
		sp.setXesStepSize(1d);
		sp.setXesIntegrationTime(1d);
		sp.setAdditionalCrystal0(false);
		sp.setAdditionalCrystal1(false);
		sp.setAdditionalCrystal2(false);
		sp.setAdditionalCrystal3(false);

		try {
			writeToXML(sp, testScratchDirectoryName + "XesScanParameters_written.xml");
		} catch (Exception e) {
			fail("Failed to write xml file - " + e.getCause().getMessage());
		}

		XesScanParameters s = createFromXML(testScratchDirectoryName + "XesScanParameters_written.xml");
		DetectorParameters d = createDetectorsFromXML("testfiles/uk/ac/gda/exafs/beans/XesScanParametersTest/DetectorParameters_withXES.xml");
		List<InvalidBeanMessage> errors = new I20Validator().validateXesScanParameters(s,d);
		if (errors.size() > 0){
			fail(errors.get(0).getPrimaryMessage());
		}
		if (!sp.equals(s)) {
			fail("Values read are incorrect - " + s.toString());
		}
	}

}
