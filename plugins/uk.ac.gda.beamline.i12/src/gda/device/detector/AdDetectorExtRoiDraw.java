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

package gda.device.detector;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.detector.addetector.ADDetector;
import gda.device.detector.areadetector.v17.FfmpegStream;
import gda.device.detector.areadetector.v17.NDOverlay;
import gda.device.detector.areadetector.v17.NDROI;

/**
 *
 */
public class AdDetectorExtRoiDraw extends ADDetector {

	private static Logger logger = LoggerFactory.getLogger(AdDetectorExtRoiDraw.class);

	private NDOverlay ndDraw;

	private NDROI ndRoi;

	private FfmpegStream mjpeg;

	@Override
	public void atScanStart() throws DeviceException {
		super.atScanStart();
		try {
			getAdBase().stopAcquiring();
			getAdBase().setImageMode(0);
		} catch (Exception e) {
			logger.error("Cannot set Image Mode", e);
		}
	}

	public void setNdDraw(NDOverlay ndDraw) {
		this.ndDraw = ndDraw;
	}

	public NDOverlay getNdDraw() {
		return ndDraw;
	}

	public void setNdRoi(NDROI ndRoi) {
		this.ndRoi = ndRoi;
	}

	public NDROI getNdRoi() {
		return ndRoi;
	}

	public FfmpegStream getMjpeg() {
		return mjpeg;
	}

	public void setMjpeg(FfmpegStream mjpeg) {
		this.mjpeg = mjpeg;
	}

	@Override
	public void reset() throws Exception {
		super.reset();
		if (ndRoi != null) {
			ndRoi.reset();
		}

		if (ndDraw != null) {
			ndDraw.reset();
		}

		if (mjpeg != null) {
			mjpeg.reset();
		}
	}
}
