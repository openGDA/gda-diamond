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

package gda.images.camera;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertSame;

import java.io.File;

import org.junit.Test;

/**
 * Tests the {@link Utilities} class.
 */
public class UtilitiesTest extends OavTestBase {

	/**
	 * Tests the Phase I calculations using an axis orientation matrix and
	 * "right" horizontal direction.
	 */
	@Test
	public void testPhaseICalculationsWithMatrixAndLeftHorizontalDirection() {
		setNewPropertiesForPhaseIWithLeftHorizontalDirection();
		doCalculationsForPhaseIWithLeftHorizontalDirection();
	}

	/**
	 * Tests the I24 calculations, using an axis orientation matrix.
	 */
	@Test
	public void testI24CalculationsUsingMatrix() {
		setNewPropertiesForI24();
		doCalculationsForI24();
	}

	/**
	 * Tests the I04.1 calculations, using an axis orientation matrix.
	 */
	@Test
	public void testJ04CalculationsUsingMatrix() {
		setNewPropertiesForJ04x();
		doCalculationsForJ04();
	}

	@Override
	protected double[] calculateActualMove(double[] requested, double phi) {
		return Utilities.micronToXYZMove(requested[0], requested[1], requested[2], phi);
	}

	@Test
	public void testPixelsToMicrons() {
		File displayConfigFile = new File("testfiles/gda/images/camera/display.configuration");
		BeamDataComponent component = BeamDataComponent.getTestingInstance(displayConfigFile.getAbsolutePath());
		component.setOpticalCamera(createDummyCamera());

		BeamDataComponent.setInstance(component);
		assertSame(component, BeamDataComponent.getInstance());

		// (10, 20) pixel move
		double[] actualMove = Utilities.pixelsToMicrons(10, 20);
		// expect actual move of (20, 50) microns
		assertEquals(20, actualMove[0], 0.001);
		assertEquals(50, actualMove[1], 0.001);
	}

	@Test
	public void testPixelToMicronMove() {
		File displayConfigFile = new File("testfiles/gda/images/camera/display.configuration");
		BeamDataComponent component = BeamDataComponent.getTestingInstance(displayConfigFile.getAbsolutePath());
		component.setOpticalCamera(createDummyCamera());

		BeamDataComponent.setInstance(component);
		assertSame(component, BeamDataComponent.getInstance());

		// (10, 20) pixel move from centre pixel position of (512, 384)
		double[] actualMove = Utilities.pixelToMicronMove(512+10, 384+20);
		// expect actual move of (20, 50) microns but horizontal direction is reversed, hence (-20, 50)
		assertEquals(-20, actualMove[0], 0.001);
		assertEquals(50, actualMove[1], 0.001);
	}

	@Test
	public void testCalculateSampleStageMove() {
		setNewPropertiesForPhaseIWithLeftHorizontalDirection();

		File displayConfigFile = new File("testfiles/gda/images/camera/display.configuration");
		BeamDataComponent component = BeamDataComponent.getTestingInstance(displayConfigFile.getAbsolutePath());
		component.setOpticalCamera(createDummyCamera());

		BeamDataComponent.setInstance(component);
		assertSame(component, BeamDataComponent.getInstance());

		// (10, 20) pixel move from centre pixel position of (512, 384)
		double[] actualMove = Utilities.calculateSampleStageMove(512+10, 384+20, 0);
		// expect actual move of (20, 50) microns but horizontal direction is reversed, hence (-20, 50)
		assertEquals(20,  actualMove[0], 0.001);
		assertEquals(-50, actualMove[1], 0.001);
		assertEquals(0,   actualMove[2], 0.001);
	}

	/**
	 * Creates a dummy {@link Camera} that always returns a zoom level of 1, and 2/2.5 microns per X/Y pixel
	 * respectively.
	 */
	protected static Camera createDummyCamera() {
		return new DummyOpticalCamera() {
			@Override
			public double getZoom() {
				return 1.0;
			}

			@Override
			public double getMicronsPerXPixel() {
				return 2;
			}

			@Override
			public double getMicronsPerYPixel() {
				return 2.5;
			}
		};
	}

}
