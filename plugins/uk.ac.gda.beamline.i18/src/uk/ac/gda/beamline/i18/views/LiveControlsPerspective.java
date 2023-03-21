/*-
 * Copyright © 2023 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i18.views;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IConfigurationElement;
import org.eclipse.core.runtime.IExecutableExtension;
import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.factory.Finder;
import uk.ac.gda.client.livecontrol.LiveControlsView;

public class LiveControlsPerspective implements IPerspectiveFactory, IExecutableExtension {

	private static final Logger logger = LoggerFactory.getLogger(LiveControlsPerspective.class);

	private static final String LIVE_CONTROLS_FOLDER_NAME = "LIVE_CONTROLS_FOLDER";

	private LiveControlsPerspectiveConfiguration configuration;

	@Override
	public void createInitialLayout(IPageLayout layout) {

		if (configuration == null) {
			logger.warn("No configuration object has been set - cannot create LiveControlsPerspective");
			return;
		}

		// Add offsets view to the right of simulated positions
		IFolderLayout liveControlsFolder = layout.createFolder("LIVE_CONTROLS", IPageLayout.RIGHT, 0.5f, LIVE_CONTROLS_FOLDER_NAME);
		liveControlsFolder.addView(LiveControlsView.ID+":"+configuration.getLiveControlSet());

	}

	@Override
	public void setInitializationData(IConfigurationElement config, String propertyName, Object data)
			throws CoreException {
		if (propertyName.equals("class") && data instanceof String str) {
			Finder.findOptionalOfType(str, LiveControlsPerspectiveConfiguration.class)
				.ifPresentOrElse(configObject -> {
					logger.info("Creating LiveControls Perspective using configuration object {}", str);
					configuration = configObject;
				},
				() -> logger.warn("Could not find configuration object {} to use for LiveControlsPerspective", str));
		}
	}

}
