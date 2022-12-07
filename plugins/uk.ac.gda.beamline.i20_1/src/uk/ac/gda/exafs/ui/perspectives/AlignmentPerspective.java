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

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.IViewLayout;

import gda.jython.InterfaceProvider;
import gda.rcp.views.JythonTerminalView;
import uk.ac.gda.exafs.alignment.ui.AlignmentStageCalibrationView;
import uk.ac.gda.exafs.alignment.ui.BeamlineAlignmentView;
import uk.ac.gda.exafs.alignment.ui.DetectorLiveModeView;
import uk.ac.gda.exafs.alignment.ui.DetectorRoiView;
import uk.ac.gda.exafs.alignment.ui.SampleStageMotorsView;
import uk.ac.gda.exafs.plotting.ui.ExperimentDataPlotView;

/**
 * Shows recent data from the XH detector for I20-1 EDE branchline.
 */
public class AlignmentPerspective implements IPerspectiveFactory {

	public static final String ID = "uk.ac.gda.beamline.i20_1.AlignmentPerspective";
	public static final String LIVE_PLOT_VIEW_ID = "uk.ac.gda.client.liveplotview";

	public static String SINGLE_SPECTRUM_PLOT_VIEW_NAME = "Single Spectrum";
	public static String SINGLE_SPECTRUM_PLOT_VIEW_ID = "uk.ac.gda.exafs.ui.views.singlespectrumplotview";

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

		IFolderLayout focusingControlsFolder = layout.createFolder(FOCUSING_CONTROLS_FOLDER_ID, IPageLayout.LEFT, 0.32f, editorArea);
		focusingControlsFolder.addView(DetectorRoiView.ID);
		focusingControlsFolder.addView(SampleStageMotorsView.ID);
		propertyLayout = layout.getViewLayout(SampleStageMotorsView.ID);
		propertyLayout.setCloseable(false);
		focusingControlsFolder.addView(AlignmentStageCalibrationView.ID);

		IFolderLayout topPlotFolder = layout.createFolder(TOPPLOT_FOLDER_ID, IPageLayout.RIGHT, 0.40f, FOCUSING_CONTROLS_FOLDER_ID);
		topPlotFolder.addView(DetectorLiveModeView.ID);
		topPlotFolder.addView(ExperimentDataPlotView.ID);
		layout.addView(JythonTerminalView.ID, IPageLayout.BOTTOM, 0.6f,TOPPLOT_FOLDER_ID);

		InterfaceProvider.getScanDataPointProvider().addScanEventObserver(new PlotStyleUpdater());
	}
}
