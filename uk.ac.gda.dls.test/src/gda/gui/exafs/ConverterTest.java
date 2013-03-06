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

import junit.framework.TestCase;

/**
 * Test suite for Exafs quantity converter class
 */
public class ConverterTest extends TestCase {
	/**
	 * @param args
	 *            command line arguments
	 */
	public static void main(String[] args) {
		junit.textui.TestRunner.run(ConverterTest.class);
	}

	/**
	 * Converts a value using previously specified values for the edge energy and twoD.
	 */
	public void testConvert() {
		// double d = Converter.convert(value, convertFromUnit, convertToUnit);
	}

	/**
	 * Converts a value using temporary values for the edge energy and twoD.
	 */
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
}
