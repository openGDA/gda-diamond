/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

import uk.ac.gda.exafs.ede.alignment.ui.DetectorLiveModeView;
import uk.ac.gda.exafs.ede.experiment.ui.CyclicExperimentView;
import uk.ac.gda.exafs.ede.experiment.ui.ExperimentSingleSpectrumView;
import uk.ac.gda.exafs.ede.experiment.ui.LinearExperimentView;
import uk.ac.gda.exafs.plotting.ui.ExperimentDataPlotView;

public class ExperimentPerspective implements IPerspectiveFactory {

	private static final String EXPERIMENT_CONTROLS_FOLDER_ID = "experimentControls";
	private static final String TOPPLOT_FOLDER_ID = "topplot";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		layout.setEditorAreaVisible(false);

		IFolderLayout alignmentControlsFolder = layout.createFolder(EXPERIMENT_CONTROLS_FOLDER_ID, IPageLayout.LEFT, 0.65f, editorArea);
		alignmentControlsFolder.addView(ExperimentSingleSpectrumView.ID);
		alignmentControlsFolder.addView(LinearExperimentView.LINEAR_EXPERIMENT_VIEW_ID);
		alignmentControlsFolder.addView(CyclicExperimentView.CYCLIC_EXPERIMENT_VIEW_ID);

		IFolderLayout topPlotFolder = layout.createFolder(TOPPLOT_FOLDER_ID, IPageLayout.RIGHT, 0.60f, EXPERIMENT_CONTROLS_FOLDER_ID);
		topPlotFolder.addView(DetectorLiveModeView.ID);
		topPlotFolder.addView(ExperimentDataPlotView.ID);
		layout.addView(JythonTerminalView.ID, IPageLayout.BOTTOM, 0.6f,TOPPLOT_FOLDER_ID);
	}
}