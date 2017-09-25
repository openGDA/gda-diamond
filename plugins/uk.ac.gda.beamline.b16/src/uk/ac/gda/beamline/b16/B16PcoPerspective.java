/*-
 * Copyright © 2015 Diamond Light Source Ltd.
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

import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPerspectiveFactory;

public class B16PcoPerspective implements IPerspectiveFactory {

	public static final String ID = "uk.ac.gda.beamline.b16.B16PcoPerspective";
	private static final String IDPlotView1d = "org.dawb.workbench.plotting.views.toolPageView.1D";
	private static final String IDPlotView2d = "org.dawb.workbench.plotting.views.toolPageView.fixed";
	private static final String secondaryId = "pv//PCO//BL16B-EA-DET-03@";
	//private static final String secondaryId = "pv//SIMAD//BL07I-TST-DET-01@";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		addViews(layout);
	}

	private void addViews(IPageLayout layout) {
		layout.setEditorAreaVisible(false);
		String editorArea = layout.getEditorArea();

		float splitLR = 0.33f;
		IFolderLayout leftBottomFolder = layout.createFolder(
				"B16Pco_left_bottom",
				IPageLayout.LEFT,
				splitLR,
				editorArea);
		leftBottomFolder.addView(gda.rcp.views.JythonTerminalView.ID);
		leftBottomFolder.addView(uk.ac.gda.views.baton.BatonView.ID);
		leftBottomFolder.addPlaceholder("org.eclipse.ui.console.ConsoleView");
		leftBottomFolder.addPlaceholder("org.eclipse.ui.views.ProgressView");

		IFolderLayout leftTopFolder = layout.createFolder(
				"B16_left_top",
				IPageLayout.TOP,
				0.33f,
				"B16Pco_left_bottom");
		leftTopFolder.addPlaceholder(uk.ac.gda.client.liveplot.LivePlotView.ID);
		//file-explorer placeholder perhaps? project?

		IFolderLayout rightTopFolder = layout.createFolder(
				"B16Pco_right_top",
				IPageLayout.RIGHT,
				1.0f - splitLR,
				editorArea);
		rightTopFolder.addView(uk.ac.gda.epics.adviewer.views.TwoDArrayView.ID + ":" + secondaryId);

		IFolderLayout rightMiddleFolder = layout.createFolder(
				"B16Pco_right_middle",
				IPageLayout.BOTTOM,
				0.4f,
				"B16Pco_right_top");
		rightMiddleFolder.addView(IDPlotView1d);

		IFolderLayout rightBottomFolder = layout.createFolder(
				"B16Pco_right_bottom",
				IPageLayout.BOTTOM,
				0.25f,
				"B16Pco_right_middle");
		rightBottomFolder.addView(IDPlotView2d + ":org.dawb.workbench.plotting.tools.lineProfileTool");
	}
}
