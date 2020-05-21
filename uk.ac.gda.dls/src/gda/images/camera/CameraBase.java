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

import static java.lang.Math.abs;

import gda.device.DeviceBase;
import gda.device.DeviceException;

/**
 * Base class for object implementing the Camera interface
 */
public abstract class CameraBase extends DeviceBase implements Camera {

	public static final int UNSET_ARRAY_INDEX = -1; // unset array index value - before it is actively set

	protected int cameraZoomIndexStatus = UNSET_ARRAY_INDEX;

	protected String cameraName = "A";

	protected String imageFile = null;

	/**
	 * Invoked (indirectly) by {@link #setZoom} for indexed zoom levels,
	 * @param verifiedIndex settings index; already verified to lie within range
	 */
	protected abstract void updateCameraToIndexedSettings(int verifiedIndex) throws DeviceException;

	@Override
	public String getImageFileName() throws DeviceException {
		return imageFile;
	}

	public void setImageFile(String imageFile) {
		this.imageFile = imageFile;
	}

	@Override
	public String getCameraName() throws DeviceException {
		return cameraName;
	}

	@Override
	public void selectZoomAt(int targetIndex) throws DeviceException {
		if( targetIndex < 0 ) return; // ignore negative target index

		double[] availableZoomLevels = getZoomLevels();
		if( targetIndex >= availableZoomLevels.length ) return; // ignore target index outside range

		updateCameraToIndexedSettings(targetIndex); // apply indexed zoom level to camera hardware
		setZoomIndex(targetIndex); // store recognised index in camera state, once zoom succeeds
	}

	@Override
	public final int getZoomIndex() {
		return cameraZoomIndexStatus;
	}

	protected final void setZoomIndex(int index) {
		if(0 > index) {
			cameraZoomIndexStatus = UNSET_ARRAY_INDEX;
		} else {
			cameraZoomIndexStatus = index;
		}
	}

	protected abstract double getZoomSimilarityTolerance();

	@Override
	public final void setZoom(double zoom) throws DeviceException
	{
		selectZoomAt( indexOfFirstSimilarElement(getZoomLevels(), zoom, getZoomSimilarityTolerance()) );
	}

	/**
	 * Checks a value against a reference value, indicating if they are similar to within a plus/minus tolerance
	 * @param x a value to check for similarity
	 * @param reference the expected value
	 * @param tol the tolerance
	 * @return true iff |x - ref| < |tol|
	 */
	protected static boolean areSimilar(double x, double reference, double tol) {
		return abs(x - reference) < abs(tol);
	}

	/**
	 * Searches an array for first element found to be within tolerance of a reference value:
	 * (See {@link #areSimilar(double, double, double)} for within tolerance definition.
	 * @param array An array to search
	 * @param reference A reference value to compare
	 * @param tol the similarity tolerance
	 * @return array index of the first similar element, or -1 if no similar elements are found
	 */
	protected static int indexOfFirstSimilarElement(double[] array, double reference, double tol) {
		int ii = UNSET_ARRAY_INDEX;

		for(double element : array) {
			ii++;
			if(areSimilar(reference, element, tol)) {
				return ii;
			}
		}
		return UNSET_ARRAY_INDEX;
	}
}
