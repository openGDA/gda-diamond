/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package gda.scan.ede;

import java.io.Serializable;

import gda.scan.ScanDataPoint;
import gda.scan.ede.position.EdePositionType;

/**
 * Message bean holding the current progress and latest spectra from an EDEScan.
 */
public class EdeScanProgressBean implements Serializable {

	private final int groupNumOfThisSDP;
	private final int frameNumOfThisSDP;
	private final EdeScanType scanType;
	private final EdePositionType positionType;
	private final ScanDataPoint thisPoint;

	public EdeScanProgressBean(int groupNumOfThisSDP, int frameNumOfThisSDP, EdeScanType scanType,
			EdePositionType positionType, ScanDataPoint thisPoint) {
		this.groupNumOfThisSDP = groupNumOfThisSDP;
		this.frameNumOfThisSDP = frameNumOfThisSDP;
		this.scanType = scanType;
		this.positionType = positionType;
		this.thisPoint = thisPoint;
	}

	public int getGroupNumOfThisSDP() {
		return groupNumOfThisSDP;
	}

	public int getFrameNumOfThisSDP() {
		return frameNumOfThisSDP;
	}

	public EdeScanType getScanType() {
		return scanType;
	}

	public EdePositionType getPositionType() {
		return positionType;
	}

	public ScanDataPoint getThisPoint() {
		return thisPoint;
	}
}
