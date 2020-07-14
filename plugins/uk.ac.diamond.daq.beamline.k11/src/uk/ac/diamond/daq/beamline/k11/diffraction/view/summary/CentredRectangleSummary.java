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

	public CentredRectangleSummary(Consumer<String> printOut, Supplier<ScanningAcquisition> acquisitionSupplier) {
		super(printOut, acquisitionSupplier);
		SpringApplicationContextProxy.addDisposableApplicationListener(this,
				new ScanningAcquisitionListener(this, acquisitionSupplier));
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
		return getScanningParameters().getScanpathDocument().getScannableTrackDocuments().get(0).getPoints();
	}

	public int getyAxisPoints() {
		return getScanningParameters().getScanpathDocument().getScannableTrackDocuments().get(1).getPoints();
	}

	@Override
	public String toString() {
		double stepX = xRange / getxAxisPoints();
		double stepY = yRange / getyAxisPoints();
		int totalPoints = getxAxisPoints() * getyAxisPoints();
		double duration = totalPoints * getExposure();
		return String.format(
				"Rectangle%nCentre: [%.1f, %.1f]%nSize: [%.1f,%.1f]%nPoints: [%d,%d] Steps: [%.1f,%.1f] Duration: %.1fs Total: [%d]%n%s",
				xCentre, yCentre, xRange, yRange, getxAxisPoints(), getyAxisPoints(), stepX, stepY, duration, totalPoints,
				printOutMutators());
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
		// if (isRandom()) {
		// sb.append("Random");
		// }
		return sb.toString();
	}
}
