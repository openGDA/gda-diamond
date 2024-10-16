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

package uk.ac.gda.beamline.b18;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jython.InterfaceProvider;
import uk.ac.gda.client.experimentdefinition.ui.handlers.RefreshProjectCommandHandler;
import uk.ac.gda.util.io.FileUtils;

public class CopyTemplateFiles {
	private static final Logger logger = LoggerFactory.getLogger(CopyTemplateFiles.class);

	private static final String TEMPLATE_SOURCE_PATH_PREF = "scan.xml.template.source.dir";
	private static final String TEMPLATE_DEST_SUBDIR = "scan.xml.template.dest.dir";

	private CopyTemplateFiles() {
	}

	public static void copy() {
		// Get preferences for template source and destination directories from plugin_customization
		IPreferenceStore preferences = B18BeamlineActivator.getDefault().getPreferenceStore();
		String templateFilesSourceDir = preferences.getString(TEMPLATE_SOURCE_PATH_PREF);
		String templateFilesDestDir = preferences.getString(TEMPLATE_DEST_SUBDIR);

		if (templateFilesDestDir.isEmpty() || templateFilesSourceDir.isEmpty()) {
			logger.warn("Cannot copy template files : source and/or destination directories have not been set");
			return;
		}

		// Create paths to source and destination directories :
		Path destDir = Paths.get(InterfaceProvider.getPathConstructor().getVisitDirectory(), templateFilesDestDir);
		Path sourceDir = Paths.get(templateFilesSourceDir);

		// If destination and source directories are the same, do nothing
		if (destDir.equals(sourceDir)) {
			logger.warn("Not copying template files - source and destination directories ({}) are the same!", destDir);
			return;
		}

		// Get list of xml files
		List<File> xmlFiles = getFileList(sourceDir, ".xml");
		if (xmlFiles.isEmpty()) {
			logger.warn("Cannot copy template files from {} - no xml files found!", templateFilesSourceDir);
			return;
		}

		// Create the directory for the template files in the visit directory
		if (!destDir.toFile().isDirectory()) {
			destDir.toFile().mkdirs();
		}

		// Copy the xml files in
		boolean filesUpdated = false;
		StringBuilder errorMessages = new StringBuilder();

		logger.info("Copying template files from {} to {}.", sourceDir, destDir);
		for(File xmlFile : xmlFiles) {
			try {
				if (xmlFile.exists() && !xmlFile.canRead()) {
					throw new IOException("Don't have read permission for file "+xmlFile.getAbsolutePath());
				}
				File destFile = destDir.resolve(xmlFile.getName()).toFile();
				if (!destFile.exists()) {
					logger.debug("Copying template file from {} to {}.", xmlFile.getAbsolutePath(), destFile.getAbsolutePath());
					FileUtils.copy(xmlFile, destFile);
					filesUpdated = true;
				} else {
					logger.debug("Not copying template file {} - file already exists in directory {}.", xmlFile.getAbsolutePath(), destDir.toString());

				}
			} catch (IOException e) {
				errorMessages.append(e.getMessage() +"\n");
				logger.warn("Problem copying template file {}", e.getMessage());
			}
		}

		// Show any errors in a dialog box
		if (errorMessages.length()>0) {
			MessageDialog dialog = new FileWarningDialog(PlatformUI.getWorkbench().getDisplay().getActiveShell(),
					"Problem copying XML templates", null,
					"Problem copying XML templates to "+destDir+" : \n\n"+errorMessages.toString(),
					MessageDialog.WARNING, 0, new String[] {"OK"});
			dialog.setBlockOnOpen(true);
			dialog.open();
		}

		// Update the Experiment Explorer view to make sure the new folder is show in the scan tree.
		if (filesUpdated) {
			try {
				RefreshProjectCommandHandler refreshCommand = new RefreshProjectCommandHandler();
				refreshCommand.execute(null);
			} catch (Exception e) {
				logger.error("Problem refreshing experiment view", e);
			}
		}
	}

	/**
	 * Return list of File objects in directory that have filename ending with specified extension.
	 * @param directoryName
	 * @param extension
	 * @return
	 */
	private static List<File> getFileList(Path directoryName, String extension) {
		File directory = directoryName.toFile();
		File[] filesInDirectory = null;
		if (directory.isDirectory()) {
			filesInDirectory = directory.listFiles();
		}
		List<File> matchingFiles = new ArrayList<>();
		if (filesInDirectory != null && filesInDirectory.length>0) {
			for(File file : filesInDirectory) {
				if (file.getName().endsWith(extension)) {
					matchingFiles.add(file);
				}
			}
		}
		return matchingFiles;
	}

	private static class FileWarningDialog extends MessageDialog {

		public FileWarningDialog(Shell parentShell, String dialogTitle, Image dialogTitleImage, String dialogMessage,
				int dialogImageType, int defaultIndex, String[] dialogButtonLabels) {
			super(parentShell, dialogTitle, dialogTitleImage, dialogMessage, dialogImageType, defaultIndex, dialogButtonLabels);
		}

		@Override
		protected boolean isResizable() {
			return true;
		}

		@Override
		protected Point getInitialSize() {
			return getShell().computeSize(600, SWT.DEFAULT);
		}
	}
}
