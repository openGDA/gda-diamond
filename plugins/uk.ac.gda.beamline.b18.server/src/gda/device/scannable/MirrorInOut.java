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
import gda.device.Motor;

public class MirrorInOut extends ScannableBase {

	private Motor mirror;
	private double pos;

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	@Override
	public Object rawGetPosition() {
		this.inputNames = new String[]{getName()};

		try {
			pos = mirror.getPosition();
		} catch (NumberFormatException e) {
			e.printStackTrace();
		} catch (DeviceException e) {
			e.printStackTrace();
		}

		if (pos<0)
			return "in";
		else if (pos>=0)
			return "out";

		return "";
	}

	public Motor getMirror() {
		return mirror;
	}

	public void setMirror(Motor mirror) {
		this.mirror = mirror;
	}
}
