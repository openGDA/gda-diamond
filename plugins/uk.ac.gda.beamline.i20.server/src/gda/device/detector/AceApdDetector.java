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

import java.io.IOException;

import gda.device.DeviceException;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.epics.LazyPVFactory;
import gda.epics.PV;
import gda.factory.FactoryException;

/**
 * For I20 only. Control of the ACE APD detector, with VETO control and readout via the Xspress2 scaler channels.
 */
public class AceApdDetector extends TfgScalerWithFrames {

	private static final long serialVersionUID = 1L;

	private static String STARTCOUNT = "STARTCOUNT";
	private static String STOPCOUNT = "STOPCOUNT";

	String epicsTemplateName = "BL20I-EA-DET-04:";
	PV<Integer> startPV;
	PV<Integer> stopPV;

	public AceApdDetector() {
	}

	@Override
	public void configure() throws FactoryException {
		super.configure();
		startPV = LazyPVFactory.newIntegerPV(epicsTemplateName + STARTCOUNT);
		stopPV = LazyPVFactory.newIntegerPV(epicsTemplateName + STOPCOUNT);
	}

	@Override
	public void collectData() throws DeviceException {
		try {
			stopPV.putNoWait(1);
			startPV.putNoWait(1);
			super.collectData();
		} catch (IOException e) {
			throw new DeviceException("Exception trying to start the " + getName() + " detector", e);
		}
	}

	public String getEpicsTemplateName() {
		return epicsTemplateName;
	}

	public void setEpicsTemplateName(String epicsTemplateName) {
		this.epicsTemplateName = epicsTemplateName;
	}
}
