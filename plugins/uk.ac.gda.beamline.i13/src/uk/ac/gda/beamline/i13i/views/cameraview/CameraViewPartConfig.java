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

import uk.ac.gda.beamline.i13i.DisplayScaleProvider;
import gda.device.Scannable;
import gda.device.detector.areadetector.v17.ADBase;
import gda.device.detector.areadetector.v17.FfmpegStream;
import gda.device.detector.areadetector.v17.NDArray;
import gda.device.detector.areadetector.v17.NDProcess;


public interface CameraViewPartConfig {
	ADBase getAdBase();
	NDArray getNdArray();
	NDProcess getNdProcess();
	FfmpegStream getFfmpegStream();
	String getSetExposureTimeCmd();
	String getAutoCentreCmd();
	BeamCenterProvider getBeamCenterProvider();
	ImageViewerListener getImageViewerListener();
	int getfFMpegImgWidthRequired();
	int getfFMpegImgHeightRequired();
	Scannable getRotationAxisXScannable();
	DisplayScaleProvider getDisplayScaleProvider();
	Scannable getCameraXYScannable();
	String getShowNormalisedImageCmd();
	String getHistogramPlotId();
}
