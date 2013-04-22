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

package uk.ac.gda.beamline.i05.scannable;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;
import gda.device.DeviceException;
import gda.device.ScannableMotion;
import gda.device.scannable.DummyUnitsScannable;

import org.junit.Before;
import org.junit.Test;

public class I05AppleTest {

	ScannableMotion gap, lower, upper;
	I05Apple apple; 
	
	@Before
	public void setup() throws DeviceException {
		apple = new I05Apple();
		gap = new DummyUnitsScannable("gap", 100.0, "mm", "mm");
		gap.setTolerances(new Double[] { 0.1});
		lower = new DummyUnitsScannable("lower", 0.0, "mm", "mm");
		lower.setTolerances(new Double[] { 0.1});
		upper = new DummyUnitsScannable("upper", 0.0, "mm", "mm");
		upper.setTolerances(new Double[] { 0.1});
		apple.setLowerPhaseScannable(lower);
		apple.setUpperPhaseScannable(upper);
		apple.setGapScannable(gap);
	}
	
	@Test
	public void testH100Pol() throws DeviceException {
		String pol = apple.getPolarisation();
		assertEquals("H100 energy does not match", I05Apple.HORIZONTAL, pol);
	}
	
	@Test
	public void testH100() throws DeviceException {
		double energy = apple.getEnergy();
		assertEquals("H100 energy does not match", 292.0, energy, 2.0);
	}

	@Test
	public void testV100_1Pol() throws DeviceException {
		lower.moveTo(70.0);
		upper.moveTo(70.0);
		String pol = apple.getPolarisation();
		assertEquals("H100 energy does not match", I05Apple.VERTICAL, pol);
	}
	
	@Test
	public void testV100_2Pol() throws DeviceException {
		lower.moveTo(-70.0);
		upper.moveTo(-70.0);
		String pol = apple.getPolarisation();
		assertEquals("H100 energy does not match", I05Apple.VERTICAL, pol);
	}
	
	@Test
	public void testV100_1() throws DeviceException {
		lower.moveTo(70.0);
		upper.moveTo(70.0);
		double energy = apple.getEnergy();
		assertEquals("V100 energy does not match", 576.0, energy, 2.0);
	}
	
	@Test
	public void testV100_2() throws DeviceException {
		lower.moveTo(-70.0);
		upper.moveTo(-70.0);
		double energy = apple.getEnergy();
		assertEquals("V100 energy does not match", 576.0, energy, 2.0);
	}

	@Test
	public void testFailForMismatch() throws DeviceException {
		lower.moveTo(-7.0);
		upper.moveTo(17.0);
		
		try {
			apple.getEnergy();
			fail("getEnergy does not thow exception with differing phases");
		} catch (DeviceException de) {
			// expected
		}
		try {
			apple.getPolarisation();
			fail("getPolarisation does not thow exception with differing phases");
		} catch (DeviceException de) {
			// expected
		}
	}
	
	@Test
	public void testCircPhaseCalc() throws DeviceException {
		gap.moveTo(32.0);
		double phase = apple.getPhaseForGap(I05Apple.CIRCULAR_LEFT);
		assertEquals("testCircPhaseCalc phase does not match", 45.45, phase, 0.2);
	}
}