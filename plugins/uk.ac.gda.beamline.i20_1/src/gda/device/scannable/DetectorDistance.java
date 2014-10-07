/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

public class DetectorDistance extends ScannableBase {

	private ScannableMotor detectorZ;
	private ScannableMotor sampleZ;

	@Override
	public void asynchronousMoveTo(Object externalPosition) throws DeviceException {
		super.asynchronousMoveTo((double) externalPosition + (double) sampleZ.getPosition());
	}

	@Override
	public Object getPosition() throws DeviceException {
		return (double) detectorZ.getPosition() - (double) sampleZ.getPosition();
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return detectorZ.isBusy() || sampleZ.isBusy();
	}

	public Scannable getDetectorZ() {
		return detectorZ;
	}

	public void setDetectorZ(ScannableMotor detectorZ) {
		this.detectorZ = detectorZ;
	}

	public Scannable getSampleZ() {
		return sampleZ;
	}

	public void setSampleZ(ScannableMotor sampleZ) {
		this.sampleZ = sampleZ;
	}

}
