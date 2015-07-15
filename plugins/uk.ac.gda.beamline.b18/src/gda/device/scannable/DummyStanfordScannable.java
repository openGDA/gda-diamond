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

import gda.device.Scannable;

public class DummyStanfordScannable extends ScannableBase implements Scannable{
	String value;
	String unit;
	String sensitivity;

	@Override
	public void rawAsynchronousMoveTo(Object position){
		sensitivity = String.valueOf(position);
		value = sensitivity.substring(0, sensitivity.indexOf(" "));
		unit = sensitivity.substring(sensitivity.indexOf(" ")+1);
	}

	@Override
	public Object rawGetPosition(){
		return value + " " + unit;
	}

	@Override
	public boolean isBusy(){
		return false;
	}
}
