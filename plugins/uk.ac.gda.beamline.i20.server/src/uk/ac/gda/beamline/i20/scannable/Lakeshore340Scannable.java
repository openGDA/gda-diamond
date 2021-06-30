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

import org.apache.commons.lang.ArrayUtils;

import gda.device.DeviceException;
import gda.device.scannable.ScannableBase;
import gda.factory.FactoryException;
import uk.ac.gda.beans.exafs.i20.CryostatProperties;

public class Lakeshore340Scannable extends ScannableBase{
	private String pvName;
	private double tolerance = 0.0;
	private double deadtime = 0.0;
	private int waitTime = 20;
	private int tempSelect = 0;
	private boolean isMoving = false;
	private Lakeshore340StatusRunner statusRunner;
	private Thread statusThread;
	private ILakeshore340 controller;

	public ILakeshore340 getController() {
		return controller;
	}

	public void setController(ILakeshore340 lakeshore340Controller) {
		this.controller = lakeshore340Controller;
		this.controller.configure();
	}

	@Override
	public void configure() throws FactoryException {
		if (isConfigured()) {
			return;
		}
		statusRunner = new Lakeshore340StatusRunner(this);
		statusThread = new Thread(statusRunner);
		statusThread.setDaemon(true);
		statusThread.start();
		setConfigured(true);
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		Double demandValue = Double.parseDouble(position.toString());
		try {
			isMoving = true;
			if (!statusThread.isAlive())
				statusThread.start();
			controller.setSetpointControl(demandValue);
		} catch (IOException e) {
			isMoving = false;
			throw new DeviceException("IOException while trying to get the apply the setpoint", e);
		}
	}

	@Override
	public Double rawGetPosition() throws DeviceException {
		try {
			return controller.getTempReadback(tempSelect);
		} catch (IOException e) {
			throw new DeviceException("IOException while trying to get the temperature", e);
		}
	}

	public int getTempSelect() {
		return tempSelect;
	}

	public void setTempSelect(int tempSelect) {
		this.tempSelect = tempSelect;
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return statusThread.isAlive() && isMoving;
	}

	@Override
	public void stop() throws DeviceException {
		statusRunner.keepRunning = false;
		try {
			controller.setSetpointControl(rawGetPosition());
		} catch (IOException e) {
			throw new DeviceException("IOException while trying to stop", e);
		}
	}

	public void setup(String controlMode, String heaterRange, int waitTime, Double manualOutput, Double pValue, Double iValue, Double dValue, double tolerance) throws DeviceException {
		setControlmode(controlMode);
		setRange(heaterRange);
		this.waitTime = waitTime;
		// if manual output
		if (controlMode == CryostatProperties.CONTROL_MODE[0]) {
			try {
				controller.setManualOutput(manualOutput);
			} catch (IOException e) {
				throw new DeviceException("IOException when setting manual output value!");
			}
		}
		// if manual PID
		String controlModeValue = CryostatProperties.CONTROL_MODE[1];
		if (controlMode.equals(controlModeValue)) {
			try {
				controller.setpValue(pValue);
			} catch (IOException e) {
				throw new DeviceException("IOException when setting p value!");
			}
			try {
				controller.setiValue(iValue);
			} catch (IOException e1) {
				throw new DeviceException("IOException when setting i value!");
			}
			try {
				controller.setdValue(dValue);
			} catch (IOException e) {
				throw new DeviceException("IOException when setting d value!");
			}
		}
		this.tolerance = tolerance;
	}

	private void setRange(String heaterRange) throws DeviceException {
		int index = ArrayUtils.indexOf(CryostatProperties.HEATER_RANGE, heaterRange);
		if (index < 0) {
			throw new DeviceException("Heater range string not acceptable!");
		}
		try {
			controller.setRange(Double.valueOf(index));
		} catch (IOException e) {
			throw new DeviceException("IOException when setting heater range!");
		}
	}

	private void setControlmode(String controlMode) throws DeviceException {
		int index = ArrayUtils.indexOf(CryostatProperties.CONTROL_MODE, controlMode);
		if (index < 0)
			throw new DeviceException("Control mode string not acceptable!");
		try {
			controller.setControlmode(Double.valueOf(index));
		} catch (IOException e) {
			throw new DeviceException("IOException when setting control mode!");
		}
	}

	protected boolean withinDeadband() throws DeviceException {
		try {
			Double currentValue = rawGetPosition();
			Double currentSetpoint = controller.getSetpoint();
			return Math.abs(currentValue - currentSetpoint) < tolerance;
		} catch (IOException e) {
			throw new DeviceException("IOException while trying to get the temperature reading", e);
		}
	}

	public String getPvName() {
		return pvName;
	}

	public void setPvName(String pvName) {
		if (!pvName.endsWith(":"))
			pvName += ":";
		this.pvName = pvName;
	}

	public double getTolerance() {
		return tolerance;
	}

	public void setTolerance(double tolerance) {
		this.tolerance = tolerance;
	}

	public double getDeadtime() {
		return deadtime;
	}

	public void setDeadtime(double deadtime) {
		this.deadtime = deadtime;
	}

	public int getWaitTime() {
		return waitTime;
	}

	public void setWaitTime(int waitTime) {
		this.waitTime = waitTime;
	}

	public String getRangeString() throws IOException {
		int index = (int) Math.round(controller.getRange());
		return CryostatProperties.HEATER_RANGE[index];
	}

	public String getControlmodeString() {
		int index = (int) Math.round(getDeadtime());
		return CryostatProperties.CONTROL_MODE[index];
	}

	public void setMoving(boolean isMoving) {
		this.isMoving = isMoving;
	}

	public boolean isMoving() {
		return isMoving;
	}

}