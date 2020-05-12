/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

import gda.configuration.properties.LocalProperties;
import uk.ac.diamond.daq.beamline.k11.view.DiffractionScanSelection;
import uk.ac.diamond.daq.beamline.k11.view.PerspectiveDashboard;
import uk.ac.diamond.daq.beamline.k11.view.TomographyConfigurationView;
import uk.ac.diamond.daq.experiment.ui.plan.DetectorFramePeekView;
import uk.ac.diamond.daq.experiment.ui.plan.PlanManagerView;
import uk.ac.diamond.daq.experiment.ui.plan.PlanOverview;
import uk.ac.diamond.daq.experiment.ui.plan.PlanProgressPlotView;

public final class K11DefaultViews {

	private K11DefaultViews() {
		// static access only
	}

	public static final String PERSPECTIVE_DASHBOARD_VIEW = PerspectiveDashboard.ID;
	public static final String JYTON_CONSOLE_VIEW = "gda.rcp.jythonterminalview";

	public static final String MAPPED_DATA = "org.dawnsci.mapping.ui.mappeddataview";
	public static final String MAP_VIEW = "org.dawnsci.mapping.ui.mapview";

	public static final String SPECTRUM_VIEW = "org.dawnsci.mapping.ui.spectrumview";
	public static final String MAPPING_EXPERIMENT_VIEW = "uk.ac.diamond.daq.mapping.ui.experiment.mappingExperimentView";

	public static final String SCAN_SETUP_VIEW = DiffractionScanSelection.ID;

	public static final String TOMOGRAPHY_ACQUISITION_CONFIGURATION = TomographyConfigurationView.ID;

	public static final String PLAN_MANAGER = PlanManagerView.ID;
	public static final String PLAN_PROGRESS_PLOT = PlanProgressPlotView.ID;
	public static final String PLAN_OVERVIEW = PlanOverview.ID;
	public static final String DETECTOR_FRAME_PEEK = DetectorFramePeekView.ID;

	public static final String getQueueId() {
		String queueViewId = StatusQueueView.createId(LocalProperties.get(LocalProperties.GDA_ACTIVEMQ_BROKER_URI, ""),
				"org.eclipse.scanning.api",
				"org.eclipse.scanning.api.event.status.StatusBean",
				EventConstants.STATUS_TOPIC,
				EventConstants.SUBMISSION_QUEUE);
		return queueViewId + "partName=Queue";
	}
}
