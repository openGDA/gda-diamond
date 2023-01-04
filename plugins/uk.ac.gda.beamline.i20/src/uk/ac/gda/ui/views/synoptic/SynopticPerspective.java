/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

package uk.ac.gda.ui.views.synoptic;

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;

import uk.ac.gda.client.livecontrol.LiveControlsView;

public class SynopticPerspective implements IPerspectiveFactory {
	private static final String POSITIONS_FOLDER_NAME = "XES_POSITIONS_FOLDER";
	private static final String SIMULATED_POSITIONS_FOLDER_NAME = "XES_SIMULATED_POSITIONS_FOLDER";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		layout.setEditorAreaVisible(false);

		// Simulated positions view on the right
		IFolderLayout xesOffsetFolder = layout.createFolder(POSITIONS_FOLDER_NAME, IPageLayout.RIGHT, 0.6f, editorArea);
		IFolderLayout simulatedPositionsFolder = layout.createFolder(SIMULATED_POSITIONS_FOLDER_NAME, IPageLayout.BOTTOM, 0.5f, POSITIONS_FOLDER_NAME);
		simulatedPositionsFolder.addView(LiveControlsView.ID+":lower_simulated_positions_controlset");

		// Crystal analysers views on the left
		IFolderLayout xesCalibrationFolder = layout.createFolder("XES_ANALYSERS", IPageLayout.LEFT, 0.6f, editorArea);
		IFolderLayout xesCrystalsFolder = layout.createFolder("XES_CRYSTALS", IPageLayout.TOP, 0.78f, "XES_ANALYSERS");
		xesCrystalsFolder.addView(SynopticView.ID+":spectrometerRowsPicture");
		xesCrystalsFolder.addView(LiveControlsView.ID+":all_lower_crystal_controls");
		xesCrystalsFolder.addView(LiveControlsView.ID+":lower_crystal_material_controls");
		xesCrystalsFolder.addView(LiveControlsView.ID+":lower_detector_controls");

		// Add the calibration controls below the simulation positions
		IFolderLayout xesCalibrationControlsFolder = layout.createFolder("XES_CALIB_CONTROLS", IPageLayout.BOTTOM, 0.8f, SIMULATED_POSITIONS_FOLDER_NAME);
		xesCalibrationControlsFolder.addView(LiveControlsView.ID+":lower_calibration_controlset");

		// Add offsets view to the right of simulated positions
		IFolderLayout offsetsFolder = layout.createFolder("XES_OFFSETS", IPageLayout.RIGHT, 0.5f, SIMULATED_POSITIONS_FOLDER_NAME);
		offsetsFolder.addView(LiveControlsView.ID+":lower_offsets_controlset");
	}
}


