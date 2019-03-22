/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package gda.device.detector.xstrip;

import gda.device.detector.DetectorData;

public class XhDetectorData extends DetectorData {

	private static final long serialVersionUID = 1L;

	private static final double MIN_BIAS_VOLTAGE = 1.0;
	private static final double MAX_BIAS_VOLTAGE = 137.0;

	public enum HEAD {
		XH, XSTRIP
	}

	public static final String CURRENT_HEAD_PROPERTY_NAME = "currentHead";
	private HEAD currentHead;

	public HEAD getCurrentHead() {
		return currentHead;
	}
	public void setCurrentHead(HEAD head) {
		this.firePropertyChange(CURRENT_HEAD_PROPERTY_NAME, currentHead, currentHead = head);
	}

	public Double getMaxBias() {
		return MAX_BIAS_VOLTAGE;
	}

	public Double getMinBias() {
		return MIN_BIAS_VOLTAGE;
	}

	public boolean isVoltageInRange(double value) {
		return (getMinBias() <= value & value <= getMaxBias());
	}
}
