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
import gda.device.detector.DetectorData;
import gda.device.detector.DetectorStatus;
import gda.device.detector.EdeDetectorBase;
import gda.device.frelon.Frelon;
import gda.device.frelon.Frelon.ROIMode;
import gda.device.lima.LimaCCD;
import gda.device.lima.LimaCCD.AcqMode;
import gda.device.lima.LimaCCD.AcqStatus;
import gda.device.lima.LimaCCD.AcqTriggerMode;
import gda.device.lima.LimaCCD.ImageType;
import gda.factory.FactoryException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EdeFrelon extends EdeDetectorBase {

	private static final Logger logger = LoggerFactory.getLogger(EdeFrelon.class);
	private static final double PIXEL_RATE=10.0; // MPixel/s per channel
	private static final double PIXEL_SIZE=14; // micro-meter
	private static final double LINE_TRANSFER_TIME_EXAFS=0.000004; // second 4us
	private static final double LINE_TRANSFER_TIEM_IMAGING=0.000008; //second 8us
	private static final int RESOLUTION=16; // bit
	private static final double READOUT_SPEED=40.0; // MPixel/s
	private static final double FULL_FRAME_RATE_WITHOUT_BINNING_IMAGING=8.35; //Frames/s
	private static final double FULL_FRAME_RATE_WITHOUT_BINNING_EXAFS=16.7; //Frames/s
	private static final double FRAME_TRANSFER_RATE_WITHOU_BINNIN_IMAGING=15.7; //Frames/s, exposure<59ms
	private static final double FRAME_TRANSFER_RATE_WITHOU_BINNIN_EXAFS=27.6; //Frames/s, exposure<58ms

	private LimaCCD limaCcd;
	private Frelon frelon;

	private long imageWidth;
	private long imageHeight;
	private ImageType imageType;

	public EdeFrelon() {
		super();
	}

	public EdeFrelon(Frelon frelon, LimaCCD limaCcd) {
		super();
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
	public synchronized int[] readoutFrames(int startFrame, int finalFrame) throws DeviceException {
		byte[] byteData = null;
		int[] intData = null;
		try {
			int n = 0;
			int lastImageNumber = -1;
			if ((lastImageNumber = getLimaCcd().getLastImageReady()) != finalFrame - startFrame) {
				logger.error("EdeFrelon.readoutFrames: image not ready {} should be {}", lastImageNumber, finalFrame
						- startFrame);
				throw new DeviceException("EdeFrelon.readoutFrames: image not ready");
			}

			intData = new int[(int) (imageWidth * imageHeight * (finalFrame - startFrame + 1))];
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
		try {
			getLimaCcd().setAcqExpoTime(expoTime);
		} catch (DevFailed e) {
			logger.error("failed to set LimaCcd acq_expo_time for " + getName(), e);
			throw new DeviceException("failed to set LimaCcd acq_expo_time for " + getName(), e);
		}

		try {
			if (getLimaCcd().getAcqMode()==AcqMode.ACCUMULATION) {
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
					return getLimaCcd().getAccNbFrames();
				} catch (DevFailed e) {
					logger.error("Failed to get LimaCcd acc_nb_frames", e);
					throw new DeviceException(getName(), "Fail to set LimaCcd acc_nb_frames.", e);
				}
			}
		} catch (DevFailed e) {
			logger.error("Failed to get LimaCcd acq_mode", e);
			throw new DeviceException(getName(), "Fail to get LimaCcd acq_mode.", e);
		}
		return 1;
	}

	@Override
	protected void configureDetectorForCollection() throws DeviceException {
		// read detector configuration data and send them to detector hardware
		FrelonCcdDetectorData frelonCcdDetectorData = (FrelonCcdDetectorData) getDetectorData();
		try {
			// set the internal config for pixel rate, PRECISION or SPEED.
			getFrelon().setSPB2Config(frelonCcdDetectorData.getSpb2Config());
		} catch (DevFailed e1) {
			logger.error("Failed to set Frelon detector HD_configuration.", e1);
			throw new DeviceException(getName(), "Fail to set Frelon detector HD_configuration", e1);
		}
		try {
			getFrelon().setImageMode(frelonCcdDetectorData.getImageMode());
		} catch (DevFailed e2) {
			logger.error("Failed to set Frelon detector image mode", e2);
			throw new DeviceException(getName(), "Fail to set Frelon detector image mode", e2);
		}
		try {
			getFrelon().setInputChannels(frelonCcdDetectorData.getInputChannel());
		} catch (DevFailed e2) {
			logger.error("Failed to set Frelon detector input channel", e2);
			throw new DeviceException(getName(), "Fail to set Frelon detector input channel", e2);
		}
		// set the bin size for the detector
		getLimaCcd().setImageBin(frelonCcdDetectorData.getHotizontalBinValue(), frelonCcdDetectorData.getVerticalBinValue());

		try {
			getFrelon().setROIMode(frelonCcdDetectorData.getRoiMode());
		} catch (DevFailed e) {
			logger.error("Fail to set Frelon detector ROI mode.", e);
			throw new DeviceException(getName(), "Fail to set Frelon detector ROI mode", e);
		}
		try {
			ROIMode roiMode = getFrelon().getROIMode();
			if (roiMode != ROIMode.NONE) {
				// setting the AOI (area of interest) to Frelon detector
				try {
					getLimaCcd().setImageROIInt(frelonCcdDetectorData.getAreaOfInterest());
				} catch (DevFailed e1) {
					logger.error("Failed to set Lima CCD area of interest for " + roiMode.name() + " ROI.", e1);
					throw new DeviceException(getName(), "Failed to set Lima CCD area of interest " + roiMode.name()
							+ " ROI.", e1);
				}
			}
			if (roiMode == ROIMode.KINETIC) {
				// set roi_bin_offset in pixels vertically or lines
				getFrelon().setROIBinOffset(frelonCcdDetectorData.getRoiBinOffset());
			}
		} catch (DevFailed e) {
			logger.error("Fail to set Frelon detector ROI bin offset.", e);
			throw new DeviceException(getName(), "Fail to set Frelon detector ROI bin offset.", e);
		}
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
					throw new DeviceException(getName(), "Fail to set LimaCcd acc_max_expotime.", e);
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
	protected void createDetectorDataFromJson(String property) {
		detectorData = GSON.fromJson(property, FrelonCcdDetectorData.class);
	}

	@Override
	protected DetectorData createDetectorData() {
		return new FrelonCcdDetectorData();
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


}
