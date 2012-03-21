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

public class StanfordScannable extends ScannableBase implements Scannable{
	
	private CAClient ca_client = new CAClient();
	
	private String value_pv;
	private String unit_pv;
	
	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		
		//"pA/V"
		//"nA/V"
		//"\u03BCA/V"
		//"1 mA/V");
		
		//"1 "
		//"2 "
		//"5 "
		//"10 "
		//"20 "
		//"50 "
		//"100 "
		//"200 "
		//"500 "
		
		String sensitivity = String.valueOf(position);
		String value = sensitivity.substring(0, sensitivity.indexOf(" "));
		String unit = sensitivity.substring(sensitivity.indexOf(" ")+1);
		
		try {
			ca_client.caput(value_pv, value);
			ca_client.caput(unit_pv, unit);
		} catch (Exception e) {
			if( e instanceof DeviceException)
				throw (DeviceException)e;
			throw new DeviceException(getName() +" exception in rawAsynchronousMoveTo", e);
		}
	}
	
	@Override
	public Object rawGetPosition() throws DeviceException {
		try {
			return ca_client.caget(value_pv) + " " + ca_client.caget(unit_pv);
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

	public String getValue_pv() {
		return value_pv;
	}

	public void setValue_pv(String sensitivityPv) {
		value_pv = sensitivityPv;
	}

	public String getUnit_pv() {
		return unit_pv;
	}

	public void setUnit_pv(String unitPv) {
		unit_pv = unitPv;
	}
}
