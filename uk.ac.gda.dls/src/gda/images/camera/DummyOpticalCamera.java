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

	private static final int RESET_INDEX = 0;

	private static final double SIMILARITY_THRESHOLD = 0.01;

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
	public void configure() {
		setZoomIndex(RESET_INDEX);
		setConfigured(true);
	}

	@Override
	public void captureImage(String imageName) throws DeviceException {
		notifyIObservers(this, IMAGE_UPDATED + cameraName);
	}

	@Override
	public BufferedImage getImage() {
		// do nothing
		return null;
	}

	@Override
	public double getFocus() {
		return this.focus;
	}

	@Override
	public double[] getFocusLevels() {
		return focusPositions;
	}

	@Override
	public double getZoom() {
		return this.zoom;
	}

	@Override
	public double[] getZoomLevels() {
		return zoomPositions;
	}

	@Override
	public void setFocus(double focus) {
		// loop through possible positions, if a match found then set it.
		for (double known : focusPositions) {
			if( areSimilar(focus, known, SIMILARITY_THRESHOLD) ) {
				this.focus = focus;
				notifyIObservers(this, FOCUS_SET + focus);
				return;
			}
		}
	}

    @Override
	protected void updateCameraToIndexedSettings(int verifiedIndex) {

    	zoom = getZoomLevels()[verifiedIndex];
		notifyIObservers(this, ZOOM_SET + zoom);
	}

	@Override
	public double getMicronsPerXPixel() {
		return micronsPerXPixel;
	}

	@Override
	public double getMicronsPerYPixel() {
		return micronsPerYPixel;
	}

	@Override
	protected double getZoomSimilarityTolerance() {
		return SIMILARITY_THRESHOLD;
	}

}
