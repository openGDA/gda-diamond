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
import gda.device.EnumPositioner;
import gda.device.Scannable;

public class MirrorCoating extends ScannableBase implements Scannable {

	private EnumPositioner mirror;
	private String mirrorType;
	private String pos;

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		pos = mirror.getPosition().toString();

		if (pos.equals("Chromium"))
			return "Cr";
		else if (pos.equals("Platinum"))
			return "Pt";
		else if (pos.equals("Nickel"))
			return "Ni";
		else if (pos.equals("Platinum"))
			return "Pt";

		return "Unknown";
	}

	public EnumPositioner getMirror() {
		return mirror;
	}

	public void setMirror(EnumPositioner mirror) {
		this.mirror = mirror;
	}

	public String getMirrorType() {
		return mirrorType;
	}

	public void setMirrorType(String mirrorType) {
		this.mirrorType = mirrorType;
	}

}
