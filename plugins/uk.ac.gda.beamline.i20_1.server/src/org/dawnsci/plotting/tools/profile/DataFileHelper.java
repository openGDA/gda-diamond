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

public class DataFileHelper {

	private DataFileHelper() {}

	private static String tempPath = System.getProperty("java.io.tmpdir");

	public static String copyToTempFolder(File file, String suffix) throws IOException {
		String newFileName = getFileNameWithSuffix(file, suffix);
		Path path = Files.copy(file.toPath(), Paths.get(tempPath + File.separator + newFileName), StandardCopyOption.REPLACE_EXISTING);
		return path.toString();
	}

	public static String getFileNameWithSuffix(File file, String suffix) {
		return FilenameUtils.removeExtension(file.getName()) + "_" + suffix + "." +  FilenameUtils.getExtension(file.getName());
	}

	public static String getFileNameWithSuffixAndExt(File file, String suffix, String ext) {
		return FilenameUtils.removeExtension(file.getName()) + "_" + suffix + "." +  ext;
	}

	public static String getFileNameWithPrefixSuffixAndExt(File file, String prefix, String suffix, String ext) {
		return prefix + "_" + FilenameUtils.removeExtension(file.getName()) + "_" + suffix + "." +  ext;
	}

	// TODO Check folder exist
	public static String convertFromNexusToAsciiFolder(String nexusFilePath) {
		String nexusFolder = FilenameUtils.getFullPath(nexusFilePath);
		int nexusLocation = nexusFolder.lastIndexOf("nexus");
		if (nexusLocation != -1) {
			String path = nexusFolder.substring(0, nexusLocation);
			return path + "ascii/";
		}
		return nexusFolder;
	}
}
