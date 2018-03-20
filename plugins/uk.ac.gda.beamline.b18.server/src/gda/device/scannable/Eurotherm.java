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

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.epics.CAClient;
import gov.aps.jca.CAException;
import gov.aps.jca.TimeoutException;

public class Eurotherm extends ScannableBase implements Scannable {

	private CAClient ca_client = new CAClient();

	private String setpoint_pv;
	private String readback_pv;
	private String upper_limit_pv;

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		try {
			ca_client.caput(setpoint_pv, String.valueOf(position));
		} catch (Exception e) {
			if( e instanceof DeviceException)
				throw (DeviceException)e;
			throw new DeviceException(getName() +" exception in rawAsynchronousMoveTo", e);
		}
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		try {
			return Double.parseDouble(ca_client.caget(readback_pv));
		} catch (Exception e) {
			if( e instanceof DeviceException)
				throw (DeviceException)e;
			throw new DeviceException(getName() +" exception in rawGetPosition", e);
		}
	}

	public String getSetpoint_pv() {
		return setpoint_pv;
	}

	public void setSetpoint_pv(String setpointPv) {
		setpoint_pv = setpointPv;
	}

	public String getReadback_pv() {
		return readback_pv;
	}

	public void setReadback_pv(String readbackPv) {
		readback_pv = readbackPv;
	}

	public String getUpperLimit() throws CAException, TimeoutException, InterruptedException{
		return ca_client.caget(upper_limit_pv);
	}

	public void setUpper_limit_pv(String upperLimitPv) {
		upper_limit_pv = upperLimitPv;
	}

	public String getLowerLimit() {
		return "0.0";
	}




}
