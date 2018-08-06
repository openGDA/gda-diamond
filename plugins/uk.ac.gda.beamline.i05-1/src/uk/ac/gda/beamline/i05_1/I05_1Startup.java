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
import org.eclipse.ui.IPerspectiveDescriptor;
import org.eclipse.ui.IPerspectiveListener;
import org.eclipse.ui.IStartup;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.WorkbenchException;
import org.eclipse.ui.preferences.ScopedPreferenceStore;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.JythonStatus;
import uk.ac.gda.devices.vgscienta.IVGScientaAnalyserRMI;

public class I05_1Startup implements IStartup {
	private static final Logger logger = LoggerFactory.getLogger(I05_1Startup.class);

	/**
	 * This listener will zero supplies on the analyser if the perspective is switched when no scan is running
	 */
	private final IPerspectiveListener analyserListener = new IPerspectiveListener() {

		private final IVGScientaAnalyserRMI analyser = Finder.getInstance().find("analyser");

		@Override
		public void perspectiveChanged(IWorkbenchPage page, IPerspectiveDescriptor perspective, String changeId) {
			// Note: This is not fired when the user changes perspective! It is fired when the perspective itself
			// is changed eg reset.
		}

		@Override
		public void perspectiveActivated(IWorkbenchPage page, IPerspectiveDescriptor perspective) {
			// Check if a scan is running if not stop the analyser
			if (InterfaceProvider.getScanStatusHolder().getScanStatus() == JythonStatus.IDLE) {
				logger.info("Perspective Activated: No scan running: Stop analyser");
				try {
					// Stop the analyser and zero supplies
					analyser.zeroSupplies();
				} catch (Exception e) {
					logger.error("Failed to stop analyser on perspective switch", e);
				}
			}
		}
	};

	@Override
	public void earlyStartup() {
		// This is to fix ARPES-253. Create a preference store and then set aspectRatio to false this will make
		// 2D plots fill the available space by default.
		IPreferenceStore store = new ScopedPreferenceStore(InstanceScope.INSTANCE, "org.dawnsci.plotting");
		store.setValue("org.dawb.plotting.system.aspectRatio", false);

		// Need to run the startup in the UI thread
		PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
			@Override
			public void run() {
				IWorkbench workbench = PlatformUI.getWorkbench();

				logger.info("Creating perspectives");
				for (String id : new String[] { "uk.ac.gda.arpes.perspectives.ArpesExperimentPerspective",
						"uk.ac.gda.arpes.perspectives.ArpesAlignmentPerspective" }) {
					try {
						workbench.showPerspective(id, workbench.getActiveWorkbenchWindow());
					} catch (WorkbenchException e) {
						logger.error("Error creating workbench", e);
					}
				}

				logger.info("Adding perspective switch listener");
				workbench.getActiveWorkbenchWindow().addPerspectiveListener(analyserListener);
			}
		});
	}
}
