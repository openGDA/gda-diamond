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

import java.io.File;
import java.io.IOException;

import org.eclipse.core.filesystem.EFS;
import org.eclipse.core.filesystem.IFileStore;
import org.eclipse.core.runtime.preferences.InstanceScope;
import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.ui.IPerspectiveDescriptor;
import org.eclipse.ui.IPerspectiveListener;
import org.eclipse.ui.IStartup;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.WorkbenchException;
import org.eclipse.ui.ide.IDE;
import org.eclipse.ui.preferences.ScopedPreferenceStore;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.PathConstructor;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.Jython;
import uk.ac.gda.devices.vgscienta.IVGScientaAnalyserRMI;
import uk.ac.gda.util.io.FileUtils;

public class I05_1Startup implements IStartup {
	private static final Logger logger = LoggerFactory.getLogger(I05_1Startup.class);

	private final IVGScientaAnalyserRMI analyser = Finder.getInstance().find("analyser");

	@Override
	public void earlyStartup() {
		// Need to run the startup in the UI thread
		PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
			@Override
			public void run() {

				// This is to fix ARPES-253. Create a preference store and then set aspectRatio to false this will make
				// 2D plots fill the available space by default.
				IPreferenceStore store = new ScopedPreferenceStore(InstanceScope.INSTANCE, "org.dawnsci.plotting");
				store.setValue("org.dawb.plotting.system.aspectRatio", false);

				IWorkbench workbench = PlatformUI.getWorkbench();

				logger.info("Creating perspectives");
				for (String id : new String[] { "uk.ac.gda.beamline.i05_1.perspectives.I05_1ArpesExperimentPerspective",
						"uk.ac.gda.beamline.i05_1.perspectives.I05_1ArpesAlignmentPerspective" }) {
					try {
						workbench.showPerspective(id, workbench.getActiveWorkbenchWindow());
					} catch (WorkbenchException e) {
						logger.error("Error creating workbench", e);
					}
				}

				logger.info("Adding perspective switch listener");
				workbench.getActiveWorkbenchWindow().addPerspectiveListener(new IPerspectiveListener() {

					@Override
					public void perspectiveChanged(IWorkbenchPage page, IPerspectiveDescriptor perspective, String changeId) {
						logger.info("Perspective changed");
						// Note: This is not fired when the user changes perspective! It is fired when the perspective itself
						// is changed eg reset.
					}

					@Override
					public void perspectiveActivated(IWorkbenchPage page, IPerspectiveDescriptor perspective) {

						logger.info("Perspective Activated: {}", page.getLabel());
						logger.debug("iwbPage label: {}, perspective label: {}", page.getLabel(), perspective.getLabel());
						// Check if a scan is running if not stop the analyser
						if (InterfaceProvider.getScanStatusHolder().getScanStatus() == Jython.IDLE) {
							logger.info("Perspective Activated: No scan running: Stop analyser");
							try {
								// Stop the analyser and zero supplies
								analyser.zeroSupplies();
							} catch (Exception e) {
								logger.error("Failed to stop analyser on perspective switch", e);
							}
						}

						// PerspectiveListener to populate the editor with an initial sample .arpes analyser configuration
						if (perspective.getId().equals("uk.ac.gda.beamline.i05_1.perspectives.I05_1ArpesAlignmentPerspective")) {

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
									logger.info("Copied sample analyser config file to: {}", tgtPth);

									if (tgtPth.exists() && tgtPth.isFile()) {
										IFileStore fileStore = EFS.getLocalFileSystem().getStore(tgtPth.toURI());
										try {
											IDE.openEditorOnFileStore(page, fileStore);
										} catch (PartInitException e) {
											logger.error("Could not open sample analyser config file {}", tgtPth, e);
										}
									}
								} catch (IOException e) {
									logger.error("Could not copy sample analyser config file from: {} to user dir: {}", srcPth, tgtPth, e);
								}
							} else {
								logger.info("not opening new editor, sample analyser config file {} already exists in user dir", sampFileName);
							}
						}
					}
				});
			}
		});
	}

}