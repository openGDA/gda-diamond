/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package uk.ac.gda.server.exafs.scan.preparers;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;

import gda.device.scannable.ScannableMotor;
import gda.jython.InterfaceProvider;
import gda.jython.JythonServerFacade;
import uk.ac.gda.beans.exafs.b18.B18SampleParameters;
import uk.ac.gda.beans.exafs.b18.FurnaceParameters;
import uk.ac.gda.beans.exafs.b18.LN2CryoStageParameters;
import uk.ac.gda.beans.exafs.b18.SampleWheelParameters;
import uk.ac.gda.beans.exafs.b18.XYThetaStageParameters;
import uk.ac.gda.server.exafs.b18.scan.preparers.B18SamplePreparer;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;

public class B18SamplePreparerTest {

	private ScannableMotor mocked_sxcryo_scannable;
	private ScannableMotor mocked_xytheta_scannable;
	private ScannableMotor mocked_ln2cryo_scannable;
	private ScannableMotor mocked_lakeshore_scannable;
	private ScannableMotor mocked_furnace_scannable;
	private ScannableMotor mocked_pulsetube_scannable;
	private ScannableMotor mocked_user_scannable;
	private ScannableMotor mocked_samplewheel_scannable;
	private B18SamplePreparer preparer;

	@Before
	public void setupObjects() {

		JythonServerFacade jythonserverfacade = Mockito.mock(JythonServerFacade.class);
		InterfaceProvider.setTerminalPrinterForTesting(jythonserverfacade);

		mocked_sxcryo_scannable = createMockScannableMotor("mocked_sxcryo_scannable");
		mocked_xytheta_scannable = createMockScannableMotor("mocked_xytheta_scannable");
		mocked_ln2cryo_scannable = createMockScannableMotor("mocked_ln2cryo_scannable");
		mocked_lakeshore_scannable = createMockScannableMotor("mocked_lakeshore_scannable");
		mocked_furnace_scannable = createMockScannableMotor("mocked_furnace_scannable");
		mocked_pulsetube_scannable = createMockScannableMotor("mocked_pulsetube_scannable");
		mocked_samplewheel_scannable = createMockScannableMotor("mocked_samplewheel_scannable");
		mocked_user_scannable = createMockScannableMotor("mocked_user_scannable");

		preparer = new B18SamplePreparer(mocked_sxcryo_scannable, mocked_xytheta_scannable, mocked_ln2cryo_scannable,
				mocked_lakeshore_scannable, mocked_furnace_scannable, mocked_pulsetube_scannable,
				mocked_samplewheel_scannable, mocked_user_scannable);
	}

	private ScannableMotor createMockScannableMotor(String string) {
		ScannableMotor newMock = Mockito.mock(ScannableMotor.class);
		Mockito.when(newMock.getName()).thenReturn(string);
		return newMock;
	}

	@Test
	public void testNoSampleEnvironment() {
		try {
			String sampleName = "sample1";
			String description1 = "This is my first sample";

			B18SampleParameters parameters = new B18SampleParameters();
			parameters.setName(sampleName);
			parameters.setDescription1(description1);
			// this preparer does not vary its behaviour based on the scan
			preparer.configure(null, parameters);

			SampleEnvironmentIterator iterator = preparer.createIterator(null);

			assertEquals(1, iterator.getNumberOfRepeats());
			assertEquals(sampleName, iterator.getNextSampleName());
			assertEquals(2, iterator.getNextSampleDescriptions().size());
			assertEquals(description1, iterator.getNextSampleDescriptions().get(0));
			assertEquals("", iterator.getNextSampleDescriptions().get(1));
		} catch (Exception e) {
			fail(e.getMessage());
		}
	}

	@Test
	public void testXYThetaEnvironment() {
		try {
			String sampleName = "sample1";
			String description1 = "This is my first sample";

			XYThetaStageParameters xytParameters = new XYThetaStageParameters();
			xytParameters.setX(1);
			xytParameters.setY(2);
			xytParameters.setTheta(3);

			B18SampleParameters parameters = new B18SampleParameters();
			parameters.setName(sampleName);
			parameters.setDescription1(description1);
			parameters.setStage(B18SampleParameters.STAGE[1]);
			parameters.setXYThetaStageParameters(xytParameters);

			// this preparer does not vary its behaviour based on the scan
			preparer.configure(null, parameters);

			SampleEnvironmentIterator iterator = preparer.createIterator(null);

			assertEquals(1, iterator.getNumberOfRepeats());
			assertEquals(sampleName, iterator.getNextSampleName());
			assertEquals(2, iterator.getNextSampleDescriptions().size());
			assertEquals(description1, iterator.getNextSampleDescriptions().get(0));
			assertEquals("", iterator.getNextSampleDescriptions().get(1));

			assertEquals("mocked_sxcryo_scannable", mocked_sxcryo_scannable.getName());

			iterator.next();
			Mockito.verify(mocked_xytheta_scannable).moveTo(new double[] { 1, 2, 3 });
		} catch (Exception e) {
			fail(e.getMessage());
		}
	}

