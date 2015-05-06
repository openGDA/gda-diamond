/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i05_1;

import org.eclipse.core.runtime.preferences.InstanceScope;
import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.WorkbenchException;
import org.eclipse.ui.part.IntroPart;
import org.eclipse.ui.preferences.ScopedPreferenceStore;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class I05_1Intro extends IntroPart {
	private static final Logger logger = LoggerFactory.getLogger(I05_1Intro.class);
	
	@Override
	public void standbyStateChanged(boolean standby) {
	}

	@Override
	public void createPartControl(Composite parent) {
		
		// This is to fix ARPES-253. Create a preference store and then set aspectRatio to false this will make
		// 2D plots fill the available space by default.
		IPreferenceStore store = new ScopedPreferenceStore(InstanceScope.INSTANCE, "org.dawnsci.plotting");
		store.setValue("org.dawb.plotting.system.aspectRatio", false);
		
		for (String id : new String[] {
				"uk.ac.gda.client.scripting.JythonPerspective",	
				"uk.ac.gda.beamline.i05_1.perspectives.I05_1ArpesExperimentPerspective",
				"uk.ac.gda.beamline.i05_1.perspectives.I05_1ArpesAlignmentPerspective"
				}) {
			try {
				PlatformUI.getWorkbench().showPerspective(id, PlatformUI.getWorkbench().getActiveWorkbenchWindow());
			} catch (WorkbenchException e) {
				logger.error("Error creating workbench: " + e.getMessage());
			}
		}
	}

	@Override
	public void setFocus() {
	}
}