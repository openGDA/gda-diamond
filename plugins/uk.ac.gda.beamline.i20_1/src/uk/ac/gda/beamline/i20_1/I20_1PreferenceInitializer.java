/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i20_1;

import org.eclipse.core.runtime.preferences.AbstractPreferenceInitializer;
import org.eclipse.jface.preference.IPreferenceStore;

public class I20_1PreferenceInitializer extends AbstractPreferenceInitializer {

	public static final String REFRESHRATE = "uk.ac.gda.beamline.i20_1.refreshrate.preference";
	public static final String SNAPSHOTTIME = "uk.ac.gda.beamline.i20_1.snapshottime.preference";
	public static final String SCANSPERFRAME = "uk.ac.gda.beamline.i20_1.scansperframe.preference";
	public static final String VERTICALBINNING = "uk.ac.gda.beamline.i20_1.verticalbinning.preference";
	public static final String CCDLINEBEGIN = "uk.ac.gda.beamline.i20_1.ccdlinebegin.preference";
	public static String LIVEMODETIME = "uk.ac.gda.beamline.i20_1.livemodetime.preference";
	public static final String LIVEMODESCANSPERFRAME = "uk.ac.gda.beamline.i20_1.livemodescansperframe.preference";
	public static final String LIVEMODESHOWI0IT = "uk.ac.gda.beamline.i20_1.livemodeshowi0it.preference";

	public I20_1PreferenceInitializer() {
	}

	@Override
	public void initializeDefaultPreferences() {
		IPreferenceStore store = Activator.getDefault().getPreferenceStore();
		store.setDefault(REFRESHRATE, 1);
		store.setDefault(SNAPSHOTTIME, 1);
		store.setDefault(SCANSPERFRAME, 1);
		store.setDefault(LIVEMODETIME, 1);
		store.setDefault(VERTICALBINNING, 1);
		store.setDefault(CCDLINEBEGIN, 0);
		store.setDefault(LIVEMODESCANSPERFRAME, 1);
		store.setDefault(LIVEMODESHOWI0IT, false);

	}

}

