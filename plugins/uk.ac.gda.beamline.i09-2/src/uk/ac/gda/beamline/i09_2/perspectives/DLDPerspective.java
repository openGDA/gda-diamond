package uk.ac.gda.beamline.i09_2.perspectives;

import org.eclipse.search.ui.NewSearchUI;
import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.progress.IProgressConstants;
import org.python.pydev.ui.wizards.files.PythonModuleWizard;
import org.python.pydev.ui.wizards.files.PythonPackageWizard;
import org.python.pydev.ui.wizards.files.PythonSourceFolderWizard;
import org.python.pydev.ui.wizards.project.PythonProjectWizard;

import gda.rcp.views.JythonTerminalView;
import uk.ac.gda.beamline.i09_2.addons.ResetMovingSumAddon;
import uk.ac.gda.client.live.stream.view.LiveStreamView;
import uk.ac.gda.client.livecontrol.LiveControlsView;
import uk.ac.gda.client.liveplot.LivePlotView;
import uk.ac.gda.client.scripting.JythonPerspective;
import uk.ac.gda.views.baton.BatonView;

public class DLDPerspective implements IPerspectiveFactory {

	public static final String ID="uk.ac.gda.beamline.i09-2.perspectives.DLD";

	private static final String TERMINAL_FOLDER = "terminalFolder";
	private static final String PROJ_FOLDER = "projFolder";
	private static final String STATUS_FOLDER = "statusFolder";
	private static final String PLOT_1D_FOLDER = "Plot1DFolder";
	private static final String PLOT_2D_FOLDER = "Plot2DFolder";
	private static final String ACCUM_PLOT_FOLDER = "accumulatedPlotFolder";

	private static final String GDA_NAVIGATOR_VIEW_ID = "uk.ac.gda.client.navigator";
	private static final String STATUS_VIEW_ID = "uk.ac.gda.beamline.i09-2.statusView";

	private static final String TOOLPAGE_FOLDER = "toolpageFolder";
	private static final String DLD_CONTROL_FOLDER="dldcontrol";
	private static final String LIVE_CONTROL_FOLDER="livecontrol";
	private static final String DASHBOARD_FOLDER = "dashboard";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		layout.setFixed(false);
		defineLayout(layout);
		defineActions(layout);
		activateAddons();
	}

	private void activateAddons() {
		ResetMovingSumAddon resetMovingSumAddon = new ResetMovingSumAddon();
		resetMovingSumAddon.configure();
	}

	private void defineLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		layout.setEditorAreaVisible(false);

		// left row
		IFolderLayout left = layout.createFolder(PROJ_FOLDER, IPageLayout.LEFT, (float)0.15, editorArea); //$NON-NLS-1$
		left.addView(IPageLayout.ID_PROJECT_EXPLORER);
		left.addPlaceholder(GDA_NAVIGATOR_VIEW_ID);
		left.addPlaceholder("uk.ac.diamond.sda.navigator.views.FileView");

		IFolderLayout liveBeamlineControlFolder=layout.createFolder(LIVE_CONTROL_FOLDER, IPageLayout.TOP, (float)0.7, PROJ_FOLDER); //$NON-NLS-1$
		liveBeamlineControlFolder.addView(LiveControlsView.ID + ":beamline_control_set");
		liveBeamlineControlFolder.addPlaceholder(LiveControlsView.ID + ":*");
		liveBeamlineControlFolder.addPlaceholder(LiveControlsView.ID);
		liveBeamlineControlFolder.addPlaceholder(IPageLayout.ID_OUTLINE);

		IFolderLayout dashboardFolder=layout.createFolder(DASHBOARD_FOLDER, IPageLayout.TOP, (float)0.2, LIVE_CONTROL_FOLDER); //$NON-NLS-1$
		dashboardFolder.addView("uk.ac.gda.rcp.views.dashboardView");

		IFolderLayout dldLiveControlFolder=layout.createFolder(DLD_CONTROL_FOLDER, IPageLayout.TOP, (float)0.2, DASHBOARD_FOLDER); //$NON-NLS-1$
		dldLiveControlFolder.addView(LiveControlsView.ID + ":dld_count_rate");

		// middle row
		IFolderLayout statusFolder =  layout.createFolder(STATUS_FOLDER, IPageLayout.LEFT, (float)0.4, editorArea);
		statusFolder.addView(STATUS_VIEW_ID);
		statusFolder.addPlaceholder(BatonView.ID);
		statusFolder.addPlaceholder(IProgressConstants.PROGRESS_VIEW_ID);
		statusFolder.addPlaceholder("org.eclipse.ui.console.ConsoleView");

		IFolderLayout terminalfolder= layout.createFolder(TERMINAL_FOLDER, IPageLayout.BOTTOM, (float)0.4, STATUS_FOLDER); //$NON-NLS-1$
		terminalfolder.addView(JythonTerminalView.ID);
		terminalfolder.addPlaceholder(IPageLayout.ID_PROBLEM_VIEW);
		terminalfolder.addPlaceholder(IProgressConstants.PROGRESS_VIEW_ID);
		terminalfolder.addPlaceholder(NewSearchUI.SEARCH_VIEW_ID);
		terminalfolder.addPlaceholder(IPageLayout.ID_BOOKMARKS);

		IFolderLayout scanPlotFolder=layout.createFolder(PLOT_1D_FOLDER, IPageLayout.TOP, (float)0.4, TERMINAL_FOLDER); //$NON-NLS-1$
		scanPlotFolder.addView(LivePlotView.ID);
		scanPlotFolder.addPlaceholder("org.dawnsci.mapping.ui.spectrumview");

		// third row
		IFolderLayout detectorPlotFolder=layout.createFolder(PLOT_2D_FOLDER, IPageLayout.RIGHT, (float)0.3, editorArea); //$NON-NLS-1$
		detectorPlotFolder.addView("uk.ac.gda.beamline.i09-2.dld.live.stream.view.LiveImageXY:dld_liveimagexy#EPICS_ARRAY");
		detectorPlotFolder.addPlaceholder(LiveStreamView.ID+":*");
		detectorPlotFolder.addPlaceholder("org.dawb.workbench.views.dataSetView");

		// forth row
		IFolderLayout accumPlotFolder=layout.createFolder(ACCUM_PLOT_FOLDER, IPageLayout.RIGHT, (float)0.5, PLOT_2D_FOLDER); //$NON-NLS-1$
		accumPlotFolder.addView("uk.ac.gda.beamline.i09-2.dld.live.stream.view.AccumImageXY:dld_accumimagexy#EPICS_ARRAY");
		accumPlotFolder.addView("uk.ac.gda.beamline.i09-2.dld.live.stream.view.ES32AccumImageXY:es32_liveview#EPICS_ARRAY");
	}

	private void defineActions(IPageLayout layout) {
		layout.addPerspectiveShortcut(DLDPerspective.ID);
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
