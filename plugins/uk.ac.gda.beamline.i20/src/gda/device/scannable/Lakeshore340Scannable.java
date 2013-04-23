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

package gda.device.scannable;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.epics.LazyPVFactory;
import gda.epics.PV;
import gda.epics.ReadOnlyPV;
import gda.factory.FactoryException;

import java.io.IOException;

import org.apache.commons.lang.ArrayUtils;

import uk.ac.gda.beans.exafs.i20.CryostatParameters;

public class Lakeshore340Scannable extends ScannableBase implements Scannable {

	private String pvName;
	private double tolerance = 0.0;
	private double deadtime = 0.0;
	private int tempSelect = 0;
	private PV<Double> setpointControlPV;
	private ReadOnlyPV<Double> setpointReadbackPV;
	private PV<Double> rangeControlPV;
	private ReadOnlyPV<Double> rangeReadbackPV;
	private PV<Double> controlmodeControlPV;
	private ReadOnlyPV<Double> controlmodeReadbackPV;
	private PV<Double> manualOutputControlPV;
	private ReadOnlyPV<Double> manualOutputReadbackPV;
	private PV<Double> pValueControlPV;
	private ReadOnlyPV<Double> pValueReadbackPV;
	private PV<Double> iValueControlPV;
	private ReadOnlyPV<Double> iValueReadbackPV;
	private PV<Double> dValueControlPV;
	private ReadOnlyPV<Double> dValueReadbackPV;
	private PV<Boolean> rampEnableControlPV;
	private ReadOnlyPV<Boolean> rampEnableReadbackPV;
	private ReadOnlyPV<Double> tempReadback0PV;
	private ReadOnlyPV<Double> tempReadback1PV;
	private ReadOnlyPV<Double> tempReadback2PV;
	private ReadOnlyPV<Double> tempReadback3PV;

	@Override
	public void configure() throws FactoryException {
		setpointControlPV = LazyPVFactory.newDoublePV(getPvName() + "SETP_S");
		setpointReadbackPV = LazyPVFactory.newReadOnlyDoublePV(getPvName() + "SETP");
		rangeControlPV = LazyPVFactory.newDoublePV(getPvName() + "RANGE_S");
		rangeReadbackPV = LazyPVFactory.newReadOnlyDoublePV(getPvName() + "RANGE");
		controlmodeControlPV = LazyPVFactory.newDoublePV(getPvName() + "CMODE_S");
		controlmodeReadbackPV = LazyPVFactory.newReadOnlyDoublePV(getPvName() + "CMODE");
		manualOutputControlPV = LazyPVFactory.newDoublePV(getPvName() + "MOUT_S");
		manualOutputReadbackPV = LazyPVFactory.newReadOnlyDoublePV(getPvName() + "MOUT");
		pValueControlPV = LazyPVFactory.newDoublePV(getPvName() + "P_S");
		pValueReadbackPV = LazyPVFactory.newReadOnlyDoublePV(getPvName() + "P");
		iValueControlPV = LazyPVFactory.newDoublePV(getPvName() + "I_S");
		iValueReadbackPV = LazyPVFactory.newReadOnlyDoublePV(getPvName() + "I");
		dValueControlPV = LazyPVFactory.newDoublePV(getPvName() + "D_S");
		dValueReadbackPV = LazyPVFactory.newReadOnlyDoublePV(getPvName() + "D");
		rampEnableControlPV = LazyPVFactory.newBooleanFromDoublePV(getPvName() + "RAMPST_S");
		rampEnableReadbackPV = LazyPVFactory.newReadOnlyBooleanFromDoublePV(getPvName() + "RAMPST_S");
		tempReadback0PV = LazyPVFactory.newReadOnlyDoublePV(getPvName() + "KRDG0");
		tempReadback1PV = LazyPVFactory.newReadOnlyDoublePV(getPvName() + "KRDG1");
		tempReadback2PV = LazyPVFactory.newReadOnlyDoublePV(getPvName() + "KRDG2");
		tempReadback3PV = LazyPVFactory.newReadOnlyDoublePV(getPvName() + "KRDG3");
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		Double demandValue = Double.parseDouble(position.toString());
		try {
			setpointControlPV.putWait(demandValue);
		} catch (IOException e) {
			throw new DeviceException("IOException while trying to get the apply the setpoint", e);
		}
		try {
			rampEnableControlPV.putWait(true);
		} catch (IOException e) {
			throw new DeviceException("IOException while trying to enable the ramp", e);
		}
	}

