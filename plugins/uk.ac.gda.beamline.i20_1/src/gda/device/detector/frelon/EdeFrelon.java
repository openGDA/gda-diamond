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

import fr.esrf.Tango.DevFailed;
import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.detector.DetectorStatus;
import gda.device.detector.EdeDetectorBase;
import gda.device.frelon.Frelon;
import gda.device.lima.LimaBin;
import gda.device.lima.LimaCCD;
import gda.device.lima.LimaCCD.AcqMode;
import gda.device.lima.LimaCCD.AcqStatus;
import gda.device.lima.LimaCCD.AcqTriggerMode;
import gda.device.lima.LimaCCD.ImageType;
import gda.device.lima.impl.LimaROIIntImpl;
import gda.factory.FactoryException;

import java.util.HashMap;

import org.apache.commons.lang.ArrayUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.ui.data.TimingGroup;

public class EdeFrelon extends EdeDetectorBase {

	private static final Logger logger = LoggerFactory.getLogger(EdeFrelon.class);
	//	private static final double PIXEL_RATE=10.0; // MPixel/s per channel
	//	private static final double PIXEL_SIZE=14; // micro-meter
	//	private static final double LINE_TRANSFER_TIME_EXAFS=0.000004; // second 4us
	//	private static final double LINE_TRANSFER_TIEM_IMAGING=0.000008; //second 8us
	//	private static final int RESOLUTION=16; // bit
	//	private static final double READOUT_SPEED=40.0; // MPixel/s
	//	private static final double FULL_FRAME_RATE_WITHOUT_BINNING_IMAGING=8.35; //Frames/s
	//	private static final double FULL_FRAME_RATE_WITHOUT_BINNING_EXAFS=16.7; //Frames/s
	//	private static final double FRAME_TRANSFER_RATE_WITHOU_BINNIN_IMAGING=15.7; //Frames/s, exposure<59ms
	//	private static final double FRAME_TRANSFER_RATE_WITHOU_BINNIN_EXAFS=27.6; //Frames/s, exposure<58ms

	private LimaCCD limaCcd;
	private Frelon frelon;

	private long imageWidth;
	private long imageHeight;
	private ImageType imageType;

	public EdeFrelon() {
		inputNames = new String[] {};
	}

	public EdeFrelon(Frelon frelon, LimaCCD limaCcd) {
		inputNames = new String[] {};
		this.setFrelon(frelon);
		this.setLimaCcd(limaCcd);
	}

	@Override
	public void configure() throws FactoryException {
		if (!isConfigured()) {
			super.configure();
			try {
				updateImageProperties();
			} catch (DeviceException e) {
				logger.error("Failed to get Image properties from the detector "+getName(), e);
				throw new FactoryException(e.getMessage(), e);
			}
			setConfigured(true);
		}
	}

