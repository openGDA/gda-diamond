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

package uk.ac.diamond.daq.beamline.k11.diffraction.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;

import uk.ac.diamond.daq.mapping.ui.diffraction.base.DiffractionParameterAcquisition;
import uk.ac.gda.api.acquisition.AcquisitionController;

/**
 * Controls the tomography perspective delegating its subsections to other specialised controllers.
 *
 * @author Maurizio Nagni
 */
@Controller
public class DiffractionPerspectiveController {
	@Autowired
	private AcquisitionController<DiffractionParameterAcquisition> diffractionAcquisitionController;

	public AcquisitionController<DiffractionParameterAcquisition> getDiffractionAcquisitionController() {
		return diffractionAcquisitionController;
	}
}
