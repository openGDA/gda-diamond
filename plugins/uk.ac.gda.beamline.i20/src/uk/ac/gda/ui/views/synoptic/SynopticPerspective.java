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
	private static final String SYNOPTICVIEWS_PERSPECTIVE_ID = "synopticViewsPerspective";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		layout.setEditorAreaVisible(false);

		// Motor offset view
		IFolderLayout xesOffsetFolder = layout.createFolder("XES_POSITIONS_FOLDER", IPageLayout.RIGHT, 0.1f, SYNOPTICVIEWS_PERSPECTIVE_ID);
		IFolderLayout simulatedPositionsFolder = layout.createFolder("XES_SIMULATED_POSITIONS", IPageLayout.BOTTOM, 0.5f, "XES_POSITIONS_FOLDER");
		simulatedPositionsFolder.addView(LiveControlsView.ID+":xesSimulatedPosition");
		simulatedPositionsFolder.addView("uk.ac.gda.ui.views.synoptic.xesOffsetView");

		// XES stage view
		IFolderLayout xesStageFolder = layout.createFolder("XES_STAGE", IPageLayout.LEFT, 0.43f, SYNOPTICVIEWS_PERSPECTIVE_ID);
		xesStageFolder.addView(SynopticView.ID+":xesStageView");

		// Crystal analysers and calibration views
		IFolderLayout xesCalibrationFolder = layout.createFolder("XES_ANALYSERS", IPageLayout.LEFT, 0.7f, SYNOPTICVIEWS_PERSPECTIVE_ID);
		IFolderLayout xesCrystalsFolder = layout.createFolder("XES_CRYSTALS", IPageLayout.TOP, 0.78f, "XES_ANALYSERS");
		xesCrystalsFolder.addView(SynopticView.ID+":xesAnalysersView");

		IFolderLayout xesCalibrationControlsFolder = layout.createFolder("XES_CALIB_CONTROLS", IPageLayout.BOTTOM, 0.2f, "XES_ANALYSERS");
		xesCalibrationControlsFolder.addView("uk.ac.gda.ui.views.synoptic.xesCalibrationView");
	}
}
