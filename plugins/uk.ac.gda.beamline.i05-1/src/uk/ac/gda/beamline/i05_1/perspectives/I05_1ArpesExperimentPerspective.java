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

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;

import org.eclipse.core.filesystem.EFS;
import org.eclipse.core.filesystem.IFileStore;
import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.ide.IDE;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.data.PathConstructor;

public class I05_1ArpesExperimentPerspective implements IPerspectiveFactory {

	public static final String ID = "uk.ac.gda.beamline.i05_1.perspectives.I05_1ArpesExperimentPerspective";

	private static final Logger logger = LoggerFactory.getLogger(I05_1ArpesExperimentPerspective.class);

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

		createExampleArpesFileIfRequired();

		logger.info("Finished building ARPES experiment perspective");
	}

	private void createExampleArpesFileIfRequired() {

		// Find the target location for the example .arpes file
		final String tgtDataRootPath = PathConstructor.createFromProperty("gda.analyser.sampleConf.dir");
		final String exampleFileName = LocalProperties.get("gda.analyser.sampleConf");
		final File targetFile = new File(tgtDataRootPath, exampleFileName);

		// Find the full path to initialExampleAnalyserConfig.arpes in the config
		String configDir = LocalProperties.getConfigDir();
		File exampleFile = new File(configDir, exampleFileName);

		// Example file doesn't exist so copy it
		if (!targetFile.exists()) {
			try {
				Files.copy(exampleFile.toPath(), targetFile.toPath());
			} catch (IOException e) {
				logger.error("Failed copying sample analyser config file from {} to {}", exampleFile, targetFile, e);
			}
			logger.info("Copied sample analyser config file from {} to {}", exampleFile, targetFile);
		}

		// Open the example in the editor
		IWorkbenchPage page = PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage();
		IFileStore fileStore = EFS.getLocalFileSystem().getStore(targetFile.toURI());
		try {
			IDE.openEditorOnFileStore(page, fileStore);
		} catch (PartInitException e) {
			logger.error("Could not open sample analyser config file {} in editor", targetFile, e);
		}

	}
}
