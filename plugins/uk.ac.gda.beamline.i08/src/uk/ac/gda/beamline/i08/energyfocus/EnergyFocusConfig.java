/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i08.energyfocus;

import java.io.Serializable;

import org.eclipse.scanning.api.annotation.ui.FieldDescriptor;

public class EnergyFocusConfig implements Serializable {

	private static final long serialVersionUID = 1L;

	@FieldDescriptor(hint = "Slope dividend")
	private String slopeDividend;

	@FieldDescriptor(hint = "Intercept")
	private String interception;

	@FieldDescriptor(hint = "Slope divisor")
	private String slopeDivisor;

	public EnergyFocusConfig() {
	}

	public EnergyFocusConfig(String slopeDividend, String interception, String slopeDivisor) {
		super();
		this.slopeDividend = slopeDividend;
		this.interception = interception;
		this.slopeDivisor = slopeDivisor;
	}

	public String getSlopeDividend() {
		return slopeDividend;
	}
	public void setSlopeDividend(String slopeDividend) {
		this.slopeDividend = slopeDividend;
	}
	public String getInterception() {
		return interception;
	}
	public void setInterception(String interception) {
		this.interception = interception;
	}
	public String getSlopeDivisor() {
		return slopeDivisor;
	}
	public void setSlopeDivisor(String slopeDivisor) {
		this.slopeDivisor = slopeDivisor;
	}
	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((slopeDividend == null) ? 0 : slopeDividend.hashCode());
		result = prime * result + ((interception == null) ? 0 : interception.hashCode());
		result = prime * result + ((slopeDivisor == null) ? 0 : slopeDivisor.hashCode());
		return result;
	}
	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		EnergyFocusConfig other = (EnergyFocusConfig) obj;
		if (slopeDividend == null) {
			if (other.slopeDividend != null)
				return false;
		} else if (!slopeDividend.equals(other.slopeDividend))
			return false;
		if (interception == null) {
			if (other.interception != null)
				return false;
		} else if (!interception.equals(other.interception))
			return false;
		if (slopeDivisor == null) {
			if (other.slopeDivisor != null)
				return false;
		} else if (!slopeDivisor.equals(other.slopeDivisor))
			return false;
		return true;
	}
	@Override
	public String toString() {
		return "EnergyFocusConfig [slopeDividend=" + slopeDividend + ", interception=" + interception
				+ ", slopeDivisor=" + slopeDivisor + "]";
	}
}
