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

import uk.ac.diamond.daq.mapping.api.document.scanning.ShapeType;

/**
 * Formats a report for {@link ShapeType#POINT} elements
 *
 * @author Maurizio Nagni
 */
public class PointSummary extends ShapeSummaryBase  {

	private double xPosition;
	private double yPosition;

	public PointSummary(Consumer<String> printOut) {
		super(printOut);
	}

	public double getxPosition() {
		return xPosition;
	}

	public void setxPosition(double xPosition) {
		this.xPosition = xPosition;
		printOut(toString());
	}

	public double getyPosition() {
		return yPosition;
	}

	public void setyPosition(double yPosition) {
		this.yPosition = yPosition;
		printOut(toString());
	}

	@Override
	public String toString() {
		return String.format("Point\n" + "Centre: [%.1f, %.1f]", xPosition, yPosition);
	}
}