	@Override
	public void synchronizWithDetectorData() {
		setDetectorData(getDetectorData());
		LimaBin imageBin;
		try {
			imageBin = limaCcd.getImageBin();
			((FrelonCcdDetectorData)getDetectorData()).setHotizontalBinValue((int) imageBin.getBinX());
			((FrelonCcdDetectorData)getDetectorData()).setVerticalBinValue((int) imageBin.getBinY());
		} catch (DevFailed e) {
			logger.error("Fail to get Lima ccd image_bin.", e);
		}
		try {
			((FrelonCcdDetectorData)getDetectorData()).setAccumulationMaximumExposureTime(limaCcd.getAccMaxExpoTime());
		} catch (DevFailed e) {
			logger.error("Fail to get lima ccd acc_max_expotime", e);
		}
		try {
			((FrelonCcdDetectorData)getDetectorData()).setAccumulationTimeMode(limaCcd.getAccTimeMode());
		} catch (DevFailed e) {
			logger.error("Fail to get lima ccd acc_time_mode", e);
		}
		try {
			((FrelonCcdDetectorData)getDetectorData()).setAcqMode(limaCcd.getAcqMode());
		} catch (DevFailed e) {
			logger.error("Fail to get lima ccd acq_mode", e);
		}
		try {
			LimaROIIntImpl imageROIInt = (LimaROIIntImpl) limaCcd.getImageROIInt();
			((FrelonCcdDetectorData)getDetectorData()).setAreaOfInterest(imageROIInt);
			setLowerChannel(imageROIInt.getBeginX());
			setUpperChannel(imageROIInt.getLengthX()+imageROIInt.getBeginX());
			setNumberRois(getRois().length);
		} catch (DevFailed e) {
			logger.error("Fail to get lima ccd image_roi", e);
		}
		try {
			((FrelonCcdDetectorData)getDetectorData()).setEv2CorrectionActive(frelon.isE2VCorrectionActive());
		} catch (DevFailed e) {
			logger.error("Fail to get frelon e2v_correction", e);
		}
		try {
			((FrelonCcdDetectorData)getDetectorData()).setExposureTime(limaCcd.getAcqExpoTime());
		} catch (DevFailed e) {
			logger.error("Fail to get lima ccd acq_expo_time", e);
		}
		try {
			((FrelonCcdDetectorData)getDetectorData()).setImageMode(frelon.getImageMode());
		} catch (DevFailed e) {
			logger.error("Fail to get frelon image_mode", e);
		}
		try {
			((FrelonCcdDetectorData)getDetectorData()).setInputChannel(frelon.getInputChannels());
		} catch (DevFailed e) {
			logger.error("Fail to get frelon input_channel", e);
		}
		try {
			((FrelonCcdDetectorData)getDetectorData()).setLatencyTime(limaCcd.getLatencyTime());
		} catch (DevFailed e) {
			logger.error("Fail to get lima ccd latency_time", e);
		}
		try {
			((FrelonCcdDetectorData)getDetectorData()).setNumberOfImages(limaCcd.getAcqNbFrames());
		} catch (DevFailed e) {
			logger.error("Fail to get lima ccd acq_nb_frames", e);
		}
		try {
			((FrelonCcdDetectorData)getDetectorData()).setRoiBinOffset((int) frelon.getROIBinOffset());
		} catch (DevFailed e) {
			logger.error("Fail to get frelon roi_bin_offset", e);
		}
		try {
			((FrelonCcdDetectorData)getDetectorData()).setRoiMode(frelon.getROIMode());
		} catch (DevFailed e) {
			logger.error("Fail to get frelon roi_mode", e);
		}
		try {
			((FrelonCcdDetectorData)getDetectorData()).setSpb2Config(frelon.getSPB2Config());
		} catch (DevFailed e) {
			logger.error("Fail to get frelon spb2_config", e);
		}
		try {
			((FrelonCcdDetectorData)getDetectorData()).setTriggerMode(limaCcd.getAcqTriggerMode());
		} catch (DevFailed e) {
			logger.error("Fail to get lima ccd acq_trigger_mode", e);
		}
	}

	@Override
	public synchronized int[] readoutFrames(int startFrame, int finalFrame) throws DeviceException {
		byte[] byteData = null;
		int[] intData = null;
		updateImageProperties();
		try {
			int n = 0;
			//			int lastImageNumber = -1;
			//			if ((lastImageNumber = getLimaCcd().getLastImageReady()) != finalFrame - startFrame+1) {
			//				logger.error("EdeFrelon.readoutFrames: image not ready {} should be {}", lastImageNumber, finalFrame - startFrame+1);
			//				throw new DeviceException("EdeFrelon.readoutFrames: image not ready");
			//			}

			intData = new int[(int) (imageWidth * imageHeight * (finalFrame - startFrame + 1))];
			//			byteData= getLimaCcd().getImage(0); //read and dump the 1st frame which frequently crap
			for (int i = startFrame; i <= finalFrame; i++) {
				byteData = getLimaCcd().getImage(i);
				if (imageType == ImageType.BPP32S) {
					if (byteData.length != imageWidth * imageHeight * 4) {
						logger.error("EdeFrelon.readoutFrames: failed: expected {} bytes, got {}", imageWidth
								* imageHeight * 4, byteData.length);
						throw new DeviceException("EdeFrelon.readoutFrames: failed to read all the image data");
					}
					for (int j = 0; j < byteData.length; j += 4, n++) {
						intData[n] = ((byteData[j + 3] & 0xff) << 24) | ((byteData[j + 2] & 0xff) << 16)
								| ((byteData[j + 1] & 0xff) << 8) | (byteData[j] & 0xff);
					}
				} else if (imageType == ImageType.BPP16) {
					if (byteData.length != imageWidth * imageHeight * 2) {
						logger.warn("byteData length = {}, image width = {}, image height = {}", byteData.length,imageWidth,imageHeight);
						logger.error("EdeFrelon.readoutFrames: failed: expected {} bytes, got {}", imageWidth
								* imageHeight * 2, byteData.length);
						throw new DeviceException("EdeFrelon.readoutFrames: failed to read all the image data");
					}
					for (int j = 0; j < byteData.length; j += 2, n++) {
						intData[n] = ((byteData[j + 1] & 0xff) << 8) | (byteData[j] & 0xff);
					}
				} else {
					logger.error("EdeFrelon.readoutFrames: Unsupported image type {}", imageType);
					throw new DeviceException("EdeFrelon.readoutFrames: Unsupported image type");
				}

			}
		} catch (DevFailed e) {
			logger.error("EdeFrelon.readoutFrames: failed {}", e.errors[0].desc);
			throw new DeviceException("EdeFrelon.readoutFrames: failed " + e.errors[0].desc);
		}

		int[] single = new int[FrelonCcdDetectorData.MAX_PIXEL];
		for (int i = 0; i < (finalFrame - startFrame + 1); i++) {
			System.arraycopy(intData, FrelonCcdDetectorData.MAX_PIXEL*i, single, 0, FrelonCcdDetectorData.MAX_PIXEL);
			ArrayUtils.reverse(single);
			System.arraycopy(single, 0, intData, FrelonCcdDetectorData.MAX_PIXEL*i, FrelonCcdDetectorData.MAX_PIXEL);
		}

		return intData;
	}

