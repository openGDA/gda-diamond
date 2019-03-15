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

import org.dawnsci.ede.EdePositionType;
import org.dawnsci.ede.EdeScanType;

/**
 * Message bean holding the current progress and latest spectra from an EDEScan.
 */
public class EdeScanProgressBean implements Serializable {

	private static final long serialVersionUID = 1L;

	private final int groupNumOfThisSDP;
	private final int frameNumOfThisSDP;
	private String customLabelForSDP;
	private final EdeScanType scanType;
	private final EdePositionType positionType;
	private String fileName;

	public EdeScanProgressBean(int groupNumOfThisSDP, int frameNumOfThisSDP, EdeScanType scanType,
			EdePositionType positionType, String filename) {
		this.groupNumOfThisSDP = groupNumOfThisSDP;
		this.frameNumOfThisSDP = frameNumOfThisSDP;
		this.scanType = scanType;
		this.positionType = positionType;
		this.fileName = filename;
		customLabelForSDP = null;
	}

	public int getGroupNumOfThisSDP() {
		return groupNumOfThisSDP;
	}

	public int getFrameNumOfThisSDP() {
		return frameNumOfThisSDP;
	}

	public void setCustomLabelForSDP(String customLabelForSDP) {
		this.customLabelForSDP = customLabelForSDP;
	}

	public String getCustomLabelForSDP() {
		return this.customLabelForSDP;
	}

	public EdeScanType getScanType() {
		return scanType;
	}

	public EdePositionType getPositionType() {
		return positionType;
	}

	public String getFilename() {
		return fileName;
	}
}
