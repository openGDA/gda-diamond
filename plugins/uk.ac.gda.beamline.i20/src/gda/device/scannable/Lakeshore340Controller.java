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

import java.io.IOException;

import gda.epics.LazyPVFactory;
import gda.epics.PV;
import gda.epics.ReadOnlyPV;
import uk.ac.gda.beans.exafs.i20.CryostatProperties;

public class Lakeshore340Controller implements ILakeshore340{
	private String basePvName;
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
	private ReadOnlyPV<Double> tempReadback0PV;
	private ReadOnlyPV<Double> tempReadback1PV;
	private ReadOnlyPV<Double> tempReadback2PV;
	private ReadOnlyPV<Double> tempReadback3PV;

	@Override
	public void configure() {
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
		tempReadback0PV = LazyPVFactory.newReadOnlyDoublePV(getPvName() + "KRDG0");
		tempReadback1PV = LazyPVFactory.newReadOnlyDoublePV(getPvName() + "KRDG1");
		tempReadback2PV = LazyPVFactory.newReadOnlyDoublePV(getPvName() + "KRDG2");
		tempReadback3PV = LazyPVFactory.newReadOnlyDoublePV(getPvName() + "KRDG3");
	}

	@Override
	public Double getTempReadback(int index) throws IOException {
		if (index == 0)
			return tempReadback0PV.get();
		else if (index == 1)
			return tempReadback1PV.get();
		else if (index == 2)
			return tempReadback2PV.get();
		else
			return tempReadback3PV.get();
	}

	public String getPvName() {
		return basePvName;
	}

	public void setPvName(String pvName) {
		if (!pvName.endsWith(":"))
			pvName += ":";
		this.basePvName = pvName;
	}

	@Override
	public void setSetpoint(Double setpoint) throws IOException {
		this.setpointControlPV.putWait(setpoint);
	}

	@Override
	public Double getSetpoint() throws IOException {
		return setpointReadbackPV.get();
	}

	@Override
	public void setRange(Double range) throws IOException {
		this.rangeControlPV.putWait(range);
	}

	@Override
	public Double getRange() throws IOException {
		return rangeReadbackPV.get();
	}

	@Override
	public String getRangeString() throws IOException {
		int index = (int) Math.round(getRange());
		return CryostatProperties.HEATER_RANGE[index];
	}

	@Override
	public void setControlmode(Double controlMode) throws IOException {
		this.controlmodeControlPV.putWait(controlMode);
	}

	@Override
	public Double getControlmode() throws IOException {
		return controlmodeReadbackPV.get();
	}

	@Override
	public void setManualOutput(Double manualOutput) throws IOException {
		this.manualOutputControlPV.putWait(manualOutput);
	}

	@Override
	public Double getManualOutput() throws IOException {
		return manualOutputReadbackPV.get();
	}

	@Override
	public void setpValue(Double pValue) throws IOException {
		this.pValueControlPV.putWait(pValue);
	}

	@Override
	public Double getpValue() throws IOException {
		return pValueReadbackPV.get();
	}

	@Override
	public void setiValue(Double iValue) throws IOException {
		this.iValueControlPV.putWait(iValue);
	}

	@Override
	public Double getiValue() throws IOException {
		return iValueReadbackPV.get();
	}

	@Override
	public void setdValue(Double dValue) throws IOException {
		this.dValueControlPV.putWait(dValue);
	}

	@Override
	public Double getdValue() throws IOException {
		return dValueReadbackPV.get();
	}

	@Override
	public void setSetpointControl(double setpointControl) throws IOException{
		setpointControlPV.putWait(setpointControl);
	}

}