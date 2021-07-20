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
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import gda.device.EnumPositioner;
import gda.device.Scannable;
import gda.device.scannable.ScannableMotor;
import gda.factory.Factory;
import gda.factory.FactoryException;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.JythonServerFacade;
import uk.ac.gda.beans.exafs.i18.AttenuatorParameters;
import uk.ac.gda.beans.exafs.i18.I18SampleParameters;
import uk.ac.gda.beans.exafs.i18.SampleStageParameters;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;

public class I18SamplePreparerTest {

	private static final String TABLE_X_NAME = "tableX";
	private static final String TABLE_Y_NAME = "tableY";
	private static final String TABLE_Z_NAME = "tableZ";
	private static final String VHM_NAME = "kbVhmX";
	private static final String D7A_NAME = "d7a";
	private static final String D7B_NAME = "d7b";
	private ScannableMotor tableX;
	private ScannableMotor tableY;
	private ScannableMotor tableZ;
	private ScannableMotor kbVfmX;
	private EnumPositioner d7a;
	private EnumPositioner d7b;
	private I18SamplePreparer preparer;

	@Before
	public void setupObjects() throws FactoryException {

		JythonServerFacade jythonserverfacade = mock(JythonServerFacade.class);
		InterfaceProvider.setTerminalPrinterForTesting(jythonserverfacade);

		Factory factory = mock(Factory.class);

		tableX = mockAndPutInFinder(ScannableMotor.class, TABLE_X_NAME, factory);
		tableY = mockAndPutInFinder(ScannableMotor.class, TABLE_Y_NAME, factory);
		tableZ = mockAndPutInFinder(ScannableMotor.class, TABLE_Z_NAME, factory);

		d7a = mockAndPutInFinder(EnumPositioner.class, D7A_NAME, factory);
		d7b = mockAndPutInFinder(EnumPositioner.class, D7B_NAME, factory);

		kbVfmX = mockAndPutInFinder(ScannableMotor.class, VHM_NAME, factory);

		Finder.addFactory(factory);

		preparer = new I18SamplePreparer();
	}

	@After
	public void cleanUpFinder() {
		Finder.removeAllFactories();
	}

	private <T extends Scannable> T mockAndPutInFinder(Class<T> scannableClass, String scannableName, Factory finderFactory) throws FactoryException {
		T mock = mock(scannableClass);
		when(mock.getName()).thenReturn(scannableName);
		when(finderFactory.getFindable(scannableName)).thenReturn(mock);
		return mock;
	}

	@Test
	public void testSampleStageWithoutVFMAndWithStage1() throws Exception {
		String sampleName = "sample1";
		String description1 = "This is my first sample";

		SampleStageParameters sampleStageParameters = new SampleStageParameters();
		sampleStageParameters.setX(1.);
		sampleStageParameters.setY(2.);
		sampleStageParameters.setZ(3.);
		sampleStageParameters.setXName(TABLE_X_NAME);
		sampleStageParameters.setYName(TABLE_Y_NAME);
		sampleStageParameters.setZName(TABLE_Z_NAME);

		AttenuatorParameters atn1Parameters = new AttenuatorParameters();
		atn1Parameters.setName(D7A_NAME);
		atn1Parameters.setSelectedPosition("first");

		AttenuatorParameters atn2Parameters = new AttenuatorParameters();
		atn2Parameters.setName(D7B_NAME);
		atn2Parameters.setSelectedPosition("second");

		I18SampleParameters parameters = new I18SampleParameters();
		parameters.setName(sampleName);
		parameters.setDescription(description1);
		parameters.setSampleStageParameters(sampleStageParameters);
		parameters.addAttenuator(atn1Parameters);
		parameters.addAttenuator(atn2Parameters);
		parameters.setVfmxActive(false);

		preparer.configure(null, parameters);
		SampleEnvironmentIterator iterator = preparer.createIterator(null);

		assertEquals(1, iterator.getNumberOfRepeats());
		assertEquals(sampleName, iterator.getNextSampleName());
		assertEquals(1, iterator.getNextSampleDescriptions().size());
		assertEquals(description1, iterator.getNextSampleDescriptions().get(0));

		iterator.next();
		verify(tableX).moveTo(1.);
		verify(tableY).moveTo(2.);
		verify(tableZ).moveTo(3.);
		verify(d7a).moveTo("first");
		verify(d7b).moveTo("second");
		verifyNoInteractions(kbVfmX);
	}

}