	@Override
	public void setCollectionTime(double collectionTime) throws DeviceException {
		try {
			if (getLimaCcd().getAcqTriggerMode() == AcqTriggerMode.EXTERNAL_GATE) {
				// collection time or exposure time is controlled by gate width of the signal.
				return;
			}
		} catch (DevFailed e1) {
			logger.error("Failed to get acquire trigger mode from detector.", e1);
			throw new DeviceException(getName(), "Failed to get acquire trigger mode from detector.", e1);
		}
		super.setCollectionTime(collectionTime);
		if (collectionTime!=0.0) {
			((FrelonCcdDetectorData)getDetectorData()).setExposureTime(collectionTime);
		}
		try {
			getLimaCcd().setAcqExpoTime(((FrelonCcdDetectorData)getDetectorData()).getExposureTime());
		} catch (DevFailed e) {
			logger.error("failed to set exposure time for " + getName(), e);
			throw new DeviceException("failed to set exposure time for " + getName(), e);
		}
	}
	@Override
	public double getCollectionTime() throws DeviceException {
		try {
			logger.info("Exposure time on detector {} is {}, GDA demand time is {}.", getName(), limaCcd.getAcqExpoTime(), collectionTime);
		} catch (DevFailed e) {
			logger.error("Failed to get acq_expo_time from detector.", e);
			throw new DeviceException(getName(), "Failed to get acq_expo_time from detector.", e);
		}
		return super.getCollectionTime();
	}

	@Override
	public void collectData() throws DeviceException {
		try {
			getLimaCcd().setAcqNbFrames(((FrelonCcdDetectorData) getDetectorData()).getNumberOfImages());
		} catch (DevFailed e) {
			logger.error("failed to set acq_nb_frames for " + getName(), e);
			throw new DeviceException("failed to set acq_nb_frames for " + getName(), e);
		}
		start();
	}

