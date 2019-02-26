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

	private static final String EV_STRING = "eV";
	private static final String PERANGSTROM_STRING = "\u00c5\u207b\u00b9";

	private static final double ENERGY_EV = 8932.2489387;
	private static final double VECTOR_PER_ANGSTROM = 44.4632177;

	private static final double EDGE_ENERGY_KEV = 1.4;

	/**
	 * Converts a value using temporary values for the edge energy and twoD.
	 */
	@Test
	public void testConvertWithValues() {
		double twoD = 0.0;
		double edgeEnergy = 0.0;
		double value = 0.0;
		String convertFromUnit = null;
		String convertToUnit = null;

		convertFromUnit = "eV";
		convertToUnit = "KeV";

		Converter.convert(value, convertFromUnit, convertToUnit, edgeEnergy, twoD);

		convertFromUnit = "eV";
		convertToUnit = "mDeg";

		Converter.convert(value, convertFromUnit, convertToUnit, edgeEnergy, twoD);

		convertFromUnit = "eV";
		convertToUnit = "Ang";

		Converter.convert(value, convertFromUnit, convertToUnit, edgeEnergy, twoD);

		convertFromUnit = "eV";
		convertToUnit = "PerAngstrom";

		Converter.convert(value, convertFromUnit, convertToUnit, edgeEnergy, twoD);
	}

	//----------------------------------------------------------------------------------------
	// Convert eV -> PerAngstrom
	//----------------------------------------------------------------------------------------
	@Test
	public void testConvertEvToPerAngstromZero() {
		Converter.setEdgeEnergy(0);
		assertEquals(0.0, Converter.convert(0.0, EV_STRING, PERANGSTROM_STRING), FP_TOLERANCE);
	}

	@Test
	public void testConvertEvToPerAngstrom() {
		Converter.setEdgeEnergy(EDGE_ENERGY_KEV);
		assertEquals(VECTOR_PER_ANGSTROM, Converter.convert(ENERGY_EV, EV_STRING, PERANGSTROM_STRING), FP_TOLERANCE);
	}

	/*----------------------------------------------------------------------------------------------
	 * Convert from Per-Angstrom
	 *
	 * testConvertPerAngstromToEvZero() is ignored because of unpredictable results
	 *
	 * - When run individually, it fails with a ClassCastException, thrown by Quantity.valueOf():
	 * this is presumably a bug in the JScience Quantity class, which may be fixed in JScience4
	 *
	 * - When run as part of the whole class, Quantity.valueOf() successfully creates the
	 * Quantity, but PhotonEnergy.photonEnergyOf() returns a null photon energy, which then
	 * causes a NullPointerException. This should probably be fixed in Converter.
	 * ----------------------------------------------------------------------------------------------*/
	@Ignore("Not run because of unpredictable results")
	@Test
	public void testConvertPerAngstromToEvZero() {
		Converter.setEdgeEnergy(0);
		Converter.convert(0.0, PERANGSTROM_STRING, EV_STRING);
	}

	@Test
	public void testConvertPerAngstromToEv() {
		Converter.setEdgeEnergy(EDGE_ENERGY_KEV);
		assertEquals(ENERGY_EV, Converter.convert(VECTOR_PER_ANGSTROM, PERANGSTROM_STRING, EV_STRING), FP_TOLERANCE);
	}

	/*---------------------------------------------------------------------------------------------
	 * Test round-trip conversion
	 * ----------------------------------------------------------------------------------------------*/
	@Test
	public void testRoundTripConversionEv() {
		Converter.setEdgeEnergy(EDGE_ENERGY_KEV);
		final double perAngstrom = Converter.convert(ENERGY_EV, EV_STRING, PERANGSTROM_STRING);
		final double eV = Converter.convert(perAngstrom, PERANGSTROM_STRING, EV_STRING);
		assertEquals(ENERGY_EV, eV, FP_TOLERANCE);
	}

	@Test
	public void testRoundTripConversionPerAngstrom() {
		Converter.setEdgeEnergy(EDGE_ENERGY_KEV);
		final double eV = Converter.convert(VECTOR_PER_ANGSTROM, PERANGSTROM_STRING, EV_STRING);
		final double perAngstrom = Converter.convert(eV, EV_STRING, PERANGSTROM_STRING);
		assertEquals(VECTOR_PER_ANGSTROM, perAngstrom, FP_TOLERANCE);
	}

}
