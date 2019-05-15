/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

import gda.images.camera.BeamDataComponent.BeamData;
import gda.images.camera.Utilities.OmegaDirection;

/**
 * Provides utility functions related to manipulating the sample viewed by a gda.images.camera object or viewed by a
 * gda.images.GUI panel.
 */
public class Geometry {

	private static final Logger logger = LoggerFactory.getLogger(Geometry.class);

	private final RealMatrix axisOrientationMatrix;
	private final OmegaDirection omegaDirection;
	private final boolean allowBeamAxisMovement;
	private final boolean gonioOnLeftOfImage;

	private final BeamDataComponent beamDataComponent;
	private final Camera camera;

	public Geometry(RealMatrix axisOrientationMatrix, OmegaDirection omegaDirection, boolean allowBeamAxisMovement, boolean gonioOnLeftOfImage, BeamDataComponent beamDataComponent, Camera camera) {
		this.axisOrientationMatrix = axisOrientationMatrix;
		this.omegaDirection = omegaDirection;
		this.allowBeamAxisMovement = allowBeamAxisMovement;
		this.gonioOnLeftOfImage = gonioOnLeftOfImage;
		this.beamDataComponent = beamDataComponent;
		this.camera = camera;
	}

	/**
	 * Given the requested vertical and horizontal movements in microns of the sample as viewed in the image plane of a
	 * sample viewing camera, and the current goniometer angle, calculates the required xyz movements of the sample
	 * stage to achieve this.
	 * <p>
	 * This requires the java property gda.images.horizontaldirection.
	 *
	 * @param deltaHum
	 * @param deltaVum
	 * @param omega
	 * @return double[] - the x,y, and z sample stage movements required
	 */
	public double[] micronToXYZMove(double deltaHum, double deltaVum, double omega) {
		return micronToXYZMove(deltaHum, deltaVum, 0, omega);
	}

	/**
	 * @param h horizontal movement
	 * @param v vertical movement
	 * @param b movement along beam path
	 * @param omega current angle, in degrees
	 *
	 * @return beamline-specific movement
	 */
	public double[] micronToXYZMove(double h, double v, double b, double omega) {
		// This is designed for phase 1 mx, with the hardware located to the right of the beam, and the z axis is
		// perpendicular to the beam and normal to the rotational plane of the omega axis. When the x axis is vertical
		// then the y axis is anti-parallel to the beam direction.

		// On I24, the hardware is located to the right of the beam. The x axis is along the rotation axis, and at
		// omega=0, the y axis is along the beam and the z axis is vertically down.

		// By definition, when omega = 0, the x axis will be positive in the vertical direction and a positive omega
		// movement will rotate clockwise when looking at the viewed down the microglide z-axis. This is standard in
		// crystallography.

		double angle = Math.toRadians(omega);

		if (omegaDirection == OmegaDirection.ANTICLOCKWISE) {
			angle = -angle;
		}

		if (!allowBeamAxisMovement) {
			b = 0;
		}

		// These calculations are done as though we are looking at the back of
		// the gonio, with the beam coming from the left. They follow the
		// mathematical convention that X +ve goes right, Y +ve goes vertically
		// up. Z +ve is away from the gonio (away from you). This is NOT the
		// standard phase I convention.
		final double x = b * cos(angle) - v * sin(angle);
		final double y = b * sin(angle) + v * cos(angle);
		double z = h;

		if (!gonioOnLeftOfImage) {
			z *= -1;
		}

		RealVector movement = MatrixUtils.createRealVector(new double[] {x, y, z});
		RealVector beamlineMovement = axisOrientationMatrix.operate(movement);
		return beamlineMovement.getData();
	}

	/**
	 * Converts from pixels to microns, using the microns per pixel values of the current zoom level.
	 */
	public double[] pixelsToMicrons(int h, int v) {
		try {
			BeamData currentBeamData = beamDataComponent.getCurrentBeamData();
			if (currentBeamData == null) {
				return new double[] {0, 0};
			}
			int hMicrons = (int) (h * camera.getMicronsPerXPixel());
			int vMicrons = (int) (v * camera.getMicronsPerYPixel());
			return new double[] {hMicrons, vMicrons};

		} catch (Exception e) {
			logger.error("Error while trying to get micron/pixel conversion from optical camera.", e);
			return new double[] {0, 0};
		}
	}

	/**
	 * Given the pixel coordinates of the item to be moved to the beam centre, calculates the horizontal and vertical
	 * movements required in microns of the sample stage in the plane of the image.
	 * <p>
	 * This uses the scaling factors of the PXCamera's current zoom level.
	 *
	 * @param horizDisplayClicked
	 * @param vertDisplayClicked
	 * @return double[] - the required horizontal and vertical movements in microns
	 */
	public double[] pixelToMicronMove(int horizDisplayClicked, int vertDisplayClicked) {
		BeamData currentBeamData = beamDataComponent.getCurrentBeamData();
		if (currentBeamData == null) {
			return new double[] {0, 0};
		}

		int vertMove = vertDisplayClicked - currentBeamData.yCentre;
		int horizMove = currentBeamData.xCentre - horizDisplayClicked;

		return pixelsToMicrons(horizMove, vertMove);
	}

	/**
	 * Given the locations on the sample viewing camera image, returns the sample stage movements required to move what
	 * is at that location into the beam.
	 * <p>
	 * This assumes that there is a gda.images.camera.Camera object available which is properly configured. The scaling
	 * factors of its current zoom level are used in the calculation.
	 *
	 * @param Hpix
	 * @param Vpix
	 * @param omega
	 * @return double[] - the x,y, and z sample stage movements required
	 */
	public double[] calculateSampleStageMove(int Hpix, int Vpix, double omega) {
		double[] micronMoves = pixelToMicronMove(Hpix, Vpix);
		return micronToXYZMove(micronMoves[0], micronMoves[1], omega);
	}

}