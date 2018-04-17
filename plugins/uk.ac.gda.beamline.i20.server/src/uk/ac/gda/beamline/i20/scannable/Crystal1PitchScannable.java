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

package uk.ac.gda.beamline.i20.scannable;

import java.io.IOException;

import gda.device.DeviceException;
import gda.device.scannable.ScannableMotor;
import gda.epics.LazyPVFactory;
import gda.epics.PV;

/**
 * For I20 only. Only allows movement of the Crystal1Pitch motor if intensity feedback has been disabled.
 */
public class Crystal1PitchScannable extends ScannableMotor {
	private String intensityFeedbackPVName = "BL20I-OP-QCM-01:PY:FBON";
	private PV<Boolean> intensityFeedbackPV;

	public String getIntensityFeedbackPVName() {
		return intensityFeedbackPVName;
	}

	public void setIntensityFeedbackPVName(String intensityFeedbackPVName) {
		this.intensityFeedbackPVName = intensityFeedbackPVName;
	}

	@Override
	public void rawAsynchronousMoveTo(Object internalPosition) throws DeviceException {
		if (!isIntensityFeedbackDisabled())
			throw new DeviceException("Will not move " + getName() + " as intensity feedback is active.");
		super.rawAsynchronousMoveTo(internalPosition);
	}

	private boolean isIntensityFeedbackDisabled() throws DeviceException {
		if (intensityFeedbackPV == null)
			intensityFeedbackPV = LazyPVFactory.newBooleanFromEnumPV(intensityFeedbackPVName);
		try {
			return !intensityFeedbackPV.get();
		} catch (IOException e) {
			throw new DeviceException("Cannot fetch intensity feedback of " + getName());
		}
	}

}