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

import java.util.Arrays;
import java.util.Objects;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonTypeInfo;
import com.fasterxml.jackson.annotation.JsonTypeInfo.As;
import com.fasterxml.jackson.annotation.JsonTypeInfo.Id;

import gda.device.Scannable;
import gda.device.scannable.ScannableUtils;

public class SpectrumEvent {
	private int spectrumNumber;
	@JsonIgnore
	private Scannable scannable;
	private String scannableName;

    @JsonTypeInfo(use=Id.CLASS, include=As.PROPERTY, property="class", visible=true)
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



	/**
	 * Set the position of a scannable.
	 * If the position is a String it is parsed to an array of values/single value.
	 * Values are also converted from String to Double using {@link ScannableUtils#objectToDouble(Object)}
	 * if valid conversion is possible.
	 *
	 * @param position
	 */
	public void setPosition(Object position) {

		if (position instanceof String) {
			String pos = (String) position;
			String[] splitStr = pos.split("\\s+");
			if (splitStr.length == 1) {
				this.position = convertString(splitStr[0]);
			} else {
				this.position = Arrays.stream(splitStr).map(this::convertString).toArray();
			}
		} else {
			this.position = position;
		}
	}

	/**
	 * Convert string to a double using {@link ScannableUtils#objectToDouble(Object)}.
	 * If conversion is not possible, the original object is returned.
	 * @param s
	 * @return
	 */
	private Object convertString(String s) {
		Double d = ScannableUtils.objectToDouble(s);
		return d == null ? s : d;
	}

	public String getScannableName() {
		return scannableName;
	}
	public void setScannableName(String scannableName) {
		this.scannableName = scannableName;
	}

	@Override
	public String toString() {
		return String.format("Spectrum %d : %s to position %s", spectrumNumber, scannableName, position);
	}

	@Override
	public int hashCode() {
		return Objects.hash(position, scannableName, spectrumNumber);
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
		return Objects.equals(position, other.position) && Objects.equals(scannableName, other.scannableName)
				&& spectrumNumber == other.spectrumNumber;
	}
}
