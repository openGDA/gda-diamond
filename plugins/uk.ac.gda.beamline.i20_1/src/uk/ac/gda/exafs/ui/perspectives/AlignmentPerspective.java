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

package uk.ac.gda.exafs.ui.perspectives;

import gda.rcp.views.JythonTerminalView;

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.IViewLayout;

import uk.ac.gda.exafs.ui.views.AlignmentStageCalibrationView;
import uk.ac.gda.exafs.ui.views.BeamlineAlignmentView;
import uk.ac.gda.exafs.ui.views.EdeManualCalibrationPlotView;
import uk.ac.gda.exafs.ui.views.FocusingView;
import uk.ac.gda.exafs.ui.views.SingleSpectrumView;

/**
 * Shows recent data from the XH detector for I20-1 EDE branchline.
 */
public class AlignmentPerspective implements IPerspectiveFactory {

	public static final String ID = "uk.ac.gda.beamline.i20_1.AlignmentPerspective";

	// plot where snapshot spectra placed
	public static String SPECTRAPLOTID =  "uk.ac.diamond.scisoft.analysis.rcp.liveModePlot";
	public static String SPECTRAPLOTNAME =  "Live Mode";

	public static String SINGLE_SPECTRUM_PLOT_VIEW_NAME = "Single spectrum plot";
	public static String SINGLE_SPECTRUM_PLOT_VIEW_ID = "uk.ac.gda.beamline.i20_1.SingleSpectrumPlot";

	public static final String REF_PLOT_NAME = "Reference Spectrum";

	public static final String EDE_PLOT_NAME = "EDE Data Spectrum";

	private static final String TOPPLOT_FOLDER_ID = "topplot";
	private static final String ALIGNMENT_CONTROLS_FOLDER_ID = "alignmentControls";
	private static final String FOCUSING_CONTROLS_FOLDER_ID = "focusingControls";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		layout.setEditorAreaVisible(false);

		IFolderLayout alignmentControlsFolder = layout.createFolder(ALIGNMENT_CONTROLS_FOLDER_ID, IPageLayout.LEFT, 0.32f, editorArea);
		alignmentControlsFolder.addView(BeamlineAlignmentView.ID);
		IViewLayout propertyLayout = layout.getViewLayout(BeamlineAlignmentView.ID);
		propertyLayout.setCloseable(false);
		alignmentControlsFolder.addView(SingleSpectrumView.ID);

		IFolderLayout focusingControlsFolder = layout.createFolder(FOCUSING_CONTROLS_FOLDER_ID, IPageLayout.LEFT, 0.32f, editorArea);
		focusingControlsFolder.addView(FocusingView.ID);
		propertyLayout = layout.getViewLayout(FocusingView.ID);
		propertyLayout.setCloseable(false);
		focusingControlsFolder.addView(AlignmentStageCalibrationView.ID);

		IFolderLayout topPlotFolder = layout.createFolder(TOPPLOT_FOLDER_ID, IPageLayout.RIGHT, 0.40f, FOCUSING_CONTROLS_FOLDER_ID);
		topPlotFolder.addView(SPECTRAPLOTID);
		topPlotFolder.addPlaceholder(SINGLE_SPECTRUM_PLOT_VIEW_ID);
		topPlotFolder.addPlaceholder(EdeManualCalibrationPlotView.REFERENCE_ID);
		topPlotFolder.addPlaceholder(EdeManualCalibrationPlotView.EDE_ID);
		topPlotFolder.addPlaceholder("uk.ac.gda.client.liveplotview");
		layout.addView(JythonTerminalView.ID, IPageLayout.BOTTOM, 0.6f,TOPPLOT_FOLDER_ID);
	}
}
