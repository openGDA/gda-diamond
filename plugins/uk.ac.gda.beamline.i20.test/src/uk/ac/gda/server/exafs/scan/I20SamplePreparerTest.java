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

package uk.ac.gda.server.exafs.scan;

import static org.junit.Assert.assertTrue;

import java.util.ArrayList;
import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;

import gda.device.EnumPositioner;
import gda.device.Scannable;
import gda.device.scannable.DummyScannable;
import uk.ac.gda.beans.exafs.i20.I20SampleParameters;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;
import uk.ac.gda.server.exafs.scan.preparers.I20SamplePreparer;

public class I20SamplePreparerTest {

	private Scannable sample_x;
	private Scannable sample_y;
	private Scannable sample_z;
	private Scannable sample_rot;
	private Scannable sample_fine_rot;
	private Scannable sample_roll;
	private Scannable sample_pitch;
	private EnumPositioner filterwheel;
	private I20SamplePreparer thePreparer;

	@Before
	public void setup() {
		sample_x = createMockScannable("sample_x");
		sample_y = createMockScannable("sample_y");
		sample_z = createMockScannable("sample_z");
		sample_rot = createMockScannable("sample_rot");
		sample_fine_rot = createMockScannable("sample_fine_rot");
		sample_roll = createMockScannable("sample_roll");
		sample_pitch = createMockScannable("sample_pitch");
		filterwheel = (EnumPositioner) createMock(EnumPositioner.class, "filterwheel");
		thePreparer = new I20SamplePreparer(filterwheel);
	}

	private Scannable createMockScannable(String string) {
		return createMock(DummyScannable.class, string);
	}

	private Scannable createMock(Class<? extends Scannable> clazz, String name) {
		Scannable newMock = Mockito.mock(clazz);
		Mockito.when(newMock.getName()).thenReturn(name);
		return newMock;
	}

	@Test
	public void testI20SingleSampleIterator() throws Exception {

		String name = "one sample name";
		String desc = "one sample desc";

		List<String> descList = new ArrayList<String>();
		descList.add(desc);

		I20SampleParameters samParams = new I20SampleParameters();
		samParams.setName(name);
		samParams.setDescriptions(descList);

		thePreparer.configure(null, samParams);

		SampleEnvironmentIterator theIterator = thePreparer.createIterator("Xanes");

		// the movement operation
		theIterator.next();

		Mockito.verifyNoInteractions(sample_x, sample_y, sample_z, sample_rot, sample_fine_rot, sample_roll,
				sample_pitch);

		assertTrue(theIterator.getNumberOfRepeats() == 1);

		assertTrue(theIterator.getNextSampleName().equals(name));

		assertTrue(theIterator.getNextSampleDescriptions().get(0).equals(desc));

	}

	@Test
	public void testSampleWheelMoved() throws Exception {

		I20SampleParameters samParams = new I20SampleParameters();
		samParams.setSampleWheelPosition("Empty");
		samParams.setUseSampleWheel(true);

		thePreparer.configure(null, samParams);

		Mockito.verify(filterwheel).moveTo("Empty");
	}

	@Test
	public void testSampleWheelNotMoved() throws Exception {

		I20SampleParameters samParams = new I20SampleParameters();
		samParams.setSampleWheelPosition("Empty");

		thePreparer.configure(null, samParams);

		Mockito.verifyNoInteractions(filterwheel);
	}
}
