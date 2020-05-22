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

import uk.ac.diamond.daq.mapping.ui.diffraction.model.ShapeType;

/**
 * Formats a report for {@link ShapeType#CENTRED_RECTANGLE} elements
 *
 * @author Maurizio Nagni
 */
public class CentredRectangleSummary extends ShapeSummaryBase {

	private boolean alternating;
	private boolean continuous;

	private double xCentre;
	private double yCentre;
	private double xRange;
	private double yRange;

	private int xAxisPoints;
	private int yAxisPoints;

	public CentredRectangleSummary(Consumer<String> printOut) {
		super(printOut);
	}

	public boolean isAlternating() {
		return alternating;
	}

	public void setAlternating(boolean alternating) {
		this.alternating = alternating;
		printOut(toString());
	}

	public boolean isContinuous() {
		return continuous;
	}

	public void setContinuous(boolean continuous) {
		this.continuous = continuous;
		printOut(toString());
	}

	public double getxCentre() {
		return xCentre;
	}

	public void setxCentre(double xCentre) {
		this.xCentre = xCentre;
		printOut(toString());
	}

	public double getyCentre() {
		return yCentre;
	}

	public void setyCentre(double yCentre) {
		this.yCentre = yCentre;
		printOut(toString());
	}

	public double getxRange() {
		return xRange;
	}

	public void setxRange(double xRange) {
		this.xRange = xRange;
		printOut(toString());
	}

	public double getyRange() {
		return yRange;
	}

	public void setyRange(double yRange) {
		this.yRange = yRange;
		printOut(toString());
	}

	public int getxAxisPoints() {
		return xAxisPoints;
	}

	public void setxAxisPoints(int xAxisPoints) {
		this.xAxisPoints = xAxisPoints;
		printOut(toString());
	}

	public int getyAxisPoints() {
		return yAxisPoints;
	}

	public void setyAxisPoints(int yAxisPoints) {
		this.yAxisPoints = yAxisPoints;
		printOut(toString());
	}

	@Override
	public String toString() {
		return String.format(
				"Rectangle\n" + "Centre: [%.1f, %.1f]\n" + "Size: [%.1f,%.1f]\n"
						+ "Points - Per side: [%d,%d] Total: [%d]\n" + printOutMutators(),
				xCentre, yCentre, xRange, yRange, xAxisPoints, yAxisPoints, xAxisPoints * yAxisPoints);
	}

	private String printOutMutators() {
		StringBuffer sb = new StringBuffer();
		if (isContinuous()) {
			sb.append("Continuous ");
		} else {
			sb.append("Stepped ");
		}
		if (isAlternating()) {
			sb.append("Snake ");
		}
		// if (isRandom()) {
		// sb.append("Random");
		// }
		return sb.toString();
	}
}
