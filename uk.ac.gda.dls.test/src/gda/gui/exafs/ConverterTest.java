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

import org.junit.BeforeClass;
import org.junit.Test;

import gda.jscience.physics.units.NonSIext;

/**
 * Test suite for Exafs quantity converter class
 */
public class ConverterTest {
	// Tolerance for imprecision of conversions
	private static final double FP_TOLERANCE = 0.00001;

	/**
	 * The value of energy corresponding to the given wave vector differs in the 4th decimal place from the value returned by JScience2.<br>
	 * It appears that the rounding of some of the intermediate calculations is different between the two versions.<br>
	 * Since these conversions are used only in the EXAFS GUI, not in the scan itself (see comment in DAQ-2047), this is not significant.
	 */
	private static final double ENERGY_EV = 8932.248938701445;

	private static final double VECTOR_PER_ANGSTROM = 44.46321582035057;

	private static final double EDGE_ENERGY_EV = 1400.0;

	@BeforeClass
	public static void setUpClass() {
		NonSIext.initializeClass();
	}

	//----------------------------------------------------------------------------------------
	// Convert eV -> PerAngstrom
	//----------------------------------------------------------------------------------------
	@Test(expected = NullPointerException.class)
	public void testConvertEvToPerAngstromZero() {
		assertEquals(0.0, Converter.convertEnergyToWaveVector(0.0, 0.0), FP_TOLERANCE);
	}

	@Test
	public void testConvertEvToPerAngstrom() {
		assertEquals(VECTOR_PER_ANGSTROM, Converter.convertEnergyToWaveVector(ENERGY_EV, EDGE_ENERGY_EV), FP_TOLERANCE);
	}

	/*----------------------------------------------------------------------------------------------
	 * Convert Per-Angstrom -> eV
	 * ----------------------------------------------------------------------------------------------*/
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
