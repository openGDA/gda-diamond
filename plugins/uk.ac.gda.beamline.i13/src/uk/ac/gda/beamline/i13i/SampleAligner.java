/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i13i;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.ScannableMotionUnits;
import gda.device.scannable.ScannableUtils;

import org.apache.commons.math.linear.MatrixUtils;
import org.apache.commons.math.linear.RealVector;
import org.eclipse.swt.graphics.ImageData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beamline.i13i.views.cameraview.ImageViewerListener;
import uk.ac.gda.epics.adviewer.composites.imageviewer.IImagePositionEvent;
import uk.ac.gda.epics.adviewer.composites.imageviewer.ImageViewer;

public class SampleAligner  implements ImageViewerListener{
	private static final Logger logger = LoggerFactory.getLogger(SampleAligner.class);	
	
	Scannable rotationAxisXScannable;
	Scannable cameraXYScannable;
	DisplayScaleProvider displayScaleProvider;
	DisplayScaleProvider cameraScaleProvider;
	ScannableMotionUnits sampleCentringXMotor;
	ScannableMotionUnits sampleCentringYMotor;
	ScannableMotionUnits sampleBaseXMotor;
	ScannableMotionUnits sampleBaseYMotor;
	ScannableMotionUnits cameraStageXMotor;
	ScannableMotionUnits cameraStageYMotor;
	int imageWidth=4008;
	int imageHeight=2672;
	
	


	public Scannable getRotationAxisXScannable() {
		return rotationAxisXScannable;
	}

	public void setRotationAxisXScannable(Scannable rotationAxisXScannable) {
		this.rotationAxisXScannable = rotationAxisXScannable;
	}

	public DisplayScaleProvider getDisplayScaleProvider() {
		return displayScaleProvider;
	}

	public void setDisplayScaleProvider(DisplayScaleProvider displayScaleProvider) {
		this.displayScaleProvider = displayScaleProvider;
	}



	public ScannableMotionUnits getSampleCentringXMotor() {
		return sampleCentringXMotor;
	}

	public void setSampleCentringXMotor(ScannableMotionUnits sampleCentringXMotor) {
		this.sampleCentringXMotor = sampleCentringXMotor;
	}

	public ScannableMotionUnits getSampleCentringYMotor() {
		return sampleCentringYMotor;
	}

	public void setSampleCentringYMotor(ScannableMotionUnits sampleCentringYMotor) {
		this.sampleCentringYMotor = sampleCentringYMotor;
	}

	public ScannableMotionUnits getCameraStageXMotor() {
		return cameraStageXMotor;
	}

	public void setCameraStageXMotor(ScannableMotionUnits cameraStageXMotor) {
		this.cameraStageXMotor = cameraStageXMotor;
	}

	public ScannableMotionUnits getCameraStageYMotor() {
		return cameraStageYMotor;
	}

	public void setCameraStageYMotor(ScannableMotionUnits cameraStageYMotor) {
		this.cameraStageYMotor = cameraStageYMotor;
	}

	public ScannableMotionUnits getSampleBaseXMotor() {
		return sampleBaseXMotor;
	}

	public void setSampleBaseXMotor(ScannableMotionUnits sampleBaseXMotor) {
		this.sampleBaseXMotor = sampleBaseXMotor;
	}

	public ScannableMotionUnits getSampleBaseYMotor() {
		return sampleBaseYMotor;
	}

	public void setSampleBaseYMotor(ScannableMotionUnits sampleBaseYMotor) {
		this.sampleBaseYMotor = sampleBaseYMotor;
	}

	public int getImageWidth() {
		return imageWidth;
	}

	public void setImageWidth(int imageWidth) {
		this.imageWidth = imageWidth;
	}

	public int getImageHeight() {
		return imageHeight;
	}

	public void setImageHeight(int imageHeight) {
		this.imageHeight = imageHeight;
	}

	public Scannable getCameraXYScannable() {
		return cameraXYScannable;
	}

	public void setCameraXYScannable(Scannable cameraXYScannable) {
		this.cameraXYScannable = cameraXYScannable;
	}

	static RealVector createVectorOf(double... data) {
		return MatrixUtils.createRealVector(data);
	}
	@Override
	public void imageFinished(IImagePositionEvent event, ImageViewer viewer) throws DeviceException {
		final int[] clickCoordinates = event.getImagePosition();
		final RealVector actualClickPoint = createVectorOf(clickCoordinates[0], clickCoordinates[1]);		
		ImageData imageData = viewer.getImageData();
		final RealVector imageDataSize = createVectorOf(imageData.width, imageData.height);
		final RealVector imageSize = createVectorOf(imageWidth, imageHeight );
		
		final RealVector clickPointInImage = actualClickPoint.ebeMultiply(imageSize).ebeDivide(imageDataSize);		
		double beamCenterX = ScannableUtils.getCurrentPositionArray(rotationAxisXScannable)[0];
		double beamCenterY = ScannableUtils.getCurrentPositionArray(cameraXYScannable)[1];
		final RealVector beamCenterV = createVectorOf(beamCenterX, beamCenterY);
		final RealVector pixelOffset = beamCenterV.subtract(clickPointInImage);

		
			double moveInX = -pixelOffset.getEntry(0) / displayScaleProvider.getPixelsPerMMInX();
			double moveInY = -pixelOffset.getEntry(1) / displayScaleProvider.getPixelsPerMMInY();

			try {
				sampleCentringXMotor.asynchronousMoveTo(ScannableUtils.getCurrentPositionArray(sampleCentringXMotor)[0]+moveInX);
				sampleCentringYMotor.asynchronousMoveTo(ScannableUtils.getCurrentPositionArray(sampleCentringYMotor)[0]+moveInY);
			} catch (DeviceException e) {
				logger.error("Error moving motor", e);
			}
			

		
	}
	
	public DisplayScaleProvider getCameraScaleProvider() {
		return cameraScaleProvider;
	}

	public void setCameraScaleProvider(DisplayScaleProvider cameraScaleProvider) {
		this.cameraScaleProvider = cameraScaleProvider;
	}
}
