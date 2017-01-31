/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

import java.util.Arrays;
import java.util.List;
import java.util.Properties;

import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.WorkbenchException;
import org.eclipse.ui.intro.IIntroManager;
import org.eclipse.ui.intro.IIntroSite;
import org.eclipse.ui.intro.config.IIntroAction;

import gda.device.FindableObjectHolder;
import gda.factory.Finder;

public class I22DefaultPerspectiveAction implements IIntroAction {

	public I22DefaultPerspectiveAction() {
	}

	@SuppressWarnings("unchecked")//casting raw_defaults to defaults
	@Override
	public void run(IIntroSite site, Properties params) {
		IIntroManager iMan = PlatformUI.getWorkbench().getIntroManager();
		System.out.println(iMan.closeIntro(iMan.getIntro()));
		closeAllPerspectives();
		FindableObjectHolder holder = (FindableObjectHolder)Finder.getInstance().find("clientReferences");
		List<String> defaults = null;
		if (holder != null) {
			Object raw_defaults = holder.get(params.get("p_set"));
			if (raw_defaults instanceof List<?>) {
				defaults = (List<String>)raw_defaults;
			}
		}
		if (defaults == null) {
			defaults = Arrays.asList(new String[] {
					"gda.rcp.ncd.perspectives.SaxsProcessingPerspective",  // must precede the Saxs & Waxs Perspectives to avoid NPE error in [S|W]axs Data Source View
					"gda.rcp.ncd.perspectives.SaxsPerspective",
					"gda.rcp.ncd.perspectives.WaxsPerspective",
					"gda.rcp.ncd.perspectives.NcdDetectorPerspective",
					"gda.rcp.ncd.perspectives.SetupPerspective",
					"uk.ac.gda.client.scripting.JythonPerspective"
			});
		}
		for (String id : defaults) {
			try {
				PlatformUI.getWorkbench().showPerspective(id, PlatformUI.getWorkbench().getActiveWorkbenchWindow());
			} catch (WorkbenchException e) {
				// we see if that fails and it is not the end of the world
			}
		}
	}

	private void closeAllPerspectives() {
		PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().closeAllPerspectives(true, false);
	}

}
