/*-
 * Copyright © 2015 Diamond Light Source Ltd.
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

package gda.device.detector.frelon;

import gda.device.detector.DetectorData;
import gda.device.frelon.Frelon.ROIMode;
import gda.device.frelon.Frelon.SPB2Config;
import gda.device.lima.LimaROIInt;

public class FrelonCcdDetectorData extends DetectorData {
	public static final int MAX_PIXEL = 2048;

	private ROIMode roiMode=ROIMode.KINETIC;
	private int hotizontalBinValue=1;
	private int verticalBinValue = 1; // vert.binning i.e. image_bin Y component
	private int yStartPixel = 0; //CCD line begin in Frelon GUI, or roi_bin_offset in line, must be multiple of vertivalBinValue
	private int yLength = 2048;
	private SPB2Config spb2Config; //hardware pixel rate configuration: Speed or Precision
	private LimaROIInt areaOfInterest;

	public ROIMode getRoiMode() {
		return roiMode;
	}
	public void setRoiMode(ROIMode roiMode) {
		this.roiMode = roiMode;
	}
	public int getHotizontalBinValue() {
		return hotizontalBinValue;
	}
	public void setHotizontalBinValue(int hotizontalBinValue) {
		this.hotizontalBinValue = hotizontalBinValue;
	}
	public int getVerticalBinValue() {
		return verticalBinValue;
	}
	public void setVerticalBinValue(int binValue) {
		verticalBinValue = binValue;
	}
	public int getyStartPaxel() {
		return yStartPixel;
	}
	public void setyStartPaxel(int yStartPaxel) {
		yStartPixel = yStartPaxel;
	}
	public int getyLength() {
		return yLength;
	}
	public void setyLength(int yLength) {
		this.yLength = yLength;
	}
	public SPB2Config getSpb2Config() {
		return spb2Config;
	}
	public void setSpb2Config(SPB2Config spb2Config) {
		this.spb2Config = spb2Config;
	}
	public LimaROIInt getAreaOfInterest() {
		return areaOfInterest;
	}
	public void setAreaOfInterest(LimaROIInt areaOfInterest) {
		// set the limits for ROI in energy direction
		setLowerChannel(areaOfInterest.getBeginX());
		setUpperChannel(areaOfInterest.getEndX());
		this.areaOfInterest = areaOfInterest;
	}

}
