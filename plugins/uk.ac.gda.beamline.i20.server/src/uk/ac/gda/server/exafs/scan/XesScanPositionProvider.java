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

package uk.ac.gda.server.exafs.scan;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import gda.scan.ScanPositionProvider;

/**
 * Implementation of ScanPositionProvider for XES scans.
 * This stores an internal list of 'primary' points generated from start, stop, step values;
 * a 'secondary' set of points can be generated from a given start value, a step size and
 * the number of points in the primary list.
 *
 */
public class XesScanPositionProvider implements ScanPositionProvider {

	private List<Double> primaryPoints = Collections.emptyList();
	private List<Double> secondaryPoints = Collections.emptyList();

	public void createPrimaryPoints(double start, double stop, double step) {
		primaryPoints = generatePrimaryPoints(start, stop, step);
	}

	public void createSecondaryPoints(double start, double step) {
		secondaryPoints = generateSecondaryPoints(start, primaryPoints.size(), step);
	}

	public void createSecondaryPoints() {
		secondaryPoints = primaryPoints;
	}

	private List<Double> generatePrimaryPoints(double start, double stop, double step) {
		List<Double> points = new ArrayList<>();
		double currentPoint = Math.min(start, stop);
		double finalPoint = Math.max(start, stop);
		while(currentPoint <= finalPoint) {
			points.add(currentPoint);
			currentPoint += Math.abs(step);
		}
		if (start > stop) {
			return points.reversed();
		}
		return points;
	}

	private List<Double> generateSecondaryPoints(double start, double numPoints, double step) {
		List<Double> points = new ArrayList<>();
		double currentPoint = start;
		for(int count=0; count<numPoints; count++) {
			points.add(currentPoint);
			currentPoint += step;
		}
		return points;
	}
	@Override
	public Object get(int index) {
		if (primaryPoints.size()>index) {
			if (secondaryPoints.size()>index) {
				return new double[] {primaryPoints.get(index), secondaryPoints.get(index)};
			} else {
				return primaryPoints.get(index);
			}
		}
		return 0;
	}

	@Override
	public int size() {
		return primaryPoints.size();
	}

	@Override
	public String toString() {
		String infoString = "";
		if (!primaryPoints.isEmpty()) {
			infoString += "[Range1 : "+generateRangeString(primaryPoints);
		}
		if (!secondaryPoints.isEmpty()) {
			infoString += ", Range2 : "+generateRangeString(secondaryPoints)+"]";
		} else {
			infoString += "]";
		}
		return infoString;
	}

	private String generateRangeString(List<Double> values) {
		return String.format("%.2f, %.2f, %.2f", values.get(0), values.get(values.size()-1), values.get(1)-values.get(0));
	}

}
