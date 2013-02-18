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

package uk.ac.gda.beamline.i05.perspectives;

import gda.configuration.properties.LocalProperties;

import org.csstudio.sds.ui.runmode.RunModeService;
import org.eclipse.core.runtime.Path;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.IFolderLayout;

public class ArpesAlignmentPerspective implements IPerspectiveFactory {

	@Override
	public void createInitialLayout(IPageLayout layout) {
		layout.setEditorAreaVisible(false);
		
		String path = LocalProperties.get("gda.dal.screens") + "synoptic.css-sds";
		Path sdsDisplay = new Path(path);
		RunModeService.getInstance().openDisplayViewInRunMode(sdsDisplay);
		
		layout.addView("uk.ac.gda.client.arpes.cameraview", IPageLayout.RIGHT, 0.47f, IPageLayout.ID_EDITOR_AREA);
		layout.addView("uk.ac.gda.arpes.ui.continuousmodecontroller", IPageLayout.TOP, 0.37f, "uk.ac.gda.client.arpes.cameraview");
		layout.addView("uk.ac.gda.rcp.views.dashboardView", IPageLayout.TOP, 0.5f, "uk.ac.gda.arpes.ui.continuousmodecontroller");

		{
			IFolderLayout folderLayout = layout.createFolder("folder_2", IPageLayout.BOTTOM, 0.5f, IPageLayout.ID_EDITOR_AREA);
			folderLayout.addView("gda.rcp.jythonterminalview");
			folderLayout.addView("gda.rcp.views.baton.BatonView");
		}
		{
			IFolderLayout folderLayout = layout.createFolder("folder", IPageLayout.TOP, 0.26f, "folder_2");
			folderLayout.addView("uk.ac.gda.client.CommandQueueViewFactory");
		}
		{
			IFolderLayout folderLayout = layout.createFolder("folder_1", IPageLayout.TOP, 0.58f, "folder_2");
			folderLayout.addView("org.csstudio.sds.ui.internal.runmode.DisplayViewPart");
		}

	}
}