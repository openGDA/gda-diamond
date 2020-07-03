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

package uk.ac.gda.beamline.i10.perspectives;

import org.dawnsci.mapping.ui.MappingPerspective;
import org.eclipse.search.ui.NewSearchUI;
import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.python.pydev.ui.wizards.files.PythonModuleWizard;
import org.python.pydev.ui.wizards.files.PythonPackageWizard;
import org.python.pydev.ui.wizards.files.PythonSourceFolderWizard;
import org.python.pydev.ui.wizards.project.PythonProjectWizard;

import gda.rcp.views.JythonTerminalView;
import uk.ac.gda.client.liveplot.LivePlotView;
import uk.ac.gda.client.scripting.JythonPerspective;

public class I10ScanPerspective implements IPerspectiveFactory {
	static final String ID = "uk.ac.gda.beamline.i10.perspectives.I10ScanPerspective";

	private static final String TERMINAL_FOLDER = "terminalFolder";
	private static final String PROJ_FOLDER = "projFolder";
	private static final String STATUS_FOLDER = "statusFolder";
	private static final String PLOT_1D_FOLDER = "Plot1DFolder";

	private static final String GDA_NAVIGATOR_VIEW_ID = "uk.ac.gda.client.navigator";
	private static final String STATUS_VIEW_ID = "uk.ac.gda.beamline.i10.statusView";

	private static final String TOOLPAGE_FOLDER = "toolpageFolder";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		layout.setFixed(false);
		defineLayout(layout);
		defineActions(layout);
	}

	private void defineLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();

		IFolderLayout leftfolder = layout.createFolder(PROJ_FOLDER, IPageLayout.LEFT, (float)0.65, editorArea); //$NON-NLS-1$
		leftfolder.addView(IPageLayout.ID_PROJECT_EXPLORER);
		leftfolder.addPlaceholder(GDA_NAVIGATOR_VIEW_ID);
		leftfolder.addPlaceholder("uk.ac.diamond.sda.navigator.views.FileView");

		IFolderLayout bottomLeftfolder =  layout.createFolder(STATUS_FOLDER, IPageLayout.BOTTOM, (float)0.85, PROJ_FOLDER);
		bottomLeftfolder.addView(STATUS_VIEW_ID);
		bottomLeftfolder.addPlaceholder(uk.ac.gda.views.baton.BatonView.ID);
		bottomLeftfolder.addPlaceholder("org.eclipse.ui.views.ProgressView");
		bottomLeftfolder.addPlaceholder("org.eclipse.ui.console.ConsoleView");

		IFolderLayout topMiddlefolder=layout.createFolder(PLOT_1D_FOLDER, IPageLayout.RIGHT, (float)0.25, PROJ_FOLDER); //$NON-NLS-1$
		topMiddlefolder.addView(LivePlotView.ID);
		topMiddlefolder.addPlaceholder("org.dawnsci.mapping.ui.spectrumview");
		topMiddlefolder.addPlaceholder("uk.ac.diamond.scisoft.analysis.rcp.plotView1");

        IFolderLayout middlefolder = layout.createFolder(TERMINAL_FOLDER,IPageLayout.BOTTOM, 0.5f, PLOT_1D_FOLDER);
        middlefolder.addView(gda.rcp.views.JythonTerminalView.ID);

		IFolderLayout middleRightfolder = layout.createFolder(TOOLPAGE_FOLDER, IPageLayout.BOTTOM, 0.5f, editorArea);
		middleRightfolder.addView("uk.ac.gda.client.livecontrol.LiveControlsView");
		middleRightfolder.addPlaceholder(IPageLayout.ID_OUTLINE);
		middleRightfolder.addPlaceholder("org.dawb.workbench.plotting.views.toolPageView.1D");
		middleRightfolder.addPlaceholder("org.dawb.workbench.plotting.views.toolPageView.2D");
		middleRightfolder.addPlaceholder("org.dawb.workbench.views.dataSetView");
		middleRightfolder.addPlaceholder("uk.ac.diamond.scisoft.analysis.rcp.views.SidePlotView:Plot 1");
		middleRightfolder.addPlaceholder("uk.ac.diamond.scisoft.analysis.rcp.views.HistogramView:Plot 1");


		layout.setEditorAreaVisible(false);
	}

	private void defineActions(IPageLayout layout) {
        layout.addPerspectiveShortcut(I10ScanPerspective.ID);
        layout.addPerspectiveShortcut(AreaDetectorPerspective.ID);
        layout.addPerspectiveShortcut(JythonPerspective.ID);
        layout.addPerspectiveShortcut(MappingPerspective.ID);

        layout.addNewWizardShortcut(PythonProjectWizard.WIZARD_ID); //$NON-NLS-1$
        layout.addNewWizardShortcut(PythonSourceFolderWizard.WIZARD_ID); //$NON-NLS-1$
        layout.addNewWizardShortcut(PythonPackageWizard.WIZARD_ID); //$NON-NLS-1$
        layout.addNewWizardShortcut(PythonModuleWizard.WIZARD_ID); //$NON-NLS-1$
        layout.addNewWizardShortcut("org.eclipse.ui.wizards.new.folder");//$NON-NLS-1$
        layout.addNewWizardShortcut("org.eclipse.ui.wizards.new.file");//$NON-NLS-1$
        layout.addNewWizardShortcut("org.eclipse.ui.editors.wizards.UntitledTextFileWizard");//$NON-NLS-1$

        layout.addShowViewShortcut(LivePlotView.ID);
        layout.addShowViewShortcut(JythonTerminalView.ID);
        layout.addShowViewShortcut(IPageLayout.ID_PROJECT_EXPLORER);
        layout.addShowViewShortcut(NewSearchUI.SEARCH_VIEW_ID);
        layout.addShowViewShortcut(IPageLayout.ID_OUTLINE);
        layout.addShowViewShortcut(IPageLayout.ID_PROBLEM_VIEW);
        layout.addShowViewShortcut(GDA_NAVIGATOR_VIEW_ID);
        layout.addShowViewShortcut(IPageLayout.ID_TASK_LIST);

        layout.addActionSet(IPageLayout.ID_NAVIGATE_ACTION_SET);
    }
}
