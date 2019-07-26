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

import gda.device.DeviceException;

/**
 * Simulated object fulfilling the gda.images.camera.Camera interface To have a proper simulation create a test image at
 * /tmp/test.jpg.
 */
public class DummyOpticalCamera extends CameraBase {
	private double[] zoomPositions = { 1.0, 1.25, 1.5, 1.75 };

	private double[] focusPositions = { 1.0, 1.25, 1.5, 1.75 };

	private double focus = 1.0;

	private double zoom = 1.0;

	protected double micronsPerXPixel = 1.0;

	protected double micronsPerYPixel = 1.0;

	/**
	 * Constructor.
	 */
	public DummyOpticalCamera() {
		this.imageFile = "/tmp/test.jpg";
	}

	public void setMicronsPerXPixel(double micronsPerXPixel) {
		this.micronsPerXPixel = micronsPerXPixel;
	}

	public void setMicronsPerYPixel(double micronsPerYPixel) {
		this.micronsPerYPixel = micronsPerYPixel;
	}

	@Override
	public void captureImage(String imageName) throws DeviceException {
		notifyIObservers(this, IMAGE_UPDATED + cameraName);
	}

	@Override
	public BufferedImage getImage() throws DeviceException {
		// do nothing
		return null;
	}

	@Override
	public double getFocus() throws DeviceException {
		return this.focus;
	}

	@Override
	public double[] getFocusLevels() throws DeviceException {
		return focusPositions;
	}

	@Override
	public double getZoom() throws DeviceException {
		return this.zoom;
	}

	@Override
	public double[] getZoomLevels() throws DeviceException {
		return zoomPositions;
	}

	@Override
	public void setFocus(double focus) throws DeviceException {
		// loop through possible positions, if a match found then set it.
		for (double known : focusPositions) {
			if (known == focus) {
				this.focus = focus;
				notifyIObservers(this, FOCUS_SET + focus);
				return;
			}
		}
	}

	@Override
	public void setZoom(double zoom) throws DeviceException {
		// loop through possible positions, if a match found then set it.
		for (double known : zoomPositions) {
			if (known == zoom) {
				this.zoom = zoom;
				notifyIObservers(this, ZOOM_SET + zoom);
				return;
			}
		}
	}

	@Override
	public double getMicronsPerXPixel() {
		return micronsPerXPixel;
	}

	@Override
	public double getMicronsPerYPixel() {
		return micronsPerYPixel;
	}

}
