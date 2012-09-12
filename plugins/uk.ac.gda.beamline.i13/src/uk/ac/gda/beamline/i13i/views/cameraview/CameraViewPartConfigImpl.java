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

package uk.ac.gda.beamline.i13i.views.cameraview;

import gda.device.Scannable;
import gda.device.detector.areadetector.v17.ADBase;
import gda.device.detector.areadetector.v17.FfmpegStream;
import gda.device.detector.areadetector.v17.NDArray;
import gda.device.detector.areadetector.v17.NDProcess;

import org.springframework.beans.factory.InitializingBean;

import uk.ac.gda.beamline.i13i.DisplayScaleProvider;

public class CameraViewPartConfigImpl implements CameraViewPartConfig, InitializingBean {

	NDArray ndArray;
	NDProcess ndProcess;
	FfmpegStream ffmpegStream;
	String setExposureTimeCmd;
	ADBase adBase;
	private BeamCenterProvider beamCenterProvider;
	private ImageViewerListener imageViewerListener;
	
	int fFMpegImgWidthRequired=0;
	int fFMpegImgHeightRequired=0;
	private Scannable rotationAxisXScannable;
	private DisplayScaleProvider displayScaleProvider;
	private Scannable cameraXYScannable;
	private ImageViewerListener imageViewerListener2;

	@Override
	public void afterPropertiesSet() throws Exception {
		if (ndArray == null)
			throw new IllegalArgumentException("ndArray not defined");
		if (ndProcess == null)
			throw new IllegalArgumentException("ndProcess not defined");
		if (ffmpegStream == null)
			throw new IllegalArgumentException("ffmpegStream not defined");
		if (setExposureTimeCmd == null)
			throw new IllegalArgumentException("setExposureTimeCmd not defined");
		if (adBase == null)
			throw new IllegalArgumentException("adBase not defined");
		if (fFMpegImgWidthRequired < 1)
			throw new IllegalArgumentException("fFMpegImgWidthRequired < 1");
		if (fFMpegImgHeightRequired < 1)
			throw new IllegalArgumentException("fFMpegImgHeightRequired < 1");
		if (rotationAxisXScannable == null)
			throw new IllegalArgumentException("rotationAxisXScannable not defined");
		if (displayScaleProvider == null)
			throw new IllegalArgumentException("displayScaleProvider not defined");
		if (imageViewerListener == null)
			throw new IllegalArgumentException("imageViewerListener not defined");

	}

	@Override
	public NDArray getNdArray() {
		return ndArray;
	}

	public void setNdArray(NDArray ndArray) {
		this.ndArray = ndArray;
	}

	@Override
	public NDProcess getNdProcess() {
		return ndProcess;
	}

	public void setNdProcess(NDProcess ndProcess) {
		this.ndProcess = ndProcess;
	}

	@Override
	public FfmpegStream getFfmpegStream() {
		return ffmpegStream;
	}

	public void setFfmpegStream(FfmpegStream ffmpegStream) {
		this.ffmpegStream = ffmpegStream;
	}

	@Override
	public String getSetExposureTimeCmd() {
		return setExposureTimeCmd;
	}

	public void setSetExposureTimeCmd(String setExposureTimeCmd) {
		this.setExposureTimeCmd = setExposureTimeCmd;
	}

	@Override
	public ADBase getAdBase() {
		return adBase;
	}

	public void setAdBase(ADBase adBase) {
		this.adBase = adBase;
	}

	@Override
	public BeamCenterProvider getBeamCenterProvider() {
		return beamCenterProvider;
	}	
	public void setBeamCenterProvider(BeamCenterProvider beamCenterProvider) {
		this.beamCenterProvider = beamCenterProvider;
	}


	@Override
	public ImageViewerListener getImageViewerListener() {
		return imageViewerListener;
	}

	public void setImageViewerListener(ImageViewerListener imageViewerListener) {
		this.imageViewerListener = imageViewerListener;
	}

	@Override
	public int getfFMpegImgWidthRequired() {
		return fFMpegImgWidthRequired;
	}

	public void setfFMpegImgWidthRequired(int fFMpegImgWidthRequired) {
		this.fFMpegImgWidthRequired = fFMpegImgWidthRequired;
	}

	@Override
	public int getfFMpegImgHeightRequired() {
		return fFMpegImgHeightRequired;
	}

	public void setfFMpegImgHeightRequired(int fFMpegImgHeightRequired) {
		this.fFMpegImgHeightRequired = fFMpegImgHeightRequired;
	}


	@Override
	public Scannable getRotationAxisXScannable() {
		return rotationAxisXScannable;
	}

	public void setRotationAxisXScannable(Scannable rotationAxisXScannable) {
		this.rotationAxisXScannable = rotationAxisXScannable;
	}

	@Override
	public DisplayScaleProvider getDisplayScaleProvider() {
		return displayScaleProvider;
	}

	public void setDisplayScaleProvider(DisplayScaleProvider displayScaleProvider) {
		this.displayScaleProvider = displayScaleProvider;
	}

	@Override
	public Scannable getCameraXYScannable() {
		return cameraXYScannable;
	}

	public void setCameraXYScannable(Scannable cameraXYScannable) {
		this.cameraXYScannable = cameraXYScannable;
	}

	@Override
	public ImageViewerListener getImageViewerListener2() {
		return imageViewerListener2;
	}

	public void setImageViewerListener2(ImageViewerListener imageViewerListener2) {
		this.imageViewerListener2 = imageViewerListener2;
	}

	
}
