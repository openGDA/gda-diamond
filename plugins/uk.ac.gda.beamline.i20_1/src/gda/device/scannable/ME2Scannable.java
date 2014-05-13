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

package gda.device.scannable;

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.enumpositioner.EnumPositionerBase;

public class ME2Scannable extends EnumPositionerBase {

	public enum Positions {
		Rhodium, Silicon, out
	}

	private EnumPositioner stripeScannable;
	private ScannableMotor yScannable;
	private Double yInPosition = 0.0;
	private Double yOutPosition = 0.0;

	public ME2Scannable() {
		setPositions(new String[] { Positions.Rhodium.toString(), Positions.Silicon.toString(),
				Positions.out.toString() });
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return stripeScannable.isBusy() && yScannable.isBusy();
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {

		Positions targetPosition = Positions.valueOf(position.toString());

		switch (targetPosition) {
		case Rhodium:
			stripeScannable.asynchronousMoveTo(Positions.Rhodium.toString());
			yScannable.asynchronousMoveTo(yInPosition);
			break;
		case Silicon:
			stripeScannable.asynchronousMoveTo(Positions.Silicon.toString());
			yScannable.asynchronousMoveTo(yInPosition);
			break;
		case out:
			yScannable.asynchronousMoveTo(yOutPosition);
			break;
		}
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		Double currentYPosition = Double.parseDouble(yScannable.getPosition().toString());
		String currentStripePosition = stripeScannable.getPosition().toString();
		if (currentYPosition > yOutPosition - 0.1 && currentYPosition < yOutPosition + 0.1) {
			return Positions.out.toString();
		} else if (currentYPosition > yInPosition - 0.1 && currentYPosition < yInPosition + 0.1) {
			return currentStripePosition;
		}
		return "unknown";
	}

	public EnumPositioner getStripeScannable() {
		return stripeScannable;
	}

	public void setStripeScannable(EnumPositioner stripeScannable) {
		this.stripeScannable = stripeScannable;
	}

	public ScannableMotor getyScannable() {
		return yScannable;
	}

	public void setyScannable(ScannableMotor yScannable) {
		this.yScannable = yScannable;
	}

	public Double getyInPosition() {
		return yInPosition;
	}

	public void setyInPosition(Double yInPosition) {
		this.yInPosition = yInPosition;
	}

	public Double getyOutPosition() {
		return yOutPosition;
	}

	public void setyOutPosition(Double yOutPosition) {
		this.yOutPosition = yOutPosition;
	}

}
