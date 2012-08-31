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
import gda.device.ScannableMotionUnits;
import gda.device.scannable.ScannableUtils;

import org.apache.commons.math.linear.MatrixUtils;
import org.apache.commons.math.linear.RealVector;
import org.eclipse.draw2d.geometry.Point;
import org.eclipse.swt.graphics.ImageData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.rcp.plotting.tools.IImagePositionEvent;
import uk.ac.gda.beamline.i13i.views.cameraview.BeamCenterProvider;
import uk.ac.gda.beamline.i13i.views.cameraview.ImageViewerListener;
import uk.ac.gda.client.viewer.ImageViewer;

public class SampleAligner  implements ImageViewerListener{
	private static final Logger logger = LoggerFactory.getLogger(SampleAligner.class);	
	
	ImageModeManager imageModeManager;
	BeamCenterProvider beamCenterProvider;
	DisplayScaleProvider displayScaleProvider;
	ScannableMotionUnits xMotor;
	ScannableMotionUnits yMotor;
	int imageWidth=2000;
	int imageHeight=1000;
	
	
	public ImageModeManager getImageModeManager() {
		return imageModeManager;
	}

	public void setImageModeManager(ImageModeManager imageModeManager) {
		this.imageModeManager = imageModeManager;
	}	
	
	public BeamCenterProvider getBeamCenterProvider() {
		return beamCenterProvider;
	}

	public void setBeamCenterProvider(BeamCenterProvider beamCenterProvider) {
		this.beamCenterProvider = beamCenterProvider;
	}


	public DisplayScaleProvider getDisplayScaleProvider() {
		return displayScaleProvider;
	}

	public void setDisplayScaleProvider(DisplayScaleProvider displayScaleProvider) {
		this.displayScaleProvider = displayScaleProvider;
	}

	public ScannableMotionUnits getxMotor() {
		return xMotor;
	}

	public void setxMotor(ScannableMotionUnits xMotor) {
		this.xMotor = xMotor;
	}

	public ScannableMotionUnits getyMotor() {
		return yMotor;
	}

	public void setyMotor(ScannableMotionUnits yMotor) {
		this.yMotor = yMotor;
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

	static RealVector createVectorOf(double... data) {
		return MatrixUtils.createRealVector(data);
	}
	@Override
	public void imageFinished(IImagePositionEvent event, ImageViewer viewer) {
		if(imageModeManager.getMode().getName().equals("SampleCentring")){
			
			final int[] clickCoordinates = event.getImagePosition();
			final RealVector actualClickPoint = createVectorOf(clickCoordinates[0], clickCoordinates[1]);		
			ImageData imageData = viewer.getImageData();
			final RealVector imageDataSize = createVectorOf(imageData.width, imageData.height);
			final RealVector imageSize = createVectorOf(imageWidth, imageHeight );
			
			final RealVector clickPointInImage = actualClickPoint.ebeMultiply(imageSize).ebeDivide(imageDataSize);		

			Point beamCenter = beamCenterProvider.getBeamCenter();
			final RealVector beamCenterV = createVectorOf(beamCenter.x, beamCenter.y);
			final RealVector pixelOffset = beamCenterV.subtract(clickPointInImage);

			
			double moveInX = pixelOffset.getEntry(0) / displayScaleProvider.getPixelsPerMMInX();
			double moveInY = -pixelOffset.getEntry(1) / displayScaleProvider.getPixelsPerMMInY();
			try {
				xMotor.asynchronousMoveTo(ScannableUtils.getCurrentPositionArray(xMotor)[0]+moveInX);
				yMotor.asynchronousMoveTo(ScannableUtils.getCurrentPositionArray(yMotor)[0]+moveInY);
			} catch (DeviceException e) {
				logger.error("Error moving motor", e);
			}
			
		}

		
	}
	

}
