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

package uk.ac.gda.beamline.i22;

import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IStartup;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.WorkbenchException;

/**
 * Setting up the data prior to other views connecting to it.
 */
public class I22StartupService implements IStartup {

	@Override
	public void earlyStartup() {
		Display.getDefault().asyncExec(new Runnable() {

			@Override
			public void run() {
				System.out.println("STARTUP");
				for (String id : new String[] {
						"gda.rcp.ncd.perspectives.WaxsPerspective",
						"gda.rcp.ncd.perspectives.SaxsProcessingPerspective",
						"gda.rcp.ncd.perspectives.SaxsPerspective",
						"gda.rcp.ncd.perspectives.NcdDetectorPerspective",
						"gda.rcp.ncd.perspectives.SetupPerspective",
						"uk.ac.gda.client.scripting.JythonPerspective"
				}) {
					try {
						PlatformUI.getWorkbench().showPerspective(id, PlatformUI.getWorkbench().getActiveWorkbenchWindow());
					} catch (WorkbenchException e) {
						// we see if that fails and it is not the end of the world
					}
				}
			}
		});
	}
}