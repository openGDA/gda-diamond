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

import org.eclipse.scanning.api.event.EventConstants;
import org.eclipse.scanning.event.ui.view.StatusQueueView;
import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.IViewLayout;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;

/**
 * @author Maurizio Nagni
 */
public class Tomography  implements IPerspectiveFactory {

	public static final String ID = "uk.ac.diamond.daq.beamline.k11.perspective.TomographyPerspective";

	private static final String TOMO_MAIN_VIEW = "uk.ac.diamond.daq.beamline.k11.tomography";
	private static final String LIVE_VIEW = "uk.ac.diamond.daq.client.gui.camera.liveview.SimpleLiveStreamView";
	private static final String CAMERA_CONTROLLER_VIEW = "uk.ac.diamond.daq.client.gui.camera.CameraConfigurationView";
	private static final String JYTON_CONSOLE_VIEW = "gda.rcp.jythonterminalview";

	private static final Logger logger = LoggerFactory.getLogger(Tomography.class);

	@Override
	public void createInitialLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		logger.trace("Building K11 Tomography perspective");
		layout.setEditorAreaVisible(false);

		String tomoMain = "tomographyManagement";
		final IFolderLayout mainFolder = layout.createFolder(tomoMain, IPageLayout.LEFT, 0.20f, editorArea);
		mainFolder.addView(TOMO_MAIN_VIEW);
		IViewLayout topViewLayout = layout.getViewLayout(TOMO_MAIN_VIEW);
		topViewLayout.setCloseable(false);

		String tomoTools = "tomographyTools";
		final IFolderLayout toolsFolder = layout.createFolder(tomoTools, IPageLayout.RIGHT, 0.75f, editorArea);
		toolsFolder.addView(LIVE_VIEW);
		toolsFolder.addView(CAMERA_CONTROLLER_VIEW);
		IViewLayout topRightLayout = layout.getViewLayout(CAMERA_CONTROLLER_VIEW);
		topRightLayout.setCloseable(false);

		String tomoMonitor = "tomographyMonitors";
		final IFolderLayout monitorLayout = layout.createFolder(tomoMonitor, IPageLayout.BOTTOM, 0.75f, tomoTools);
		monitorLayout.addView(JYTON_CONSOLE_VIEW);
		String queueViewId = StatusQueueView.createId(LocalProperties.get(LocalProperties.GDA_ACTIVEMQ_BROKER_URI, ""),
				"org.eclipse.scanning.api",
				"org.eclipse.scanning.api.event.status.StatusBean",
				EventConstants.STATUS_TOPIC,
				EventConstants.SUBMISSION_QUEUE);


		queueViewId = queueViewId + "partName=Queue";
		monitorLayout.addView(queueViewId);


		logger.trace("Finished building K11 Tomography perspective");
	}
}