	@Override
	public Double rawGetPosition() throws DeviceException {
		try {
			if (tempSelect == 0)
				return tempReadback0PV.get();
			else if (tempSelect == 1)
				return tempReadback1PV.get();
			else if (tempSelect == 2)
				return tempReadback2PV.get();
			else
				return tempReadback3PV.get();
		} catch (IOException e) {
			throw new DeviceException("IOException while trying to get the temperature reading", e);
		}
	}

	@Override
	public boolean isBusy() throws DeviceException {
		try {
			return rampEnableReadbackPV.get() && !withinDeadband();
		} catch (IOException e) {
			throw new DeviceException("IOException while trying to get the Lakeshore status", e);
		}
	}

	public void setupFromBean(CryostatParameters bean) throws DeviceException {
		// FIXME no logic here, should we set all parameters all the time??
		// not using waittime. Should I? Should this relate to ramp rate?
		setControlmode(bean.getControlMode());
		setRange(bean.getHeaterRange());
		try {
			setManualOutput(bean.getManualOutput());
		} catch (IOException e) {
			throw new DeviceException("IOException when setting manual output value!");
		}
		try {
			setpValue(bean.getP());
		} catch (IOException e) {
			throw new DeviceException("IOException when setting p value!");
		}
		try {
			setiValue(bean.getI());
		} catch (IOException e1) {
			throw new DeviceException("IOException when setting i value!");
		}
		try {
			setdValue(bean.getD());
		} catch (IOException e) {
			throw new DeviceException("IOException when setting d value!");
		}
		setTolerance(bean.getTolerance());
	}

	private void setRange(String heaterRange) throws DeviceException {
		int index = ArrayUtils.indexOf(CryostatParameters.HEATER_RANGE, heaterRange);
		if (index < 0) {
			throw new DeviceException("Heater range string not acceptable!");
		}
		try {
			setRange(new Double(index));
		} catch (IOException e) {
			throw new DeviceException("IOException when setting heater range!");
		}
	}

	private void setControlmode(String controlMode) throws DeviceException {
		int index = ArrayUtils.indexOf(CryostatParameters.CONTROL_MODE, controlMode);
		if (index < 0) {
			throw new DeviceException("Control mode string not acceptable!");
		}
		try {
			setControlmode(new Double(index));
		} catch (IOException e) {
			throw new DeviceException("IOException when setting control mode!");
		}
	}

	private boolean withinDeadband() throws DeviceException {
		try {
			Double currentValue = rawGetPosition();
			Double currentSetpoint = getSetpoint();
			return Math.abs(currentValue - currentSetpoint) < tolerance;
		} catch (IOException e) {
			throw new DeviceException("IOException while trying to get the temperature reading", e);
		}
	}

	public String getPvName() {
		return pvName;
	}

	public void setPvName(String pvName) {
		if (!pvName.endsWith(":")) {
			pvName += ":";
		}
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

	public void setSetpoint(Double setpoint) throws IOException {
		this.setpointControlPV.putWait(setpoint);
	}

	public Double getSetpoint() throws IOException {
		return setpointReadbackPV.get();
	}

	public void setRange(Double range) throws IOException {
		this.rangeControlPV.putWait(range);
	}

	public Double getRange() throws IOException {
		return rangeReadbackPV.get();
	}

	public void setControlmode(Double controlmode) throws IOException {
		this.controlmodeControlPV.putWait(controlmode);
	}

	public Double getControlmode() throws IOException {
		return controlmodeReadbackPV.get();
	}

	public void setManualOutput(Double manualOutput) throws IOException {
		this.manualOutputControlPV.putWait(manualOutput);
	}

	public Double getManualOutput() throws IOException {
		return manualOutputReadbackPV.get();
	}

	public void setpValue(Double pValue) throws IOException {
		this.pValueControlPV.putWait(pValue);
	}

	public Double getpValue() throws IOException {
		return pValueReadbackPV.get();
	}

	public void setiValue(Double iValue) throws IOException {
		this.iValueControlPV.putWait(iValue);
	}

	public Double getiValue() throws IOException {
		return iValueReadbackPV.get();
	}

	public void setdValue(Double dValue) throws IOException {
		this.dValueControlPV.putWait(dValue);
	}

	public Double getdValue() throws IOException {
		return dValueReadbackPV.get();
	}
}
