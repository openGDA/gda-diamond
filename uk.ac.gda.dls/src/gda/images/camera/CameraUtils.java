/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;

import javax.imageio.ImageIO;

public class CameraUtils {

	public static byte[] convertBufferedImageToByteArray(BufferedImage image) throws DeviceException {
		try {
			final ByteArrayOutputStream stream = new ByteArrayOutputStream();
			ImageIO.write(image, "png", stream);
			return stream.toByteArray();
		} catch (Exception e) {
			final String message = "Could not convert image";
			throw new DeviceException(message, e);
		}
	}
	
	public static BufferedImage convertByteArrayToBufferedImage(byte[] imageData) throws DeviceException {
		ByteArrayInputStream stream = new ByteArrayInputStream(imageData);
		try {
			final BufferedImage image = ImageIO.read(stream);
			return image;
		} catch (Exception e) {
			final String message = "Could not convert image";
			throw new DeviceException(message, e);
		}
	}
	
}
