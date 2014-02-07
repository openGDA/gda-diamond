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

import static org.junit.Assert.*;
import gda.device.DeviceException;
import gda.device.ScannableMotion;
import gda.device.scannable.DummyUnitsScannable;

import java.awt.geom.Line2D;
import java.awt.geom.Point2D;
import java.awt.geom.Rectangle2D;
import java.util.List;

import org.junit.Before;
import org.junit.Test;

import uk.ac.gda.beamline.i05.scannable.I05Apple.TrajectorySolver;

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
		String pol = apple.getCurrentPolarisation();
		assertEquals("H100 energy does not match", I05Apple.HORIZONTAL, pol);
	}

	@Test
	public void testV100_1Pol() throws DeviceException {
		lower.moveTo(70.0);
		upper.moveTo(70.0);
		String pol = apple.getCurrentPolarisation();
		assertEquals("H100 energy does not match", I05Apple.VERTICAL, pol);
	}
	
	@Test
	public void testV100_2Pol() throws DeviceException {
		lower.moveTo(-70.0);
		upper.moveTo(-70.0);
		String pol = apple.getCurrentPolarisation();
		assertEquals("H100 energy does not match", I05Apple.VERTICAL, pol);
	}
	
	@Test
	public void testFailForMismatch() throws DeviceException {
		lower.moveTo(-7.0);
		upper.moveTo(17.0);
		try {
			apple.getCurrentPolarisation();
			fail("getPolarisation does not thow exception with differing phases");
		} catch (DeviceException de) {
			// expected
		}
	}

	@Test
	public void testCircPhaseCalc() throws DeviceException {
		double phase = apple.getPhaseForGap(32.0, I05Apple.CIRCULAR_LEFT);
		assertEquals("testCircPhaseCalc phase does not match", -45.45, phase, 0.2);
	}
	
	/*
	 * Trajectory solver tests
	 */

	
	@Test
	public void testSimpleAvoid() throws DeviceException {
		Rectangle2D[] rectangles = new Rectangle2D[] { new Rectangle2D.Double(7, 0, 9, 5), 
				new Rectangle2D.Double(12, 0, 2, 10)};
		Line2D line = new Line2D.Double(2, 3, 1, 11);
		TrajectorySolver ts = new I05Apple().new TrajectorySolver(rectangles);
		List<Line2D> list = ts.avoidZone(line);
		Point2D[] pointArray = I05Apple.trajectoryToPointArray(list);
		assertArrayEquals(new Point2D[] {new Point2D.Double(2, 3), new Point2D.Double(1, 11)}, pointArray);
	}

	@Test
	public void testTrivialAvoid() throws DeviceException {
		Rectangle2D[] rectangles = new Rectangle2D[] { new Rectangle2D.Double(7, 0, 9, 5), 
				new Rectangle2D.Double(12, 0, 2, 10)};
		Line2D line = new Line2D.Double(3, 3, 5, 10);
		TrajectorySolver ts = new I05Apple().new TrajectorySolver(rectangles);
		List<Line2D> list = ts.avoidZone(line);
		Point2D[] pointArray = I05Apple.trajectoryToPointArray(list);
		assertArrayEquals(new Point2D[] {new Point2D.Double(3, 3), new Point2D.Double(5, 10)}, pointArray);
	}

	@Test
	public void testSingleAvoid() throws DeviceException {
		Rectangle2D[] rectangles = new Rectangle2D[] { new Rectangle2D.Double(7, 0, 9, 5), 
				new Rectangle2D.Double(12, 0, 2, 10)};
		Line2D line = new Line2D.Double(5, 2, 11, 6);
		TrajectorySolver ts = new I05Apple().new TrajectorySolver(rectangles);
		List<Line2D> list = ts.avoidZone(line);
		Point2D[] pointArray = I05Apple.trajectoryToPointArray(list);
		assertArrayEquals(new Point2D[] {new Point2D.Double(5, 2), new Point2D.Double(7, 5), new Point2D.Double(11, 6)}, pointArray);
	}

	@Test
	public void testComplexAvoid() throws DeviceException {
		Rectangle2D[] rectangles = new Rectangle2D[] { new Rectangle2D.Double(7, 0, 9, 5), 
				new Rectangle2D.Double(12, 0, 2, 10)};
		Line2D line = new Line2D.Double(5, 5, 17, 1);
		TrajectorySolver ts = new I05Apple().new TrajectorySolver(rectangles);
		List<Line2D> list = ts.avoidZone(line);
		Point2D[] pointArray = I05Apple.trajectoryToPointArray(list);
		assertArrayEquals(new Point2D[] {new Point2D.Double(5, 5), new Point2D.Double(12, 10), new Point2D.Double(14, 10), new Point2D.Double(16, 5), new Point2D.Double(17, 1)}, pointArray);
	}
	
	@Test
	public void testTrickyAvoid() throws DeviceException {
		Rectangle2D[] rectangles = new Rectangle2D[] { new Rectangle2D.Double(7, 0, 9, 5), 
				new Rectangle2D.Double(12, 0, 2, 10)};
		Line2D line = new Line2D.Double(5, 0, 13.5, 10);
		TrajectorySolver ts = new I05Apple().new TrajectorySolver(rectangles);
		List<Line2D> list = ts.avoidZone(line);
		Point2D[] pointArray = I05Apple.trajectoryToPointArray(list);
		assertArrayEquals(new Point2D[] {new Point2D.Double(5, 0), new Point2D.Double(7, 5), new Point2D.Double(12, 10), new Point2D.Double(13.5, 10)}, pointArray);
	}
}