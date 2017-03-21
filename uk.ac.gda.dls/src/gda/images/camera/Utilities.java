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

import static java.lang.Math.cos;
import static java.lang.Math.sin;
import gda.configuration.properties.LocalProperties;
import gda.images.camera.BeamDataComponent.BeamData;
import gda.spring.propertyeditors.RealMatrixPropertyEditor;
import gda.util.exceptionUtils;

import org.apache.commons.math.linear.MatrixUtils;
import org.apache.commons.math.linear.RealMatrix;
import org.apache.commons.math.linear.RealVector;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Provides utility functions related to manipulating the sample viewed by a gda.images.camera object or viewed by a
 * gda.images.GUI panel.
 */
public class Utilities {
	
	private static final Logger logger = LoggerFactory.getLogger(Utilities.class);

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
	public static double[] micronToXYZMove(double deltaHum, double deltaVum, double omega) {
		return micronToXYZMove(deltaHum, deltaVum, 0, omega);
	}

	/**
	 * Denotes the direction of a +ve omega rotation, when the goniometer is
	 * viewed from behind (with the beam travelling right).
	 */
	public enum OmegaDirection {
		
		/** +ve rotation of omega is clockwise */
		CLOCKWISE,
		
		/** +ve rotation of omega is anticlockwise */
		ANTICLOCKWISE
	}
	
	public static RealMatrix createMatrixFromProperty(String propName) {
		
		RealMatrixPropertyEditor mpe = new RealMatrixPropertyEditor();
		mpe.setAsText(LocalProperties.get(propName));
		RealMatrix axisOrientationMatrix = mpe.getValue();
		if (axisOrientationMatrix.getRowDimension() != 3 || axisOrientationMatrix.getColumnDimension() != 3) {
			throw new IllegalArgumentException("Axis orientation matrix is not 3×3: " + axisOrientationMatrix);
		}
		
		return axisOrientationMatrix;
	}
	
	/**
	 * @param h horizontal movement
	 * @param v vertical movement
	 * @param b movement along beam path
	 * @param omega current angle, in degrees
	 * 
	 * @return beamline-specific movement
	 */
	public static double[] micronToXYZMove(double h, double v, double b, double omega) {
		final String omegaDirectionProperty = LocalProperties.get(LocalProperties.GDA_PX_SAMPLE_CONTROL_OMEGA_DIRECTION);
		boolean allowBeamAxisMovement = LocalProperties.check(LocalProperties.GDA_PX_SAMPLE_CONTROL_ALLOW_BEAM_AXIS_MOVEMENT);
		
		RealMatrix axisOrientationMatrix = createMatrixFromProperty(LocalProperties.GDA_PX_SAMPLE_CONTROL_AXIS_ORIENTATION);
		
		boolean omegaPositiveIsAnticlockwise = omegaDirectionProperty.equalsIgnoreCase("anticlockwise");
		OmegaDirection omegaDirection = omegaPositiveIsAnticlockwise ? OmegaDirection.ANTICLOCKWISE : OmegaDirection.CLOCKWISE;
		
		final boolean gonioOnLeftOfImage = isGonioOnLeftOfImage();
		
		return micronToXYZMove(h, v, b, omega, axisOrientationMatrix, omegaDirection, allowBeamAxisMovement, gonioOnLeftOfImage);
	}
	
	public static boolean isGonioOnLeftOfImage() {
		// Get the direction of the z axis wrt the horizontal movement when viewed from the image's viewpoint (this
		// depends on the camera oreintation wrt the z-axis). It must be assumed that otherwise, the camera views in
		// the beam vector and its image edges are parallel to the microglide axes)
		final String LEFT = "left";
		final String whichEdgeIsXAxisPositive = LocalProperties.get(LocalProperties.GDA_IMAGES_HORIZONTAL_DIRECTION, LEFT);
		final boolean gonioOnLeftOfImage = !whichEdgeIsXAxisPositive.equalsIgnoreCase(LEFT);
		return gonioOnLeftOfImage;
	}
	
	public static double[] micronToXYZMove(double h, double v, double b, double omega, RealMatrix axisOrientationMatrix, OmegaDirection omegaDirection, boolean allowBeamAxisMovement, boolean gonioOnLeftOfImage) {
		// This is designed for phase 1 mx, with the hardware located to the right of the beam, and the z axis is
		// perpendicular to the beam and normal to the rotational plane of the omega axis. When the x axis is vertical
		// then the y axis is anti-parallel to the beam direction.

		// On I24, the hardware is located to the right of the beam. The x axis is along the rotation axis, and at
		// omega=0, the y axis is along the beam and the z axis is vertically down.

		// By definition, when omega = 0, the x axis will be positive in the vertical direction and a positive omega
		// movement will rotate clockwise when looking at the viewed down the microglide z-axis. This is standard in
		// crystallography.

		double θ = Math.toRadians(omega);

		if (omegaDirection == OmegaDirection.ANTICLOCKWISE) {
			θ = -θ;
		}
		
		if (!allowBeamAxisMovement) {
			b = 0;
		}
		
		// These calculations are done as though we are looking at the back of
		// the gonio, with the beam coming from the left. They follow the
		// mathematical convention that X +ve goes right, Y +ve goes vertically
		// up. Z +ve is away from the gonio (away from you). This is NOT the
		// standard phase I convention.
		final double x = b * cos(θ) - v * sin(θ);
		final double y = b * sin(θ) + v * cos(θ);
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
	public static double[] pixelsToMicrons(int h, int v) {
		try {
			BeamDataComponent beamDataComponent = BeamDataComponent.getInstance();
			
			BeamData currentBeamData = beamDataComponent.getCurrentBeamData();
			if (currentBeamData == null) {
				return new double[] {0, 0};
			}
			Camera camera = beamDataComponent.getCamera();
			int hMicrons = (int) (h * camera.getMicronsPerXPixel());
			int vMicrons = (int) (v * camera.getMicronsPerYPixel());
			return new double[] {hMicrons, vMicrons};
			
		} catch (Exception e) {
			exceptionUtils.logException(logger, "Error while trying to get micron/pixel conversion from optical camera.", e);
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
	public static double[] pixelToMicronMove(int horizDisplayClicked, int vertDisplayClicked) {
		BeamData currentBeamData = BeamDataComponent.getInstance().getCurrentBeamData();
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
	public static double[] calculateSampleStageMove(int Hpix, int Vpix, double omega) {
		double[] micronMoves = pixelToMicronMove(Hpix, Vpix);
		return micronToXYZMove(micronMoves[0], micronMoves[1], omega);
	}

}