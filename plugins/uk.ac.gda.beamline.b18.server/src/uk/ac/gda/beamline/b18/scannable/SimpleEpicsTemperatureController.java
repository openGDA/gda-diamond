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

package uk.ac.gda.beamline.b18.scannable;

import java.io.IOException;

import gda.device.DeviceException;
import gda.device.temperature.TemperatureBase;
import gda.epics.LazyPVFactory;
import gda.epics.PV;
import gda.epics.ReadOnlyPV;
import gda.factory.FactoryException;
import gda.util.PollerEvent;

public class SimpleEpicsTemperatureController extends TemperatureBase {

	private static final String LIMITS_NOT_SUPPORTED = "Hardware limits are not supported";
	private static final String RAMPING_NOT_SUPPORTED = "Temperature ramping is not supported; use a single set point instead";

	private PV<Double> setPointPV;
	private ReadOnlyPV<Double> readBackPV;

	public String getSetPointPVName() {
		return setPointPV.getPvName();
	}

	public void setSetPointPVName(String setPointPVName) {
		setPointPV = LazyPVFactory.newDoublePV(setPointPVName);
	}

	public String getReadBackPVName() {
		return readBackPV.getPvName();
	}

	public void setReadBackPVName(String readBackPVName) {
		readBackPV = LazyPVFactory.newReadOnlyDoublePV(readBackPVName);
	}

	@Override
	public void configure() throws FactoryException {
		if (isConfigured()) {
			return;
		}
		super.configure();
		setConfigured(true);
	}

	@Override
	public boolean isAtTargetTemperature() throws DeviceException {
		boolean atTargetTemperature = super.isAtTargetTemperature();
		if (atTargetTemperature) {
			busy = false;
		}
		return atTargetTemperature;
	}

	@Override
	public double getCurrentTemperature() throws DeviceException {
		if (!isConfigured()) {
			throw new IllegalStateException("Call configure() before use!");
		}
		try {
			return readBackPV.get().doubleValue();
		} catch (IOException e) {
			throw new DeviceException(e);
		}
	}

	@Override
	protected void startTowardsTarget() throws DeviceException {
		if (!isConfigured()) {
			throw new IllegalStateException("Call configure() before use!");
		}
		setPoint = targetTemp; // this shouldn't really be necessary, but TemperatureBase checks current temp against
								// setPoint, not targetTemp, when waiting for temperature
		try {
			setPointPV.putNoWait(Double.valueOf(setPoint));
		} catch (IOException e) {
			throw new DeviceException(e);
		}
		busy = true;
		notify();
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		if (position instanceof Number) {
			setTargetTemperature(((Number) position).doubleValue());
		}
	}

	@Override
	public void pollDone(PollerEvent pe) {
		throw new UnsupportedOperationException("Polling is not supported");
	}

	@Override
	protected void doStart() throws DeviceException {
		throw new UnsupportedOperationException(RAMPING_NOT_SUPPORTED);
	}

	@Override
	protected void doStop() throws DeviceException {
		throw new UnsupportedOperationException(RAMPING_NOT_SUPPORTED);
	}

	@Override
	protected void sendRamp(int ramp) throws DeviceException {
		throw new UnsupportedOperationException(RAMPING_NOT_SUPPORTED);
	}

	@Override
	protected void startNextRamp() throws DeviceException {
		throw new UnsupportedOperationException(RAMPING_NOT_SUPPORTED);
	}

	@Override
	protected void setHWLowerTemp(double lowerTemp) throws DeviceException {
		throw new UnsupportedOperationException(LIMITS_NOT_SUPPORTED);
	}

	@Override
	protected void setHWUpperTemp(double upperTemp) throws DeviceException {
		throw new UnsupportedOperationException(LIMITS_NOT_SUPPORTED);
	}

	@Override
	public void hold() throws DeviceException {
		throw new UnsupportedOperationException(RAMPING_NOT_SUPPORTED);
	}

	@Override
	public void runRamp() throws DeviceException {
		throw new UnsupportedOperationException(RAMPING_NOT_SUPPORTED);
	}
}
