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

import static org.junit.Assert.assertEquals;

import org.junit.Ignore;
import org.junit.Test;

/**
 * Test suite for Exafs quantity converter class
 */
public class ConverterTest {
	// Tolerance for imprecision of conversions
	private static final double FP_TOLERANCE = 0.00001;

	private static final double ENERGY_EV = 8932.2489387;
	private static final double VECTOR_PER_ANGSTROM = 44.4632177;

	private static final double EDGE_ENERGY_EV = 1400.0;

	//----------------------------------------------------------------------------------------
	// Convert eV -> PerAngstrom
	//----------------------------------------------------------------------------------------
	@Test
	public void testConvertEvToPerAngstromZero() {
		assertEquals(0.0, Converter.convertEnergyToWaveVector(0.0, 0.0), FP_TOLERANCE);
	}

	@Test
	public void testConvertEvToPerAngstrom() {
		assertEquals(VECTOR_PER_ANGSTROM, Converter.convertEnergyToWaveVector(ENERGY_EV, EDGE_ENERGY_EV), FP_TOLERANCE);
	}

	/*----------------------------------------------------------------------------------------------
	 * Convert Per-Angstrom -> eV
	 *
	 * testConvertPerAngstromToEvZero() is ignored because of unpredictable results
	 *
	 * - When run individually, it fails with a ClassCastException, thrown by Quantity.valueOf():
	 * this is presumably a bug in the JScience Quantity class, which may be fixed in JScience4
	 *
	 * - When run as part of the whole class, Quantity.valueOf() successfully creates the
	 * Quantity, but PhotonEnergy.photonEnergyOf() returns a null photon energy, which then
	 * causes a NullPointerException.
	 * This may seem wrong, but is the behaviour that the EXAFS GUI expects.
	 * ----------------------------------------------------------------------------------------------*/
	@Ignore("Not run because of unpredictable results")
	@Test(expected = NullPointerException.class)
	public void testConvertPerAngstromToEvZero() {
		Converter.convertWaveVectorToEnergy(0.0, 0.0);
	}

	@Test
	public void testConvertPerAngstromToEv() {
		assertEquals(ENERGY_EV, Converter.convertWaveVectorToEnergy(VECTOR_PER_ANGSTROM, EDGE_ENERGY_EV), FP_TOLERANCE);
	}

	/*---------------------------------------------------------------------------------------------
	 * Test round-trip conversion
	 * ----------------------------------------------------------------------------------------------*/
	@Test
	public void testRoundTripConversionEv() {
		final double perAngstrom = Converter.convertEnergyToWaveVector(ENERGY_EV, EDGE_ENERGY_EV);
		final double eV = Converter.convertWaveVectorToEnergy(perAngstrom, EDGE_ENERGY_EV);
		assertEquals(ENERGY_EV, eV, FP_TOLERANCE);
	}

	@Test
	public void testRoundTripConversionPerAngstrom() {
		final double eV = Converter.convertWaveVectorToEnergy(VECTOR_PER_ANGSTROM, EDGE_ENERGY_EV);
		final double perAngstrom = Converter.convertEnergyToWaveVector(eV, EDGE_ENERGY_EV);
		assertEquals(VECTOR_PER_ANGSTROM, perAngstrom, FP_TOLERANCE);
	}

}
