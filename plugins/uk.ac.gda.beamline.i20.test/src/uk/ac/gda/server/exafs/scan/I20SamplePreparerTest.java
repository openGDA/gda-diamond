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
import org.powermock.api.mockito.PowerMockito;

import gda.device.EnumPositioner;
import gda.device.Scannable;
import gda.device.scannable.DummyScannable;
import gda.gui.RCPController;
import uk.ac.gda.beamline.i20.scannable.Lakeshore340Scannable;
import uk.ac.gda.beans.exafs.i20.CryostatParameters;
import uk.ac.gda.beans.exafs.i20.CryostatProperties;
import uk.ac.gda.beans.exafs.i20.CryostatSampleDetails;
import uk.ac.gda.beans.exafs.i20.I20SampleParameters;
import uk.ac.gda.beans.exafs.i20.SampleStageParameters;
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
	private Scannable cryostick_pos;
	private Lakeshore340Scannable cryostat;
	private RCPController rcp_controller;
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

		cryostat = (Lakeshore340Scannable) createMock(Lakeshore340Scannable.class, "cryostat");
		cryostick_pos = createMockScannable("cryostick_pos");

		rcp_controller = PowerMockito.mock(RCPController.class);

		thePreparer = new I20SamplePreparer(sample_x, sample_y, sample_z, sample_rot, sample_fine_rot, sample_roll,
				sample_pitch, filterwheel, cryostat, cryostick_pos, rcp_controller);
	}

	private Scannable createMockScannable(String string) {
		return createMock(DummyScannable.class, string);
	}

	private Scannable createMock(Class<? extends Scannable> clazz, String name) {
		Scannable newMock = PowerMockito.mock(clazz);
		Mockito.when(newMock.getName()).thenReturn(name);
		return newMock;
	}

	@Test
	public void testRoomTempIterator() throws Exception {
		String name = "room temp name";
		String desc = "room temp desc";

		SampleStageParameters roomTempParameters = new SampleStageParameters();
		roomTempParameters.setSamXEnabled(false);
		roomTempParameters.setSamYEnabled(true);
		roomTempParameters.setSamZEnabled(false);
		roomTempParameters.setRotEnabled(true);
		roomTempParameters.setRollEnabled(false);
		roomTempParameters.setPitchEnabled(true);
		roomTempParameters.setFineRotEnabled(false);

		roomTempParameters.setSample_y(1.0);
		roomTempParameters.setSample_rotation(2.0);
		roomTempParameters.setSample_pitch(3.0);

		roomTempParameters.setSample_name(name);
		roomTempParameters.setSample_description(desc);

		I20SampleParameters samParams = new I20SampleParameters();
		samParams.addRoomTemperatureParameter(roomTempParameters);
		samParams.setSampleEnvironment(I20SampleParameters.SAMPLE_ENV[1]);

		thePreparer.configure(null, samParams);

		SampleEnvironmentIterator theIterator = thePreparer.createIterator("Xanes");

		// the movement operation
		theIterator.next();

		assertTrue(theIterator.getNumberOfRepeats() == 1);

		assertTrue(theIterator.getNextSampleName().equals(name));

		assertTrue(theIterator.getNextSampleDescriptions().get(0).equals(desc));

		// verify movement
		Mockito.verify(sample_y).asynchronousMoveTo(1.0);
		Mockito.verify(sample_rot).asynchronousMoveTo(2.0);
		Mockito.verify(sample_pitch).asynchronousMoveTo(3.0);
		Mockito.verifyZeroInteractions(sample_x, sample_z, sample_fine_rot, sample_roll);

		theIterator.resetIterator();

		theIterator.next();

		// verify movement again
		Mockito.verify(sample_y, Mockito.times(2)).asynchronousMoveTo(1.0);
		Mockito.verify(sample_rot, Mockito.times(2)).asynchronousMoveTo(2.0);
		Mockito.verify(sample_pitch, Mockito.times(2)).asynchronousMoveTo(3.0);
		Mockito.verifyZeroInteractions(sample_x, sample_z, sample_fine_rot, sample_roll);
	}

	@Test
	public void testXESRoomTempIterator() throws Exception {

		String name = "xes temp name";
		String desc = "xes temp desc";

		SampleStageParameters roomTempParameters = new SampleStageParameters();
		roomTempParameters.setSamXEnabled(false);
		roomTempParameters.setSamYEnabled(true);
		roomTempParameters.setSamZEnabled(false);
		roomTempParameters.setRotEnabled(true);
		roomTempParameters.setRollEnabled(false);
		roomTempParameters.setPitchEnabled(true);
		roomTempParameters.setFineRotEnabled(false);

		roomTempParameters.setSample_y(1.0);
		roomTempParameters.setSample_rotation(2.0);
		roomTempParameters.setSample_pitch(3.0);

		roomTempParameters.setSample_name(name);
		roomTempParameters.setSample_description(desc);

		I20SampleParameters samParams = new I20SampleParameters();
		samParams.addRoomTemperatureParameter(roomTempParameters);
		samParams.setSampleEnvironment(I20SampleParameters.SAMPLE_ENV[1]);

		thePreparer.configure(null, samParams);

		SampleEnvironmentIterator theIterator = thePreparer.createIterator("XES");

		// the movement operation
		theIterator.next();

		assertTrue(theIterator.getNumberOfRepeats() == 1);

		assertTrue(theIterator.getNextSampleName().equals(name));

		assertTrue(theIterator.getNextSampleDescriptions().get(0).equals(desc));

		// verify movement
		Mockito.verify(sample_y).asynchronousMoveTo(1.0);
		Mockito.verify(sample_rot).asynchronousMoveTo(2.0);
		Mockito.verifyZeroInteractions(sample_x, sample_z, sample_fine_rot, sample_roll, sample_pitch);

		theIterator.resetIterator();

		theIterator.next();

		// verify movement again
		Mockito.verify(sample_y, Mockito.times(2)).asynchronousMoveTo(1.0);
		Mockito.verify(sample_rot, Mockito.times(2)).asynchronousMoveTo(2.0);
		Mockito.verifyZeroInteractions(sample_x, sample_z, sample_fine_rot, sample_roll, sample_pitch);
	}

	@Test
	public void testI20CryostatIteratorOneTemp() throws Exception {
		String name = "one cryo name";
		String desc = "one cryo desc";

		CryostatSampleDetails sample1 = new CryostatSampleDetails();
		sample1.setNumberOfRepetitions(1);
		sample1.setPosition(7.0);
		sample1.setFinePosition(2.1);
		sample1.setSample_name(name);
		sample1.setSampleDescription(desc);

		List<CryostatSampleDetails> samples = new ArrayList<CryostatSampleDetails>();
		samples.add(sample1);

		CryostatParameters cryoParams = new CryostatParameters();
		cryoParams.setLoopChoice(CryostatProperties.LOOP_OPTION[0]);
		cryoParams.setTemperature("350.0");
		cryoParams.setTolerance(5.0);
		cryoParams.setWaitTime(10);
		cryoParams.setControlMode(CryostatProperties.CONTROL_MODE[4]);
		cryoParams.setHeaterRange(CryostatProperties.HEATER_RANGE[1]);
		cryoParams.setSamples(samples);

		I20SampleParameters samParams = new I20SampleParameters();
		samParams.setSampleEnvironment(I20SampleParameters.SAMPLE_ENV[2]);
		samParams.setCryostatParameters(cryoParams);

		thePreparer.configure(null, samParams);

		SampleEnvironmentIterator theIterator = thePreparer.createIterator("Xanes");

		// the movement operation
		theIterator.next();

		assertTrue(theIterator.getNumberOfRepeats() == 1);

		assertTrue(theIterator.getNextSampleName().equals(name));

		assertTrue(theIterator.getNextSampleDescriptions().get(0).equals(desc));

		// verify movement
		Mockito.verifyZeroInteractions(sample_x, sample_y, sample_z, sample_rot, sample_fine_rot, sample_roll,
				sample_pitch);
		Mockito.verify(cryostat).asynchronousMoveTo(350.0);
	}

	@Test
	public void testI20CryostatIteratorList() throws Exception {
		String name = "one cryo name";
		String desc = "one cryo desc";

		CryostatSampleDetails sample1 = new CryostatSampleDetails();
		sample1.setNumberOfRepetitions(1);
		sample1.setPosition(7.0);
		sample1.setFinePosition(2.1);
		sample1.setSample_name(name);
		sample1.setSampleDescription(desc);

		List<CryostatSampleDetails> samples = new ArrayList<CryostatSampleDetails>();
		samples.add(sample1);

		CryostatParameters cryoParams = new CryostatParameters();
		cryoParams.setLoopChoice(CryostatProperties.LOOP_OPTION[0]);
		cryoParams.setTemperature("350.0, 400.0, 410");
		cryoParams.setTolerance(5.0);
		cryoParams.setWaitTime(10);
		cryoParams.setControlMode(CryostatProperties.CONTROL_MODE[4]);
		cryoParams.setHeaterRange(CryostatProperties.HEATER_RANGE[1]);
		cryoParams.setSamples(samples);

		I20SampleParameters samParams = new I20SampleParameters();
		samParams.setSampleEnvironment(I20SampleParameters.SAMPLE_ENV[2]);
		samParams.setCryostatParameters(cryoParams);

		thePreparer.configure(null, samParams);

		SampleEnvironmentIterator theIterator = thePreparer.createIterator("Xanes");

		// the movement operation
		theIterator.next();

		assertTrue(theIterator.getNumberOfRepeats() == 3);

		assertTrue(theIterator.getNextSampleName().equals(name));

		assertTrue(theIterator.getNextSampleDescriptions().get(0).equals(desc));

		// verify movement
		Mockito.verifyZeroInteractions(sample_x, sample_y, sample_z, sample_rot, sample_fine_rot, sample_roll,
				sample_pitch);
		Mockito.verify(cryostat).asynchronousMoveTo(350.0);

		theIterator.next();
		Mockito.verifyZeroInteractions(sample_x, sample_y, sample_z, sample_rot, sample_fine_rot, sample_roll,
				sample_pitch);
		Mockito.verify(cryostat).asynchronousMoveTo(400.0);

		theIterator.next();
		Mockito.verifyZeroInteractions(sample_x, sample_y, sample_z, sample_rot, sample_fine_rot, sample_roll,
				sample_pitch);
		Mockito.verify(cryostat).asynchronousMoveTo(410.0);
	}

	@Test
	public void testI20CryostatIteratorRange() throws Exception {

		String name = "one cryo name";
		String desc = "one cryo desc";

		CryostatSampleDetails sample1 = new CryostatSampleDetails();
		sample1.setNumberOfRepetitions(1);
		sample1.setPosition(7.0);
		sample1.setFinePosition(2.1);
		sample1.setSample_name(name);
		sample1.setSampleDescription(desc);

		List<CryostatSampleDetails> samples = new ArrayList<CryostatSampleDetails>();
		samples.add(sample1);

		CryostatParameters cryoParams = new CryostatParameters();
		cryoParams.setLoopChoice(CryostatProperties.LOOP_OPTION[0]);
		cryoParams.setTemperature("350.0;400.0; 25.0");
		cryoParams.setTolerance(5.0);
		cryoParams.setWaitTime(10);
		cryoParams.setControlMode(CryostatProperties.CONTROL_MODE[4]);
		cryoParams.setHeaterRange(CryostatProperties.HEATER_RANGE[1]);
		cryoParams.setSamples(samples);

		I20SampleParameters samParams = new I20SampleParameters();
		samParams.setSampleEnvironment(I20SampleParameters.SAMPLE_ENV[2]);
		samParams.setCryostatParameters(cryoParams);

		thePreparer.configure(null, samParams);

		SampleEnvironmentIterator theIterator = thePreparer.createIterator("Xanes");

		// the movement operation
		theIterator.next();

		assertTrue(theIterator.getNumberOfRepeats() == 3);

		assertTrue(theIterator.getNextSampleName().equals(name));

		assertTrue(theIterator.getNextSampleDescriptions().get(0).equals(desc));

		// verify movement
		Mockito.verifyZeroInteractions(sample_x, sample_y, sample_z, sample_rot, sample_fine_rot, sample_roll,
				sample_pitch);
		Mockito.verify(cryostat).asynchronousMoveTo(350.0);

		theIterator.next();
		Mockito.verifyZeroInteractions(sample_x, sample_y, sample_z, sample_rot, sample_fine_rot, sample_roll,
				sample_pitch);
		Mockito.verify(cryostat).asynchronousMoveTo(375.0);

		theIterator.next();
		Mockito.verifyZeroInteractions(sample_x, sample_y, sample_z, sample_rot, sample_fine_rot, sample_roll,
				sample_pitch);
		Mockito.verify(cryostat).asynchronousMoveTo(400.0);

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
		samParams.setSampleEnvironment(I20SampleParameters.SAMPLE_ENV[0]);

		thePreparer.configure(null, samParams);

		SampleEnvironmentIterator theIterator = thePreparer.createIterator("Xanes");

		// the movement operation
		theIterator.next();

		Mockito.verifyZeroInteractions(sample_x, sample_y, sample_z, sample_rot, sample_fine_rot, sample_roll,
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

		Mockito.verifyZeroInteractions(filterwheel);
	}
}
