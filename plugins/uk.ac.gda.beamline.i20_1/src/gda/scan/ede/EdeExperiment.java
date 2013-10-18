/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package gda.scan.ede;

import gda.jython.InterfaceProvider;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Base class for all EDE experiment classes.
 * <p>
 * These classes all work in a similar manner: they take experimental parameters in the form of a series of
 * EdeScanParameters, EdeScanPosition and StripDetector objects. Then in their runExperiment method they build and run
 * MultiScan which generates a single Nexus file. At they end they produce a single EDE format ASCII file whose filename
 * the runExperiment method returns.
 */
public abstract class EdeExperiment {

	/**
	 * The name of the ScriptController object which is sent progress information and normalised spectra by experiments
	 */
	public static final String PROGRESS_UPDATER_NAME = "EDEProgressUpdater";

	private static final Logger edelogger = LoggerFactory.getLogger(EdeExperiment.class);

	protected String filenameTemplate = "";

	/**
	 * Run the scans and write the data files.
	 * <p>
	 * Should not return until data collection completed.
	 * 
	 * @throws Exception
	 */
	public abstract String runExperiment() throws Exception;

	public String getFilenameTemplate() {
		return filenameTemplate;
	}

	/**
	 * A String format for the name of the ascii file to be written.
	 * <p>
	 * It <b>must</b> contain a '%s' to substitute the nexus file name into the given template.
	 * <p>
	 * E.g. if the nexus file created was: '/dls/i01/data/1234.nxs' then the filenameTemplate given in this method
	 * should be something like: 'Fe-Kedge_%s' for the final ascii file to be: '/dls/i01/data/Fe-Kedge_1234.txt'
	 * 
	 * @param filenameTemplate
	 */
	public void setFilenameTemplate(String filenameTemplate) {
		this.filenameTemplate = filenameTemplate;
	}

	protected void log(String message) {
		InterfaceProvider.getTerminalPrinter().print(message);
		edelogger.info(message);
	}
}
