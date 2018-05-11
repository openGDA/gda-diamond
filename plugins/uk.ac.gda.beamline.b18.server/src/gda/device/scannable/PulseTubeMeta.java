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
import gda.epics.CAClient;

public class PulseTubeMeta extends ScannableBase {

	private CAClient ca_client = new CAClient();

	private String readback_pv = "BL18B-EA-TEMPC-03:STEMP";

	@Override
	public boolean isBusy() throws DeviceException {
		// TODO Auto-generated method stub
		return false;
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




}