	private void start() throws DeviceException {
		// call prepare and start from Frelon
		try {
			// prepare the camera for a new acquisition, have to be called each time a parameter is set.
			getLimaCcd().prepareAcq();
		} catch (DevFailed e) {
			logger.error("Call to limaCcd.prepareAcq() failed", e);
			throw new DeviceException(getName(), "Call to limaCcd.prepareAcq() failed.", e);
		}
		try {
			getLimaCcd().startAcq();
		} catch (DevFailed e) {
			logger.error("Call to llimaCcd.startAcq() failed", e);
			throw new DeviceException(getName(), "Call to limaCcd.startAcq() failed.", e);
		}
	}
	@Override
	public void stop() throws DeviceException {
		try {
			getLimaCcd().stopAcq();
		} catch (DevFailed e) {
			logger.error("Call to llimaCcd.stopAcq() failed", e);
			throw new DeviceException(getName(), "Call to limaCcd.stopAcq() failed.", e);
		}
		super.stop();
	}
	/**
	 * retrieve calculated accumulation number of frames per image from the detector.
	 * the third parameter is not used here. It is just API signature used by XH detector.
	 */
	@Override
	public int getNumberScansInFrame(double expoTime, double accTime, int numberOfImages) throws DeviceException {
		// TODO Query the detector to find out how many accumulations that can fit
		int accNbFrames=-1;
		try {
			getLimaCcd().setAcqExpoTime(expoTime);
		} catch (DevFailed e) {
			logger.error("failed to set LimaCcd acq_expo_time for " + getName(), e);
			throw new DeviceException("failed to set LimaCcd acq_expo_time for " + getName(), e);
		}

		try {
			AcqMode acqMode = getLimaCcd().getAcqMode();
			getLimaCcd().setAcqMode(AcqMode.ACCUMULATION);
			try {
				getLimaCcd().setAccTimeMode(((FrelonCcdDetectorData)getDetectorData()).getAccumulationTimeMode());
			} catch (DevFailed e) {
				logger.error("Failed to set LimaCcd acc_time_mode", e);
				throw new DeviceException(getName(), "Fail to set LimaCcd acc_time_mode.", e);
			}
			try {
				getLimaCcd().setAccMaxExpoTime(accTime);
			} catch (DevFailed e) {
				logger.error("Failed to set LimaCcd acc_max_expotime", e);
				throw new DeviceException(getName(), "Fail to set LimaCcd acc_max_expotime.", e);
			}
			try {
				// prepare the camera for a new acquisition, have to be called each time a parameter is set.
				getLimaCcd().prepareAcq();
			} catch (DevFailed e) {
				logger.error("Call to limaCcd.prepareAcq() failed", e);
				throw new DeviceException(getName(), "Call to limaCcd.prepareAcq() failed.", e);
			}
			try {
				accNbFrames = getLimaCcd().getAccNbFrames();
				logger.info("Number of accumulations returned from {} is {}.", getName(), accNbFrames);
			} catch (DevFailed e) {
				logger.error("Failed to get LimaCcd acc_nb_frames", e);
				throw new DeviceException(getName(), "Fail to set LimaCcd acc_nb_frames.", e);
			}
			getLimaCcd().setAcqMode(acqMode);
		} catch (DevFailed e) {
			logger.error("Failed to get LimaCcd acq_mode", e);
			throw new DeviceException(getName(), "Fail to get LimaCcd acq_mode.", e);
		}
		return accNbFrames;
	}

