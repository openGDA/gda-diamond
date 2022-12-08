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

package uk.ac.gda.exafs.data;

import uk.ac.gda.common.rcp.PreferenceDataStore;

public enum EdeDataStore {
	INSTANCE;

	private static final String EDE_DATA_PERFERENCES = "uk.ac.gda.beamline.i20_1";
	private final PreferenceDataStore preferenceDataStore;

	private EdeDataStore() {
		preferenceDataStore = new PreferenceDataStore(EDE_DATA_PERFERENCES);

	}

	public PreferenceDataStore getPreferenceDataStore() {
		return preferenceDataStore;
	}
}