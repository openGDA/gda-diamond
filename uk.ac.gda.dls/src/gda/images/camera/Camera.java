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

import java.awt.image.BufferedImage;

import gda.device.Device;
import gda.device.DeviceException;

/**
 * Interface for sample viewing camera objects. These control the focus and zoom settings of a camera's optics and
 * capture individual images.
 * <p>
 * They also contain scaling factors to convert between pixels and microns for calculations relating to sample control.
 * The gda.images package assumes that the camera is on-axis looking at the sample which is held on an XYZ stage.
 * <p>
 * These objects are not for creating/displaying a stream of images
 */
public interface Camera extends Device, ImageScaleProvider {
	/**
	 * Message sent when image updated from camera
	 */
	public static final String IMAGE_UPDATED = "Image updated from camera ";

	/**
	 * Message sent when zoom changed in camera
	 */
	public static final String ZOOM_SET = "Camera zoom set to ";

	/**
	 * Message sent when focus changed in camera
	 */
	public static final String FOCUS_SET = "Camera focus set to ";

	/**
	 * get the name of the file that image is written to
	 *
	 * @return string - filename
	 * @throws DeviceException
	 */
	public String getImageFileName() throws DeviceException;

	/**
	 * @return string - name of the camera
	 * @throws DeviceException
	 */
	public String getCameraName() throws DeviceException;

	/**
	 * @return double - current focus level
	 * @throws DeviceException
	 */
	public double getFocus() throws DeviceException;

	/**
	 * @return double - current zoom level
	 * @throws DeviceException
	 */
	public double getZoom() throws DeviceException;

	/**
	 * Sets the zoom level. Number must be a member of the list returned by {@link #getZoomLevels()}.
	 *
	 * @param zoom
	 * @throws DeviceException
	 */
	public void setZoom(double zoom) throws DeviceException;

	/**
	 * Sets the zoom level via an index, based on array values (see {@link #getZoomLevels()}):
	 * @param targetIndex array index of new zoom level, ignored if out of range
	 * @throws DeviceException
	 */
	public void selectZoomAt(int targetIndex) throws DeviceException;

	/**
	 * @return the zoom index of the present zoom setting, else -1 if no zoom level is set, or no levels are present
	 */
	public int getZoomIndex();

	/**
	 * Sets the focus level. Number must be a member of the list returned by getFcouslevels.
	 *
	 * @param focus
	 * @throws DeviceException
	 */
	public void setFocus(double focus) throws DeviceException;

	/**
	 * Writes the current image to disk.
	 * <p>
	 * Filename should be the full path of the file to create. If it is null then the file listed in the configuration
	 * file will be overwritten.
	 *
	 * @param filename
	 * @throws DeviceException
	 */
	public void captureImage(String filename) throws DeviceException;

	/**
	 * Captures and returns an image.
	 */
	public BufferedImage getImage() throws DeviceException;

	/**
	 * @return double[] - the possible zoom levels
	 * @throws DeviceException
	 */
	public double[] getZoomLevels() throws DeviceException;

	/**
	 * @return double[] - the possible focus levels
	 * @throws DeviceException
	 */
	public double[] getFocusLevels() throws DeviceException;
}