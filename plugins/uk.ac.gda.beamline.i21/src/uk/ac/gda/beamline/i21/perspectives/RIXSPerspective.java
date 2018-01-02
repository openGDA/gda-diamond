package uk.ac.gda.beamline.i21.perspectives;

import org.dawnsci.plotting.views.ToolPageView;
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
import uk.ac.diamond.daq.mapping.ui.experiment.MappingPerspective;
import uk.ac.gda.client.live.stream.view.LiveStreamView;
import uk.ac.gda.client.live.stream.view.SnapshotView;
import uk.ac.gda.client.liveplot.LivePlotView;
import uk.ac.gda.client.scripting.JythonPerspective;

public class RIXSPerspective implements IPerspectiveFactory {

	public static final String ID="uk.ac.gda.beamline.i21.perspectives.RIXSPerspective";

	private static final String TERMINAL_FOLDER = "terminalFolder";
	private static final String PROJ_FOLDER = "projFolder";
	private static final String STATUS_FOLDER = "statusFolder";
	private static final String PLOT_1D_FOLDER = "Plot1DFolder";
	private static final String PLOT_2D_FOLDER = "Plot2DFolder";
	
	private static final String GDA_NAVIGATOR_VIEW_ID = "uk.ac.gda.client.navigator";
	private static final String STATUS_VIEW_ID = "uk.ac.gda.beamline.i21.statusView";

	private static final String TOOLPAGE_FOLDER = "toolpageFolder";
	
	@Override
	public void createInitialLayout(IPageLayout layout) {
		layout.setFixed(false);
		defineLayout(layout);
		defineActions(layout);
	}

	private void defineLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		layout.setEditorAreaVisible(false);
		
		IFolderLayout left = layout.createFolder(PROJ_FOLDER, IPageLayout.LEFT, (float)0.15, editorArea); //$NON-NLS-1$
		left.addView(IPageLayout.ID_PROJECT_EXPLORER);
		left.addView(GDA_NAVIGATOR_VIEW_ID);
        
		IFolderLayout statusFolder =  layout.createFolder(STATUS_FOLDER, IPageLayout.LEFT, (float)0.5, editorArea);
		statusFolder.addView(STATUS_VIEW_ID);
        
		IFolderLayout detectorPlotFolder=layout.createFolder(PLOT_2D_FOLDER, IPageLayout.RIGHT, (float)0.6, STATUS_FOLDER); //$NON-NLS-1$
		detectorPlotFolder.addView(LiveStreamView.ID+":andor_cam#EPICS_ARRAY");
		detectorPlotFolder.addPlaceholder("uk.ac.gda.client.live.stream.view.LiveStreamView:*");
		
		IFolderLayout toolpageFolder=layout.createFolder(TOOLPAGE_FOLDER, IPageLayout.BOTTOM, (float)0.5, PLOT_2D_FOLDER); //$NON-NLS-1$
		toolpageFolder.addPlaceholder(SnapshotView.ID);
		toolpageFolder.addPlaceholder(ToolPageView.TOOLPAGE_2D_VIEW_ID);

		IFolderLayout scanPlotFolder=layout.createFolder(PLOT_1D_FOLDER, IPageLayout.BOTTOM, (float)0.15, STATUS_FOLDER); //$NON-NLS-1$
        scanPlotFolder.addView(LivePlotView.ID);
        scanPlotFolder.addPlaceholder("org.dawnsci.mapping.ui.spectrumview");
        
        IFolderLayout terminalfolder= layout.createFolder(TERMINAL_FOLDER, IPageLayout.BOTTOM, (float)0.5, PLOT_1D_FOLDER); //$NON-NLS-1$
        terminalfolder.addView(JythonTerminalView.ID);
        terminalfolder.addView("uk.ac.gda.client.livecontrol.LiveControlsView");
        terminalfolder.addView(IPageLayout.ID_PROBLEM_VIEW);
        terminalfolder.addPlaceholder(IProgressConstants.PROGRESS_VIEW_ID);
        terminalfolder.addPlaceholder(NewSearchUI.SEARCH_VIEW_ID);
        terminalfolder.addPlaceholder(IPageLayout.ID_BOOKMARKS);
	}

	private void defineActions(IPageLayout layout) {
        layout.addPerspectiveShortcut(RIXSPerspective.ID);
        layout.addPerspectiveShortcut(JythonPerspective.ID);
        layout.addPerspectiveShortcut(MappingPerspective.ID);
        layout.addPerspectiveShortcut(ScanPerspective.ID);

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
