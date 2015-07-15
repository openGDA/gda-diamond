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

package uk.ac.gda.beamline.i05;

import java.io.File;
import java.io.IOException;

import org.eclipse.core.filesystem.EFS;
import org.eclipse.core.filesystem.IFileStore;
import org.eclipse.core.runtime.preferences.InstanceScope;
import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.IPerspectiveDescriptor;
import org.eclipse.ui.IPerspectiveListener;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.WorkbenchException;
import org.eclipse.ui.ide.IDE;
import org.eclipse.ui.part.IntroPart;
import org.eclipse.ui.preferences.ScopedPreferenceStore;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.PathConstructor;
import gda.jython.Jython;
import gda.jython.JythonServerFacade;
import uk.ac.gda.util.io.FileUtils;

public class I05Intro extends IntroPart {
	private static final Logger logger = LoggerFactory.getLogger(I05Intro.class);

	@Override
	public void standbyStateChanged(boolean standby) {
	}

	@Override
	public void createPartControl(Composite parent) {

		// This is to fix ARPES-253. Create a preference store and then set aspectRatio to false this will make
		// 2D plots fill the available space by default.
		IPreferenceStore store = new ScopedPreferenceStore(InstanceScope.INSTANCE, "org.dawnsci.plotting");
		store.setValue("org.dawb.plotting.system.aspectRatio", false);

		logger.info("Creating perspectives");
		for (String id : new String[] { "uk.ac.gda.client.scripting.JythonPerspective",
				"uk.ac.gda.beamline.i05.perspectives.ArpesExperimentPerspective",
				"uk.ac.gda.beamline.i05.perspectives.ArpesAlignmentPerspective" }) {
			try {
				PlatformUI.getWorkbench().showPerspective(id, PlatformUI.getWorkbench().getActiveWorkbenchWindow());
			} catch (WorkbenchException e) {
				logger.error("Error creating workbench: " + e.getMessage());
			}
		}

		logger.info("Adding perspective switch listener");
		PlatformUI.getWorkbench().getActiveWorkbenchWindow().addPerspectiveListener(new IPerspectiveListener() {

			@Override
			public void perspectiveChanged(IWorkbenchPage page, IPerspectiveDescriptor perspective, String changeId) {
				logger.info("Perspective changed");
				// Note: This is not fired when the user changes perspective! It is fired when the perspective itself
				// is changed eg reset.
			}

			@Override
			public void perspectiveActivated(IWorkbenchPage page, IPerspectiveDescriptor perspective) {

				logger.info("Perspective Activated: " + page.getLabel());
				logger.debug("iwbPage label:" + page.getLabel() + ", perspective label:" + perspective.getLabel());
				// Check if a scan is running if not stop the analyser
				if (JythonServerFacade.getInstance().getScanStatus() == Jython.IDLE) {
					logger.info("Perspective Activated: No scan running: Stop analyser");
					// am is arpesmonitor python class so call stop
					JythonServerFacade.getInstance().runCommand("am.stop()");
				}

				// PerspectiveListener to populate the editor with an initial sample .arpes analyser configuration
				if (perspective.getId().equals("uk.ac.gda.beamline.i05.perspectives.ArpesExperimentPerspective")) {

					// full path to initialExampleAnalyserConfig.arpes
					String sampFileName = PathConstructor.createFromProperty("gda.analyser.sampleConf");
					// location that is available in dummy and live and is version controlled
					String srcDataRootPath = PathConstructor.createFromProperty("gda.analyser.sampleConf.dir");
					File srcPth = new File(srcDataRootPath, sampFileName);

					String tgtDataRootPath = PathConstructor.createFromProperty("gda.analyser.sampleConf.dir");
					// location that is available in dummy and live variants and is visitor-specific
					String cfgTgtPath = PathConstructor.createFromTemplate(tgtDataRootPath + "/$visit$/xml");
					File tgtXmlDir = new File(cfgTgtPath);
					File tgtPth = new File(tgtXmlDir, sampFileName);

					// only needs to be invoked once for a each new visit, thereafter workspace caching determines
					// editor(s) visible, you can delete file in visit xml dir to allow this clause to re-execute
					if (!tgtPth.exists()) {
						try {
							tgtXmlDir.mkdir(); // ensure xml directory exists
							FileUtils.copy(srcPth, tgtPth);
							logger.info("Copied sample analyser config file to:" + tgtPth);

							if (tgtPth.exists() && tgtPth.isFile()) {
								IFileStore fileStore = EFS.getLocalFileSystem().getStore(tgtPth.toURI());
								try {
									IDE.openEditorOnFileStore(page, fileStore);
								} catch (PartInitException e) {
									logger.error("Could not open sample analyser config file " + tgtPth, e);
								}
							}
						} catch (IOException e) {
							logger.error("Could not copy sample analyser config file from:" + srcPth + " to user dir:"
									+ tgtPth, e);
						}
					} else {
						logger.info("not opening new editor, sample analyser config file " + sampFileName
								+ " already exists in user dir");
					}
				}
			}
		});
	}

	@Override
	public void setFocus() {
		// Do nothing
	}
}
