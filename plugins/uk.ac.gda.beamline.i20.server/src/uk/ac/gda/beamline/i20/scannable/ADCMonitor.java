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

import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.detector.DetectorBase;
import gda.epics.LazyPVFactory;
import gda.epics.PV;
import gda.factory.FactoryException;

public class ADCMonitor extends DetectorBase {

	private static final long serialVersionUID = 1L;

	private final String pvPrefix;
	private final String readoutPVName;
	private final String columnName;
	private PV<Double> samplePeriodPV;
	private PV<ADCMonitorModes> modePV;
	private PV<Integer> triggerPV;
	private PV<Double> readoutPV;

	public ADCMonitor(String name, String pvPrefix, String readoutPV, String columnName) {
		setName(name);
		this.pvPrefix = pvPrefix;
		this.readoutPVName = readoutPV;
		this.columnName = columnName;
	}

	@Override
	public void configure() throws FactoryException {
		super.configure();
		setInputNames(new String[] {});
		setExtraNames(new String[] { columnName });
		setOutputFormat(new String[] { "%.5g" });
		samplePeriodPV = LazyPVFactory.newDoublePV(pvPrefix + ":PERIOD");
		modePV = LazyPVFactory.newEnumPV(pvPrefix + ":MODE", ADCMonitorModes.class);
		triggerPV = LazyPVFactory.newIntegerPV(pvPrefix + ":SOFTTRIGGER");
		readoutPV = LazyPVFactory.newDoublePV(readoutPVName);
	}

	@Override
	public void collectData() throws DeviceException {
		try {
			samplePeriodPV.putWait(getCollectionTime());
			triggerPV.putNoWait(1);
		} catch (IOException e) {
			throw new DeviceException(e.getMessage(), e);
		}
	}

	@Override
	public int getStatus() throws DeviceException {
		try {
			ADCMonitorModes currentMode = modePV.get();
			if (currentMode == ADCMonitorModes.Continuous || currentMode == ADCMonitorModes.Gate)
				return Detector.IDLE;
			if (triggerPV.get() == 0)
				return Detector.IDLE;
			return Detector.BUSY;
		} catch (IOException e) {
			throw new DeviceException(e.getMessage(), e);
		}
	}

	@Override
	public Object readout() throws DeviceException {
		try {
			return readoutPV.get();
		} catch (IOException e) {
			throw new DeviceException(e.getMessage(), e);
		}
	}

	@Override
	public void atScanStart() throws DeviceException {
		super.atScanStart();
		try {
			modePV.putWait(ADCMonitorModes.Trigger);
		} catch (IOException e) {
			throw new DeviceException(e.getMessage(), e);
		}
	}

	@Override
	public void atScanEnd() throws DeviceException {
		super.atScanEnd();
		try {
			modePV.putWait(ADCMonitorModes.Continuous);
		} catch (IOException e) {
			throw new DeviceException(e.getMessage(), e);
		}
	}

	@Override
	public void atCommandFailure() throws DeviceException {
		atScanEnd();
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {
		return false;
	}

}