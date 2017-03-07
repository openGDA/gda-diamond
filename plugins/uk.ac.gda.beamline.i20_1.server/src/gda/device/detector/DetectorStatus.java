/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

import gda.device.Detector;

/**
 * Messaging bean showing the current XStrip detector status (same values as in GDA DetectorStatus class ) and the
 * current group/frame/scan being collected.
 */
public class DetectorStatus {

	private int detectorStatus;

	private final DetectorScanInfo currentScanInfo = new DetectorScanInfo(null,null,null);

	@Override
	public String toString() {
		String detStatus = "";

		switch (detectorStatus) {
		case Detector.BUSY:
			detStatus = "Busy";
			break;
		case Detector.FAULT:
			detStatus = "Fault";
			break;
		case Detector.IDLE:
			detStatus = "Idle";
			break;
		case Detector.MONITORING:
			detStatus = "Monitoring";
			break;
		case Detector.PAUSED:
			detStatus = "Paused";
			break;
		case Detector.STANDBY:
			detStatus = "Standby";
			break;
		}
		return detStatus + " " + currentScanInfo.toString();
	}

	public DetectorScanInfo getCurrentScanInfo() {
		return currentScanInfo;
	}

	public int getDetectorStatus() {
		return detectorStatus;
	}

	public void setDetectorStatus(int detectorStatus) {
		this.detectorStatus = detectorStatus;
	}
}