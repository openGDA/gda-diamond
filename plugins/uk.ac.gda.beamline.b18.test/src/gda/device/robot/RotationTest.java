/*-
 * Copyright © 2023 Diamond Light Source Ltd.
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

package gda.device.robot;

import java.util.PrimitiveIterator.OfDouble;
import java.util.Random;

import org.junit.Assert;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RotationTest {
	private static final Logger logger = LoggerFactory.getLogger(RotationTest.class);

	private RotatedXyScannable scannable = new RotatedXyScannable();

	@Test
	public void testRotation() {
		scannable.setAngle(-45);
		scannable.setOrigin(0, 0);
		test( scannable.getStageXY(2, 2), Math.sqrt(8),0 );
		test( scannable.getLabXY(Math.sqrt(8), 0), 2, 2);
	}

	/**
	 * Test that transformations between lab and stage coordinate system produces consistent results :
	 * <li> Generate random lab(x,y) value -> transform to stage(x,y) value.
	 * <li> Calculate lab(x,y) value from computed stage(x,y) value.
	 * <li> Check computed lab(x,y) matches original lab(x,y) value.
	 */
	@Test
	public void testLabFromStage() {
		logger.info("Testing lab -> robot transformation");
		scannable.setAngle(-45);
		scannable.setOrigin(5, 5);

		var str = createRandomGenerator(123456, 20);
		int numVals = 10;

		// Generate random lab coordinates, compute robot coords and transform back to labl
		for(int i=0; i<numVals; i++) {
			// Compute robot (x,y) from lab (x,y) values
			double labX = str.next();
			double labY = str.next();
			var robotPos = scannable.getStageXY(labX, labY);
			logger.info("Lab : {},{}  Stage : {}", labX, labY, robotPos);

			// Transform robot (x,y) back to lab (x,y)
			var labPos = scannable.getLabXY(robotPos[0], robotPos[1]);

			// Check computed lab (x,y) match original values
			test(labPos, labX, labY);
		}
	}

	/**
	 * Same procedure as {@link #testLabFromStage()} except starting with random stage(x,y) value.
	 */
	@Test
	public void testRobotFromLab() {
		logger.info("Testing robot -> lab transformation");
		scannable.setAngle(26);
		scannable.setOrigin(106, 73.5);

		var str = createRandomGenerator(234567, 30);
		int numVals = 10;

		for(int i=0; i<numVals; i++) {
			double robotX = str.next();
			double robotY = str.next();
			var labPos = scannable.getLabXY(robotX, robotY);
			logger.info("Stage : {},{}  Lab : {}", robotX, robotY, labPos);
			var robotPos = scannable.getStageXY(labPos[0], labPos[1]);
			test(robotPos, robotX, robotY);
		}
	}

	private void test(double[] point, double... vals) {
		Assert.assertArrayEquals(vals, point, 1e-6);
		logger.info("Point {} is ok", point);
	}

	private OfDouble createRandomGenerator(int seed, double range) {
		Random rand = new Random(seed);
		return rand.doubles(-range, range).iterator();
	}
}
