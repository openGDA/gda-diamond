/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i20;

import gda.configuration.properties.LocalProperties;

import java.io.File;

import org.eclipse.core.runtime.Platform;
import org.eclipse.ui.IStartup;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Setting up the data prior to other views connecting to it.
 */
public class StartupService implements IStartup {

	private static final Logger logger = LoggerFactory.getLogger(StartupService.class);

	@Override
	public void earlyStartup() {

		if (!LocalProperties.get("gda.factory.factoryName").equals("i20"))
			return;

		String path = Platform.getInstanceLocation().getURL().getPath();
		String synopticProjectFile = path + "/SDS/.project";

		// if synoptic does not exist, then this is the first time the GDA has been run in this workspace, so show the
		// Welcome screen
		if (new File(synopticProjectFile).exists()) {
			SynopticControl.showSynoptic();
		} else {
			PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
				@Override
				public void run() {
					try {
						PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage()
								.showView("org.eclipse.ui.internal.introview");
						IWorkbenchPage page = PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage();
						page.setPartState(page.findViewReference("org.eclipse.ui.internal.introview"),
								IWorkbenchPage.STATE_MAXIMIZED);
					} catch (PartInitException e) {
						logger.error(
								"Failed to open the welcome screen. The client will be in XAS/XANES mode. PartInitException:",
								e);
					}
				}
			});
		}

	}
}
