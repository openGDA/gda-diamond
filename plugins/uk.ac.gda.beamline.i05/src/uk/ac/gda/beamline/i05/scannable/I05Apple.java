/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i05.scannable;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableMotionBase;

public class I05Apple extends ScannableMotionBase {
	
	Scannable gapScannable;
	Scannable phaseScannable;
	
	@Override
	public Object getPosition() throws DeviceException {
		return null;
	}

	public String getPolaristation() throws DeviceException {
		return "wrong";
	}
	public void setPolaristation(String newpol) throws DeviceException {
	
	}
	public double getEnergy() throws DeviceException {
		return -1;
	}
	public void setEnergy(double neweng) throws DeviceException {
		
	}

	public Scannable getGapScannable() {
		return gapScannable;
	}

	public void setGapScannable(Scannable gapScannable) {
		this.gapScannable = gapScannable;
	}

	public Scannable getPhaseScannable() {
		return phaseScannable;
	}

	public void setPhaseScannable(Scannable phaseScannable) {
		this.phaseScannable = phaseScannable;
	}
}
