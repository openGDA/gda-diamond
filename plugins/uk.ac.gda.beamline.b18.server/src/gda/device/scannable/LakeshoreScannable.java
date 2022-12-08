/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

import java.util.List;

import gda.device.DeviceException;
import gda.epics.CAClient;

public class LakeshoreScannable extends ScannableBase {

	private CAClient ca_client = new CAClient();

	private String temp0Pv;
	private String temp1Pv;
	private String temp2Pv;
	private String temp3Pv;
	private String setPointSetPv;
	private String inputPv;
	private int tempSelect=-1;
	private List<Integer> temps;

	@SuppressWarnings("unchecked")
	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		List<Object> parameters = (List<Object>) position;
		double temp = (Double) parameters.get(1);

		temps = (List<Integer>) parameters.get(0);

		try {
			if (temps != null) {
				if (temps.contains(0))
					ca_client.caput(inputPv, 1);
				else if (temps.contains(1))
					ca_client.caput(inputPv, 2);
				else if (temps.contains(2))
					ca_client.caput(inputPv, 3);
				else if (temps.contains(3))
					ca_client.caput(inputPv, 4);
			}
			ca_client.caput(setPointSetPv, temp);
		} catch (Exception e) {
			if( e instanceof DeviceException)
				throw (DeviceException)e;
			throw new DeviceException(getName() +" exception in rawAsynchronousMoveTo", e);
		}
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		try {
			String output = "";
			output = ca_client.caget(temp0Pv);
			if (temps != null) {
				if (temps.contains(0))
					output = ca_client.caget(temp0Pv);
				else if (temps.contains(1))
					output = ca_client.caget(temp1Pv);
				else if (temps.contains(2))
					output = ca_client.caget(temp2Pv);
				else if (temps.contains(3))
					output = ca_client.caget(temp3Pv);
			}
			else if(tempSelect==0)
				output = ca_client.caget(temp0Pv);
			else if(tempSelect==1)
				output = ca_client.caget(temp1Pv);
			else if(tempSelect==2)
				output = ca_client.caget(temp2Pv);
			else if(tempSelect==3)
				output = ca_client.caget(temp3Pv);

			return Double.parseDouble(output);
		} catch (Exception e) {
			if( e instanceof DeviceException)
				throw (DeviceException)e;
			throw new DeviceException(getName() +" exception in rawGetPosition", e);
		}
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	public String getTemp0Pv() {
		return temp0Pv;
	}

	public void setTemp0Pv(String temp0Pv) {
		this.temp0Pv = temp0Pv;
	}

	public String getTemp1Pv() {
		return temp1Pv;
	}

	public void setTemp1Pv(String temp1Pv) {
		this.temp1Pv = temp1Pv;
	}

	public String getTemp2Pv() {
		return temp2Pv;
	}

	public void setTemp2Pv(String temp2Pv) {
		this.temp2Pv = temp2Pv;
	}

	public String getTemp3Pv() {
		return temp3Pv;
	}

	public void setTemp3Pv(String temp3Pv) {
		this.temp3Pv = temp3Pv;
	}

	public String getSetPointSetPv() {
		return setPointSetPv;
	}

	public void setSetPointSetPv(String setPointSetPv) {
		this.setPointSetPv = setPointSetPv;
	}

	public String getInputPv() {
		return inputPv;
	}

	public void setInputPv(String inputPv) {
		this.inputPv = inputPv;
	}

	public int getTempSelect() {
		return tempSelect;
	}

	public void setTempSelect(int tempSelect) {
		this.tempSelect = tempSelect;
	}

}
