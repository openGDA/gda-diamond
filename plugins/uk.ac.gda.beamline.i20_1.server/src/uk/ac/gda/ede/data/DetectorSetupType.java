/*-
 * Copyright © 2016 Diamond Light Source Ltd.
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

package uk.ac.gda.ede.data;
/**
 * Enum of available detector types
 * Refactored from DetectorModel class
 * @since 27/1/2016
 */
public enum DetectorSetupType {
	NOT_SET("not_set"), XH("xh"), XSTRIP("xstrip"), FRELON("frelon");
	private final String detectorName;

	private DetectorSetupType(String detectorName) {
		this.detectorName = detectorName;
	}

	public String getDetectorName() {
		return detectorName;
	}
}
