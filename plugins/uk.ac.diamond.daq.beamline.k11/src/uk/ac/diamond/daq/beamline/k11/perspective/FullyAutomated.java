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

import org.eclipse.scanning.api.event.EventConstants;
import org.eclipse.scanning.event.ui.view.StatusQueueView;
import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.IViewLayout;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;

public class FullyAutomated  implements IPerspectiveFactory {

	public static final String ID = "uk.ac.diamond.daq.beamline.k11.perspective.FullyAutomated";

	private static final Logger logger = LoggerFactory.getLogger(FullyAutomated.class);

	@Override
	public void createInitialLayout(IPageLayout layout) {

		logger.trace("Building K11 Fully Automated perspective");
		layout.setEditorAreaVisible(false);

		final IFolderLayout left = layout.createFolder("experimentmanagement", IPageLayout.RIGHT, 0.2f, IPageLayout.ID_EDITOR_AREA);
		left.addView("uk.ac.diamond.daq.beamline.k11.experiment");
		IViewLayout vLayout = layout.getViewLayout("uk.ac.diamond.daq.beamline.k11.experiment");
		vLayout.setCloseable(false);

		final IFolderLayout planProgressLayout = layout.createFolder("planprogress", IPageLayout.RIGHT, 0.2f, "experimentmanagement");
		planProgressLayout.addView("uk.ac.diamond.daq.experiment.ui.plan.progressPlotView");
		vLayout = layout.getViewLayout("uk.ac.diamond.daq.experiment.ui.plan.progressPlotView");
		vLayout.setCloseable(false);

		final IFolderLayout planManager = layout.createFolder("planmanager", IPageLayout.RIGHT, 0.58f, "planprogress");
		planManager.addView("uk.ac.diamond.daq.experiment.ui.plan.manager");
		vLayout = layout.getViewLayout("uk.ac.diamond.daq.experiment.ui.plan.manager");
		vLayout.setCloseable(false);

		final IFolderLayout planOverview = layout.createFolder("planoverview", IPageLayout.BOTTOM, 0.25f, "planmanager");
		planOverview.addView("uk.ac.diamond.daq.experiment.ui.plan.overview");
		vLayout = layout.getViewLayout("uk.ac.diamond.daq.experiment.ui.plan.overview");
		vLayout.setCloseable(false);


		final IFolderLayout planOutputLayout = layout.createFolder("planoutput", IPageLayout.BOTTOM, 0.6f, "planprogress");
		planOutputLayout.addView("uk.ac.diamond.daq.beamline.k11.detectorFramePeekView");
		vLayout = layout.getViewLayout("uk.ac.diamond.daq.beamline.k11.detectorFramePeekView");
		vLayout.setCloseable(false);

		final IFolderLayout folderLayout = layout.createFolder("console_folder", IPageLayout.BOTTOM, 0.65f, "planoverview");
		folderLayout.addView("gda.rcp.jythonterminalview");
		String queueViewId = StatusQueueView.createId(LocalProperties.get(LocalProperties.GDA_ACTIVEMQ_BROKER_URI, ""),
				"org.eclipse.scanning.api",
				"org.eclipse.scanning.api.event.status.StatusBean",
				EventConstants.STATUS_TOPIC,
				EventConstants.SUBMISSION_QUEUE);


		queueViewId = queueViewId + "partName=Queue";
		folderLayout.addView(queueViewId);


		logger.trace("Finished building K11 Fully Automated perspective");
	}
}
