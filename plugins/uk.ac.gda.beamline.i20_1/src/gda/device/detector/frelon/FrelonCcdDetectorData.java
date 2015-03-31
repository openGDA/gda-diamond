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
import gda.device.frelon.Frelon.ImageMode;
import gda.device.frelon.Frelon.InputChannels;
import gda.device.frelon.Frelon.ROIMode;
import gda.device.frelon.Frelon.SPB2Config;
import gda.device.lima.LimaCCD.AcqTriggerMode;
import gda.device.lima.LimaROIInt;

public class FrelonCcdDetectorData extends DetectorData {
	public static final int MAX_PIXEL = 2048;
	private static final int VERTICAL_BIN_SIZE_LIMIT = 2048;
	private static final int HORIZONRAL_BIN_SIZE_LIMIT = 8;
	//Frelon parameters
	private ImageMode imageMode=ImageMode.FRAME_TRANSFERT;
	private InputChannels inputChannel=InputChannels.I1_2_3_4;
	private boolean ev2CorrectionActive=false;
	private ROIMode roiMode=ROIMode.KINETIC;
	private int yStartPixel = 0; //CCD line begin in Frelon GUI, or roi_bin_offset in line
	private SPB2Config spb2Config=SPB2Config.PRECISION; //hardware pixel rate configuration: Speed or Precision
	// Lima parameters
	private int hotizontalBinValue=1; // 1, 2, 4, 8.
	private int verticalBinValue = 1; // vert.binning i.e. image_bin Y component
	private double exposureTime=1.0;
	private int numberOfImages=1;
	private AcqTriggerMode triggerMode=AcqTriggerMode.EXTERNAL_GATE;
	private LimaROIInt areaOfInterest; // in units of binning sizes in x and y directions

	//Frelon attriutes
	public ImageMode getImageMode() {
		return imageMode;
	}
	public void setImageMode(ImageMode imageMode) {
		this.imageMode = imageMode;
	}

	public InputChannels getInputChannel() {
		return inputChannel;
	}
	public void setInputChannel(InputChannels inputChannel) {
		this.inputChannel = inputChannel;
	}
	public boolean isEv2CorrectionActive() {
		return ev2CorrectionActive;
	}
	public void setEv2CorrectionActive(boolean ev2CorrectionActive) {
		this.ev2CorrectionActive = ev2CorrectionActive;
	}
	public ROIMode getRoiMode() {
		return roiMode;
	}
	public void setRoiMode(ROIMode roiMode) {
		this.roiMode = roiMode;
	}
	public int getRoiBinOffset() {
		return yStartPixel;
	}
	public void setRoiBinOffset(int yStartPixel) {
		this.yStartPixel = yStartPixel;
	}
	public SPB2Config getSpb2Config() {
		return spb2Config;
	}
	public void setSpb2Config(SPB2Config spb2Config) {
		this.spb2Config = spb2Config;
	}
	//LIMA attributes
	public int getHotizontalBinValue() {
		return hotizontalBinValue;
	}
	public void setHotizontalBinValue(int hotizontalBinValue) {
		if (hotizontalBinValue>HORIZONRAL_BIN_SIZE_LIMIT) {
			throw new IllegalArgumentException("The limit of horizontal binning size is "+HORIZONRAL_BIN_SIZE_LIMIT+" pixels.");
		}
		this.hotizontalBinValue = hotizontalBinValue;
	}
	public int getVerticalBinValue() {
		return verticalBinValue;
	}
	public void setVerticalBinValue(int binValue) {
		if (binValue>VERTICAL_BIN_SIZE_LIMIT) {
			throw new IllegalArgumentException("The limit of vertical binning size is "+VERTICAL_BIN_SIZE_LIMIT+" lines.");
		}
		verticalBinValue = binValue;
	}

	public double getExposureTime() {
		return exposureTime;
	}
	public void setExposureTime(double exposureTime) {
		this.exposureTime = exposureTime;
	}
	public int getNumberOfImages() {
		return numberOfImages;
	}
	public void setNumberOfImages(int numberOfImages) {
		this.numberOfImages = numberOfImages;
	}
	public AcqTriggerMode getTriggerMode() {
		return triggerMode;
	}
	public void setTriggerMode(AcqTriggerMode triggerMode) {
		this.triggerMode = triggerMode;
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
