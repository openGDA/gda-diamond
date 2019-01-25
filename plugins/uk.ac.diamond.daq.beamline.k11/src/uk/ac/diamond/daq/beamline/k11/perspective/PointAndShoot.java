/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

public class PointAndShoot implements IPerspectiveFactory {

	public static final String ID = "uk.ac.diamond.daq.beamline.k11.perspective.PointAndShootPerspective";

	private static final Logger logger = LoggerFactory.getLogger(PointAndShoot.class);

	@Override
	public void createInitialLayout(IPageLayout layout) {

		logger.trace("Building K11 Point and Shoot perspective");
		layout.setEditorAreaVisible(false);

		final IFolderLayout left = layout.createFolder("experimentmanagement", IPageLayout.RIGHT, 0.2f, IPageLayout.ID_EDITOR_AREA);
		left.addView("uk.ac.diamond.daq.beamline.k11.experiment");
		IViewLayout vLayout = layout.getViewLayout("uk.ac.diamond.daq.beamline.k11.experiment");
		vLayout.setCloseable(false);
		left.addView("org.dawnsci.mapping.ui.mappeddataview");
		vLayout = layout.getViewLayout("org.dawnsci.mapping.ui.mappeddataview");
		vLayout.setCloseable(false);

		final IFolderLayout dataLayout = layout.createFolder("mappeddata", IPageLayout.RIGHT, 0.2f, "experimentmanagement");
		dataLayout.addView("org.dawnsci.mapping.ui.mapview");
		vLayout = layout.getViewLayout("org.dawnsci.mapping.ui.mapview");
		vLayout.setCloseable(false);

		final IFolderLayout mappingParams = layout.createFolder("scansetup", IPageLayout.RIGHT, 0.58f, "mappeddata");
		mappingParams.addView("uk.ac.diamond.daq.beamline.k11.scanSetup");
		vLayout = layout.getViewLayout("uk.ac.diamond.daq.beamline.k11.scanSetup");
		vLayout.setCloseable(false);
		mappingParams.addView("uk.ac.diamond.daq.mapping.ui.experiment.mappingExperimentView");
		vLayout = layout.getViewLayout("uk.ac.diamond.daq.mapping.ui.experiment.mappingExperimentView");
		vLayout.setCloseable(false);

		final IFolderLayout dataoutLayout = layout.createFolder("spectrum", IPageLayout.BOTTOM, 0.5f, "mappeddata");
		dataoutLayout.addView("org.dawnsci.mapping.ui.spectrumview");
		vLayout = layout.getViewLayout("org.dawnsci.mapping.ui.spectrumview");
		vLayout.setCloseable(false);

		final IFolderLayout folderLayout = layout.createFolder("console_folder", IPageLayout.BOTTOM, 0.65f, "scansetup");
		folderLayout.addView("gda.rcp.jythonterminalview");
		String queueViewId = StatusQueueView.createId(LocalProperties.get(LocalProperties.GDA_ACTIVEMQ_BROKER_URI, ""),
				"org.eclipse.scanning.api",
				"org.eclipse.scanning.api.event.status.StatusBean",
				EventConstants.STATUS_SET,
				EventConstants.STATUS_TOPIC,
				EventConstants.SUBMISSION_QUEUE);


		queueViewId = queueViewId + "partName=Queue";
		folderLayout.addView(queueViewId);

		logger.trace("Finished building K11 Point and Shoot perspective");
	}
}
