/*-
 * Copyright © 2023 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11;

import org.eclipse.scanning.api.event.scan.ScanBean;
import org.eclipse.scanning.api.event.status.StatusBean;
import org.eclipse.scanning.event.ui.view.QueuedScanRepeatHandler;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.client.exception.GDAClientRestException;
import uk.ac.gda.ui.tool.rest.ClientRestServices;


/**
 * This rerun handler generates new filepaths for each repetition
 * to avoid overwriting data (a small but important K11 quirk!).
 */
public class ExperimentAwareRerunHandler extends QueuedScanRepeatHandler {

	private static final Logger logger = LoggerFactory.getLogger(ExperimentAwareRerunHandler.class);

	@Override
	public boolean isHandled(StatusBean bean) {
		return super.isHandled(bean) && bean instanceof ScanBean;
	}

	@Override
	protected StatusBean duplicate(StatusBean bean) throws Exception {
		var duplicate = (ScanBean) super.duplicate(bean);
		duplicate.setFilePath(null);
		duplicate.getScanRequest().setFilePath(requestFilePath(duplicate.getName()));
		return duplicate;
	}

	private String requestFilePath(String name) {
		try {
			return ClientRestServices.getExperimentController().prepareAcquisition(name).getPath();
		} catch (GDAClientRestException e) {
			logger.error("Error generating experiment-compatible file path - experiment file will not link to this measurement!", e);
			return null;
		}
	}

}
