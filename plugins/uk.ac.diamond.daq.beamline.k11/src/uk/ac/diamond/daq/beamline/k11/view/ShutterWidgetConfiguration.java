/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.view;

import java.util.Map;
import java.util.Objects;

import gda.factory.FindableBase;

public class ShutterWidgetConfiguration extends FindableBase {

	/**
	 * Name of scannable to be retrieved via Finder
	 */
	private String shutterScannableName;

	/**
	 * User-friendly shutter name to display in UI
	 */
	private String shutterDisplayName;

	/**
	 * Keys: Names of scannables returning boolean types indicating
	 * whether the shutter is available.
	 *
	 * Values: User-friendly messages explaining a {@code false} position
	 */
	private Map<String, String> enablingScannableNamesAndMessages;

	public String getShutterName() {
		return shutterScannableName;
	}

	public void setShutterName(String shutterName) {
		this.shutterScannableName = shutterName;
	}

	public String getShutterDisplayName() {
		return shutterDisplayName;
	}

	public void setShutterDisplayName(String shutterDisplayName) {
		this.shutterDisplayName = shutterDisplayName;
	}

	public Map<String, String> getEnablingScannableNamesAndMessages() {
		return enablingScannableNamesAndMessages;
	}

	public void setEnablingScannableNamesAndMessages(Map<String, String> enablingScannableToMessageMap) {
		this.enablingScannableNamesAndMessages = enablingScannableToMessageMap;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = super.hashCode();
		result = prime * result
				+ Objects.hash(enablingScannableNamesAndMessages, shutterDisplayName, shutterScannableName);
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
		ShutterWidgetConfiguration other = (ShutterWidgetConfiguration) obj;
		return Objects.equals(enablingScannableNamesAndMessages, other.enablingScannableNamesAndMessages)
				&& Objects.equals(shutterDisplayName, other.shutterDisplayName)
				&& Objects.equals(shutterScannableName, other.shutterScannableName);
	}

}
