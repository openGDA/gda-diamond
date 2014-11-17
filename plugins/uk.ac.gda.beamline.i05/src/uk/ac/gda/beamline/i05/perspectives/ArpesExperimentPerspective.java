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


package uk.ac.gda.beamline.i05.perspectives;

import java.io.File;
import java.io.IOException;

import org.eclipse.core.filesystem.EFS;
import org.eclipse.core.filesystem.IFileStore;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.IPerspectiveListener;
import org.eclipse.ui.IPerspectiveDescriptor;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.ide.IDE;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.PathConstructor;
import uk.ac.gda.util.io.FileUtils;



public class ArpesExperimentPerspective implements IPerspectiveFactory {

	private  static final Logger logger = LoggerFactory.getLogger(ArpesExperimentPerspective.class);
	@Override
	public void createInitialLayout(IPageLayout layout) {
		layout.setEditorAreaVisible(true);
		{
			IFolderLayout folderLayout = layout.createFolder("folder", IPageLayout.RIGHT, 0.55f, IPageLayout.ID_EDITOR_AREA);
			folderLayout.addView("uk.ac.gda.client.arpes.cameraview");
			folderLayout.addView("uk.ac.gda.client.arpes.sumview");
			folderLayout.addView("uk.ac.gda.client.arpes.sweptview");
		}
		layout.addView("uk.ac.gda.client.CommandQueueViewFactory", IPageLayout.TOP, 0.55f, "uk.ac.gda.client.arpes.cameraview");
		layout.addView("uk.ac.gda.rcp.views.dashboardView", IPageLayout.TOP, 0.45f, "uk.ac.gda.client.CommandQueueViewFactory");
		{
			IFolderLayout folderLayout = layout.createFolder("folder_2", IPageLayout.BOTTOM, 0.48f, IPageLayout.ID_EDITOR_AREA);
			folderLayout.addView("gda.rcp.jythonterminalview");
			folderLayout.addView("gda.rcp.views.baton.BatonView");
		}
		layout.addView("uk.ac.gda.arpes.ui.view.samplemetadata", IPageLayout.LEFT, 0.5f, "folder_2");
		layout.addView("uk.ac.gda.arpes.ui.analyserprogress", IPageLayout.BOTTOM, 0.62f, "uk.ac.gda.arpes.ui.view.samplemetadata");
		layout.addView("org.eclipse.ui.navigator.ProjectExplorer", IPageLayout.LEFT, 0.35f, IPageLayout.ID_EDITOR_AREA);
		
		// added perspectivelistener to populate the editor with an initial sample .arpes analyser configuration xml file
		PlatformUI.getWorkbench().getActiveWorkbenchWindow().addPerspectiveListener(new IPerspectiveListener() {
			  @Override
			  public void perspectiveChanged(IWorkbenchPage page, IPerspectiveDescriptor perspective, String changeId) {
			  }

			  @Override
			  public void perspectiveActivated(IWorkbenchPage page, IPerspectiveDescriptor perspective) {
				  logger.info("perspectiveActivated: iwbPage label:"+page.getLabel()+", perspective label:"+perspective.getLabel());
				  				  
				  if (perspective.getId().equals("uk.ac.gda.beamline.i05.perspectives.ArpesExperimentPerspective")) {

					String sampFileName    = PathConstructor.createFromProperty("gda.analyser.sampleConf");       // full path to initialExampleAnalyserConfig.arpes
					String srcDataRootPath = PathConstructor.createFromProperty("gda.analyser.sampleConf.dir");   // location that is available in dummy and live and is version controlled
					File srcPth            = new File(srcDataRootPath, sampFileName);
					
					String tgtDataRootPath = PathConstructor.createFromProperty("gda.analyser.sampleConf.dir");   
					String cfgTgtPath      = PathConstructor.createFromTemplate(tgtDataRootPath + "/$visit$/xml"); // location that is available in dummy and live variants and is visitor-specific
					File tgtXmlDir         = new File(cfgTgtPath);
					File tgtPth            = new File(tgtXmlDir, sampFileName);
					
					if (!tgtPth.exists()) { // only needs to be invoked once for a each new visit, thereafter workspace caching determines editor(s) visible, you can delete file in visit xml dir to allow this clause to re-execute
						try {
							tgtXmlDir.mkdir();  // ensure xml directory exists
							FileUtils.copy(srcPth, tgtPth);
							logger.info("perspectiveActivated: copied sample analyser config file to:"+tgtPth);

							if (tgtPth.exists() && tgtPth.isFile()) {
							    IFileStore fileStore = EFS.getLocalFileSystem().getStore(tgtPth.toURI());
							    try {
							        IDE.openEditorOnFileStore(page, fileStore);
							    } catch (PartInitException e) {
									logger.error("Could not open sample analyser config file "+tgtPth, e);
							    }
							} 
						} catch (IOException e) {
							logger.error("Could not copy sample analyser config file from:"+srcPth+" to user dir:"+tgtPth, e);
						}
					} else {
						logger.info("not opening new editor, sample analyser config file "+sampFileName+" already exists in user dir");
					}				  	
			  }
		    }
			  
		});
	}
}