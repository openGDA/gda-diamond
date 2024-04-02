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

package uk.ac.gda.beamline.i14.views.beamlinereadiness;

import java.util.Objects;

import gda.factory.FindableBase;

public class DetectorCoverParameters extends FindableBase {

	private String scannableName;
	private String detectorCoverPositionsFile;

	public String getScannableName() {
		return scannableName;
	}

	public void setScannableName(String scannableName) {
		this.scannableName = scannableName;
	}

	public String getDetectorCoverPositionsFile() {
		return detectorCoverPositionsFile;
	}

	public void setDetectorCoverPositionsFile(String detectorCoverPositionsFile) {
		this.detectorCoverPositionsFile = detectorCoverPositionsFile;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = super.hashCode();
		result = prime * result + Objects.hash(detectorCoverPositionsFile, scannableName);
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
		DetectorCoverParameters other = (DetectorCoverParameters) obj;
		return Objects.equals(detectorCoverPositionsFile, other.detectorCoverPositionsFile)
				&& Objects.equals(scannableName, other.scannableName);
	}

	@Override
	public String toString() {
		return "DetectorCoverParameters [scannableName=" + scannableName + ", detectorCoverPositionsFile="
				+ detectorCoverPositionsFile + "]";
	}
}
