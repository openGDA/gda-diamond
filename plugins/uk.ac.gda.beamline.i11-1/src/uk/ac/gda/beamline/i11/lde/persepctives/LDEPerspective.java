package uk.ac.gda.beamline.i11.lde.persepctives;

import org.eclipse.search.ui.NewSearchUI;
import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.console.IConsoleConstants;
import org.eclipse.ui.progress.IProgressConstants;
import org.python.pydev.ui.wizards.files.PythonModuleWizard;
import org.python.pydev.ui.wizards.files.PythonPackageWizard;
import org.python.pydev.ui.wizards.files.PythonSourceFolderWizard;
import org.python.pydev.ui.wizards.project.PythonProjectWizard;

import gda.rcp.views.JythonTerminalView;
import uk.ac.gda.beamline.synoptics.views.DetectorFilePlotView;
import uk.ac.gda.client.liveplot.LivePlotView;
import uk.ac.gda.client.scripting.JythonPerspective;
import uk.ac.gda.epics.client.pixium.views.PixiumView;

public class LDEPerspective implements IPerspectiveFactory {

	public static final String ID="uk.ac.gda.beamline.i11.lde.perspective";

	private static final String TERMINAL_FOLDER = "terminalFolder";
	private static final String PROJ_FOLDER = "projectFolder";
	private static final String STATUS_FOLDER = "statusFolder";
	private static final String DETECTOR_PLOT_FOLDER = "detectorPlotFolder";
	private static final String DETECTOR_FOLDER = "detectorFolder";
	private static final String SCAN_PLOT_FOLDER="scanPlotFolder";

	private static final String DETECTOR_PLOT_VIEW_ID = DetectorFilePlotView.ID;
	private static final String SCAN_PLOT_VIEW_ID = LivePlotView.ID;
	private static final String GDA_NAVIGATOR_VIEW_ID = "uk.ac.gda.client.navigator";
	private static final String STATUS_VIEW_ID = "uk.ac.gda.beamline.i11.lde.views.statusView";
	private static final String DETECTOR_VIEW_ID = PixiumView.ID;

	@Override
	public void createInitialLayout(IPageLayout layout) {
		layout.setFixed(false);
		defineLayout(layout);
		defineActions(layout);
	}

	private void defineActions(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		IFolderLayout statusFolder =  layout.createFolder(STATUS_FOLDER, IPageLayout.BOTTOM, (float)0.85, editorArea);
		statusFolder.addView(STATUS_VIEW_ID);

		IFolderLayout topLeft = layout.createFolder(PROJ_FOLDER, IPageLayout.LEFT, (float)0.15, editorArea);
        topLeft.addView(IPageLayout.ID_PROJECT_EXPLORER);
        topLeft.addPlaceholder(GDA_NAVIGATOR_VIEW_ID);



        IFolderLayout detectorPlotFolder=layout.createFolder(DETECTOR_PLOT_FOLDER, IPageLayout.BOTTOM, (float)0.5, editorArea);
        detectorPlotFolder.addView("uk.ac.gda.client.live.stream.view.LiveStreamView:pixium_live_stream#EPICS_ARRAY");
        detectorPlotFolder.addView(DETECTOR_PLOT_VIEW_ID);

        IFolderLayout scanPlotFolder= layout.createFolder(SCAN_PLOT_FOLDER, IPageLayout.RIGHT, (float)0.33, DETECTOR_PLOT_FOLDER);
        scanPlotFolder.addView(SCAN_PLOT_VIEW_ID);

        IFolderLayout detectorFolder=layout.createFolder(DETECTOR_FOLDER, IPageLayout.RIGHT, (float)0.5, editorArea);
        detectorFolder.addView(DETECTOR_VIEW_ID);

        IFolderLayout terminalfolder= layout.createFolder(TERMINAL_FOLDER, IPageLayout.RIGHT, (float)0.5, SCAN_PLOT_FOLDER);
        terminalfolder.addView(JythonTerminalView.ID);
        terminalfolder.addView(IPageLayout.ID_PROBLEM_VIEW);
        terminalfolder.addPlaceholder(NewSearchUI.SEARCH_VIEW_ID);
        terminalfolder.addPlaceholder(IConsoleConstants.ID_CONSOLE_VIEW);
        terminalfolder.addPlaceholder(IPageLayout.ID_BOOKMARKS);
        terminalfolder.addPlaceholder(IProgressConstants.PROGRESS_VIEW_ID);


        layout.addPerspectiveShortcut(JythonPerspective.ID);
	}

	private void defineLayout(IPageLayout layout) {
        layout.addNewWizardShortcut(PythonProjectWizard.WIZARD_ID);
        layout.addNewWizardShortcut(PythonSourceFolderWizard.WIZARD_ID);
        layout.addNewWizardShortcut(PythonPackageWizard.WIZARD_ID);
        layout.addNewWizardShortcut(PythonModuleWizard.WIZARD_ID);
        layout.addNewWizardShortcut("org.eclipse.ui.wizards.new.folder");
        layout.addNewWizardShortcut("org.eclipse.ui.wizards.new.file");
        layout.addNewWizardShortcut("org.eclipse.ui.editors.wizards.UntitledTextFileWizard");

        layout.addShowViewShortcut(NewSearchUI.SEARCH_VIEW_ID);
        layout.addShowViewShortcut(IConsoleConstants.ID_CONSOLE_VIEW);
        layout.addShowViewShortcut(IPageLayout.ID_OUTLINE);
        layout.addShowViewShortcut(IPageLayout.ID_PROBLEM_VIEW);
        layout.addShowViewShortcut(GDA_NAVIGATOR_VIEW_ID);
        layout.addShowViewShortcut("org.eclipse.pde.runtime.LogView");
        layout.addShowViewShortcut(IPageLayout.ID_TASK_LIST);
        layout.addShowViewShortcut("org.python.pydev.views.PyRefactorView");
        layout.addShowViewShortcut("org.python.pydev.views.PyCodeCoverageView");
        layout.addShowViewShortcut("org.eclipse.ui.navigator.ProjectExplorer");

        layout.addActionSet(IPageLayout.ID_NAVIGATE_ACTION_SET);
    }

}
