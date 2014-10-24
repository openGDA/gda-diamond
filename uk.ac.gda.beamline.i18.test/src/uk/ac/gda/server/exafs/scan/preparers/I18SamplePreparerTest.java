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
import gda.device.EnumPositioner;
import gda.device.scannable.ScannableMotor;
import gda.gui.RCPController;
import gda.jython.InterfaceProvider;
import gda.jython.JythonServerFacade;

import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;
import org.powermock.api.mockito.PowerMockito;

import uk.ac.gda.beans.exafs.i18.AttenuatorParameters;
import uk.ac.gda.beans.exafs.i18.I18SampleParameters;
import uk.ac.gda.beans.exafs.i18.SampleStageParameters;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;

public class I18SamplePreparerTest {

	private RCPController rcpController;
	private ScannableMotor mocked_sc_MicroFocusSampleX;
	private ScannableMotor mocked_sc_MicroFocusSampleY;
	private ScannableMotor mocked_sc_sample_z;
	private ScannableMotor mocked_kb_vfm_x;
	private EnumPositioner d7a;
	private EnumPositioner d7b;
	private I18SamplePreparer preparer;

	@Before
	public void setupObjects() {

		JythonServerFacade jythonserverfacade = Mockito.mock(JythonServerFacade.class);
		InterfaceProvider.setTerminalPrinterForTesting(jythonserverfacade);

		rcpController = PowerMockito.mock(RCPController.class);
		Mockito.when(rcpController.getName()).thenReturn("rcpController");
		
		mocked_sc_MicroFocusSampleX = createMockScannableMotor("mocked_sc_MicroFocusSampleX");
		mocked_sc_MicroFocusSampleY = createMockScannableMotor("mocked_sc_MicroFocusSampleY");
		mocked_sc_sample_z = createMockScannableMotor("mocked_sc_sample_z");
		
		d7a = PowerMockito.mock(EnumPositioner.class);
		Mockito.when(d7a.getName()).thenReturn("d7a");
		d7b = PowerMockito.mock(EnumPositioner.class);
		Mockito.when(d7b.getName()).thenReturn("d7b");

		mocked_kb_vfm_x = createMockScannableMotor("mocked_kb_vfm_x");

		preparer = new I18SamplePreparer(rcpController, mocked_sc_MicroFocusSampleX, mocked_sc_MicroFocusSampleY, mocked_sc_sample_z,
				d7a, d7b, mocked_kb_vfm_x);
	}
	
	private ScannableMotor createMockScannableMotor(String string) {
		ScannableMotor newMock = PowerMockito.mock(ScannableMotor.class);
		Mockito.when(newMock.getName()).thenReturn(string);
		return newMock;
	}

	@Test
	public void testSampleStageWithoutVFM() {
		try {
			String sampleName = "sample1";
			String description1 = "This is my first sample";

			SampleStageParameters sampleStageParameters = new SampleStageParameters();
			sampleStageParameters.setX(1.);
			sampleStageParameters.setY(2.);
			sampleStageParameters.setZ(3.);
			
			AttenuatorParameters atn1Parameters = new AttenuatorParameters();
			atn1Parameters.setSelectedPosition("first");

			AttenuatorParameters atn2Parameters = new AttenuatorParameters();
			atn2Parameters.setSelectedPosition("second");

			I18SampleParameters parameters = new I18SampleParameters();
			parameters.setName(sampleName);
			parameters.setDescription(description1);
			parameters.setSampleStageParameters(sampleStageParameters);
			parameters.setAttenuatorParameter1(atn1Parameters);
			parameters.setAttenuatorParameter2(atn2Parameters);
			parameters.setVfmxActive(false);

			preparer.configure(null, parameters);

			SampleEnvironmentIterator iterator = preparer.createIterator(null);

			assertEquals(1, iterator.getNumberOfRepeats());
			assertEquals(sampleName, iterator.getNextSampleName());
			assertEquals(1, iterator.getNextSampleDescriptions().size());
			assertEquals(description1, iterator.getNextSampleDescriptions().get(0));

			assertEquals("mocked_sc_MicroFocusSampleX", mocked_sc_MicroFocusSampleX.getName());

			iterator.next();
			Mockito.verify(mocked_sc_MicroFocusSampleX).moveTo(1.);
			Mockito.verify(mocked_sc_MicroFocusSampleY).moveTo(2.);
			Mockito.verify(mocked_sc_sample_z).moveTo(3.);
			Mockito.verify(d7a).moveTo("first");
			Mockito.verify(d7b).moveTo("second");
			Mockito.verifyZeroInteractions(mocked_kb_vfm_x);
			
		} catch (Exception e) {
			fail(e.getMessage());
		}
	}

}
