/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.beamselectorscan;

import gda.factory.FindableBase;

/**
 * Used to inject scan and scannable names into {@link BeamSelectorScanControls}
 */
public class BeamSelectorScanUIConfiguration extends FindableBase {

	private String xAxisName;
	private String yAxisName;
	private String monoImagingScan;
	private String pinkImagingScan;

	/**
	 * The name of the X mapping axis
	 */
	public String getxAxisName() {
		return xAxisName;
	}

	public void setxAxisName(String xAxisName) {
		this.xAxisName = xAxisName;
	}

	/**
	 * The name of the Y mapping axis
	 */
	public String getyAxisName() {
		return yAxisName;
	}

	public void setyAxisName(String yAxisName) {
		this.yAxisName = yAxisName;
	}

	/**
	 * The scan ID for monochromatic imaging beam
	 */
	public String getMonoImagingScan() {
		return monoImagingScan;
	}

	public void setMonoImagingScan(String monoImagingScan) {
		this.monoImagingScan = monoImagingScan;
	}

	/**
	 * The scan ID for polychromatic (or 'pink') imaging beam
	 */
	public String getPinkImagingScan() {
		return pinkImagingScan;
	}

	public void setPinkImagingScan(String pinkImagingScan) {
		this.pinkImagingScan = pinkImagingScan;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = super.hashCode();
		result = prime * result + ((monoImagingScan == null) ? 0 : monoImagingScan.hashCode());
		result = prime * result + ((pinkImagingScan == null) ? 0 : pinkImagingScan.hashCode());
		result = prime * result + ((xAxisName == null) ? 0 : xAxisName.hashCode());
		result = prime * result + ((yAxisName == null) ? 0 : yAxisName.hashCode());
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (!super.equals(obj))
			return false;
		if (getClass() != obj.getClass())
			return false;
		BeamSelectorScanUIConfiguration other = (BeamSelectorScanUIConfiguration) obj;
		if (monoImagingScan == null) {
			if (other.monoImagingScan != null)
				return false;
		} else if (!monoImagingScan.equals(other.monoImagingScan))
			return false;
		if (pinkImagingScan == null) {
			if (other.pinkImagingScan != null)
				return false;
		} else if (!pinkImagingScan.equals(other.pinkImagingScan))
			return false;
		if (xAxisName == null) {
			if (other.xAxisName != null)
				return false;
		} else if (!xAxisName.equals(other.xAxisName))
			return false;
		if (yAxisName == null) {
			if (other.yAxisName != null)
				return false;
		} else if (!yAxisName.equals(other.yAxisName))
			return false;
		return true;
	}

}
