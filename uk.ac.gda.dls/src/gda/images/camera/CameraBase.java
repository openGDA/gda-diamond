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

import gda.device.DeviceBase;
import gda.device.DeviceException;

/**
 * Base class for object implementing the Camera interface
 */
public abstract class CameraBase extends DeviceBase implements Camera {
	
	protected String cameraName = "A";

	protected String imageFile = null;

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
	public abstract double getMicronsPerXPixel();

	@Override
	public abstract double getMicronsPerYPixel();

}
