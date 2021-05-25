/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

package gda.scan.ede.position;

import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
import org.apache.commons.math3.analysis.solvers.LaguerreSolver;
import org.apache.commons.math3.analysis.solvers.PolynomialSolver;
import org.apache.commons.math3.exception.NoBracketingException;
import org.dawnsci.ede.PolynomialParser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EnergyPositionCalculator {

	private static final Logger logger = LoggerFactory.getLogger(EnergyPositionCalculator.class);

	private double minCalibrationPosition = 0;
	private double maxCalibrationPosition = 1;
	private PolynomialFunction positionToEnergyPolynomial;

	private static final double energyPolynomialMaxXValue = 1.1;
	private static final double energyPolynomialMinXValue = -0.1;

	public void setPositionToEnergyPolynomial(PolynomialFunction positionToEnergyPolynomial) {
		this.positionToEnergyPolynomial = positionToEnergyPolynomial;
	}

	public void setPositionRange(double min, double max) {
		minCalibrationPosition = min;
		maxCalibrationPosition = max;
	}

	public double getMinEnergy() {
		return positionToEnergyPolynomial.value(0);
	}

	public double getMaxEnergy() {
		return positionToEnergyPolynomial.value(1);
	}

	public void setPolynomial(String eqnString) {
		if (eqnString != null && eqnString.length() > 0) {
			double[] polynomialCoefficients = PolynomialParser.extractCoefficientsFromString(eqnString);
			positionToEnergyPolynomial = new PolynomialFunction(polynomialCoefficients);
		} else {
			positionToEnergyPolynomial = null;
		}
	}

	public PolynomialFunction getPolynomial() {
		return positionToEnergyPolynomial;
	}

	/**
	 *  Convert from energy to motor position by solving energy calibration
	 *  polynomial for given value of energy. <p>
	 *  An IllegalArgumentException will be thrown if the energy cannot be converted to position
	 *  (i.e. polynomial cannot be solved by a value of x within valid range, normally [-0.1, 1.1] )
	 * @param energy
	 * @return motor position
	 */
	public double getPositionForEnergy(double energy) {

		if (positionToEnergyPolynomial == null) {
			logger.warn("Cannot get position for energy {} - polynomial has not been set. Returning energy value instead", energy);
			return energy;
		}

		// Solve energy calibration polynomial for position.
		double result = 0;
		try {
			// Construct new polynomial function to be used in solver, using coeffs
			// of energy calibration polynomial with energy subtracted :
			double[] coeffs = positionToEnergyPolynomial.getCoefficients();
			coeffs[0] -= energy;
			PolynomialFunction polynomial = new PolynomialFunction(coeffs);

			// Run the solver
			PolynomialSolver solver = new LaguerreSolver();
			int maxEvaluations = 10;
			result = solver.solve(maxEvaluations, polynomial, energyPolynomialMinXValue, energyPolynomialMaxXValue);
		} catch (NoBracketingException nbe) {
			String message = String.format("Cannot convert energy %5g eV to position. Requires x value outside of range of energy calibration polynomial. %.2f ... %.2f",
					energy, energyPolynomialMinXValue, energyPolynomialMaxXValue);
			logger.warn(message, nbe);
			throw new IllegalArgumentException(message);
		}

		// convert x from normalised to real position
		double position = (maxCalibrationPosition - minCalibrationPosition)*result + minCalibrationPosition;
		logger.debug(String.format("Position to energy conversion : energy = %.5g, x = %.5g, position = %.5g", energy, result, position));
		return position;
	}

	/**
	 *  Convert from motor position to energy using polynomial from calibration measurement :
	 *  	E(x) = a + b*x + c*x*x etc. where x is normalised motor position and E is energy
	 *
	 * @param position
	 * @return energy
	 */
	public double getEnergyForPosition(double position) {
		if (positionToEnergyPolynomial == null) {
			logger.warn("Cannot get energy for position {} - polynomial has not been set. Returning energy value instead", position);
			return position;
		}
		// energy calibration polynomial works off normalised position (0 < x < 1)
		double normalisedPosition = (position - minCalibrationPosition) / (maxCalibrationPosition - minCalibrationPosition);
		// show warning if position is out of range, but still calculate value.
		if ( normalisedPosition < energyPolynomialMinXValue || normalisedPosition > energyPolynomialMaxXValue ) {
			logger.warn(String.format("Possible problem converting from position to energy : value %.5g is out of range of calibration polynomial (%.5g, %.5g)", position, minCalibrationPosition, maxCalibrationPosition));
		}
		return positionToEnergyPolynomial.value(normalisedPosition);

	}
}
