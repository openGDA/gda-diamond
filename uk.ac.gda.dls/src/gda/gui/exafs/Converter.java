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

import static gda.jscience.physics.units.NonSIext.PER_ANGSTROM;
import static si.uom.SI.ELECTRON_VOLT;

import javax.measure.Quantity;
import javax.measure.quantity.Energy;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jscience.physics.quantities.QuantityConverters;
import gda.jscience.physics.quantities.WaveVector;
import gda.jscience.physics.units.NonSIext;
import tec.units.indriya.quantity.Quantities;

/**
 * A class to convert between the various units used in XAFS
 */

public class Converter {
	private static final Logger logger = LoggerFactory.getLogger(Converter.class);

	static {
		// Ensure GDA-specific units are initialised
		NonSIext.initializeClass();
	}

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
		final Quantity<Energy> edgeEnergyQuantity = Quantities.getQuantity(edgeEnergy, ELECTRON_VOLT);
		final Quantity<Energy> electronEnergyQuantity = Quantities.getQuantity(electronEnergy, ELECTRON_VOLT);
		final Quantity<WaveVector> waveVector = QuantityConverters.waveVectorOf(edgeEnergyQuantity, electronEnergyQuantity);
		return waveVector.getValue().doubleValue();
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
		final Quantity<Energy> edgeEnergyQuantity = Quantities.getQuantity(edgeEnergy, ELECTRON_VOLT);
		final Quantity<WaveVector> waveVector = Quantities.getQuantity(waveVectorValue, PER_ANGSTROM);
		final Quantity<Energy> energy = QuantityConverters.photonEnergyFromEdgeAndVector(edgeEnergyQuantity, waveVector);
		return energy.to(ELECTRON_VOLT).getValue().doubleValue();
	}
}
