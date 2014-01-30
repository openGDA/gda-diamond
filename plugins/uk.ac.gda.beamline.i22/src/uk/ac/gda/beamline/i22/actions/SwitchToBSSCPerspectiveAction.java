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

package uk.ac.gda.beamline.i22.actions;

import java.util.Properties;

import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.WorkbenchException;
import org.eclipse.ui.intro.IIntroPart;
import org.eclipse.ui.intro.IIntroSite;
import org.eclipse.ui.intro.config.IIntroAction;

public class SwitchToBSSCPerspectiveAction implements IIntroAction {

	public SwitchToBSSCPerspectiveAction() {
		System.out.println("SwitchPerspective");

		IWorkbench workbench = PlatformUI.getWorkbench();

		// open the BBSSC setup perspective
		for (String id : new String[] { "uk.ac.gda.pydev.extension.ui.JythonPerspective",
				"gda.rcp.ncd.perspectives.WaxsPerspective", "gda.rcp.ncd.perspectives.SaxsProcessingPerspective",
				"gda.rcp.ncd.perspectives.SaxsPerspective", "gda.rcp.ncd.perspectives.NcdDetectorPerspective",
				"gda.rcp.ncd.perspectives.SetupPerspective" }) {
			try {
				PlatformUI.getWorkbench().showPerspective(id, PlatformUI.getWorkbench().getActiveWorkbenchWindow());
			} catch (WorkbenchException e) {
				// we see if that fails and it is not the end of the world
			}
		}
	}

	@Override
	public void run(IIntroSite site, Properties params) {
		final IIntroPart introPart = PlatformUI.getWorkbench().getIntroManager().getIntro();
		PlatformUI.getWorkbench().getIntroManager().closeIntro(introPart);
	}
}
