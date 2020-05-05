/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

package gda.scan;

import gda.device.Scannable;

public class SpectrumEvent {
	private int spectrumNumber;
	private transient Scannable scannable;
	private String scannableName;
	private Object position;

	public SpectrumEvent() {
	}

	public SpectrumEvent(SpectrumEvent event) {
		this.spectrumNumber = event.spectrumNumber;
		this.scannable = event.scannable;
		this.position = event.position;
		scannableName = event.scannableName;
	}
	public SpectrumEvent(int spectrumNumber, Scannable scannable, Object position) {
		this.spectrumNumber = spectrumNumber;
		this.scannable = scannable;
		this.position = position;
		scannableName = scannable.getName();
	}

	public SpectrumEvent(int spectrumNumber, String scannableName, Object position) {
		this.spectrumNumber = spectrumNumber;
		this.scannableName = scannableName;
		this.position = position;
	}

	public int getSpectrumNumber() {
		return spectrumNumber;
	}
	public void setSpectrumNumber(int spectrumNumber) {
		this.spectrumNumber = spectrumNumber;
	}

	public Scannable getScannable() {
		return scannable;
	}

	public Object getPosition() {
		return position;
	}
	public void setPosition(Object position) {
		this.position = position;
	}

	public String getScannableName() {
		return scannableName;
	}
	public void setScannableName(String scannableName) {
		this.scannableName = scannableName;
	}

	@Override
	public String toString() {
		return String.format("Spectrum %d : %s to position %s", spectrumNumber, scannable.getName(), position);
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		SpectrumEvent other = (SpectrumEvent) obj;
		if (position == null) {
			if (other.position != null)
				return false;
		} else if (!position.equals(other.position))
			return false;
		if (scannable == null) {
			if (other.scannable != null)
				return false;
		} else if (!scannable.getName().equals(other.scannable.getName()))
			return false;
		return spectrumNumber == other.spectrumNumber;
	}
}
