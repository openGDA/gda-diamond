package uk.ac.gda.beamline.i21.perspectives;

import org.dawb.workbench.ui.perspective.DataBrowsingPerspective;
import org.dawnsci.mapping.ui.MappingPerspective;
import org.dawnsci.plotting.views.ToolPageView;
import org.dawnsci.processing.ui.ProcessingPerspective;
import org.eclipse.scanning.api.event.EventConstants;
import org.eclipse.scanning.api.event.queues.QueueViews;
import org.eclipse.scanning.api.event.scan.ScanBean;
import org.eclipse.scanning.api.ui.CommandConstants;
import org.eclipse.scanning.device.ui.device.DetectorView;
import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.IViewLayout;
import org.osgi.framework.FrameworkUtil;

import uk.ac.gda.client.live.stream.view.SnapshotView;
import uk.ac.gda.client.liveplot.LivePlotView;
import uk.ac.gda.client.scripting.JythonPerspective;
import uk.ac.gda.epics.adviewer.views.TwoDArrayView;

public class ScanPerspective implements IPerspectiveFactory {
	public static final String ID="uk.ac.gda.beamline.i21.perspectives.ScanPerspective";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		layout.setEditorAreaVisible(false);
		addViewShortcuts(layout);
		addPerspectiveShortcuts(layout);

		{
			IFolderLayout folderLayout = layout.createFolder("ScanDefinition", IPageLayout.RIGHT, 0.8f, IPageLayout.ID_EDITOR_AREA);
			folderLayout.addView("org.eclipse.scanning.device.ui.scanEditor");
			final String detectorId = DetectorView.createId(getUriString(), EventConstants.DEVICE_REQUEST_TOPIC, EventConstants.DEVICE_RESPONSE_TOPIC);
			folderLayout.addView(detectorId);
			folderLayout.addView("org.eclipse.scanning.device.ui.device.MonitorView");
		}
		{
			IFolderLayout folderLayout = layout.createFolder("ScanModel", IPageLayout.BOTTOM, 0.26f, "ScanDefinition");
			folderLayout.addView("org.eclipse.scanning.device.ui.modelEditor");
			folderLayout.addView("org.eclipse.scanning.device.ui.device.ControlView");
			folderLayout.addView("org.eclipse.scanning.device.ui.points.scanRegionView");
		}
		{
			IFolderLayout folderLayout = layout.createFolder("ScanValidation", IPageLayout.BOTTOM, 0.54f, "ScanModel");
			folderLayout.addView("org.eclipse.scanning.device.ui.scan.executeView");
			folderLayout.addView("uk.ac.gda.client.livecontrol.LiveControlsView");
			folderLayout.addView(getConsumerViewId());
		}
		{
			//required to see SWMR data file - i.e. data file still being filled by current data collection.
			IFolderLayout folderLayout = layout.createFolder("LiveData", IPageLayout.LEFT, 0.2f, IPageLayout.ID_EDITOR_AREA);
			folderLayout.addView("org.dawnsci.datavis.view.parts.LoadedFilePart");
			IViewLayout vLayout = layout.getViewLayout("org.dawnsci.datavis.view.parts.LoadedFilePart");
			vLayout.setCloseable(false);
		}
		{
			//required to access Existing data and Non-SWMR files, and scripts
			IFolderLayout folderLayout = layout.createFolder("StoredData", IPageLayout.BOTTOM, 0.66f, "LiveData");
			folderLayout.addView(IPageLayout.ID_PROJECT_EXPLORER);
		}
		{
			IFolderLayout folder = layout.createFolder("LiveControl", IPageLayout.RIGHT, 0.05f, IPageLayout.ID_EDITOR_AREA);
			folder.addView("gda.rcp.jythonterminalview");
			folder.addView(getQueueViewId());
		}
		{
			IFolderLayout folderLayout = layout.createFolder("DataDisplay", IPageLayout.TOP, 0.66f, "LiveControl");
			folderLayout.addView("org.dawnsci.datavis.view.parts.Plot");
			IViewLayout vLayout = layout.getViewLayout("org.dawnsci.datavis.view.parts.Plot");
			vLayout.setCloseable(false);
			folderLayout.addPlaceholder("uk.ac.gda.client.live.stream.view.LiveStreamView:*");
			folderLayout.addPlaceholder(TwoDArrayView.ID+":*");
			folderLayout.addPlaceholder(LivePlotView.ID);
			folderLayout.addPlaceholder("org.eclipse.scanning.device.ui.spectrumview"); //don't know which one works
			folderLayout.addPlaceholder("org.dawnsci.mapping.ui.spectrumview");
		}
		{
			IFolderLayout folderLayout = layout.createFolder("folder_6", IPageLayout.RIGHT, 0.63f, "DataDisplay");
			folderLayout.addView("org.dawnsci.datavis.view.parts.DatasetPart");
			IViewLayout vLayout = layout.getViewLayout("org.dawnsci.datavis.view.parts.DatasetPart");
			vLayout.setCloseable(false);
			folderLayout.addPlaceholder(SnapshotView.ID);
			folderLayout.addPlaceholder(ToolPageView.TOOLPAGE_2D_VIEW_ID);
			folderLayout.addView("org.eclipse.scanning.device.ui.vis.visualiseView"); // the map displaying scan path
		}
	}
	
	private String getUriString() {
		String broker = CommandConstants.getScanningBrokerUri();
		if (broker==null) broker = "tcp://localhost:61616";
		return broker;
	}
	
	private static String getConsumerViewId() {
		return "org.eclipse.scanning.event.ui.consumerView:partName=Consumers";
	}
	
	private static String getQueueViewId() {
		try {
			String bundle = FrameworkUtil.getBundle(ScanBean.class).getSymbolicName();
			return QueueViews.createId(CommandConstants.getScanningBrokerUri(), bundle, ScanBean.class.getName(), "Scans");
		} catch (Exception ne) {
			return QueueViews.getQueueViewID();
		}
	}
	
	/**
	 * Add view shortcuts to the perspective.
	 */
	private void addViewShortcuts(IPageLayout layout) {
		layout.addShowViewShortcut(LivePlotView.ID);
		layout.addShowViewShortcut("uk.ac.gda.client.live.stream.view.LiveStreamView");
	}

	/**
	 * Add perspective shortcuts to the perspective.
	 */
	private void addPerspectiveShortcuts(IPageLayout layout) {
		layout.addPerspectiveShortcut(MappingPerspective.ID);
		layout.addPerspectiveShortcut(JythonPerspective.ID);
		layout.addPerspectiveShortcut(ProcessingPerspective.ID);
		layout.addPerspectiveShortcut(DataBrowsingPerspective.ID);
	}
}
