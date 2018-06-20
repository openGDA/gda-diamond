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

import static java.lang.Math.cos;
import static java.lang.Math.sin;

import org.apache.commons.math.linear.MatrixUtils;
import org.apache.commons.math.linear.RealMatrix;
import org.apache.commons.math.linear.RealVector;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

import gda.device.DeviceException;
import gda.factory.FindableBase;
import gda.images.camera.Utilities.OmegaDirection;

/**
 * Base class for classes that implement {@link SampleMovementService}.
 */
public abstract class SampleMovementServiceBase extends FindableBase implements SampleMovementService, InitializingBean {

	private static final Logger logger = LoggerFactory.getLogger(SampleMovementServiceBase.class);
	
	private OmegaDirection omegaDirection;
	
	public void setOmegaDirection(OmegaDirection omegaDirection) {
		this.omegaDirection = omegaDirection;
	}
	
	private RealMatrix axisOrientationMatrix;
	
	/**
	 * Sets the beamline-specific axis orientation matrix, which is a 3×3 matrix that defines how the 'standard' axes
	 * map onto the beamline's axes.
	 */
	public void setAxisOrientationMatrix(RealMatrix axisOrientationMatrix) {
		this.axisOrientationMatrix = axisOrientationMatrix;
	}
	
	@Override
	public void afterPropertiesSet() throws Exception {
		if (omegaDirection == null) {
			throw new IllegalArgumentException("The 'omegaDirection' property is required");
		}
		if (axisOrientationMatrix == null) {
			throw new IllegalArgumentException("The 'axisOrientationMatrix' property is required");
		}
	}
	
	@Override
	public void moveSampleByMicrons(double h, double v, double b) throws DeviceException {
		logger.debug(String.format("move in microns: (h=%.2f, v=%.2f, b=%.2f)", h, v, b));
		
		double ω = getOmega();
		logger.debug(String.format("ω=%.2f°", ω));
		
		double[] xyz = doRotation(h, v, b, ω);
		
		moveSampleByMicronsAlongStandardAxes(xyz[0], xyz[1], xyz[2]);
	}
	
	protected abstract double getOmega() throws DeviceException;
	
	protected double[] doRotation(double h, double v, double b, double ω) {
		
		// hvb → xyz mapping
		final double x = b;
		final double y = v;
		final double z = h;
		
		// degrees → radians
		double θ = Math.toRadians(ω);
		
		if (omegaDirection == OmegaDirection.ANTICLOCKWISE) {
			θ = -θ;
		}
		
		// http://en.wikipedia.org/wiki/Rotation_(geometry)#Matrix_algebra
		final double xʼ = x * cos(θ) - y * sin(θ);
		final double yʼ = x * sin(θ) + y * cos(θ);
		final double zʼ = z;
		
		// xyz → hvb mapping
		final double hʼ = zʼ;
		final double vʼ = yʼ;
		final double bʼ = xʼ;
		
		return new double[] {hʼ, vʼ, bʼ};
	}
	
	@Override
	public void moveSampleByMicronsAlongStandardAxes(double h, double v, double b) throws DeviceException {
		logger.debug(String.format("move in microns (standard axes): (h=%.2f, v=%.2f, b=%.2f)", h, v, b));
		RealVector originalMovement = MatrixUtils.createRealVector(new double[] {h, v, b});
		RealVector beamlineMovement = axisOrientationMatrix.operate(originalMovement);
		moveSampleByMicronsAlongBeamlineAxes(
			beamlineMovement.getEntry(0),
			beamlineMovement.getEntry(1),
			beamlineMovement.getEntry(2));
	}
	
	@Override
	public void moveSampleByMicronsAlongBeamlineAxes(double x, double y, double z) throws DeviceException {
		logger.debug(String.format("move in microns (beamline axes): (x=%.2f, y=%.2f, z=%.2f)", x, y, z));
		double[] currentPos = getPosition();
		RealVector currentPosVector = MatrixUtils.createRealVector(currentPos);
		logger.debug(String.format("current position is %s", currentPosVector));
		RealVector move = MatrixUtils.createRealVector(new double[] {x, y, z});
		RealVector newPosition = currentPosVector.add(move);
		logger.debug(String.format("new position is %s", newPosition));
		setPosition(newPosition.getData());
	}
	
	/**
	 * Returns the current position of the sample.
	 * 
	 * @return a 3-element double array
	 */
	protected abstract double[] getPosition() throws DeviceException;
	
	/**
	 * Sets the current position of the sample.
	 * 
	 * @param position a 3-element double array
	 */
	protected abstract void setPosition(double[] position) throws DeviceException;

}
