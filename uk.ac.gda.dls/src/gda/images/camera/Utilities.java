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

import java.util.Arrays;

import org.apache.commons.math.linear.RealMatrix;

import gda.configuration.properties.LocalProperties;
import gda.spring.propertyeditors.RealMatrixPropertyEditor;

/**
 * Provides utility functions related to manipulating the sample viewed by a gda.images.camera object or viewed by a
 * gda.images.GUI panel.
 */
public class Utilities {

	public static Geometry createGeometryFromGlobals() {
		final RealMatrix axisOrientationMatrix = getAxisOrientationMatrix();
		final OmegaDirection omegaDirection = getOmegaDirection();
		final boolean allowBeamAxisMovement = isAllowBeamAxisMovement();
		final boolean gonioOnLeftOfImage = isGonioOnLeftOfImage();
		final BeamDataComponent beamDataComponent = BeamDataComponent.getInstance();
		final Camera camera = beamDataComponent.getCamera();
		return new Geometry(axisOrientationMatrix, omegaDirection, allowBeamAxisMovement, gonioOnLeftOfImage, beamDataComponent, camera);
	}

	/**
	 * @see Geometry#micronToXYZMove(double, double, double)
	 */
	public static double[] micronToXYZMove(double deltaHum, double deltaVum, double omega) {
		return createGeometryFromGlobals().micronToXYZMove(deltaHum, deltaVum, omega);
	}

	/**
	 * Denotes the direction of a +ve omega rotation, when the goniometer is
	 * viewed from behind (with the beam travelling right).
	 */
	public enum OmegaDirection {

		/** +ve rotation of omega is clockwise */
		CLOCKWISE,

		/** +ve rotation of omega is anticlockwise */
		ANTICLOCKWISE;

		public boolean correspondsTo(String directionProperty) {
			return this.name().equalsIgnoreCase(directionProperty);
		}
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
	 * @see Geometry#micronToXYZMove(double, double, double, double)
	 */
	public static double[] micronToXYZMove(double h, double v, double b, double omega) {
		return createGeometryFromGlobals().micronToXYZMove(h, v, b, omega);
	}

	public static RealMatrix getAxisOrientationMatrix() {
		return createMatrixFromProperty(LocalProperties.GDA_PX_SAMPLE_CONTROL_AXIS_ORIENTATION);
	}

	public static OmegaDirection getOmegaDirection() {
		OmegaDirection defaultSense = OmegaDirection.CLOCKWISE;
		String omegaDirectionProperty = LocalProperties.get(LocalProperties.GDA_PX_SAMPLE_CONTROL_OMEGA_DIRECTION);
		return Arrays.stream(OmegaDirection.values())
						.filter( sense -> sense.correspondsTo(omegaDirectionProperty) )
						.findFirst()
						.orElse(defaultSense);
	}

	public static boolean isAllowBeamAxisMovement() {
		return LocalProperties.check(LocalProperties.GDA_PX_SAMPLE_CONTROL_ALLOW_BEAM_AXIS_MOVEMENT);
	}

	public static boolean isGonioOnLeftOfImage() {
		// Get the direction of the z axis wrt the horizontal movement when viewed from the image's viewpoint (this
		// depends on the camera oreintation wrt the z-axis). It must be assumed that otherwise, the camera views in
		// the beam vector and its image edges are parallel to the sample positioner axes)
		final String LEFT = "left";
		final String whichEdgeIsXAxisPositive = LocalProperties.get(LocalProperties.GDA_IMAGES_HORIZONTAL_DIRECTION, LEFT);
		final boolean gonioOnLeftOfImage = !whichEdgeIsXAxisPositive.equalsIgnoreCase(LEFT);
		return gonioOnLeftOfImage;
	}

	/**
	 * @see Geometry#pixelsToMicrons(int, int)
	 */
	public static double[] pixelsToMicrons(int h, int v) {
		return createGeometryFromGlobals().pixelsToMicrons(h, v);
	}

	/**
	 * @see Geometry#pixelToMicronMove(int, int)
	 */
	public static double[] pixelToMicronMove(int horizDisplayClicked, int vertDisplayClicked) {
		return createGeometryFromGlobals().pixelToMicronMove(horizDisplayClicked, vertDisplayClicked);
	}

	/**
	 * @see Geometry#calculateSampleStageMove(int, int, double)
	 */
	public static double[] calculateSampleStageMove(int Hpix, int Vpix, double omega) {
		return createGeometryFromGlobals().calculateSampleStageMove(Hpix, Vpix, omega);
	}

}