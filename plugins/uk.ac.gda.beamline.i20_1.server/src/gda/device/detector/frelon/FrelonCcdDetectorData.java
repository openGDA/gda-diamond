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

import java.util.Arrays;
import java.util.List;

import org.apache.commons.configuration.PropertiesConfiguration;

import com.google.gson.Gson;

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
import gda.device.lima.impl.LimaROIIntImpl;
/**
 * object to hold detector's configuration data.
 * Only the writable attributes in {@link LimaCCD} and {@link Frelon} need to be cached here.
 *
 * These attribute settings in this object will be persisted by {@link EdeDetectorBase}
 * using {@link Gson} and {@link PropertiesConfiguration} from client to the server.
 */
public class FrelonCcdDetectorData extends DetectorData {

	private static final long serialVersionUID = 1L;

	public static final int MAX_PIXEL = 2048;
	public static final int VERTICAL_BIN_SIZE_LIMIT = 1024;
	public static final int HORIZONRAL_BIN_SIZE_LIMIT = 8;
	//Frelon parameters
	private ImageMode imageMode=ImageMode.FULL_FRAME;
	private InputChannels inputChannel=InputChannels.I3_4;
	private boolean ev2CorrectionActive=false;
	private ROIMode roiMode=ROIMode.KINETIC;
	private int ccdBeginLine= 1984; //CCD line begin in Frelon GUI, or roi_bin_offset in line
	private SPB2Config spb2Config=SPB2Config.SPEED; //hardware pixel rate configuration: Speed or Precision
	// Lima parameters
	private int horizontalBinValue=1; // 1, 2, 4, 8.
	private int verticalBinValue = 1; // vert.binning i.e. image_bin Y component
	private AcqMode acqMode=AcqMode.SINGLE;
	private int numberOfImages=2; // minimum 2 spectra as the 1st one usually crap need to be dropped in the future.
	private AcqTriggerMode triggerMode=AcqTriggerMode.INTERNAL_TRIGGER;
	private double latencyTime=0.0;
	private double exposureTime=1.0;
	private double accumulationMaximumExposureTime=0.1;
	private AccTimeMode accumulationTimeMode=AccTimeMode.LIVE;
	// a hack below to using concrete class not interface LimaROTInt as Gson does not support interface without extra work on InstanceCreator.
	//TODO register an InstanceCreator in Gson gson = new GsonBuilder().registerTypeAdapter(Animal.class, new InterfaceAdapter<Animal>()).create();
	private LimaROIIntImpl areaOfInterest=new LimaROIIntImpl(0, 0, 2048, 2048); // in units of binning sizes in x and y directions

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
	public void setAccumulationTimeMode(AccTimeMode accumulationTimeMode) {
		this.accumulationTimeMode = accumulationTimeMode;
	}
	public int getHorizontalBinValue() {
		return horizontalBinValue;
	}

	public void setHorizontalBinValue(int binValue) {
		if (horizontalBinValue>HORIZONRAL_BIN_SIZE_LIMIT) {
			throw new IllegalArgumentException("The limit of horizontal binning size is "+HORIZONRAL_BIN_SIZE_LIMIT+" pixels.");
		}
		List<Integer> allowedValues= Arrays.asList(1,2,4,8);
		if (allowedValues.contains(horizontalBinValue)) {
			horizontalBinValue = binValue;
		} else {
			throw new IllegalArgumentException("The horizontal binning can only be one of "+allowedValues.toArray(new Integer[] {})+" pixels.");
		}
		int xLength=MAX_PIXEL/horizontalBinValue;
		areaOfInterest.setBeginX(0);
		areaOfInterest.setLengthX(xLength);
	}
	public int getVerticalBinValue() {
		return verticalBinValue;
	}

	public void setVerticalBinValue(int binValue) {
		if (binValue>VERTICAL_BIN_SIZE_LIMIT) {
			throw new IllegalArgumentException("The limit of vertical binning size is "+VERTICAL_BIN_SIZE_LIMIT+" lines.");
		}
		List<Integer> allowedValues= Arrays.asList(1,2,4,8,16,32,64,128,256,512,1024);
		if (allowedValues.contains(binValue)) {
			verticalBinValue = binValue;
		} else {
			throw new IllegalArgumentException("The vertical binning can only be one of "+allowedValues.toArray(new Integer[] {})+" pixels.");
		}
		int yLength=MAX_PIXEL/verticalBinValue;
		areaOfInterest.setBeginY(0);
		areaOfInterest.setLengthY(yLength);
	}
	/**
	 * return area of interest from java object.
	 * These data will be used to set to camera's image_roi attribute.
	 * @return ROI
	 */
	public LimaROIIntImpl getAreaOfInterest() {
		return areaOfInterest;
	}
	/**
	 * sets area of interest to be use.
	 * These data will be send to camera's image_roi attribute before acquisition
	 * @param areaOfInterest
	 */
	public void setAreaOfInterest(LimaROIIntImpl areaOfInterest) {
		this.areaOfInterest = areaOfInterest;
	}
	public int getCcdBeginLine() {
		return ccdBeginLine;
	}
	public void setCcdBeginLine(int ccdBeginLine) {
		this.ccdBeginLine = ccdBeginLine;
	}
}
