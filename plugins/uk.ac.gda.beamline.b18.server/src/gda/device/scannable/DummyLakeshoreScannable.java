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




public class DummyLakeshoreScannable extends ScannableBase {

	double Temp;
	private int tempSelect = -1;


	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		Temp = Double.parseDouble(String.valueOf(tempSelect));
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		return Temp;
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	public int getTempSelect() {
		return tempSelect;
	}

	public void setTempSelect(int tempSelect) {
		this.tempSelect = tempSelect;
	}

}
