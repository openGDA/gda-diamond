/*-
 * Copyright © 2023 Diamond Light Source Ltd.
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

package gda.device.scannable;

import java.util.Arrays;
import java.util.List;

import uk.ac.gda.api.virtualaxis.IVirtualAxisCombinedCalculator;

/**
 * Combined axis calculator : axis is straight line in x-y coordinate system, at user specified angle to x-axis
 *
 */
public class CombinedAxisCalculator implements IVirtualAxisCombinedCalculator {

	private double xOrigin;
	private double yOrigin;

	// Angle w.r.t. the X axis (radians)
	private double axisAngle = 0;

	/**
	 * Calculate x y coordinates for given position (value) on combined axis.
	 */
	@Override
	public List<Double> getDemands(Double value, List<Double> vector) {
		double xValue = value *  Math.cos(axisAngle) + xOrigin;
		double yValue = value * Math.sin(axisAngle) + yOrigin;
		return Arrays.asList(xValue, yValue);
	}

	@Override
	public Double getRBV(List<Double> values) {
		double xValue = values.get(0);
		double yValue = values.get(1);
		if (Math.abs(Math.cos(axisAngle)) < 0.5) { // avoid divide by zero
			return (yValue - yOrigin) / Math.sin(axisAngle);
		} else {
			return (xValue - xOrigin) / Math.cos(axisAngle);
		}
	}

	/**
	 * Set the origin coordinate of the x and y axes
	 *
	 * @param xOrigin
	 * @param yOrigin
	 */
	public void setOrigin(double xOrigin, double yOrigin) {
		this.xOrigin = xOrigin;
		this.yOrigin = yOrigin;
	}

	/**
	 * Set the angle of the combined axis, w.r.t. x axis.
	 * (i.e. 0 == along x axis, 90 == along y axis etc)
	 *
	 * @param angleDegrees
	 */
	public void setAxisAngle(double angleDegrees) {
		axisAngle = Math.toRadians(angleDegrees);
	}

}