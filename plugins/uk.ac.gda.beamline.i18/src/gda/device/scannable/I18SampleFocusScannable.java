/*-
 * Copyright © 2015 Diamond Light Source Ltd.
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

/**
 * For moving the sample along the z-axis whilst preventing it shifting in x.
 * <p>
 * As I18 samples are held at 45deg to the beam so that the fluorescence detectors can see more sample then when the
 * sample is moved in z to change the focus it causes a small shift in x. So when changing the sample along the z-axis
 * during experiment setup this Scannable should be operated instead of the z motor.
 * <p>
 * So this reports the z-position, but when moved it also makes adjustments to the x motor position.
 */
public class I18SampleFocusScannable extends ScannableMotionUnitsBase {

	private Scannable xScannable;
	private Scannable zScannable;
	private boolean reverseXDirection = false;

	public I18SampleFocusScannable() {
	}

	@Override
	public void asynchronousMoveTo(Object externalPosition) throws DeviceException {

		double targetZ = ScannableUtils.objectToArray(externalPosition)[0];

		double currentXPosition = (double) xScannable.getPosition();  // assume x is always a single value motor
		double currentZPosition = (double) zScannable.getPosition();  // assume z is always a single value motor

		double deltaZ = targetZ - currentZPosition;

		double deltaX = deltaZ * 0.707;
		if (reverseXDirection){
			deltaX *= -1;
		}
		double targetX = currentXPosition + deltaX;

		xScannable.asynchronousMoveTo(targetX);
		zScannable.asynchronousMoveTo(targetZ);
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return zScannable.isBusy() || xScannable.isBusy();
	}

	@Override
	public Object getPosition() throws DeviceException {
		return zScannable.getPosition();
	}

	@Override
	public String[] getInputNames() {
		return zScannable.getInputNames();
	}

	@Override
	public String[] getExtraNames() {
		return zScannable.getExtraNames();
	}

	@Override
	public String[] getOutputFormat() {
		return zScannable.getOutputFormat();
	}

	@Override
	public String toString() {
		return zScannable.toString();
	}

	public Scannable getxScannable() {
		return xScannable;
	}

	public void setxScannable(Scannable xScannable) {
		this.xScannable = xScannable;
	}

	public Scannable getzScannable() {
		return zScannable;
	}

	public void setzScannable(Scannable zScannable) {
		this.zScannable = zScannable;
	}

	public boolean isReverseXDirection() {
		return reverseXDirection;
	}

	public void setReverseXDirection(boolean reverseXDirection) {
		this.reverseXDirection = reverseXDirection;
	}

}
