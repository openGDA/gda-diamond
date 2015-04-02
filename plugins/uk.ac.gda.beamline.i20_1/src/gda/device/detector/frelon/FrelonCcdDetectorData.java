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
import gda.device.detector.EdeDetectorBase;
import gda.device.frelon.Frelon;
import gda.device.frelon.Frelon.ImageMode;
import gda.device.frelon.Frelon.InputChannels;
import gda.device.frelon.Frelon.ROIMode;
import gda.device.frelon.Frelon.SPB2Config;
import gda.device.lima.LimaCCD;
import gda.device.lima.LimaCCD.AccTimeMode;
import gda.device.lima.LimaCCD.AcqMode;
import gda.device.lima.LimaCCD.AcqTriggerMode;
import gda.device.lima.LimaROIInt;

import org.apache.commons.configuration.PropertiesConfiguration;

import com.google.gson.Gson;
/**
 * object to hold detector's configuration data.
 * Only the writable attributes in {@link LimaCCD} and {@link Frelon} need to be cached here.
 *
 * These attribute settings in this object will be persisted by {@link EdeDetectorBase}
 * using {@link Gson} and {@link PropertiesConfiguration} from client to the server.
 */
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
	private AcqMode acqMode=AcqMode.SINGLE;
	private int numberOfImages=1;
	private AcqTriggerMode triggerMode=AcqTriggerMode.EXTERNAL_GATE;
	private double latencyTime=0.0;
	private double exposureTime=1.0;
	private double accumulationMaximumExposureTime=1.0;
	private final AccTimeMode accumulationTimeMode=AccTimeMode.LIVE;
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
	public AcqMode getAcqMode() {
		return acqMode;
	}
	public void setAcqMode(AcqMode acqMode) {
		this.acqMode = acqMode;
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

	public double getLatencyTime() {
		return latencyTime;
	}
	public void setLatencyTime(double latencyTime) {
		this.latencyTime = latencyTime;
	}

	public double getExposureTime() {
		return exposureTime;
	}
	public void setExposureTime(double exposureTime) {
		this.exposureTime = exposureTime;
	}

	public double getAccumulationMaximumExposureTime() {
		return accumulationMaximumExposureTime;
	}
	public void setAccumulationMaximumExposureTime(double accumulationMaximumExposureTime) {
		this.accumulationMaximumExposureTime = accumulationMaximumExposureTime;
	}

	public AccTimeMode getAccumulationTimeMode() {
		return accumulationTimeMode;
	}
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
	/**
	 * return area of interest from java object.
	 * These data will be used to set to camera's image_roi attribute.
	 * @return ROI
	 */
	public LimaROIInt getAreaOfInterest() {
		return areaOfInterest;
	}
	/**
	 * sets area of interest to be use.
	 * These data will be send to camera's image_roi attribute before acquisition
	 * @param areaOfInterest
	 */
	public void setAreaOfInterest(LimaROIInt areaOfInterest) {
		// set the limits for ROI in energy direction
		setLowerChannel(areaOfInterest.getBeginX());
		setUpperChannel(areaOfInterest.getEndX());
		this.areaOfInterest = areaOfInterest;
	}
}
