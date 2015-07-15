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

public class StanfordScannable extends ScannableBase implements Scannable{

	private CAClient ca_client = new CAClient();

	private String base_pv;

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
			ca_client.caput(base_pv+"SENS:SEL1", value);
			ca_client.caput(base_pv+"SENS:SEL2", unit);
		} catch (Exception e) {
			if( e instanceof DeviceException)
				throw (DeviceException)e;
			throw new DeviceException(getName() +" exception in rawAsynchronousMoveTo", e);
		}
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		this.inputNames = new String[]{getName()};
		try {
			return ca_client.caget(base_pv+"SENS:SEL1") + " " + ca_client.caget(base_pv+"SENS:SEL2");
		} catch (Exception e) {
			if( e instanceof DeviceException)
				throw (DeviceException)e;
			throw new DeviceException(getName() +" exception in rawGetPosition", e);
		}
	}

	public int getSensitivity() throws NumberFormatException, CAException, TimeoutException, InterruptedException{
		return Integer.parseInt(ca_client.caget(base_pv+"SENS:SEL1"));
	}

	public int getUnit() throws NumberFormatException, CAException, TimeoutException, InterruptedException{
		return Integer.parseInt(ca_client.caget(base_pv+"SENS:SEL2"));
	}

	public int isOn() throws NumberFormatException, CAException, TimeoutException, InterruptedException{
		return Integer.parseInt(ca_client.caget(base_pv+"IOON"));
	}

	public int getOffset() throws NumberFormatException, CAException, TimeoutException, InterruptedException{
		return Integer.parseInt(ca_client.caget(base_pv+"IOLV:SEL1"));
	}

	public int getOffsetUnit() throws NumberFormatException, CAException, TimeoutException, InterruptedException{
		return Integer.parseInt(ca_client.caget(base_pv+"IOLV:SEL2"));
	}

	public void setSensitivity(int sensitivity) throws CAException, InterruptedException{
		ca_client.caput(base_pv+"SENS:SEL1",sensitivity );
	}

	public void setUnit(int unit) throws CAException, InterruptedException{
		ca_client.caput(base_pv+"SENS:SEL2",unit );
	}

	public void setOn(int on) throws CAException, InterruptedException{
		ca_client.caput(base_pv+"IOON",on );
	}

	public void setOffset(int offset) throws CAException, InterruptedException{
		ca_client.caput(base_pv+"IOLV:SEL1",offset );
	}

	public void setOffsetUnit(int unit) throws CAException, InterruptedException{
		ca_client.caput(base_pv+"IOLV:SEL2",unit );
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	public void setBase_pv(String basePv) {
		base_pv = basePv;
	}
}
