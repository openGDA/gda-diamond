/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.perspective;

import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;

import uk.ac.diamond.daq.client.gui.camera.CameraConfigurationView;
import uk.ac.gda.perspectives.ThreeColumnPerspectiveLayoutBuilder;

/**
 * @author Maurizio Nagni
 */
public class Tomography  implements IPerspectiveFactory {
	public static final String ID = "uk.ac.diamond.daq.beamline.k11.perspective.Tomography";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		ThreeColumnPerspectiveLayoutBuilder helper = new ThreeColumnPerspectiveLayoutBuilder(ID, layout);

		// Left area
		helper.addViewToLeftFolder(K11DefaultViews.PERSPECTIVE_DASHBOARD_VIEW, false);

		// Central area
		helper.addPlaceholderToCentralFolder(CameraConfigurationView.CAMERA_CONTROLLER_VIEW);

		// Right area
		helper.addViewToRightFolder(K11DefaultViews.TOMOGRAPHY_ACQUISITION_CONFIGURATION, false);
		helper.addFolderThenViewToRightFolder(K11DefaultViews.JYTON_CONSOLE_VIEW, false, 0.7f);
		helper.addViewToRightFolder(K11DefaultViews.getQueueId(), false);
	}
}
