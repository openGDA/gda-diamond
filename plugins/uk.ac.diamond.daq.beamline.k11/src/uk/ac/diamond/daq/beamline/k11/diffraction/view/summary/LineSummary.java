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
import java.util.function.Supplier;

import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ShapeType;
import uk.ac.gda.ui.tool.spring.SpringApplicationContextProxy;

/**
 * Formats a report for {@link ShapeType#LINE} elements
 *
 * @author Maurizio Nagni
 */
public class LineSummary extends ShapeSummaryBase {

	private boolean alternating;
	private boolean continuous;

	private double xStart;
	private double xStop;
	private double yStart;
	private double yStop;

	public LineSummary(Consumer<String> printOut, Supplier<ScanningAcquisition> acquisitionSupplier) {
		super(printOut, acquisitionSupplier);
		SpringApplicationContextProxy.addDisposableApplicationListener(this,
				new ScanningAcquisitionListener(this, acquisitionSupplier));
	}

	public double getxStart() {
		return xStart;
	}

	public void setxStart(double xStart) {
		this.xStart = xStart;
		printOut(toString());
	}

	public double getxStop() {
		return xStop;
	}

	public void setxStop(double xStop) {
		this.xStop = xStop;
		printOut(toString());
	}

	public double getyStart() {
		return yStart;
	}

	public void setyStart(double yStart) {
		this.yStart = yStart;
		printOut(toString());
	}

	public double getyStop() {
		return yStop;
	}

	public void setyStop(double yStop) {
		this.yStop = yStop;
		printOut(toString());
	}

	private int getPoints() {
		return getScanningParameters().getScanpathDocument().getScannableTrackDocuments().get(0).getPoints();
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

	@Override
	public String toString() {
		double step = Math.sqrt(Math.pow(xStop - xStart, 2) + Math.pow(yStop - yStart, 2)) / getPoints();
		double duration = getPoints() * getExposure();
		return String.format(
				"Line%nStart: [%.1f,%.1f], End: [%.1f,%.1f]%nPoints: [%d]%nStep: [%.1f] Duration: %.1fs %n%s", xStart,
				yStart, xStop, yStop, getPoints(), step, duration, printOutMutators());
	}

	private String printOutMutators() {
		StringBuilder sb = new StringBuilder();
		if (isContinuous()) {
			sb.append("Continuous ");
		} else {
			sb.append("Stepped ");
		}
		if (isAlternating()) {
			sb.append("Snake ");
		}
		return sb.toString();
	}
}
