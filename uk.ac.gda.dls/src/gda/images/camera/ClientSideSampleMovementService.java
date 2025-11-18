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

import gda.device.DeviceException;

/**
 * Interface to be implemented by services that provide client-side movement of the sample.
 */
public interface ClientSideSampleMovementService {

	/**
	 * Moves the sample by the requested number of pixels. X +ve is always the
	 * right hand side of the image; Y +ve is always the top of the image.
	 *
	 * <p><img src="doc-files/onscreen.png" />
	 *
	 * <p>The requested move in pixels is converted to a 'real-world' movement in microns. The X and Y axes for the
	 * pixel movement map onto the H and V axes respectively for the 'real-world' micron movement. (If the image has
	 * been flipped horizontally, this will automatically be taken into account.)
	 *
	 * <p><img src="doc-files/pixel_coords.png" />
	 *
	 * <p>The B movement along the beam is fixed at zero, as a beam axis movement in pixels is not allowed.
	 */
	void moveSampleByPixels(int x, int y) throws DeviceException;

	/**
	 * Moves the sample in microns. H +ve is always the right hand side of the image. V +ve is always the top of the
	 * image. B +ve is along the beam.
	 */
	void moveSampleByMicrons(double h, double v, double b) throws DeviceException;
}
