package uk.ac.gda.beamline.i10.perspectives;

import java.util.Arrays;
import java.util.List;

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

import gda.configuration.properties.LocalProperties;
import gda.rcp.views.JythonTerminalView;
import uk.ac.diamond.daq.mapping.ui.experiment.MappingPerspective;
import uk.ac.gda.client.live.stream.view.LiveStreamView;
import uk.ac.gda.client.live.stream.view.LiveStreamViewWithHistogram;
import uk.ac.gda.client.live.stream.view.SnapshotView;
import uk.ac.gda.client.liveplot.LivePlotView;
import uk.ac.gda.client.scripting.JythonPerspective;

public class AreaDetectorPerspective implements IPerspectiveFactory {

	public final static String ID="uk.ac.gda.beamline.i10.perspectives.areadetector";

	private static final String TERMINAL_FOLDER = "terminalFolder";
	private static final String PROJ_FOLDER = "projFolder";
	private static final String STATUS_FOLDER = "statusFolder";
	private static final String PLOT_1D_FOLDER = "Plot1DFolder";
	private static final String PLOT_2D_FOLDER = "Plot2DFolder";

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
		layout.setEditorAreaVisible(false);
		List<String> profiles = Arrays.asList(LocalProperties.getStringArray("gda.spring.profiles.active"));

		IFolderLayout topLeft = layout.createFolder(PROJ_FOLDER, IPageLayout.LEFT, (float)0.65, editorArea); //$NON-NLS-1$
		topLeft.addView(IPageLayout.ID_PROJECT_EXPLORER);
		topLeft.addPlaceholder(GDA_NAVIGATOR_VIEW_ID);
		topLeft.addPlaceholder("uk.ac.diamond.sda.navigator.views.FileView");

		IFolderLayout bottomLeftfolder =  layout.createFolder(STATUS_FOLDER, IPageLayout.BOTTOM, (float)0.86, PROJ_FOLDER);
		bottomLeftfolder.addView(STATUS_VIEW_ID);
		bottomLeftfolder.addPlaceholder(uk.ac.gda.views.baton.BatonView.ID);
		bottomLeftfolder.addPlaceholder(IProgressConstants.PROGRESS_VIEW_ID);
		bottomLeftfolder.addPlaceholder("org.eclipse.ui.console.ConsoleView");

		IFolderLayout topMiddlefolder=layout.createFolder(PLOT_1D_FOLDER, IPageLayout.RIGHT, (float)0.20, PROJ_FOLDER); //$NON-NLS-1$
		topMiddlefolder.addView(LivePlotView.ID);
		topMiddlefolder.addPlaceholder("org.dawnsci.mapping.ui.spectrumview");
		topMiddlefolder.addPlaceholder("uk.ac.diamond.scisoft.analysis.rcp.plotView1");
		topMiddlefolder.addView(ToolPageView.FIXED_VIEW_ID+":org.dawb.workbench.plotting.tools.region.editor");
		topMiddlefolder.addPlaceholder(ToolPageView.FIXED_VIEW_ID+":org.dawnsci.plotting.histogram.histogram_tool_page_2");
		topMiddlefolder.addPlaceholder(ToolPageView.TOOLPAGE_1D_VIEW_ID);
		topMiddlefolder.addPlaceholder(ToolPageView.TOOLPAGE_2D_VIEW_ID);
		topMiddlefolder.addPlaceholder(SnapshotView.ID);

        IFolderLayout middlefolder = layout.createFolder(TERMINAL_FOLDER,IPageLayout.BOTTOM, 0.58f, PLOT_1D_FOLDER);
        middlefolder.addView(gda.rcp.views.JythonTerminalView.ID);

        middlefolder.addView("uk.ac.gda.client.livecontrol.LiveControlsView");

        IFolderLayout topRightFolder=layout.createFolder(PLOT_2D_FOLDER, IPageLayout.LEFT, (float)0.5, editorArea); //$NON-NLS-1$
		if (profiles.contains("scattering")) {
			topRightFolder.addView("uk.ac.gda.beamline.i10.pimte.live.stream.view.LiveStreamViewWithHistogram:pimte_cam#EPICS_ARRAY");
			topRightFolder.addView("uk.ac.gda.beamline.i10.pixis.live.stream.view.LiveStreamViewWithHistogram:pixis_cam#EPICS_ARRAY");
		}
		topRightFolder.addPlaceholder(LiveStreamView.ID+":*");
		topRightFolder.addPlaceholder(LiveStreamViewWithHistogram.ID+":*");
		topRightFolder.addPlaceholder("org.dawb.workbench.views.dataSetView");
		topRightFolder.addPlaceholder(IPageLayout.ID_OUTLINE);

	}

	private void defineActions(IPageLayout layout) {
        layout.addPerspectiveShortcut(AreaDetectorPerspective.ID);
        layout.addPerspectiveShortcut(I10ScanPerspective.ID);
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
