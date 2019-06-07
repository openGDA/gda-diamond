/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.b16;

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;

public class B16ScanPerspective implements IPerspectiveFactory {

	@Override
	public void createInitialLayout(IPageLayout layout) {
		addViews(layout);
	}

	private void addViews(IPageLayout layout) {
		layout.setEditorAreaVisible(true);
		String editorArea = layout.getEditorArea();
		float splitLR = 0.33f;





		// Middle

		final String MIDDLE_BOTTOM = "B16Scan_middle_bottom";
		IFolderLayout middleBottomFolder = layout.createFolder(MIDDLE_BOTTOM, IPageLayout.RIGHT, 0.33f, editorArea);
		middleBottomFolder.addView(uk.ac.gda.client.liveplot.LivePlotView.ID);


		// Right
		final String RIGHT_BOTTOM = "B16Scan_right_bottom";
		IFolderLayout rightBottomFolder = layout.createFolder(RIGHT_BOTTOM, IPageLayout.RIGHT, 0.5f, MIDDLE_BOTTOM);
		rightBottomFolder.addView(uk.ac.gda.client.live.stream.view.LiveStreamView.ID);

		final String MIDDLE_TOP = "B16Scan_middle_top";
		IFolderLayout middleTopFolder = layout.createFolder(MIDDLE_TOP, IPageLayout.TOP, 0.5f, MIDDLE_BOTTOM);
		middleTopFolder.addPlaceholder(uk.ac.gda.views.baton.BatonView.ID);
		middleTopFolder.addView("uk.ac.diamond.scisoft.analysis.rcp.plotViewMultiple:pil");
		middleTopFolder.addView("uk.ac.diamond.scisoft.analysis.rcp.plotViewMultiple:medipix4");
		middleTopFolder.addView("uk.ac.diamond.scisoft.analysis.rcp.plotViewMultiple:ipp2");
		middleTopFolder.addView("uk.ac.diamond.scisoft.analysis.rcp.plotViewMultiple:pcoedge");
		middleTopFolder.addView("uk.ac.diamond.scisoft.analysis.rcp.plotViewMultiple:pco4000");


		// Left

		final String LEFT_BOTTOM = "B16Scan_left_bottom";
		IFolderLayout leftBottomFolder = layout.createFolder(LEFT_BOTTOM, IPageLayout.TOP, 0.25f, editorArea);
		leftBottomFolder.addView(IPageLayout.ID_PROJECT_EXPLORER);



		final String LEFT_TOP = "B16Scan_left_top";
		IFolderLayout leftTopFolder = layout.createFolder(LEFT_TOP, IPageLayout.BOTTOM, 0.7f, editorArea);
		leftTopFolder.addView(gda.rcp.views.JythonTerminalView.ID);
		leftTopFolder.addPlaceholder("org.eclipse.ui.console.ConsoleView");
		leftTopFolder.addPlaceholder("org.eclipse.ui.views.ProgressView");



	}

}
