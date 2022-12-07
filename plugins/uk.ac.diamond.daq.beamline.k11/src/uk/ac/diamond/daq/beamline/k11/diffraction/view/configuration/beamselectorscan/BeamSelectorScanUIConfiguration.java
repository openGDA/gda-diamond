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

import java.util.Map;
import java.util.Objects;

import gda.factory.FindableBase;

/**
 * Used to inject scan and scannable names into {@link BeamSelectorScanControls}
 */
public class BeamSelectorScanUIConfiguration extends FindableBase {

	private String xAxisName;
	private String yAxisName;
	private String imagingHintScannableName;
	private Map<String, String> imagingBeamToMalcolmScanId;
	private String imagingDetectorId;
	private String diffractionDetectorId;

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
	 * Name of scannable which reports the Imaging configuration (mono/pink) which is currently set up
	 */
	public String getImagingHintScannableName() {
		return imagingHintScannableName;
	}

	public void setImagingHintScannableName(String imagingHintScannableName) {
		this.imagingHintScannableName = imagingHintScannableName;
	}

	public Map<String, String> getImagingBeamToMalcolmScanId() {
		return imagingBeamToMalcolmScanId;
	}

	public void setImagingBeamToMalcolmScanId(Map<String, String> imagingBeamToMalcolmScanId) {
		this.imagingBeamToMalcolmScanId = imagingBeamToMalcolmScanId;
	}

	public String getImagingDetectorId() {
		return imagingDetectorId;
	}

	public void setImagingDetectorId(String imagingDetectorName) {
		this.imagingDetectorId = imagingDetectorName;
	}

	public String getDiffractionDetectorId() {
		return diffractionDetectorId;
	}

	public void setDiffractionDetectorId(String diffractionDetectorName) {
		this.diffractionDetectorId = diffractionDetectorName;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = super.hashCode();
		result = prime * result + Objects.hash(diffractionDetectorId, imagingBeamToMalcolmScanId, imagingDetectorId,
				imagingHintScannableName, xAxisName, yAxisName);
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
		return Objects.equals(diffractionDetectorId, other.diffractionDetectorId)
				&& Objects.equals(imagingBeamToMalcolmScanId, other.imagingBeamToMalcolmScanId)
				&& Objects.equals(imagingDetectorId, other.imagingDetectorId)
				&& Objects.equals(imagingHintScannableName, other.imagingHintScannableName)
				&& Objects.equals(xAxisName, other.xAxisName) && Objects.equals(yAxisName, other.yAxisName);
	}

}
