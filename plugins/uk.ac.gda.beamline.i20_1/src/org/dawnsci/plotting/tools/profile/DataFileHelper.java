/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package org.dawnsci.plotting.tools.profile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

import org.apache.commons.io.FilenameUtils;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.swt.widgets.Shell;

public class DataFileHelper {

	private DataFileHelper() {}

	public static File[] showMultipleFileSelectionDialog(Shell shell, String path) {
		FileDialog fileDialog = new FileDialog(shell, SWT.MULTI);
		fileDialog.setFilterNames(new String[] {"Nexus (*.nxs)"});
		fileDialog.setFilterExtensions(new String[] {"*.nxs"});
		fileDialog.setText("Select file to apply new energy calibration...");
		String folder = path;
		fileDialog.setFilterPath(folder);
		if (fileDialog.open() != null) {
			String[] filenames = fileDialog.getFileNames();
			String filterPath = fileDialog.getFilterPath();
			File[] selectedFiles = new File[filenames.length];
			for (int i = 0; i < filenames.length; i++) {
				if(filterPath != null && filterPath.trim().length() > 0) {
					selectedFiles[i] = new File(filterPath, filenames[i]);
				}
				else {
					selectedFiles[i] = new File(filenames[i]);
				}
			}
			return selectedFiles;
		}
		return null;
	}

	private static String tempPath = System.getProperty("java.io.tmpdir");

	public static String copyToTempFolder(File file, String suffix) throws IOException {
		String newFileName = getFileNameWithSuffix(file, suffix);
		Path path = Files.copy(file.toPath(), Paths.get(tempPath + File.separator + newFileName), StandardCopyOption.REPLACE_EXISTING);
		return path.toString();
	}

	public static String getFileNameWithSuffix(File file, String suffix) {
		return FilenameUtils.removeExtension(file.getName()) + "-" + suffix + "." +  FilenameUtils.getExtension(file.getName());
	}

}
