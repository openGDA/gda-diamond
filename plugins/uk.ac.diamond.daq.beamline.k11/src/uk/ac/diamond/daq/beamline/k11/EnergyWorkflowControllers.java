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

package uk.ac.diamond.daq.beamline.k11;

import uk.ac.diamond.daq.beamline.configuration.api.ConfigurationWorkflow;
import uk.ac.diamond.daq.client.gui.energy.EnergyWorkflowController;
import uk.ac.diamond.daq.client.gui.energy.EnergyWorkflowController.EnergySelectionType;

/**
 * Holds K11's energy workflow controllers
 */
public class EnergyWorkflowControllers {

	private static EnergyWorkflowController imagingEnergyController;
	private static EnergyWorkflowController diffractionEnergyController;

	private EnergyWorkflowControllers() throws IllegalAccessException {
		throw new IllegalAccessException("Static access only");
	}

	public static EnergyWorkflowController getImagingEnergyController() {
		if (imagingEnergyController == null) {
			imagingEnergyController = new EnergyWorkflowController(EnergySelectionType.MONO,
					imagingMono, null);
		}
		return imagingEnergyController;
	}

	public static EnergyWorkflowController getDiffractionEnergyController() {
		if (diffractionEnergyController == null) {
			diffractionEnergyController = new EnergyWorkflowController(EnergySelectionType.BOTH,
					diffractionMono, diffractionPoly);
		}
		return diffractionEnergyController;
	}

	private static ConfigurationWorkflow diffractionMono;
	private static ConfigurationWorkflow diffractionPoly;
	private static ConfigurationWorkflow imagingMono;

	public static void setDiffractionMono(ConfigurationWorkflow diffractionMono) {
		EnergyWorkflowControllers.diffractionMono = diffractionMono;
	}

	public static void setDiffractionPoly(ConfigurationWorkflow diffractionPoly) {
		EnergyWorkflowControllers.diffractionPoly = diffractionPoly;
	}

	public static void setImagingMono(ConfigurationWorkflow imagingMono) {
		EnergyWorkflowControllers.imagingMono = imagingMono;
	}
}
