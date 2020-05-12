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

package uk.ac.diamond.daq.beamline.k11.perspective;

import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;

import uk.ac.gda.perspectives.ThreeColumnPerspectiveLayoutBuilder;

public class FullyAutomated  implements IPerspectiveFactory {

	public static final String ID = "uk.ac.diamond.daq.beamline.k11.perspective.FullyAutomated";

	@Override
	public void createInitialLayout(IPageLayout layout) {

		ThreeColumnPerspectiveLayoutBuilder helper = new ThreeColumnPerspectiveLayoutBuilder(ID, layout);
		helper.addViewToLeftFolder(K11DefaultViews.PERSPECTIVE_DASHBOARD_VIEW, false);

		helper.addViewToCentralFolder(K11DefaultViews.PLAN_PROGRESS_PLOT, false);
		helper.addFolderThenViewToCentralFolder(K11DefaultViews.DETECTOR_FRAME_PEEK, false, 0.65f);

		helper.addViewToRightFolder(K11DefaultViews.PLAN_MANAGER, false);
		helper.addFolderThenViewToRightFolder(K11DefaultViews.PLAN_OVERVIEW, false, 0.25f);
		helper.addFolderThenViewToRightFolder(K11DefaultViews.JYTON_CONSOLE_VIEW, false, 0.5f);
		helper.addViewToRightFolder(K11DefaultViews.getQueueId(), false);
	}
}
