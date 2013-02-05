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
import gda.exafs.validation.I20Validator;
import gda.util.TestUtils;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.runtime.content.IContentDescriber;
import org.junit.BeforeClass;
import org.junit.Test;

import uk.ac.gda.beans.exafs.ElementPosition;
import uk.ac.gda.beans.exafs.i20.CryostatParameters;
import uk.ac.gda.beans.exafs.i20.CustomParameter;
import uk.ac.gda.beans.exafs.i20.FurnaceParameters;
import uk.ac.gda.beans.exafs.i20.I20SampleParameters;
import uk.ac.gda.beans.exafs.i20.MicroreactorParameters;
import uk.ac.gda.beans.exafs.i20.SampleStageParameters;
import uk.ac.gda.beans.validation.InvalidBeanMessage;
import uk.ac.gda.exafs.ui.describers.I20SampleDescriber;

/**
 * class to hold I20 sample parameters
 */

public class I20SampleParametersTest {
	final static String testScratchDirectoryName =
		TestUtils.generateDirectorynameFromClassname(I20SampleParametersTest.class.getCanonicalName());
	/**
	 * 
	 * @throws Exception
	 */
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
			I20SampleParameters.createFromXML("testfiles/uk/ac/gda/exafs/beans/I20SampleParametersTest/DoesNotExist");
			fail("File does not exist");
		} catch (Exception ex) {
			if (!(ex instanceof FileNotFoundException)) {
				fail("Invalid exception thrown - " + ex.getMessage());
			}
		}
	}

	/**
	 * test for xml file with cryostat parameters
	 * @throws Exception 
	 */
	@Test
	public void testCreateFromXML_withCryostat()  throws Exception{
		
		I20SampleParameters expectedValue = new I20SampleParameters();
		expectedValue.setName("Cytochrome");
		expectedValue.addDescription("Cytochrome preparation #7");
		expectedValue.addDescription("bla bla bla");
		expectedValue.setSampleWheelPosition("Copper");
		final List<ElementPosition> eles = new ArrayList<ElementPosition>(2);
		eles.add(new ElementPosition("Fe", 1));
		eles.add(new ElementPosition("Si", 2));
		expectedValue.setSampleEnvironment(I20SampleParameters.SAMPLE_ENV[2]);
		CryostatParameters cps = new CryostatParameters();
		cps.setTemperature(295.);
		cps.setTolerance(1d);
		cps.setHeaterRange(1);
		cps.setTime(5d);
		cps.setProfileType("PID");
		cps.setP(1d);
		cps.setI(1d);
		cps.setD(1d);
		cps.setSampleHolder("3 Samples");
		cps.setSampleNumbers("1");
		cps.setPosition1(1.0);
		cps.setFinePosition1(0.1);
		cps.setSampleDescription1("My First Sample");
		expectedValue.setCryostatParameters(cps);

		isValidAndMatchesFile(expectedValue,"SampleParameters_withCryostat.xml");
	}
	
	private void isValidAndMatchesFile(I20SampleParameters expectedValue, String filename) throws Exception{
		I20SampleParameters s = I20SampleParameters.createFromXML("testfiles/uk/ac/gda/exafs/beans/I20SampleParametersTest/" + filename);
		List<InvalidBeanMessage> errors = new I20Validator().validateI20SampleParameters(s);
		if (errors.size() > 0){
			fail(errors.get(0).getPrimaryMessage());
		}
		if (!expectedValue.equals(s)) {
			fail("Values read are incorrect - " + s.toString());
		}
		
	}

	/**
	 * test for xml file with furnace parameters
	 * @throws Exception 
	 */
	public void testCreateFromXML_withFurnace()  throws Exception{
		I20SampleParameters expectedValue = new I20SampleParameters();
		expectedValue.setName("Cytochrome");
		expectedValue.addDescription("Cytochrome preparation #7");
		expectedValue.addDescription("bla bla bla");
		expectedValue.setSampleWheelPosition("Copper");
		expectedValue.setSampleEnvironment(I20SampleParameters.SAMPLE_ENV[3]);
		FurnaceParameters fps = new FurnaceParameters();
		fps.setTemperature("295");
		fps.setTolerance(1.5);
		fps.setTime(5);
		fps.setX(6.9);
		fps.setY(4.7);
		fps.setZ(2.5);
		expectedValue.setFurnaceParameters(fps);

		isValidAndMatchesFile(expectedValue,"SampleParameters_withFurnace.xml");
	}

	/**
	 * test for xml file with sample stage parameters
	 * @throws Exception 
	 */
	@Test
	public void testCreateFromXML_withSampleStage()  throws Exception{

		I20SampleParameters expectedValue = new I20SampleParameters();
		expectedValue.setName("Cytochrome");
		expectedValue.addDescription("Cytochrome preparation #7");
		expectedValue.addDescription("bla bla bla");
		expectedValue.setSampleWheelPosition("Copper");
		expectedValue.setSampleEnvironment(I20SampleParameters.SAMPLE_ENV[1]);
		SampleStageParameters ssps = new SampleStageParameters();
		ssps.setUseSample1(true);
		ssps.setSample1_x(3.4);
		ssps.setSample1_y(6.8);
		ssps.setSample1_z(2.5);
		ssps.setSample1_rotation(1.2);
		ssps.setSample1_roll(0.5);
		ssps.setSample1_pitch(0.7);
		ssps.setSample1_name("my_sample");
		ssps.setSample1_description("this is my sample");
		expectedValue.setRoomTemperatureParameters(ssps);

		isValidAndMatchesFile(expectedValue,"SampleParameters_withSampleStage.xml");
	}

	
	/**
	 * test for xml file with sample stage parameters
	 * @throws Exception 
	 */
	public void testCreateFromXML_withMicroreactor()  throws Exception{

		I20SampleParameters expectedValue = new I20SampleParameters();
		expectedValue.setName("Cytochrome");
		expectedValue.addDescription("Cytochrome preparation #8");
		expectedValue.addDescription("bla bla bla");
		expectedValue.setSampleEnvironment(I20SampleParameters.SAMPLE_ENV[4]);
		expectedValue.setSampleWheelPosition("Copper");
		MicroreactorParameters micro = new MicroreactorParameters();
		micro.setGas0Rate(20);
		micro.setGas3Rate(20);
		micro.setTemperature(200);
		micro.setMasses("2,32");
		expectedValue.setMicroreactorParameters(micro);

		isValidAndMatchesFile(expectedValue,"SampleParameters_withMicroreactor.xml");
		
		I20SampleParameters s = I20SampleParameters
				.createFromXML("testfiles/uk/ac/gda/exafs/beans/I20SampleParametersTest/SampleParameters_withMicroreactor.xml");
		Integer[] massesFromFile = s.getMicroreactorParameters().getIntegerMasses();
		assertEquals(2, massesFromFile.length);
		assertEquals(2, massesFromFile[0].intValue());
		assertEquals(32, massesFromFile[1].intValue());
		
	}

	
	/**
	 * test for xml file with custom parameters
	 * @throws Exception 
	 */
	public void testCreateFromXML_withCustom()  throws Exception{

		I20SampleParameters expectedValue = new I20SampleParameters();
		expectedValue.setName("Cytochrome");
		expectedValue.addDescription("Cytochrome preparation #7");
		expectedValue.addDescription("bla bla bla");
		expectedValue.setSampleWheelPosition("Copper");
		expectedValue.setSampleEnvironment(I20SampleParameters.SAMPLE_ENV[6]);
		CustomParameter cp = new CustomParameter();
		cp.setDeviceName("mystage");
		cp.setValue(3.142);
		expectedValue.addCustomParameter(cp);
		CustomParameter cp2 = new CustomParameter();
		cp2.setDeviceName("mydev");
		cp2.setValue(6.284);
		expectedValue.addCustomParameter(cp2);

		isValidAndMatchesFile(expectedValue,"SampleParameters_withCustom.xml");
	}

	/**
	 * Test method for {@link uk.ac.gda.beans.exafs.i20.I20SampleParameters#writeToXML(uk.ac.gda.beans.exafs.i20.I20SampleParameters, java.lang.String)}.
	 * @throws Exception 
	 */
	public void testWriteToXML()  throws Exception{
		I20SampleParameters sp = new I20SampleParameters();
		sp.setName("Cytochrome");
		sp.addDescription("Cytochrome preparation #7");
		sp.addDescription("bla bla bla");
		sp.setSampleWheelPosition("Copper");
		sp.setSampleEnvironment(I20SampleParameters.SAMPLE_ENV[3]);
		FurnaceParameters fps = new FurnaceParameters();
		fps.setTemperature("295");
		fps.setTolerance(1.5);
		fps.setTime(5);
		fps.setX(6.9);
		fps.setY(4.7);
		fps.setZ(2.5);
		sp.setFurnaceParameters(fps);
		
		try {
			I20SampleParameters.writeToXML(sp, testScratchDirectoryName + "SampleParameters_written.xml");
		} catch (Exception e) {
			fail("Failed to write xml file - " + e.getCause().getMessage());
		}

		I20SampleParameters s = I20SampleParameters.createFromXML(testScratchDirectoryName + "SampleParameters_written.xml");
		List<InvalidBeanMessage> errors = new I20Validator().validateI20SampleParameters(s);
		if (errors.size() > 0){
			fail(errors.get(0).getPrimaryMessage());
		}
		if (!sp.equals(s)) {
			fail("Values read are incorrect - " + s.toString());
		}
	}
}
