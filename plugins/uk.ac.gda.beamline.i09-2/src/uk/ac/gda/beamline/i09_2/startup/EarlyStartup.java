/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i09_2.startup;

import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IStartup;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class EarlyStartup implements IStartup {

	private static final Logger logger = LoggerFactory.getLogger(EarlyStartup.class);

	@Override
	public void earlyStartup() {
		Display.getDefault().asyncExec(new Runnable() {

			@Override
			public void run() {
				try {
					// ensure the Live Stream View has focus so the tool page views above are linked to this image
					PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(
							"uk.ac.gda.beamline.i09-2.dld.live.stream.view.LiveImageXY", "dld_liveimagexy#EPICS_ARRAY", IWorkbenchPage.VIEW_ACTIVATE);
					PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(
							"uk.ac.gda.beamline.i09-2.dld.live.stream.view.AccumImageXY", "dld_accumimagexy#EPICS_ARRAY", IWorkbenchPage.VIEW_ACTIVATE);
				} catch (PartInitException e) {
					logger.warn("showView calls failed in {}", getClass().getName());
				}
			}
		});
	}

}
