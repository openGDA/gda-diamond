package uk.ac.gda.beamline.i11.lde.persepctives;

import org.eclipse.search.ui.NewSearchUI;
import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.console.IConsoleConstants;
import org.eclipse.ui.progress.IProgressConstants;
import org.opengda.lde.ui.views.ChildrenTableView;
import org.opengda.lde.ui.views.DataCollectionStatus;
import org.opengda.lde.ui.views.LiveImageView;
import org.opengda.lde.ui.views.ReducedDataPlotView;
import org.opengda.lde.ui.views.SampleGroupView;
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
	private static final String SAMPLE_TABLE_FOLDER = "sampleTableFolder";
	private static final String DETECTOR_PLOT_FOLDER = "detectorPlotFolder";
	private static final String DETECTOR_FOLDER = "detectorFolder";
	private static final String SCAN_PLOT_FOLDER="scanPlotFolder";
	private static final String PROPERTIES_FOLDER="propertiesFolder";
	private static final String DATA_COLLECTION_STATUS_FOLDER="dataCollectionStatusFolder";
	
	private static final String CHILDREN_TABLE_VIEW_ID = ChildrenTableView.ID;
	private static final String PIXIUM_IMAGE_VIEW_ID = LiveImageView.ID;
	private static final String PIXIUM_PLOT_VIEW_ID = ReducedDataPlotView.ID;
	private static final String DETECTOR_PLOT_VIEW_ID = DetectorFilePlotView.ID;
	private static final String SCAN_PLOT_VIEW_ID = LivePlotView.ID;
	private static final String GDA_NAVIGATOR_VIEW_ID = "uk.ac.gda.client.navigator";
	private static final String STATUS_VIEW_ID = "uk.ac.gda.beamline.i11.lde.views.statusView";
	private static final String DETECTOR_VIEW_ID = PixiumView.ID;
	private static final String DATA_COLLECTION_STATUS_VIEW_ID = DataCollectionStatus.ID;
	private static final String SERVER_SAMPLES_VIEW_ID=SampleGroupView.ID;

	@Override
	public void createInitialLayout(IPageLayout layout) {
		layout.setFixed(false);
		defineLayout(layout);
		defineActions(layout);
	}

	private void defineActions(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		layout.setEditorAreaVisible(true);
		IFolderLayout statusFolder =  layout.createFolder(STATUS_FOLDER, IPageLayout.BOTTOM, (float)0.5, editorArea);
		statusFolder.addView(STATUS_VIEW_ID);

		IFolderLayout topLeft = layout.createFolder(PROJ_FOLDER, IPageLayout.LEFT, (float)0.10, editorArea); //$NON-NLS-1$
        topLeft.addView(IPageLayout.ID_PROJECT_EXPLORER);
        topLeft.addPlaceholder(GDA_NAVIGATOR_VIEW_ID);

        IFolderLayout sampleTableFolder=layout.createFolder(SAMPLE_TABLE_FOLDER, IPageLayout.BOTTOM, (float)0.60, editorArea); //$NON-NLS-1$
        sampleTableFolder.addView(CHILDREN_TABLE_VIEW_ID);
        sampleTableFolder.addView(SERVER_SAMPLES_VIEW_ID);
        
        IFolderLayout propertiesFolder=layout.createFolder(PROPERTIES_FOLDER, IPageLayout.RIGHT, (float)0.15, editorArea);
        propertiesFolder.addView(IPageLayout.ID_PROP_SHEET);
        
        IFolderLayout detectorFolder=layout.createFolder(DETECTOR_FOLDER, IPageLayout.RIGHT, (float)0.24, PROPERTIES_FOLDER); //$NON-NLS-1$
        detectorFolder.addView(DETECTOR_VIEW_ID);

        IFolderLayout dataCollectionStatusFolder=layout.createFolder(DATA_COLLECTION_STATUS_FOLDER, IPageLayout.RIGHT, (float)0.37, DETECTOR_FOLDER); //$NON-NLS-1$
        dataCollectionStatusFolder.addView(DATA_COLLECTION_STATUS_VIEW_ID);

        IFolderLayout detectorPlotFolder=layout.createFolder(DETECTOR_PLOT_FOLDER, IPageLayout.TOP, (float)0.75, STATUS_FOLDER); //$NON-NLS-1$
        detectorPlotFolder.addView(PIXIUM_IMAGE_VIEW_ID);
        detectorPlotFolder.addView(DETECTOR_PLOT_VIEW_ID);

        IFolderLayout scanPlotFolder= layout.createFolder(SCAN_PLOT_FOLDER, IPageLayout.RIGHT, (float)0.33, DETECTOR_PLOT_FOLDER); //$NON-NLS-1$
        scanPlotFolder.addView(PIXIUM_PLOT_VIEW_ID);
        scanPlotFolder.addView(SCAN_PLOT_VIEW_ID);
        
        IFolderLayout terminalfolder= layout.createFolder(TERMINAL_FOLDER, IPageLayout.RIGHT, (float)0.5, SCAN_PLOT_FOLDER); //$NON-NLS-1$
        terminalfolder.addView(JythonTerminalView.ID);
        terminalfolder.addView(IPageLayout.ID_PROBLEM_VIEW);
        terminalfolder.addPlaceholder(NewSearchUI.SEARCH_VIEW_ID);
        terminalfolder.addPlaceholder(IConsoleConstants.ID_CONSOLE_VIEW);
        terminalfolder.addPlaceholder(IPageLayout.ID_BOOKMARKS);
        terminalfolder.addPlaceholder(IProgressConstants.PROGRESS_VIEW_ID);
        
        // add status here
        //IFolderLayout sideStatusFolder = layout.createFolder("statusFolder", IPageLayout.RIGHT, 0.5f, Scan_PLOT_FOLDER);

        layout.addPerspectiveShortcut(JythonPerspective.ID);
        layout.addShowViewShortcut(SERVER_SAMPLES_VIEW_ID);
        layout.addShowViewShortcut(CHILDREN_TABLE_VIEW_ID);
        layout.addShowViewShortcut(PIXIUM_IMAGE_VIEW_ID);
        layout.addShowViewShortcut(PIXIUM_PLOT_VIEW_ID);
        layout.addShowViewShortcut(DETECTOR_PLOT_VIEW_ID);
        layout.addShowViewShortcut(LivePlotView.ID);
        layout.addShowViewShortcut(JythonTerminalView.ID);
        layout.addShowViewShortcut(IPageLayout.ID_PROJECT_EXPLORER);
	}

	private void defineLayout(IPageLayout layout) {
        layout.addNewWizardShortcut(PythonProjectWizard.WIZARD_ID); //$NON-NLS-1$        
        layout.addNewWizardShortcut(PythonSourceFolderWizard.WIZARD_ID); //$NON-NLS-1$        
        layout.addNewWizardShortcut(PythonPackageWizard.WIZARD_ID); //$NON-NLS-1$        
        layout.addNewWizardShortcut(PythonModuleWizard.WIZARD_ID); //$NON-NLS-1$        
        layout.addNewWizardShortcut("org.eclipse.ui.wizards.new.folder");//$NON-NLS-1$
        layout.addNewWizardShortcut("org.eclipse.ui.wizards.new.file");//$NON-NLS-1$
        layout.addNewWizardShortcut("org.eclipse.ui.editors.wizards.UntitledTextFileWizard");//$NON-NLS-1$

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