	@Test
	public void testLN2CryoEnvironment() {
		try {
			String sampleName = "sample1";
			String description1 = "This is my first sample";
			String description2 = "This uses the ln2 stage";

			LN2CryoStageParameters stageParams = new LN2CryoStageParameters();
			stageParams.setManual(true);
			stageParams.setAngle(2);
			stageParams.setHeight(1.5);
			stageParams.setSampleNumberA(5);
			stageParams.setSampleNumberB(7);

			B18SampleParameters parameters = new B18SampleParameters();
			parameters.setName(sampleName);
			parameters.setDescription1(description1);
			parameters.setDescription2(description2);
			parameters.setStage(B18SampleParameters.STAGE[2]);
			parameters.setLN2CryoStageParameters(stageParams);

			// this preparer does not vary its behaviour based on the scan
			preparer.configure(null, parameters);

			SampleEnvironmentIterator iterator = preparer.createIterator(null);

			assertEquals(1, iterator.getNumberOfRepeats());
			assertEquals(sampleName, iterator.getNextSampleName());
			assertEquals(2, iterator.getNextSampleDescriptions().size());
			assertEquals(description1, iterator.getNextSampleDescriptions().get(0));
			assertEquals(description2, iterator.getNextSampleDescriptions().get(1));

			iterator.next();
			Mockito.verify(mocked_ln2cryo_scannable).moveTo(new double[] { 1.5,2 });
		} catch (Exception e) {
			fail(e.getMessage());
		}
	}

	@Test
	public void testSampleWheel(){
		try {
			String sampleName = "sample1";
			String description1 = "This is my first sample";
			String description2 = "This uses the ln2 stage";

			SampleWheelParameters sampleWheelParameters = new SampleWheelParameters();
			sampleWheelParameters.setWheelEnabled(true);
			sampleWheelParameters.setManual(true);
			sampleWheelParameters.setDemand(10.0);

			B18SampleParameters parameters = new B18SampleParameters();
			parameters.setName(sampleName);
			parameters.setDescription1(description1);
			parameters.setDescription2(description2);
			parameters.setTemperatureControl(B18SampleParameters.TEMP_CONTROL[0]);
			parameters.setStage(B18SampleParameters.STAGE[0]);
			parameters.setSampleWheelParameters(sampleWheelParameters);

			// this preparer does not vary its behaviour based on the scan
			preparer.configure(null, parameters);

			SampleEnvironmentIterator iterator = preparer.createIterator(null);

			assertEquals(1, iterator.getNumberOfRepeats());
			assertEquals(sampleName, iterator.getNextSampleName());
			assertEquals(2, iterator.getNextSampleDescriptions().size());
			assertEquals(description1, iterator.getNextSampleDescriptions().get(0));
			assertEquals(description2, iterator.getNextSampleDescriptions().get(1));

			iterator.next();

			Mockito.verify(mocked_samplewheel_scannable).moveTo(10.0);
		} catch (Exception e) {
			fail(e.getMessage());
		}

	}


	@Test
	public void testFurnaceEnvironment() {
		try {
			String sampleName = "sample1";
			String description1 = "This is my first sample";
			String description2 = "This uses the ln2 stage";

			FurnaceParameters stageParams = new FurnaceParameters();
			stageParams.setTemperature(200);
			stageParams.setTolerance(1.5);
			stageParams.setTime(0.1);

			// used inside the iterator to get current temperature from the furnace
			Mockito.when(mocked_furnace_scannable.getPosition()).thenReturn(new Double(200.0));

			B18SampleParameters parameters = new B18SampleParameters();
			parameters.setName(sampleName);
			parameters.setDescription1(description1);
			parameters.setDescription2(description2);
			parameters.setTemperatureControl(B18SampleParameters.TEMP_CONTROL[2]);
			parameters.setFurnaceParameters(stageParams);

			// this preparer does not vary its behaviour based on the scan
			preparer.configure(null, parameters);

			SampleEnvironmentIterator iterator = preparer.createIterator(null);

			assertEquals(1, iterator.getNumberOfRepeats());
			assertEquals(sampleName, iterator.getNextSampleName());
			assertEquals(2, iterator.getNextSampleDescriptions().size());
			assertEquals(description1, iterator.getNextSampleDescriptions().get(0));
			assertEquals(description2, iterator.getNextSampleDescriptions().get(1));

			iterator.next();

			Mockito.verify(mocked_furnace_scannable).moveTo(200.0);
		} catch (Exception e) {
			fail(e.getMessage());
		}
	}


}
