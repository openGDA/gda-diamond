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

package gda.scan.ede.position;

import java.io.Serializable;

import org.dawnsci.ede.EdePositionType;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.Finder;

/**
 * Bean to hold the motor positions which would move the sample in or out of beam.
 */
public class ExplicitScanPositions implements Serializable, EdeScanPosition {

	private static final long serialVersionUID = 1L;

	EdePositionType type;
	Double xPosition;
	Double yPosition;
	String xMotor;
	String yMotor;
	Scannable xScannable;
	Scannable yScannable;

	public ExplicitScanPositions(EdePositionType type, Double xPosition, Double yPosition, String xMotor, String yMotor) {
		super();
		this.type = type;
		this.xPosition = xPosition;
		this.yPosition = yPosition;
		this.xMotor = xMotor;
		this.yMotor = yMotor;
	}

	public ExplicitScanPositions(EdePositionType type, Double xPosition, Double yPosition, Scannable xScannable,
			Scannable yScannable) {
		super();
		this.type = type;
		this.xPosition = xPosition;
		this.yPosition = yPosition;
		this.xScannable = xScannable;
		this.yScannable = yScannable;
	}

	@Override
	public String toString() {
		return type.toString() + " " + xMotor + ":" + xPosition + " " + yMotor + ":" + yPosition;
	}

	@Override
	public void moveIntoPosition() throws DeviceException, InterruptedException {
		if (xScannable == null) {
			xScannable = Finder.find(xMotor);
		}
		if (yScannable == null) {
			yScannable = Finder.find(yMotor);
		}
		xScannable.asynchronousMoveTo(xPosition);
		yScannable.asynchronousMoveTo(yPosition);
		xScannable.waitWhileBusy();
		yScannable.waitWhileBusy();
	}

	@Override
	public EdePositionType getType() {
		return type;
	}

	public void setType(EdePositionType type) {
		this.type = type;
	}

	public Double getxPosition() {
		return xPosition;
	}

	public void setxPosition(Double xPosition) {
		this.xPosition = xPosition;
	}

	public Double getyPosition() {
		return yPosition;
	}

	public void setyPosition(Double yPosition) {
		this.yPosition = yPosition;
	}

	public String getxMotor() {
		return xMotor;
	}

	public void setxMotor(String xMotor) {
		this.xMotor = xMotor;
	}

	public String getyMotor() {
		return yMotor;
	}

	public void setyMotor(String yMotor) {
		this.yMotor = yMotor;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((type == null) ? 0 : type.hashCode());
		result = prime * result + ((xMotor == null) ? 0 : xMotor.hashCode());
		result = prime * result + ((xPosition == null) ? 0 : xPosition.hashCode());
		result = prime * result + ((yMotor == null) ? 0 : yMotor.hashCode());
		result = prime * result + ((yPosition == null) ? 0 : yPosition.hashCode());
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj) {
			return true;
		}
		if (obj == null) {
			return false;
		}
		if (getClass() != obj.getClass()) {
			return false;
		}
		ExplicitScanPositions other = (ExplicitScanPositions) obj;
		if (type != other.type) {
			return false;
		}
		if (xMotor == null) {
			if (other.xMotor != null) {
				return false;
			}
		} else if (!xMotor.equals(other.xMotor)) {
			return false;
		}
		if (xPosition == null) {
			if (other.xPosition != null) {
				return false;
			}
		} else if (!xPosition.equals(other.xPosition)) {
			return false;
		}
		if (yMotor == null) {
			if (other.yMotor != null) {
				return false;
			}
		} else if (!yMotor.equals(other.yMotor)) {
			return false;
		}
		if (yPosition == null) {
			if (other.yPosition != null) {
				return false;
			}
		} else if (!yPosition.equals(other.yPosition)) {
			return false;
		}
		return true;
	}

	@Override
	public double getTimeToMove() {
		// TODO Auto-generated method stub
		return 0;
	}
}
