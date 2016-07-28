/*-
 * Copyright © 2016 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i20_1.utils;

import java.util.Arrays;
/**
 * Refactored from EnergyCalibrationWizardPage
 * @since 26/7/2016
 */
public class PolynomialParser {

	/**
	 *  Parse a String of format coeff1 x^power1 + coeff2 x^power2 + ..., make a double array of coefficients of each power,
	 *  suitable for using with {@link org.apache.commons.math3.analysis.polynomials.PolynomialFunction}.
	 *  <br>
	 *    For example, the input string  66.47 x^2 + 123.4*x^3 + 0.2  is converted to the array { 0.2, 0.0, 66.47, 123.4 }.
	 * <ul>
	 *  <li>Coefficients are initialized to all zero.
	 *  <li>Order of different powers in string is arbitrary; powers must be all positve integers
	 *  <li>Each term in series should be separated by + or -, separator between coefficient and x is optional (can be a space or a *)
	 *  <li>if x is missing from term, assumed coeff is for x^0; similarly x is interpreted same as x^1.
	 * </ul>
	 * @param origPolyString  Text String of format coeff1 x^power1 + coeff2 x^power2 +
	 * @return double array of polynomial coefficients.
	 * @since 6/4/2016
	 */
	static public double[] extractCoefficientsFromString( String origPolyString ) {
		final String xSymbol = "x";

		final int maxOrder = 10;
		double []coefficients = new double[maxOrder];
		Arrays.fill( coefficients,  0.0 );
		int highestOrderSet = 0;

		// split the string up into separate terms :
		// First replace "-" with "+-" ...
		String polyString = origPolyString.replace("-","+-");
		// so splitting on "+" will retain -ve coeffs.
		String []tokens = polyString.split("[+]");
		for( int i = 0; i<tokens.length && i<maxOrder; i++ ) {
			String polyTerm = tokens[i].trim();

			if ( polyTerm.isEmpty() )
				continue;

			// Parse coefficient (if present) :
			// i.e. Extract part of the string between the '-' and 'x', remove any '*'s, convert to number :
			int xCharPos = polyTerm.indexOf(xSymbol);
			int minusCharPos = polyTerm.indexOf("-");
			String coeffString;
			if ( xCharPos != -1 )
				coeffString = polyTerm.substring(minusCharPos+1, xCharPos).replace("*", "").trim();
			else
				coeffString = polyTerm.trim();

			double coeff = 1.0;
			if ( ! coeffString.isEmpty() )
				coeff = Double.parseDouble(coeffString);

			// Reverse sign of coeff if there was a '-' symbol at the front
			if ( minusCharPos != -1 )
				coeff *= -1.0;

			// Parse power term (if present)
			// i.e. Extract part of string after the '^', and convert to integer
			int power = 0;
			int powSeparatorPos = polyTerm.indexOf("^");
			if (powSeparatorPos != -1) {
				String powString = polyTerm.substring(powSeparatorPos + 1);
				power = Integer.parseInt(powString);
			} else { // No power term, so power is either 1 or 0
				if ( polyTerm.contains(xSymbol) )
					power = 1;
				else
					power = 0;
			}

			if ( power > highestOrderSet )
				highestOrderSet = power;

			// add to coefficient value already set for this power
			coefficients[power] += coeff;
		}

		//Return coeffs, removing trailing powers with coefficients of zero
		return Arrays.copyOf(coefficients, highestOrderSet+1);
	}
}
