/*-
 * Copyright © 2023 Diamond Light Source Ltd.
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

package gda.device.detector;

import org.apache.commons.math3.geometry.euclidean.twod.Vector2D;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.IDataset;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableMotor;
import gda.device.scannable.ScannableUtils;

public class MoveableImageDetector extends DatasetNexusDetector {

	private Scannable xScannable;

	private Scannable yScannable;

	private Vector2D upperPositionLimit;
	private Vector2D imageSize;
	private Vector2D lowerPositionLimit;

	/**
	 * Compute Gaussian intensity distribution on 2-dimensional dataset.
	 * Intensity is centred on position given by xScannable and yScannable
	 */
	@Override
	public IDataset getDataset() throws DeviceException {
		// Get pixel position corresponding to current position of two scanables
		double xcoord = getScannablePosition(xScannable);
		double ycoord = getScannablePosition(yScannable);
		Vector2D pixelPosition = getPixelPosition(xcoord, ycoord);

		// Compute dataset with Gaussian intensity profile with x,y centre given by current scannable positions.
		IDataset dataset = DatasetFactory.zeros((int)imageSize.getX(), (int)imageSize.getY());
		for(int i=0; i<imageSize.getX(); i++) {
			for(int j=0; j<imageSize.getY(); j++) {
				double intensity = getIntensity(pixelPosition, i, j);
				dataset.set(intensity, i, j);
			}
		}
		return dataset;
	}

	private double getScannablePosition(Scannable scn) throws DeviceException {
		double offset = 0;
		if (scn instanceof ScannableMotor scnMotor) {
			offset = scnMotor.getOffset()[0];
		}
		return ScannableUtils.objectToDouble(scn.getPosition())+offset;
	}

	/**
	 * Compute pixel position on the image plane for given x and y 'real space' coordinates by :
	 * <li> Convert real (xpos, ypos) to fractional position between lower and upper position limits
	 * <li> Pixel position = Fractional position * image size
	 * (Image plane covers real positions from lowerPositionLimit (pixel=0,0) to upperPositionLimit (pixel=imageSize.x, imageSize.y))
	 *
	 * @param xpos
	 * @param ypos
	 * @return
	 */
	public Vector2D getPixelPosition(double xpos, double ypos) {
		// Calculate the position relative to lower position limit
		Vector2D absPosition = new Vector2D(xpos, ypos);
		Vector2D relPosition = absPosition.subtract(lowerPositionLimit);

		// Range covered by limits
		Vector2D sizeFromLimits = upperPositionLimit.subtract(lowerPositionLimit);

		// pixel position = fractional real space position * image size =
		return new Vector2D(imageSize.getX()*relPosition.getX()/sizeFromLimits.getX(),
							imageSize.getY()*relPosition.getY()/sizeFromLimits.getY());
	}

	/**
	 * Compute a intensity value of Gaussian, for coordinate (xpos, ypos) with Gaussian centred at 'origin'
	 * @param origin
	 * @param xpos
	 * @param ypos
	 * @return
	 */
	public double getIntensity(Vector2D origin, double xpos, double ypos) {
		double distSq = Vector2D.distanceSq(origin, new Vector2D(xpos, ypos));
		double fallOff = imageSize.getNorm();
		return 100*Math.exp(-distSq/fallOff);
	}

	public double[] getLowerPositionLimit() {
		return lowerPositionLimit.toArray();
	}

	public void setLowerPositionLimit(double[] lowerPositionLimit) {
		this.lowerPositionLimit = new Vector2D(lowerPositionLimit);
	}

	public double[] getUpperPositionLimit() {
		return upperPositionLimit.toArray();
	}

	public void setUpperPositionLimit(double[] upperPositionLimit) {
		this.upperPositionLimit = new Vector2D(upperPositionLimit);
	}

	public double[] getImageSize() {
		return imageSize.toArray();
	}

	public void setImageSize(double[] imageSize) {
		this.imageSize = new Vector2D(imageSize);
	}

	public Scannable getxScannable() {
		return xScannable;
	}

	public void setxScannable(Scannable xScannable) {
		this.xScannable = xScannable;
	}

	public Scannable getyScannable() {
		return yScannable;
	}

	public void setyScannable(Scannable yScannable) {
		this.yScannable = yScannable;
	}



}
