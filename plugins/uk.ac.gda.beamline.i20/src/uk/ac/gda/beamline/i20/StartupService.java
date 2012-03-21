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
import gda.exafs.ui.I20SampleParametersEditor;
import gda.exafs.ui.I20SampleParametersUIEditor;

import org.eclipse.ui.IEditorReference;
import org.eclipse.ui.IStartup;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.common.rcp.util.EclipseUtils;
import uk.ac.gda.exafs.ui.describers.I20SampleDescriber;

/**
 * Setting up the data prior to other views connecting to it.
 */
public class StartupService implements IStartup {

	private static final Logger logger = LoggerFactory.getLogger(StartupService.class);


	@Override
	public void earlyStartup() {

		if (!LocalProperties.get("gda.factory.factoryName").equals("i20"))
			return;

		// open a second workbench displaying the synoptic
		try {
			if (PlatformUI.getWorkbench().getWorkbenchWindows().length < 2) {

				// check if welcome screen visible
				IWorkbenchWindow window = PlatformUI.getWorkbench().getWorkbenchWindows()[0];
				final IViewPart welcomeScreen = window.getActivePage().findView("org.eclipse.ui.internal.introview");

				if (welcomeScreen == null) {

					SynopticControl.showSynoptic();
				}
			}
		} catch (Exception e) {
			logger.warn("Exception while trying to open Synoptic in a separate workbench", e);
		}

		// If the SampleParametersEditor is there, we refresh its element list. This is because
		// it needs the definition of beans which are not made until this startup method is run,
		// but editors are created *before* this method is run.
//		PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
//			@Override
//			public void run() {
//				final IEditorReference[] eds = EclipseUtils.getDefaultPage().findEditors(null, I20SampleDescriber.ID,
//						IWorkbenchPage.MATCH_ID);
//				if (eds != null) {
//					for (int i = 0; i < eds.length; i++) {
//						I20SampleParametersUIEditor ed = (I20SampleParametersUIEditor) ((I20SampleParametersEditor) eds[i]
//								.getEditor(false)).getRichBeanEditor();
//						ed.updateElementLabel();
//					}
//				}
//			}
//		});

	}
}
