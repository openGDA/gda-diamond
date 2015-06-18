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

package uk.ac.gda.beamline.i05_1.perspectives;

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class I05_1ArpesExperimentPerspective implements IPerspectiveFactory {

	private  static final Logger logger = LoggerFactory.getLogger(I05_1ArpesExperimentPerspective.class);
	@Override
	public void createInitialLayout(IPageLayout layout) {
		logger.info("Building ARPES experiment perspective");
		layout.setEditorAreaVisible(true);
		{
			IFolderLayout folderLayout = layout.createFolder("folder", IPageLayout.RIGHT, 0.55f, IPageLayout.ID_EDITOR_AREA);
			folderLayout.addView("uk.ac.gda.client.arpes.cameraview");
			folderLayout.addView("uk.ac.gda.client.arpes.sumview");
			folderLayout.addView("uk.ac.gda.client.arpes.sweptview");
		}
		layout.addView("uk.ac.gda.rcp.views.dashboardView", IPageLayout.TOP, 0.28f, "uk.ac.gda.client.arpes.cameraview");
		layout.addView("uk.ac.gda.client.liveplotview", IPageLayout.TOP, 0.50f, "uk.ac.gda.client.arpes.cameraview");
		{
			IFolderLayout folderLayout = layout.createFolder("folder_2", IPageLayout.BOTTOM, 0.48f, IPageLayout.ID_EDITOR_AREA);
			folderLayout.addView("gda.rcp.jythonterminalview");
			folderLayout.addView("gda.rcp.views.baton.BatonView");
		}
		layout.addView("uk.ac.gda.arpes.ui.view.samplemetadata", IPageLayout.LEFT, 0.5f, "folder_2");
		layout.addView("uk.ac.gda.arpes.ui.analyserprogress", IPageLayout.BOTTOM, 0.62f, "uk.ac.gda.arpes.ui.view.samplemetadata");
		layout.addView("org.eclipse.ui.navigator.ProjectExplorer", IPageLayout.LEFT, 0.35f, IPageLayout.ID_EDITOR_AREA);

		logger.info("Finished building ARPES experiment perspective");
	}
}