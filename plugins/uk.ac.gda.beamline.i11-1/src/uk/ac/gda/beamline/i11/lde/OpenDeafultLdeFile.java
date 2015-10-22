/*-
 * Copyright © 2015 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i11.lde;

import java.io.File;

import org.eclipse.core.filesystem.EFS;
import org.eclipse.core.filesystem.IFileStore;
import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IFolder;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IWorkspace;
import org.eclipse.core.resources.IWorkspaceRoot;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.Path;
import org.eclipse.ui.IStartup;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.ide.FileStoreEditorInput;
import org.eclipse.ui.part.FileEditorInput;
import org.opengda.lde.model.ldeexperiment.presentation.LDEExperimentsEditor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.PathConstructor;
import gda.rcp.DataProject;
import uk.ac.gda.preferences.PreferenceConstants;

public class OpenDeafultLdeFile implements IStartup {

	private static final Logger logger = LoggerFactory.getLogger(OpenDeafultLdeFile.class);

	@Override
	public void earlyStartup() {
		final IWorkbench workbench = PlatformUI.getWorkbench();

		workbench.getDisplay().asyncExec(new Runnable() {

			@Override
			public void run() {
				IWorkbenchWindow window = workbench.getActiveWorkbenchWindow();
				if (window != null) {
					IWorkbenchPage activePage = window.getActivePage();
					IProject dataProject = DataProject.getDataProjectIfExists();
					// open if necessary
					if (dataProject.exists() && !dataProject.isOpen()) {
						try {
							dataProject.open(null);
						} catch (CoreException e1) {
							logger.error("Error open project " +dataProject.getLocationURI().getPath(), e1);
						}
					}
					IFolder dataFolder = dataProject.getFolder("data");
					if (dataFolder.exists()) {
						IFolder xmlFolder = dataFolder.getFolder("xml");
						if (xmlFolder.exists()) {
							IFile sampleFile=xmlFolder.getFile("newsamples.lde");
							if (sampleFile.exists()) {
							FileEditorInput editorInput=new FileEditorInput(sampleFile);
							try {
								activePage.openEditor(editorInput, LDEExperimentsEditor.ID);
							} catch (PartInitException e) {
								logger.error("Failed to open default LDE file: " + sampleFile.getLocationURI().getPath(), e);
							}
							}
						}
						
					}
					
					// TODO BLXI-321 for some unknown reason, the default perspective does not show views in correct
					// size, so do the following line.
					activePage.resetPerspective();
				}
			}
		});
	}
}
