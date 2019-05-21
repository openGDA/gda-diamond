/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package gda.gui.exafs;

import org.jscience.physics.quantities.Energy;
import org.jscience.physics.quantities.Quantity;
import org.jscience.physics.units.NonSI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jscience.physics.quantities.PhotonEnergy;
import gda.jscience.physics.quantities.Vector;
import gda.jscience.physics.quantities.WaveVector;
import gda.jscience.physics.units.NonSIext;

/**
 * A class to convert between the various units used in XAFS
 */

public class Converter {
	private static final Logger logger = LoggerFactory.getLogger(Converter.class);

	/**
	 * Default constructor prevents this class from being instantiated as only static methods exist.
	 */
	private Converter() {
	}

	/**
	 * Convert electron energy to wave vector (per Angstrom)
	 *
	 * @param electronEnergy
	 *            in eV
	 * @param edgeEnergy
	 *            in eV
	 * @return wave vector as a double
	 */
	public static double convertEnergyToWaveVector(double electronEnergy, double edgeEnergy) {
		logger.debug("convertEnergyToWaveVector(electronEnergy = {}, edgeEnergy = {}", electronEnergy, edgeEnergy);
		final Energy edgeEnergyQuantity = Quantity.valueOf(edgeEnergy, NonSI.ELECTRON_VOLT);
		final Energy electronEnergyQuantity = Quantity.valueOf(electronEnergy, NonSI.ELECTRON_VOLT);
		final Vector waveVector = WaveVector.waveVectorOf(edgeEnergyQuantity, electronEnergyQuantity);
		return waveVector.to(NonSIext.PER_ANGSTROM).getAmount();
	}

	/**
	 * Convert wave vector (per Angstrom) to electron energy
	 *
	 * @param waveVectorValue
	 *            as a double
	 * @param edgeEnergy
	 *            in eV
	 * @return electron energy in eV
	 */
	public static double convertWaveVectorToEnergy(double waveVectorValue, double edgeEnergy) {
		logger.debug("convertWaveVectorToEnergy(waveVectorValue = {}, edgeEnergy = {}", waveVectorValue, edgeEnergy);
		final Energy edgeEnergyQuantity = Quantity.valueOf(edgeEnergy, NonSI.ELECTRON_VOLT);
		final Quantity waveVector = Quantity.valueOf(waveVectorValue, NonSIext.PER_ANGSTROM);
		final Energy energy = PhotonEnergy.photonEnergyOf(edgeEnergyQuantity, waveVector);
		return energy.to(NonSI.ELECTRON_VOLT).getAmount();
	}
}
