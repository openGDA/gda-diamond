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
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.Path;
import org.eclipse.ui.IStartup;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.ide.FileStoreEditorInput;
import org.opengda.lde.model.ldeexperiment.presentation.LDEExperimentsEditor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.PathConstructor;

public class OpenDeafultLdeFile implements IStartup {

	private static final Logger logger=LoggerFactory.getLogger(OpenDeafultLdeFile.class);

	@Override
	public void earlyStartup() {
		final IWorkbench workbench = PlatformUI.getWorkbench();

		workbench.getDisplay().asyncExec(new Runnable() {
			
			@Override
			public void run() {
				IWorkbenchWindow window = workbench.getActiveWorkbenchWindow();
				if (window != null) {
					IPath path = new Path(PathConstructor.createFromDefaultProperty()+File.separator+"xml"+File.separator+"newsamples.lde");
					IFileStore fileToBeOpened= EFS.getLocalFileSystem().getStore(path);
					IWorkbenchPage page = window.getActivePage();
					FileStoreEditorInput editorInput = new FileStoreEditorInput(fileToBeOpened);
					
					try {
						page.openEditor(editorInput, LDEExperimentsEditor.ID);
					} catch (PartInitException e) {
						logger.error("Failed to open default LDE file: "+ path.getDevice(), e);
					}
					//TODO BLXI-321 for some unknown reason, the default perspective does not show views in correct size, so do the following line.
					page.resetPerspective();
				}
			}
		});
	}
}
