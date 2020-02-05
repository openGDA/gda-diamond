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

public interface K11DefaultViews {
	String TOMO_MAIN_VIEW = "uk.ac.diamond.daq.beamline.k11.tomography";
	String JYTON_CONSOLE_VIEW = "gda.rcp.jythonterminalview";

	String EXPERIMENT = "uk.ac.diamond.daq.beamline.k11.experiment";

	String MAPPED_DATA = "org.dawnsci.mapping.ui.mappeddataview";
	String MAP_VIEW = "org.dawnsci.mapping.ui.mapview";

	String SPECTRUM_VIEW = "org.dawnsci.mapping.ui.spectrumview";
	String MAPPING_EXPERIMENT_VIEW = "uk.ac.diamond.daq.mapping.ui.experiment.mappingExperimentView";

	String SCAN_SETUP_VIEW = "uk.ac.diamond.daq.beamline.k11.scanSetup";

	String TOMOGRAPHY_ACQUISITION_CONFIGURATION = "uk.ac.gda.tomography.scan.editor.view.TomographyConfigurationView";

	static String getQueueId() {
		String queueViewId = StatusQueueView.createId(LocalProperties.get(LocalProperties.GDA_ACTIVEMQ_BROKER_URI, ""),
				"org.eclipse.scanning.api",
				"org.eclipse.scanning.api.event.status.StatusBean",
				EventConstants.STATUS_TOPIC,
				EventConstants.SUBMISSION_QUEUE);
		return queueViewId + "partName=Queue";
	}
}
