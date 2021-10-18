/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i15;

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;

public class I15ScanPerspective implements IPerspectiveFactory {
	static final String ID = "uk.ac.gda.beamline.I15ScanPerspective";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		defineLayout(layout);
	}

	private void defineLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();

		IFolderLayout leftfolder = layout.createFolder("left",
				IPageLayout.LEFT, 0.25f, editorArea);
		leftfolder.addView(gda.rcp.views.JythonTerminalView.ID);
		leftfolder.addPlaceholder("org.eclipse.ui.navigator.ProjectExplorer");
		leftfolder.addPlaceholder("uk.ac.diamond.sda.navigator.views.FileView");

		IFolderLayout bottomfolder = layout.createFolder("bottom",
				IPageLayout.BOTTOM, 0.8f, editorArea);
		bottomfolder.addView(uk.ac.gda.views.baton.BatonView.ID);
		bottomfolder.addView("org.dawb.workbench.plotting.views.toolPageView.1D");
		bottomfolder.addPlaceholder("org.dawb.common.ui.views.ValueView");
		bottomfolder.addPlaceholder("org.eclipse.ui.views.ProgressView");
		bottomfolder.addPlaceholder("org.eclipse.ui.console.ConsoleView");

		IFolderLayout middlefolder = layout.createFolder("middle",
				IPageLayout.RIGHT, 0.75f, editorArea);
		middlefolder.addView(uk.ac.gda.client.liveplot.LivePlotView.ID);
		middlefolder.addView("uk.ac.diamond.scisoft.analysis.rcp.plotView1");
		middlefolder.addView("org.dawb.workbench.views.dataSetView");
		middlefolder.addView("org.dawb.workbench.plotting.views.toolPageView.2D");
		middlefolder.addPlaceholder("uk.ac.gda.client.xyplotview");

		IFolderLayout rightfolder = layout.createFolder("right",
				IPageLayout.RIGHT, 0.75f, "middle");
		rightfolder.addView(gda.rcp.views.dashboard.DashboardView.ID);
		rightfolder.addView("uk.ac.diamond.scisoft.analysis.rcp.views.SidePlotView:Plot 1");
		rightfolder.addPlaceholder("uk.ac.diamond.scisoft.analysis.rcp.views.HistogramView:Plot 1");

		layout.setEditorAreaVisible(false);
	}
}
