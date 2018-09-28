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

package uk.ac.gda.beamline.i10;

import org.eclipse.ui.IStartup;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EarlyStartup implements IStartup {
	private static final Logger logger=LoggerFactory.getLogger(EarlyStartup.class);
	@Override
	public void earlyStartup() {
		try {
			PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView("uk.ac.gda.beamline.i10.pimte.live.stream.view.LiveStreamViewWithHistogram","pimte_cam#EPICS_ARRAY", IWorkbenchPage.VIEW_ACTIVATE);
			PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView("uk.ac.gda.beamline.i10.pixis.live.stream.view.LiveStreamViewWithHistogram","pixis_cam#EPICS_ARRAY", IWorkbenchPage.VIEW_ACTIVATE);
		} catch (PartInitException e) {
			logger.warn("showView calls failed in {}", getClass().getName());
		}

	}

}
