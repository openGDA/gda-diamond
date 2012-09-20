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

package uk.ac.gda.exafs.beans.b18;

import static org.junit.Assert.fail;
import gda.exafs.validation.B18Validator;

import java.io.FileNotFoundException;
import java.util.List;

import org.junit.Test;

import uk.ac.gda.beans.exafs.b18.B18SampleParameters;
import uk.ac.gda.beans.exafs.b18.FurnaceParameters;
import uk.ac.gda.beans.exafs.b18.XYThetaStageParameters;
import uk.ac.gda.beans.validation.InvalidBeanMessage;

/**
 * class to hold sample parameters
 */
public class B18SampleParametersTest {

	@Test
	public void testCreateFromXML_FileDoesNotExist() {
		try {
			B18SampleParameters.createFromXML("testfiles/DoesNotExist");
			fail("File does not exist");
		} catch (Exception ex) {
			if (!(ex instanceof FileNotFoundException)) {
				fail("Invalid exception thrown - " + ex.getMessage());
			}
		}
	}

	/**
	 * test for xml file with furnace parameters
	 * @throws Exception 
	 */
	@Test
	public void testCreateFromXML_withFurnace()  throws Exception{
		B18SampleParameters expectedValue = new B18SampleParameters();
		expectedValue.setName("Cytochrome");
		expectedValue.setDescription1("Cytochrome preparation #7");
		expectedValue.setDescription2("Cytochrome preparation description #7");
		expectedValue.setTemperatureControl("furnace");
		FurnaceParameters fps = new FurnaceParameters();
		fps.setTemperature(295);
		fps.setTolerance(1.5);
		fps.setTime(5);
		expectedValue.setFurnaceParameters(fps);

		B18SampleParameters s = B18SampleParameters.createFromXML("testfiles/uk/ac/gda/exafs/beans/b18/SampleParameters_withFurnace.xml");
		validate(s);
		testEquals(expectedValue, s);
	}
	
	
	/**
	 * test for xml file with sample stage parameters
	 * @throws Exception 
	 */
	@Test
	public void testCreateFromXML_withSmallStage()  throws Exception{

		B18SampleParameters expectedValue = new B18SampleParameters();
		expectedValue.setName("Cytochrome");
		expectedValue.setDescription1("Cytochrome preparation #7");
		expectedValue.setDescription2("Cytochrome preparation description #7");
		expectedValue.setStage("xythetastage");
		XYThetaStageParameters ssps = new XYThetaStageParameters();
		ssps.setX(1);
		ssps.setY(2);
		ssps.setTheta(3);
		expectedValue.setXYThetaStageParameters(ssps);

		B18SampleParameters s = B18SampleParameters.createFromXML("testfiles/uk/ac/gda/exafs/beans/b18/SampleParameters_withSmallStage.xml");
		validate(s);
		testEquals(expectedValue, s);
	}
	
	private void testEquals(B18SampleParameters expectedValue, B18SampleParameters s) {
		if (!expectedValue.equals(s)) {
			fail("Values read are incorrect - " + s.toString());
		}
	}

	private void validate(B18SampleParameters s) {
		List<InvalidBeanMessage> errors = new B18Validator().validateB18SampleParameters(s);
		if (errors.size() > 0){
			fail(errors.get(0).getPrimaryMessage());
		}
	}
}
