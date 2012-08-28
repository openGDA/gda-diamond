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

import gda.device.detector.areadetector.v17.ADBase;
import gda.device.detector.areadetector.v17.FfmpegStream;
import gda.device.detector.areadetector.v17.NDArray;
import gda.device.detector.areadetector.v17.NDProcess;

import org.springframework.beans.factory.InitializingBean;

public class CameraViewPartConfigImpl implements CameraViewPartConfig, InitializingBean {

	NDArray ndArray;
	NDProcess ndProcess;
	FfmpegStream ffmpegStream;
	String setExposureTimeCmd;
	ADBase adBase;

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

}
