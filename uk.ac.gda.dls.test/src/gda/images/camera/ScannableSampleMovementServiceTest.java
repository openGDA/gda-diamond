/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

import org.apache.commons.math.linear.MatrixUtils;

import gda.device.DeviceException;
import gda.device.scannable.DummyScannable;
import gda.images.camera.Utilities.OmegaDirection;
import junit.framework.TestCase;

public class ScannableSampleMovementServiceTest extends TestCase {
	
	private DummySampleStageScannable sampleXyz;
	private DummyOmegaScannable omega;
	
	private ScannableSampleMovementService sms;
	
	final double[] ZERO_POSITION = new double[] {0, 0, 0};
	
	/**
	 * Delta used when comparing doubles.
	 */
	private static final double DELTA = 0.001;
	
	@Override
	protected void setUp() throws Exception {
		sampleXyz = new DummySampleStageScannable();
		omega = new DummyOmegaScannable();
		
		sms = new ScannableSampleMovementService();
		sms.setSampleXyz(sampleXyz);
		sms.setOmegaScannable(omega);
	}
	
	public void testWithBasicSettings() throws Exception {
		sms.setOmegaDirection(OmegaDirection.ANTICLOCKWISE);
		sms.setAxisOrientationMatrix(MatrixUtils.createRealIdentityMatrix(3));
		sms.afterPropertiesSet();
		
		assertPositionsEqual(ZERO_POSITION, sampleXyz.getPositionArray());
		assertEquals(0, omega.getAngle(), DELTA);
		
		sms.moveSampleByMicrons(10, 20, 30);
		
		assertPositionsEqual(new double[] {10, 20, 30}, sampleXyz.getPositionArray());
		assertEquals(0, omega.getAngle(), DELTA);
	}
	
	public void testWithNonZeroOmega() throws Exception {
		sms.setOmegaDirection(OmegaDirection.ANTICLOCKWISE);
		sms.setAxisOrientationMatrix(MatrixUtils.createRealIdentityMatrix(3));
		sms.afterPropertiesSet();
		
		omega.moveTo(90);
		
		assertPositionsEqual(ZERO_POSITION, sampleXyz.getPositionArray());
		assertEquals(90, omega.getAngle(), DELTA);
		
		sms.moveSampleByMicrons(10, 20, 30);
		
		assertPositionsEqual(new double[] {10, -30, 20}, sampleXyz.getPositionArray());
		assertEquals(90, omega.getAngle(), DELTA);
	}
	
	public void testWithClockwisePhiDirection() throws Exception {
		sms.setOmegaDirection(OmegaDirection.CLOCKWISE);
		sms.setAxisOrientationMatrix(MatrixUtils.createRealIdentityMatrix(3));
		sms.afterPropertiesSet();
		
		omega.moveTo(90);
		
		assertPositionsEqual(ZERO_POSITION, sampleXyz.getPositionArray());
		assertEquals(90, omega.getAngle(), DELTA);
		
		sms.moveSampleByMicrons(10, 20, 30);
		
		assertPositionsEqual(new double[] {10, 30, -20}, sampleXyz.getPositionArray());
		assertEquals(90, omega.getAngle(), DELTA);
	}
	
	public void testWithNonIdentityAxisOrientationMatrix() throws Exception {
		sms.setOmegaDirection(OmegaDirection.ANTICLOCKWISE);
		sms.setAxisOrientationMatrix(MatrixUtils.createRealMatrix(new double[][] {{0,1,0}, {0,0,1}, {1,0,0}}));
		sms.afterPropertiesSet();
		
		omega.moveTo(90);
		
		assertPositionsEqual(ZERO_POSITION, sampleXyz.getPositionArray());
		assertEquals(90, omega.getAngle(), DELTA);
		
		sms.moveSampleByMicrons(10, 20, 30);
		
		assertPositionsEqual(new double[] {-30, 20, 10}, sampleXyz.getPositionArray());
		assertEquals(90, omega.getAngle(), DELTA);
	}
	
	protected static void assertPositionsEqual(double[] expected, double[] actual) {
		assertEquals(expected.length, actual.length);
		for (int i=0; i<expected.length; i++) {
			assertEquals(expected[i], actual[i], DELTA);
		}
	}
}

class DummyOmegaScannable extends DummyScannable {

	public double getAngle() throws DeviceException {
		return (Double) getPosition();
	}

}
