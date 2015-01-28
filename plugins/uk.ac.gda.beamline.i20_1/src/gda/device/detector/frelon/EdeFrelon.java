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
import gda.device.lima.LimaCCD.AcqStatus;
import gda.device.lima.LimaCCD.ImageType;
import gda.device.lima.impl.LimaROIIntImpl;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EdeFrelon extends EdeDetectorBase {

	private static final Logger logger = LoggerFactory.getLogger(EdeFrelon.class);

	private final LimaCCD limaCcd;
	private final Frelon frelon;

	private long imageWidth;

	private long imageHeight;

	private ImageType imageType;

	public EdeFrelon(Frelon frelon, LimaCCD limaCcd) {
		this.frelon = frelon;
		this.limaCcd = limaCcd;
	}

	@Override
	public synchronized int[] readoutFrames(int startFrame, int finalFrame) throws DeviceException {
		byte[] byteData = null;
		int[] intData=null;
		try {
			int n = 0;
			int lastImageNumber=-1;
			if ((lastImageNumber = limaCcd.getLastImageReady()) != finalFrame - startFrame) {
				logger.error("EdeFrelon.readoutFrames: image not ready {} should be {}", lastImageNumber, finalFrame - startFrame);
				throw new DeviceException("EdeFrelon.readoutFrames: image not ready");
			}
			imageType = limaCcd.getImageType();
			imageWidth = limaCcd.getImageWidth();
			imageHeight = limaCcd.getImageHeight();
			intData = new int[(int) (imageWidth*imageHeight*(finalFrame - startFrame + 1))];
			for (int i = startFrame; i <= finalFrame; i++) {
				byteData = limaCcd.getImage(i);
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
			throw new DeviceException("EdeFrelon.readoutFrames: failed "+e.errors[0].desc);
		}
		return intData;
	}

	@Override
	public void setCollectionTime(double collectionTime) throws DeviceException {
		super.setCollectionTime(collectionTime);
		try {
			limaCcd.setAcqExpoTime(collectionTime);
		} catch (DevFailed e) {
			logger.error("failed to set exposure time for " + getName(), e);
			throw new DeviceException("failed to set exposure time for " + getName(), e);
		}
	}

	@Override
	public void collectData() throws DeviceException {
		try {
			limaCcd.setAcqNbFrames(1);
		} catch (DevFailed e) {
			logger.error("failed to set acq_nb_frames for " + getName(), e);
			throw new DeviceException("failed to set acq_nb_frames for " + getName(), e);
		}
		startScan();
	}

	private void startScan() throws DeviceException {
		// TODO call prepare and start from Frelon
		try {
			limaCcd.prepareAcq();
		} catch (DevFailed e) {
			logger.error("Call to limaCcd.prepareAcq() failed", e);
			throw new DeviceException(getName(), "Call to limaCcd.prepareAcq() failed.", e);
		}
		try {
			limaCcd.startAcq();
		} catch (DevFailed e) {
			logger.error("Call to llimaCcd.startAcq() failed", e);
			throw new DeviceException(getName(), "Call to limaCcd.startAcq() failed.", e);
		}
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {
		return false;
	}

	@Override
	protected DetectorData createData() {
		return new FrelonCcdDetectorData();
	}

	@Override
	public int getMaxPixel() {
		return FrelonCcdDetectorData.MAX_PIXEL;
	}

	@Override
	public int getNumberScansInFrame(double frameTime, double scanTime, int numberOfFrames) throws DeviceException {
		// TODO Query the detector to find out how many scans that can fit
		return 0;
	}

	@Override
	protected void configureDetectorForCollection() throws DeviceException {
		//fetch detector configuration data and send them to detector hardware
		FrelonCcdDetectorData frelonCcdDetectorData = (FrelonCcdDetectorData) getDetectorData();
		try {
			frelon.setSPB2Config(frelonCcdDetectorData.getSpb2Config());
		} catch (DevFailed e1) {
			logger.error("Fail to set Frelon detector HD_configuration.", e1);
			throw new DeviceException(getName(), "Fail to set Frelon detector HD_configuration", e1);
		}
		// setting the AOI (area of interest) to Frelon detector
		limaCcd.setImageBin(1, frelonCcdDetectorData.getVerticalBinValue()); //Horizontal binning always 1
		try {
			frelon.setROIMode(frelonCcdDetectorData.getRoiMode());
		} catch (DevFailed e) {
			logger.error("Fail to set Frelon detector ROI mode.", e);
			throw new DeviceException(getName(), "Fail to set Frelon detector ROI mode", e);
		}
		try {
			ROIMode roiMode = frelon.getROIMode();
			if (roiMode==ROIMode.KINETIC) {
				frelon.setROIBinOffset(frelonCcdDetectorData.getyStartPaxel());
			} else if (roiMode==ROIMode.FAST || roiMode==ROIMode.SLOW) {

			}
		} catch (DevFailed e) {
			logger.error("Fail to set Frelon detector ROI bin offset.", e);
			throw new DeviceException(getName(), "Fail to set Frelon detector ROI bin offset.", e);
		}

		try {
			//TODO set fix AOI size - X all units, Y 1 unit
			limaCcd.setImageROIInt(new LimaROIIntImpl(0,2047,1,1));
		} catch (DevFailed e) {
			// TODO Auto-generated catch block
			logger.error("TODO put description of error here", e);
		}
	}

	@Override
	public DetectorStatus fetchStatus() throws DeviceException {
		// TODO Check and report detector status
		DetectorStatus status=new DetectorStatus();
		status.setDetectorStatus(Detector.IDLE);
		AcqStatus acqStatus;
		try {
			acqStatus = limaCcd.getAcqStatus();
			if (acqStatus==AcqStatus.READY){
				status.setDetectorStatus(Detector.IDLE);
			} else if (acqStatus==AcqStatus.RUNNING){
				status.setDetectorStatus(Detector.BUSY);
			} else if (acqStatus==AcqStatus.FAULT){
				status.setDetectorStatus(Detector.FAULT);
			} else if (acqStatus==AcqStatus.CONFIGURATION){
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
}
