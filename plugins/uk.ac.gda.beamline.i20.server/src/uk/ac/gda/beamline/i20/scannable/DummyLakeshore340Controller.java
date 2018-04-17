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

package uk.ac.gda.beamline.i20.scannable;

import java.io.IOException;

public class DummyLakeshore340Controller  implements ILakeshore340{

	private double range = 0;
	private double p = 0;
	private double i = 0;
	private double d = 0;
	private double setpoint = 0;
	private double setpointControl = 0;
	private double controlMode = 0;
	private double manualOutput = 0;
	private double tempReadback = 0;

	@Override
	public void configure() {
		// TODO Auto-generated method stub

	}

	@Override
	public Double getTempReadback(int index) throws IOException {
		return tempReadback;
	}

	@Override
	public void setSetpoint(Double setpoint) throws IOException {
		this.setpoint = setpoint;
	}

	@Override
	public Double getSetpoint() throws IOException {
		return setpointControl;
	}

	@Override
	public void setRange(Double range) throws IOException {
		this.range = range;
	}

	@Override
	public Double getRange() throws IOException {
		return range;
	}

	@Override
	public String getRangeString() throws IOException {
		return "";
	}

	@Override
	public void setControlmode(Double controlMode) throws IOException {
		this.controlMode = controlMode;

	}

	@Override
	public Double getControlmode() throws IOException {
		return controlMode;
	}

	@Override
	public void setManualOutput(Double manualOutput) throws IOException {
		this.manualOutput = manualOutput;

	}

	@Override
	public Double getManualOutput() throws IOException {
		return manualOutput;
	}

	@Override
	public void setpValue(Double pValue) throws IOException {
		this.p = pValue;
	}

	@Override
	public Double getpValue() throws IOException {
		return p;
	}

	@Override
	public void setiValue(Double iValue) throws IOException {
		this.i = iValue;
	}

	@Override
	public Double getiValue() throws IOException {
		return i;
	}

	@Override
	public void setdValue(Double dValue) throws IOException {
		this.d = dValue;
	}

	@Override
	public Double getdValue() throws IOException {
		return d;
	}

	@Override
	public void setSetpointControl(double setpointControl) throws IOException {
		this.setpointControl = setpointControl;
		this.setpoint = setpoint;
		while(tempReadback<setpointControl){
			tempReadback+=0.01;
			try {
				Thread.sleep(50);
			} catch (InterruptedException e) {

			}
		}

	}

}