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

import static org.junit.Assert.*;

import java.util.Arrays;

import gda.configuration.properties.LocalProperties;

import org.junit.BeforeClass;

public abstract class OavTestBase {
	
	@BeforeClass
	static public void setUp() {
		// The beamline name is set to null to guarantee that the name won't be used in calculations
		LocalProperties.set(LocalProperties.GDA_BEAMLINE_NAME, null);
		
		LocalProperties.set(LocalProperties.GDA_IMAGES_HORIZONTAL_DIRECTION, null);
		LocalProperties.set(LocalProperties.GDA_PX_SAMPLE_CONTROL_AXIS_ORIENTATION, null);
		LocalProperties.set(LocalProperties.GDA_PX_SAMPLE_CONTROL_OMEGA_DIRECTION, null);
		LocalProperties.set(LocalProperties.GDA_PX_SAMPLE_CONTROL_ALLOW_BEAM_AXIS_MOVEMENT, null);
	}

	protected void doCalculationsForPhaseIWithRightHorizontalDirection() {
		final double[] requested = arrayOf(10, 20, 30);

		checkMove(requested,   0,  -10,  -20,     30   );
		checkMove(requested,  45,  -10,  -35.4,   7.1  );
		checkMove(requested,  90,  -10,  -30,    -20   );
		checkMove(requested, 135,  -10,  -7.1,   -35.4 );
		checkMove(requested, 180,  -10,   20,    -30   );
		checkMove(requested, 225,  -10,   35.4,  -7.1  );
		checkMove(requested, 270,  -10,   30,     20   );
		checkMove(requested, 315,  -10,   7.1,    35.4 );
	}
	
	protected void setNewPropertiesForPhaseIWithRightHorizontalDirection() {
		LocalProperties.set(LocalProperties.GDA_PX_SAMPLE_CONTROL_AXIS_ORIENTATION, "{{0;0;-1};{0;-1;0};{1;0;0}}");
		LocalProperties.set(LocalProperties.GDA_PX_SAMPLE_CONTROL_OMEGA_DIRECTION, "clockwise");
		LocalProperties.set(LocalProperties.GDA_PX_SAMPLE_CONTROL_ALLOW_BEAM_AXIS_MOVEMENT, "true");
		LocalProperties.set(LocalProperties.GDA_IMAGES_HORIZONTAL_DIRECTION, "right");
	}
	
	protected void setNewPropertiesForI24() {
		LocalProperties.set(LocalProperties.GDA_PX_SAMPLE_CONTROL_AXIS_ORIENTATION, "{{0;0;1};{-1;0;0};{0;-1;0}}");
		LocalProperties.set(LocalProperties.GDA_PX_SAMPLE_CONTROL_OMEGA_DIRECTION, "anticlockwise");
		LocalProperties.set(LocalProperties.GDA_PX_SAMPLE_CONTROL_ALLOW_BEAM_AXIS_MOVEMENT, "true");
		LocalProperties.set(LocalProperties.GDA_IMAGES_HORIZONTAL_DIRECTION, "right");
	}

	protected void doCalculationsForI24() {
		final double[] requested = arrayOf(10, 20, 30);
		
		checkMove(requested,   0,    10, -30,   -20);
		checkMove(requested,  45,    10, -35.4,   7);
		checkMove(requested,  90,    10, -20,    30);
		checkMove(requested, 135,    10,   7,    35.4);
		checkMove(requested, 180,    10,  30,    20);
		checkMove(requested, 225,    10,  35.4,  -7);
		checkMove(requested, 270,    10,  20,   -30);
		checkMove(requested, 315,    10,  -7,   -35.4);
	}

	protected void setNewPropertiesForJ04x() {
		LocalProperties.set(LocalProperties.GDA_PX_SAMPLE_CONTROL_AXIS_ORIENTATION, "{{0;0;1};{0;-1;0};{1;0;0}}");
		LocalProperties.set(LocalProperties.GDA_PX_SAMPLE_CONTROL_OMEGA_DIRECTION, "anticlockwise");
		LocalProperties.set(LocalProperties.GDA_PX_SAMPLE_CONTROL_ALLOW_BEAM_AXIS_MOVEMENT, "true");
		LocalProperties.set(LocalProperties.GDA_IMAGES_HORIZONTAL_DIRECTION, "right");
	}

	protected void doCalculationsForJ04() {
		final double[] requested = arrayOf(10, 20, 30);
		
		checkMove(requested,   0,    10,   -20,    30);
		checkMove(requested,  45,    10,     7,  35.4);
		checkMove(requested,  90,    10,    30,    20);
		checkMove(requested, 135,    10,  35.4,    -7);
		checkMove(requested, 180,    10,    20,   -30);
		checkMove(requested, 225,    10,    -7, -35.4);
		checkMove(requested, 270,    10,   -30,   -20);
		checkMove(requested, 315,    10, -35.4,     7);
	}
	
	/**
	 * Creates a double array from the given double values.
	 * 
	 * @param values the values
	 * 
	 * @return an array of the values
	 */
	private static double[] arrayOf(double... values) {
		return values;
	}
	
	/**
	 * Finds the actual move for the given requested move at the specified phi
	 * angle, and compares it with the given expected move.
	 * 
	 * @param requested the requested move
	 * @param phi the phi angle
	 * @param expected the expected move
	 */
	private void checkMove(double[] requested, double phi, double... expected) {
		double[] actual = calculateActualMove(requested, phi);
		final String beamline = LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME);
		System.out.println(beamline + ": requested " + Arrays.toString(requested) + " at phi=" + phi + "; expecting " + Arrays.toString(expected) + "; got " + Arrays.toString(actual));
		for (int i=0; i<=2; i++) {
			// Low delta - not bothered about the precise value, just that it
			// has the right sign and is approximately the same value
			assertEquals(expected[i], actual[i], 0.1);
		}
	}
	
	protected abstract double[] calculateActualMove(double[] requested, double phi);
	
}
