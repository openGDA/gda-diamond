/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i13i.perspectives;

import gda.rcp.views.JythonTerminalView;

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.IViewLayout;

import uk.ac.gda.beamline.i13i.views.ViewFactoryIds;
import uk.ac.gda.beamline.i13i.views.cameraview.CameraViewPart;
import uk.ac.gda.client.CommandQueueViewFactory;
import uk.ac.gda.client.liveplot.LivePlotView;

/**
 */
public class DataCollectionPerspective implements IPerspectiveFactory {
	
	//Do not change - used in plugin.xml
	private static final String UK_AC_GDA_BEAMLINE_I13I_PERSPECTIVES_DATA_EXPLORER = "uk.ac.gda.beamline.i13i.perspectives.DataExplorer";

	public final static String ID = "uk.ac.gda.beamline.i13i.perspectives.DataCollectionPerspective";

	private IPageLayout factory;

	public DataCollectionPerspective() {
		super();
	}

	@Override
	public void createInitialLayout(IPageLayout factory) {
		this.factory = factory;
		addViews();
		addActionSets();
		addNewWizardShortcuts();
		addPerspectiveShortcuts();
		addViewShortcuts();
	}

	private void addViews() {
		// Creates the overall folder layout.
		// Note that each new Folder uses a percentage of the remaining EditorArea.

		String editorArea = factory.getEditorArea();
		factory.addStandaloneView(ViewFactoryIds.StatusViewID, false, IPageLayout.TOP, 0.1f, editorArea);
		IViewLayout statusLayout = factory.getViewLayout(ViewFactoryIds.StatusViewID);
		statusLayout.setCloseable(false);
		statusLayout.setMoveable(false);

		IFolderLayout top = factory.createFolder("top", IPageLayout.TOP, (float) 0.4, editorArea);
		top.addView("uk.ac.gda.beamline.i13i.DetectorPlot");
		top.addPlaceholder("uk.ac.gda.beamline.i13i.NormalisedImage");

		IFolderLayout leftTop = factory.createFolder("leftTop", IPageLayout.LEFT, (float) 0.50, "top"); //$NON-NLS-1$
//		left.addView(IPageLayout.ID_PROJECT_EXPLORER);
		leftTop.addView(JythonTerminalView.ID);
		
		IFolderLayout bottom = factory.createFolder("bottom", IPageLayout.LEFT, (float) 0.95, editorArea);

		bottom.addView(ViewFactoryIds.AlignmentViewID);
		bottom.addPlaceholder(LivePlotView.ID);
		bottom.addPlaceholder("org.eclipse.ui.browser.view");
		bottom.addPlaceholder("data.dispenser.browser");
		bottom.addPlaceholder("org.eclipse.ui.browser.view:data.dispenser.browser");
		bottom.addPlaceholder("uk.ac.diamond.scisoft.analysis.rcp.plotViewDP");
		bottom.addPlaceholder(CommandQueueViewFactory.ID);

		IFolderLayout leftBottom = factory.createFolder("leftBottom", IPageLayout.LEFT, (float) 0.50, "bottom"); //$NON-NLS-1$
		

		leftBottom.addView(CameraViewPart.ID);
		

	}

	private void addActionSets() {
		factory.addActionSet(IPageLayout.ID_NAVIGATE_ACTION_SET); // NON-NLS-1
	}

	private void addPerspectiveShortcuts() {
		factory.addPerspectiveShortcut(UK_AC_GDA_BEAMLINE_I13I_PERSPECTIVES_DATA_EXPLORER); // NON-NLS-1
	}

	private void addNewWizardShortcuts() {
		factory.addNewWizardShortcut("org.eclipse.ui.wizards.new.folder");// NON-NLS-1
		factory.addNewWizardShortcut("org.eclipse.ui.wizards.new.file");// NON-NLS-1
	}

	@SuppressWarnings("deprecation")
	private void addViewShortcuts() {
		factory.addShowViewShortcut(IPageLayout.ID_RES_NAV);
		factory.addShowViewShortcut(IPageLayout.ID_PROBLEM_VIEW);
		factory.addShowViewShortcut(IPageLayout.ID_OUTLINE);
	}

}
