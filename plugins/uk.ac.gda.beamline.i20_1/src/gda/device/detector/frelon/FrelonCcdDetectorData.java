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

public class FrelonCcdDetectorData extends DetectorData {
	public static final int MAX_PIXEL = 2048;

	private ROIMode roiMode;
	private int binValue = 1;
	private int yStartPaxel = 0;
	private int yLength = 2048;
	private SPB2Config spb2Config;

	public ROIMode getRoiMode() {
		return roiMode;
	}
	public void setRoiMode(ROIMode roiMode) {
		this.roiMode = roiMode;
	}
	public int getBinValue() {
		return binValue;
	}
	public void setBinValue(int binValue) {
		this.binValue = binValue;
	}
	public int getyStartPaxel() {
		return yStartPaxel;
	}
	public void setyStartPaxel(int yStartPaxel) {
		this.yStartPaxel = yStartPaxel;
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
}
