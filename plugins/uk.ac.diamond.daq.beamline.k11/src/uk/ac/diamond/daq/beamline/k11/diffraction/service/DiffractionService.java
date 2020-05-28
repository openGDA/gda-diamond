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

package uk.ac.diamond.daq.beamline.k11.diffraction.service;

import java.io.File;
import java.net.URL;

import org.springframework.context.ApplicationListener;

import uk.ac.diamond.daq.beamline.k11.diffraction.event.DiffractionRunAcquisitionEvent;
import uk.ac.diamond.daq.beamline.k11.diffraction.service.message.DiffractionRunMessage;
import uk.ac.gda.tomography.service.Arrangement;

/**
 * Defines service operation for Diffraction process.
 *
 * @author Maurizio Nagni
 *
 */
public interface DiffractionService extends ApplicationListener<DiffractionRunAcquisitionEvent> {

	void resetInstruments(Arrangement arrangement) throws DiffractionServiceException;

	/**
	 * Executes an acquisition driven by a script using a message as configuration.
	 * Depending on the outcome runs an error script or a success script
	 *
	 * @param message
	 * @param script
	 * @param onError
	 * @param onSuccess
	 * @throws DiffractionServiceException
	 */
	void runAcquisition(DiffractionRunMessage message, File script, File onError, File onSuccess)
			throws DiffractionServiceException;

	URL takeDarkImage(DiffractionRunMessage message, File script)
			throws DiffractionServiceException;

	URL takeFlatImage(DiffractionRunMessage message, File script)
			throws DiffractionServiceException;
}