	@Override
	protected void configureDetectorForCollection() throws DeviceException {
		FrelonCcdDetectorData frelonCcdDetectorData = (FrelonCcdDetectorData) getDetectorData();
		// the following only handle 1 timing group, because it send to actual detector immediately.
		for (Integer i = 0; i < currentScanParameter.getGroups().size(); i++) {
			TimingGroup timingGroup = currentScanParameter.getGroups().get(i);
			double accumlationTime = timingGroup.getTimePerScan();
			int numberOfAccumulation = timingGroup.getNumberOfScansPerFrame();
			//			double exposureTime = timingGroup.getTimePerFrame();
			Integer numberOfImages = timingGroup.getNumberOfFrames();
			if (numberOfImages < 2) {
				//collect minimum 2 spectrum as the 1st one sometime crap.
				numberOfImages = 2;
			}
			frelonCcdDetectorData.setNumberOfImages(numberOfImages);
			if (numberOfAccumulation>1) {
				frelonCcdDetectorData.setAcqMode(AcqMode.ACCUMULATION);
				frelonCcdDetectorData.setAccumulationMaximumExposureTime(accumlationTime);
				setCollectionTime(accumlationTime*numberOfAccumulation);
			} else {
				frelonCcdDetectorData.setAcqMode(AcqMode.SINGLE);
				setCollectionTime(accumlationTime);
			}
		}

		// read detector configuration data and send them to detector hardware
		//		try {
		//			// set the internal config for pixel rate, PRECISION or SPEED.
		//			getFrelon().setSPB2Config(frelonCcdDetectorData.getSpb2Config());
		//		} catch (DevFailed e1) {
		//			logger.error("Failed to set Frelon detector HD_configuration.", e1);
		//			throw new DeviceException(getName(), "Fail to set Frelon detector HD_configuration", e1);
		//		}
		//		try {
		//			getFrelon().setImageMode(frelonCcdDetectorData.getImageMode());
		//		} catch (DevFailed e2) {
		//			logger.error("Failed to set Frelon detector image mode", e2);
		//			throw new DeviceException(getName(), "Fail to set Frelon detector image mode", e2);
		//		}
		//		try {
		//			getFrelon().setInputChannels(frelonCcdDetectorData.getInputChannel());
		//		} catch (DevFailed e2) {
		//			logger.error("Failed to set Frelon detector input channel", e2);
		//			throw new DeviceException(getName(), "Fail to set Frelon detector input channel", e2);
		//		}
		// set the bin size for the detector
		//				getLimaCcd().setImageBin(frelonCcdDetectorData.getHotizontalBinValue(), frelonCcdDetectorData.getVerticalBinValue());

		try {
			getFrelon().setROIMode(frelonCcdDetectorData.getRoiMode());
		} catch (DevFailed e) {
			logger.error("Fail to set Frelon detector ROI mode.", e);
			throw new DeviceException(getName(), "Fail to set Frelon detector ROI mode", e);
		}
		//		try {
		//			ROIMode roiMode = getFrelon().getROIMode();
		//			if (roiMode != ROIMode.NONE) {
		//				// setting the AOI (area of interest) to Frelon detector
		//				try {
		//					getLimaCcd().setImageROIInt(frelonCcdDetectorData.getAreaOfInterest());
		//				} catch (DevFailed e1) {
		//					logger.error("Failed to set Lima CCD area of interest for " + roiMode.name() + " ROI.", e1);
		//					throw new DeviceException(getName(), "Failed to set Lima CCD area of interest for " + roiMode.name()
		//							+ " ROI.", e1);
		//				}
		//			}
		//TODO commented out because this method call fails to send to device attribute.
		//			if (roiMode == ROIMode.KINETIC) {
		//				try {
		//					// set roi_bin_offset in pixels vertically or lines
		//					getFrelon().setROIBinOffset(frelonCcdDetectorData.getRoiBinOffset());
		//				} catch (DevFailed e) {
		//					logger.error("Fail to set Frelon detector ROI bin offset.", e);
		//					throw new DeviceException(getName(), "Fail to set Frelon detector ROI bin offset.", e);
		//				}
		//			}
		//	} catch (DevFailed e) {
		//		logger.error("Fail to get Frelon detector ROI bin offset.", e);
		//		throw new DeviceException(getName(), "Fail to get Frelon detector ROI bin offset.", e);
		//	}
		updateImageProperties();
		try {
			getLimaCcd().setAcqMode(frelonCcdDetectorData.getAcqMode());
		} catch (DevFailed e) {
			logger.error("Failed to set Frelon detector acq_mode", e);
			throw new DeviceException(getName(), "Fail to set Frelon detector acq_mode.", e);
		}
		try {
			getLimaCcd().setAcqNbFrames(frelonCcdDetectorData.getNumberOfImages());
		} catch (DevFailed e1) {
			logger.error("Failed to set Frelon detector acq_nb_frame", e1);
			throw new DeviceException(getName(), "Fail to set Frelon detector acq_nb_frame.", e1);
		}
		try {
			getLimaCcd().setAcqTriggerMode(frelonCcdDetectorData.getTriggerMode());
		} catch (DevFailed e2) {
			logger.error("Failed to set Frelon detector trigger mode", e2);
			throw new DeviceException(getName(), "Fail to set Frelon detector trigger mode.", e2);
		}
		try {
			if (getLimaCcd().getAcqMode()==AcqMode.ACCUMULATION) {
				try {
					getLimaCcd().setAccTimeMode(frelonCcdDetectorData.getAccumulationTimeMode());
				} catch (DevFailed e) {
					logger.error("Failed to set LimaCcd acc_time_mode", e);
					throw new DeviceException(getName(), "Fail to set LimaCcd acc_time_mode.", e);
				}
				try {
					getLimaCcd().setAccMaxExpoTime(frelonCcdDetectorData.getAccumulationMaximumExposureTime());
				} catch (DevFailed e) {
					logger.error("Failed to set LimaCcd acc_max_expotime", e);
					throw new DeviceException(getName(), "Fail to set LimaCcd acc_max_expo_time.", e);
				}
			}
		} catch (DevFailed e) {
			logger.error("Failed to get LimaCcd acq_mode", e);
			throw new DeviceException(getName(), "Fail to get LimaCcd acq_mode.", e);
		}
	}

	private void updateImageProperties() throws DeviceException {
		try {
			imageType = getLimaCcd().getImageType();
		} catch (DevFailed e) {
			logger.error("Failed to get image_type from detector "+getName(), e);
			throw new DeviceException(getName(), "Failed to get image_type from detector ", e);
		}
		try {
			imageWidth = getLimaCcd().getImageWidth();
		} catch (DevFailed e) {
			logger.error("Failed to get image_width from detector "+getName(), e);
			throw new DeviceException(getName(),"Failed to get image_width from detector ", e);
		}
		try {
			imageHeight = getLimaCcd().getImageHeight();
		} catch (DevFailed e) {
			logger.error("Failed to get image_height from detector "+getName(), e);
			throw new DeviceException(getName(),"Failed to get image_height from detector ", e);
		}

	}

