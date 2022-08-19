/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

package uk.ac.gda.sixd.perspectives;

import java.util.List;

import org.dawnsci.datavis.api.IRecentPlaces;
import org.eclipse.scanning.api.event.queues.QueueViews;
import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.osgi.framework.BundleContext;
import org.osgi.framework.FrameworkUtil;

import gda.jython.InterfaceProvider;
import gda.rcp.views.JythonTerminalView;
import gda.rcp.views.dashboard.DashboardView;
import uk.ac.gda.client.liveplot.LivePlotView;
import uk.ac.gda.sixd.views.I07DatasetPart;
import uk.ac.gda.sixd.views.I07LoadedFilePart;
import uk.ac.gda.views.baton.BatonView;

public class I07ScanPerspective implements IPerspectiveFactory {

	private static final String DATAVIS_PLOT_ID = "org.dawnsci.datavis.view.parts.Plot";
	private static final String DATAVIS_FILES = I07LoadedFilePart.getId();
	private static final String DATAVIS_DATASETS = I07DatasetPart.getId();
	private static final String JYTHON_VIEW = JythonTerminalView.ID;
	private static final String QUEUE_VIEW = QueueViews.getQueueViewID();
	private static final List<String> DETECTOR_PLOTS = List.of("uk.ac.gda.sixd.views.Pilatus1",
			"uk.ac.gda.sixd.views.Pilatus2", "uk.ac.gda.sixd.views.Pilatus3", "uk.ac.gda.sixd.views.Excalibur");
	private static final String BATON_VIEW = BatonView.ID;
	private static final String DASHBOARD_VIEW = DashboardView.ID;
	private static final String OLD_PLOT_VIEW = LivePlotView.getID();

	/** This perspective's ID */
	static final String ID = "uk.ac.gda.client.sixd.I07ScanPerspective";

	public static String getId() {
		return ID;
	}

	@Override
	public void createInitialLayout(IPageLayout layout) {
		addViews(layout);
		initialiseRecentPlaces();
	}

	private void addViews(IPageLayout layout) {
		layout.setEditorAreaVisible(true);
		String editorArea = layout.getEditorArea();

		String leftTop = "I07_left_top";
		IFolderLayout leftTopFolder = layout.createFolder(leftTop, IPageLayout.LEFT, 0.35f, editorArea);
		leftTopFolder.addView(JYTHON_VIEW);

		String rightBottom = "I07_right_bottom";
		IFolderLayout rightBottomFolder = layout.createFolder(rightBottom, IPageLayout.RIGHT, 0.75f, editorArea);
		rightBottomFolder.addView(DATAVIS_DATASETS);

		String middleTop = "I07_middle_top";
		IFolderLayout middleTopFolder = layout.createFolder(middleTop, IPageLayout.TOP, 0.6f, editorArea);
		middleTopFolder.addView(DATAVIS_PLOT_ID);
		DETECTOR_PLOTS.forEach(middleTopFolder::addView);
		middleTopFolder.addPlaceholder(OLD_PLOT_VIEW); // just in case this opens

		String leftBottom = "I07_left_bottom";
		IFolderLayout leftBottomFolder = layout.createFolder(leftBottom, IPageLayout.BOTTOM, 0.75f, leftTop);
		leftBottomFolder.addView(QUEUE_VIEW);
		leftBottomFolder.addView(DASHBOARD_VIEW);
		leftBottomFolder.addView(BATON_VIEW);

		String rightTop = "I07_right_top";
		IFolderLayout rightTopFolder = layout.createFolder(rightTop, IPageLayout.TOP, 0.5f, rightBottom);
		rightTopFolder.addView(DATAVIS_FILES);
	}

	private void initialiseRecentPlaces() {
		BundleContext bundleContext = FrameworkUtil.getBundle(this.getClass()).getBundleContext();
		IRecentPlaces recentPlaces = bundleContext.getService(bundleContext.getServiceReference(IRecentPlaces.class));
		// "sub" is not a real directory, this just initialises recent places with the parent dir of "sub"
		recentPlaces.addFiles(InterfaceProvider.getPathConstructor().getClientVisitSubdirectory("sub"));
	}
}
