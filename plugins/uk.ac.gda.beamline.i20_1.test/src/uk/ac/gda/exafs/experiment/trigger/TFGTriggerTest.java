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

package uk.ac.gda.exafs.experiment.trigger;

import static org.junit.Assert.*;

import org.junit.Test;

public class TFGTriggerTest {

	@Test
	public void testGetTfgSetupGrupsCommandParameters() throws Exception {

		TFGTrigger tfgTrigger = new TFGTrigger();
		
		tfgTrigger.getDetectorDataCollection().setTriggerDelay(4.0d);
		tfgTrigger.getDetectorDataCollection().setTriggerPulseLength(0.1d);
		tfgTrigger.getDetectorDataCollection().setNumberOfFrames(20);
		tfgTrigger.getDetectorDataCollection().setCollectionDuration(10.0d);
		
		TriggerableObject testObj = tfgTrigger.createNewSampleEnvEntry();
		testObj.setTriggerDelay(0.5d);
		testObj.setTriggerPulseLength(0.1d);
		tfgTrigger.getSampleEnvironment().add(testObj);
		
		testObj = tfgTrigger.createNewSampleEnvEntry();
		testObj.setTriggerDelay(0.8d);
		testObj.setTriggerPulseLength(20d);
		tfgTrigger.getSampleEnvironment().add(testObj);
		
		String command = tfgTrigger.getTfgSetupGrupsCommandParameters(1, false);
		assertTrue(command.equals("tfg setup-groups\n" +
			"1 0.500000 0.0 0 0 0 0\n" +
			"1 0.100000 0.0 4 0 0 0\n" +
			"1 0.200000 0.0 0 0 0 0\n" +
			"1 3.200000 0.0 8 0 0 0\n" +
			"1 0.100000 0.0 10 0 0 0\n" +
			"20 0 0.000001 0 8 0 9\n" +
			"1 6.800000 0.0 8 0 9 0\n" +
			"-1 0 0 0 0 0 0"));
	}
}