	@Override
	public DetectorStatus fetchStatus() throws DeviceException {
		// Check and report detector status
		DetectorStatus status = new DetectorStatus();
		status.setDetectorStatus(Detector.IDLE);
		AcqStatus acqStatus;
		try {
			acqStatus = getLimaCcd().getAcqStatus();
			if (acqStatus == AcqStatus.READY) {
				status.setDetectorStatus(Detector.IDLE);
			} else if (acqStatus == AcqStatus.RUNNING) {
				status.setDetectorStatus(Detector.BUSY);
			} else if (acqStatus == AcqStatus.FAULT) {
				status.setDetectorStatus(Detector.FAULT);
			} else if (acqStatus == AcqStatus.CONFIGURATION) {
				status.setDetectorStatus(Detector.STANDBY);
			} else {
				throw new DeviceException(getName(), "Unknown detector status.");
			}
		} catch (DevFailed e) {
			logger.error("limaCcd.getAcqStatus() failed.", e);
			throw new DeviceException(getName(), "limaCcd.getAcqStatus() failed.", e);
		}

		return status;
	}

	@Override
	public int getMaxPixel() {
		return FrelonCcdDetectorData.MAX_PIXEL;
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {
		return false;
	}

	@Override
	public String getDescription() throws DeviceException {
		try {
			return getLimaCcd().getCameraModel();
		} catch (DevFailed e) {
			logger.error("Failed to get Camera model from detector " + getName(), e);
			throw new DeviceException(getName(), "Failed to get Camera model from detector.", e);
		}
	}

	@Override
	public String getDetectorID() throws DeviceException {
		return getName();
	}

	@Override
	public String getDetectorType() throws DeviceException {
		try {
			return getLimaCcd().getCameraType();
		} catch (DevFailed e) {
			logger.error("Failed to get Camera Type from detector " + getName(), e);
			throw new DeviceException(getName(), "Failed to get Camera Type from detector.", e);
		}
	}
	//Non interface methods - EdeFrelon specific

	/**
	 * reset the camera to factory setting
	 * @throws DeviceException
	 */
	public void reset() throws DeviceException {
		try {
			getLimaCcd().reset();
		} catch (DevFailed e) {
			logger.error("limaCcd.reset() failed.", e);
			throw new DeviceException(getName(), "limaCcd.reset() failed.", e);
		}
	}
	public String[] getCurrentAttributesValues() throws DeviceException {
		try {
			return getFrelon().execSerialCommand(">C");
		} catch (DevFailed e) {
			logger.error("frelon.execSerialCommand failed.", e);
			throw new DeviceException(getName(), "frelon.execSerialCommand failed.", e);
		}
	}

	public void resetLink() throws DeviceException {
		try {
			frelon.resetLink();
		} catch (DevFailed e) {
			logger.error("frelon.resetLink() failed.", e);
			throw new DeviceException(getName(), "frelon.resetLink() failed.", e);
		}
	}
	public LimaCCD getLimaCcd() {
		return limaCcd;
	}

	public void setLimaCcd(LimaCCD limaCcd) {
		this.limaCcd = limaCcd;
	}

	public Frelon getFrelon() {
		return frelon;
	}

	public void setFrelon(Frelon frelon) {
		this.frelon = frelon;
	}

	@Override
	public HashMap<String, Double> getTemperatures() throws DeviceException {
		//TODO impelement frelon temperatures access
		HashMap<String, Double> dummytemps=new HashMap<String, Double>(4);
		dummytemps.put("CCDTEMP", -15.0);
		dummytemps.put("PELTCUR", 2.07);
		dummytemps.put("CCDPRES", 750.0);
		dummytemps.put("PCBTEMP", 41.0);
		return dummytemps;
	}

	@Override
	public int getNumberOfSpectra() throws DeviceException {
		try {
			return limaCcd.getAcqNbFrames();
		} catch (DevFailed e) {
			logger.error("Failed to get acq_nb_frames from detector "+getName(), e);
			throw new DeviceException(getName(),"Failed to get acq_nb_frames from detector ", e);
		}
	}
}
