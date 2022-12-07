/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i20;

import org.eclipse.core.runtime.preferences.InstanceScope;
import org.eclipse.e4.ui.workbench.lifecycle.PostContextCreate;
import org.osgi.service.prefs.BackingStoreException;
import org.osgi.service.prefs.Preferences;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class I20Startup {
	private static final Logger logger = LoggerFactory.getLogger(I20Startup.class);
	private static final String XES_PREFERENCE_IS_SET = "xes_preference_is_set";
	private static final String SHOW_INTRO = "showIntro.Preference";

	/**
	 * Display a dialog box to allow user to select XES/XAS experiment mode.
	 * THis is displayed when client started up for the first time by a new new user.
	 * and after workspace settings have been cleared (e.g. client started with --reset)
	 */
	@PostContextCreate
	private void startup() {

		// Lookup the 'show intro' preference from plugin customization -
		// if it's set to false, return immediately and don't show the intro dialog.
		boolean showIntroPref = I20BeamlineActivator.getDefault().getPreferenceStore().getBoolean(SHOW_INTRO);
		if (!showIntroPref) {
			return;
		}

		// Get preference to see if XES/XAS experiment mode has been set.
		Preferences preferences = getPreferences();
		String xesPreferenceIsSet = preferences.get(XES_PREFERENCE_IS_SET, Boolean.FALSE.toString());
		logger.debug("XES preference has been set ? {}", xesPreferenceIsSet);

		// Open dialog box to allow user to select XES/XAS experiment mode
		if (!Boolean.parseBoolean(xesPreferenceIsSet)) {
			logger.debug("Displaying I20IntroDialog for user to select XES/XAS experiment mode");

			I20IntroDialog introDialog = new I20IntroDialog(null);
			introDialog.setBlockOnOpen(true);
			introDialog.open();

			preferences.put(XES_PREFERENCE_IS_SET, Boolean.TRUE.toString());
			// Try to save to disc immediately
			try {
				preferences.flush();
			} catch (BackingStoreException e) {
				logger.warn("Problem saving XES preference", e);
			}
		}
	}

	/**
	 * Return instance properties for storing the user preference
	 * @return
	 */
	private Preferences getPreferences() {
		return InstanceScope.INSTANCE.getNode("uk.ac.gda.beamline.i20");
	}
}
