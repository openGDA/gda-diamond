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

package uk.ac.gda.beamline.i13i.views.adScaleAdjustmentView;

import gda.device.detector.areadetector.v17.NDArray;
import gda.device.detector.areadetector.v17.NDPluginBase;
import gda.device.detector.areadetector.v17.NDProcess;
import gda.device.detector.areadetector.v17.NDStats;

public class ADControllerImpl implements ADController {
	public NDStats imageNDStats;
	public NDProcess liveViewNDProc;
	private NDArray imageNDArray;
	private int imageHistSize;
	private int imageMin;
	private int imageMax;
	private String detectorName;

	@Override
	public NDStats getImageNDStats() {
		return imageNDStats;
	}

	@Override
	public NDProcess getLiveViewNDProc() {
		return liveViewNDProc;
	}

	public void setLiveViewNDProc(NDProcess ndProc) {
		this.liveViewNDProc = ndProc;
	}

	@Override
	public int getImageHistSize() {
		return imageHistSize;
	}

	@Override
	public int getImageMin() {
		return imageMin;
	}

	@Override
	public int getImageMax() {
		return imageMax;
	}

	@Override
	public String getDetectorName() {
		return detectorName;
	}

	public void setImageNDStats(NDStats ndStats) {
		this.imageNDStats = ndStats;
	}

	public void setImageHistSize(int imageHistSize) {
		this.imageHistSize = imageHistSize;
	}

	public void setImageMin(int imageMin) {
		this.imageMin = imageMin;
	}

	public void setImageMax(int imageMax) {
		this.imageMax = imageMax;
	}

	public void setDetectorName(String detectorName) {
		this.detectorName = detectorName;
	}

	public void setImageNDArray(NDArray imageNDArray) {
		this.imageNDArray = imageNDArray;
	}

	private int[] determineDataDimensions() throws Exception {
		// only called if configured to readArrays (and hence ndArray is set)
		NDPluginBase pluginBase = imageNDArray.getPluginBase();
		int nDimensions = pluginBase.getNDimensions_RBV();
		int[] dimFromEpics = new int[3];
		dimFromEpics[0] = pluginBase.getArraySize2_RBV();
		dimFromEpics[1] = pluginBase.getArraySize1_RBV();
		dimFromEpics[2] = pluginBase.getArraySize0_RBV();

		int[] dims = java.util.Arrays.copyOfRange(dimFromEpics, 3 - nDimensions, 3);
		return dims;
	}

	@Override
	public ImageData getImageData() throws Exception {

		int[] dims = determineDataDimensions();

		int expectedNumPixels = dims[0];
		for (int i = 1; i < dims.length; i++) {
			expectedNumPixels = expectedNumPixels * dims[i];
		}
		Object imageData = imageNDArray.getImageData(expectedNumPixels);
		ImageData data = new ImageData();
		data.dimensions = dims;
		data.data = imageData;
		return data;
	}

	@Override
	public NDArray getImageNDArray() {
		return imageNDArray;
	}

}
