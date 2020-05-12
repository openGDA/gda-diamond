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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.summary;

import java.util.function.Consumer;

/**
 * A base class common to all the shape reporting.
 *
 * <p>
 * Each shape may contains different properties and, as such, is not possible to have a common {@code toString} for all.
 * For this reason each shape is required to implements its own subclass to match the available data.
 * </p>
 *
 * @author Maurizio Nagni
 */
public class ShapeSummaryBase  {

	private final Consumer<String> printOut;

	/**
	 * @param printOut a consumer to use the report a summary
	 */
	public ShapeSummaryBase(Consumer<String> printOut) {
		this.printOut = printOut;
	}

	/**
	 * Uses the consumer to print out the report summary
	 * @param text
	 */
	void printOut(String text) {
		printOut.accept(text);
	}
}
