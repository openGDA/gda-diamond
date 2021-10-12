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

package uk.ac.gda.beamline.i06_1.perspectives;

import java.util.Arrays;
import java.util.List;

import org.dawnsci.plotting.views.ToolPageView;
import org.eclipse.search.ui.NewSearchUI;
import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.python.pydev.ui.wizards.files.PythonModuleWizard;
import org.python.pydev.ui.wizards.files.PythonPackageWizard;
import org.python.pydev.ui.wizards.files.PythonSourceFolderWizard;
import org.python.pydev.ui.wizards.project.PythonProjectWizard;

import gda.configuration.properties.LocalProperties;
import gda.rcp.views.JythonTerminalView;
import uk.ac.gda.client.live.stream.view.LiveStreamView;
import uk.ac.gda.client.live.stream.view.LiveStreamViewWithHistogram;
import uk.ac.gda.client.live.stream.view.SnapshotView;
import uk.ac.gda.client.liveplot.LivePlotView;
import uk.ac.gda.client.scripting.JythonPerspective;
import uk.ac.gda.nano.views.DiffractionAndDichroismView;
import uk.ac.gda.nano.views.RegionalisedScanView;
import uk.ac.gda.nano.views.SuperConductingMagnetView;

public class Experiment implements IPerspectiveFactory {

	static final String ID = "uk.ac.gda.beamline.i06_1.perspectives.Experiment";

	private static final String TERMINAL_FOLDER = "terminalFolder";
	private static final String PROJ_FOLDER = "projFolder";
	private static final String PLOT_1D_FOLDER = "Plot1DFolder";
	private static final String PLOT_2D_FOLDER = "Plot2DFolder";

	private static final String GDA_NAVIGATOR_VIEW_ID = "uk.ac.gda.client.navigator";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		layout.setFixed(false);
		defineLayout(layout);
		defineActions(layout);
	}

	private void defineLayout(IPageLayout layout) {
		layout.setEditorAreaVisible(true);

		IFolderLayout bottomLeftfolder =  layout.createFolder(PROJ_FOLDER, IPageLayout.LEFT, (float)0.33, IPageLayout.ID_EDITOR_AREA);
		bottomLeftfolder.addView(IPageLayout.ID_PROJECT_EXPLORER);
		bottomLeftfolder.addView(uk.ac.gda.views.baton.BatonView.ID);
		bottomLeftfolder.addPlaceholder(GDA_NAVIGATOR_VIEW_ID);
		bottomLeftfolder.addPlaceholder(IPageLayout.ID_OUTLINE);

		IFolderLayout topRightFolder=layout.createFolder(PLOT_2D_FOLDER, IPageLayout.RIGHT, (float)0.53, IPageLayout.ID_EDITOR_AREA); //$NON-NLS-1$
		List<String> profiles = Arrays.asList(LocalProperties.getStringArray("gda.spring.profiles.active"));
		if (profiles.contains("DD")) {
			topRightFolder.addView("uk.ac.gda.beamline.i06-1.pixis.live.stream.view.LiveStreamViewWithHistogram:pixis#EPICS_ARRAY");
		}
		topRightFolder.addPlaceholder(LiveStreamViewWithHistogram.ID+":*");
		topRightFolder.addPlaceholder(LiveStreamView.ID);
		topRightFolder.addPlaceholder(LiveStreamView.ID+":*");

		IFolderLayout topMiddlefolder=layout.createFolder(PLOT_1D_FOLDER, IPageLayout.TOP, (float)0.6, IPageLayout.ID_EDITOR_AREA); //$NON-NLS-1$
		topMiddlefolder.addView(LivePlotView.ID);
		topMiddlefolder.addPlaceholder(ToolPageView.FIXED_VIEW_ID+":org.dawb.workbench.plotting.tools.region.editor");
		topMiddlefolder.addPlaceholder(ToolPageView.FIXED_VIEW_ID+":org.dawnsci.plotting.histogram.histogram_tool_page_2");
		topMiddlefolder.addPlaceholder(ToolPageView.TOOLPAGE_1D_VIEW_ID);
		topMiddlefolder.addPlaceholder(ToolPageView.TOOLPAGE_2D_VIEW_ID);
		topMiddlefolder.addPlaceholder(SnapshotView.ID);

		IFolderLayout topLeftfolder = layout.createFolder(TERMINAL_FOLDER, IPageLayout.TOP, (float)0.6, PROJ_FOLDER); //$NON-NLS-1$
		topLeftfolder.addView(gda.rcp.views.JythonTerminalView.ID);
		topLeftfolder.addView(RegionalisedScanView.ID);
		if (profiles.contains("magnet")) {
			topLeftfolder.addView(SuperConductingMagnetView.ID);
		}
		if (profiles.contains("DD")) {
			topLeftfolder.addView(DiffractionAndDichroismView.ID);
		}

	}

	private void defineActions(IPageLayout layout) {
        layout.addPerspectiveShortcut(JythonPerspective.ID);
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
