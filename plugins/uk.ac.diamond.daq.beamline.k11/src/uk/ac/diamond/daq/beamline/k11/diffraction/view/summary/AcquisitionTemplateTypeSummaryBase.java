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

import java.text.DecimalFormat;
import java.util.Optional;
import java.util.function.IntBinaryOperator;
import java.util.function.Supplier;
import java.util.stream.Collectors;

import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.gda.api.acquisition.parameters.DetectorDocument;

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
public class AcquisitionTemplateTypeSummaryBase  {

	private static final  DecimalFormat decimalFormat = new DecimalFormat("#0.00");
	private static final DecimalFormat integerFormat = new DecimalFormat("#");
	private static final String PROPERTY_FORMAT = "%s: [%s]";
	private final Supplier<ScanningAcquisition> acquisitionSupplier;

	public AcquisitionTemplateTypeSummaryBase(Supplier<ScanningAcquisition> acquisitionSupplier) {
		this.acquisitionSupplier = acquisitionSupplier;
	}

	protected ScanningAcquisition getAcquisition() {
		return acquisitionSupplier.get();
	}

	protected double getExposure() {
		return Optional.ofNullable(getScanningParameters().getDetector())
				.map(DetectorDocument::getExposure)
				.orElseGet(() -> 0d);
	}

	protected String startToString() {
		String content = getScanningParameters().getScanpathDocument().getScannableTrackDocuments().stream()
			.map(ScannableTrackDocument::getStart)
			.map(decimalFormat::format)
			.collect(Collectors.joining(", "));
		return String.format(PROPERTY_FORMAT, "Start", content);
	}

	protected String stopToString() {
		String content = getScanningParameters().getScanpathDocument().getScannableTrackDocuments().stream()
			.map(ScannableTrackDocument::getStop)
			.map(decimalFormat::format)
			.collect(Collectors.joining(", "));
		return String.format(PROPERTY_FORMAT, "Stop", content);
	}

	protected String pointsToString() {
		String content = getScanningParameters().getScanpathDocument().getScannableTrackDocuments().stream()
			.map(ScannableTrackDocument::getPoints)
			.map(integerFormat::format)
			.collect(Collectors.joining(", "));
		return String.format(PROPERTY_FORMAT, "Points", content);
	}

	protected String stepToString() {
		String content = getScanningParameters().getScanpathDocument().getScannableTrackDocuments().stream()
			.map(ScannableTrackDocument::calculatedStep)
			.map(decimalFormat::format)
			.collect(Collectors.joining(", "));
		return String.format(PROPERTY_FORMAT, "Steps", content);
	}

	protected String durationToString() {
		return String.format("%s: [%s]s", "Duration", decimalFormat.format(totPoints() * getExposure()));
	}

	protected String lineDurationToString() {
		// divide by two because the totPoints are counted on all the axes (for now, no more than 2)
		return String.format("%s: [%s]s", "Duration", totPoints() * getExposure());
	}

	private int totPoints() {
		return getScanningParameters().getScanpathDocument().getScannableTrackDocuments().stream()
				.filter(d -> d.calculatedStep() > 0)
				.map(ScannableTrackDocument::getPoints)
				.mapToInt(Integer::intValue)
				.reduce(1, totalPoints());
	}

	protected String mutatorToString() {
		String content = getScanningParameters().getScanpathDocument().getMutators().entrySet().stream()
			.map(c -> c.getKey().name())
			.collect(Collectors.joining(", "));
		return String.format(PROPERTY_FORMAT, "Mutators", content);
	}

	protected String exposureToString() {
		return String.format("%s: [%s]s", "Exposure", getExposure());
	}

	@Override
	public String toString() {
		switch (getSelectedAcquisitionTemplateType()) {
		case TWO_DIMENSION_POINT:
			return pointToString();
		case TWO_DIMENSION_LINE:
			return lineToString();
		case TWO_DIMENSION_GRID:
			return rectangleToString();
		default:
			return "";
		}
	}

	private IntBinaryOperator totalPoints() {
		switch (getSelectedAcquisitionTemplateType()) {
		case TWO_DIMENSION_POINT:
			// A Single point
			return (a, b) -> 1;
		case TWO_DIMENSION_LINE:
			// Takes the axis with the max points (really they are the same)
			return Math::max;
		case TWO_DIMENSION_GRID:
			// multiply the axes points
			return (a, b) -> a*b;
		default:
			return (a, b) -> 0;
		}
	}

	private String pointToString() {
		return String.format("Point%n%s%n%s %s%n%s", startToString(), exposureToString(), lineDurationToString(), mutatorToString());
	}

	private String lineToString() {
		return String.format("Line%n%s %s%n%s %s%n%s %s%n%s", startToString(), stopToString(),
				pointsToString(), stepToString(), lineDurationToString(), exposureToString(), mutatorToString());
	}

	private String rectangleToString() {
		return String.format("Rectangle%n%s %s%n%s %s%n%s %s%n%s ", startToString(), stopToString(),
				pointsToString(), stepToString(), durationToString(), exposureToString(), mutatorToString());
	}

	// ------------ UTILS ----
	private ScanningAcquisition getScanningAcquisition() {
		return this.acquisitionSupplier.get();
	}

	private ScanningParameters getScanningParameters() {
		return getScanningAcquisition().getAcquisitionConfiguration().getAcquisitionParameters();
	}

	private AcquisitionTemplateType getSelectedAcquisitionTemplateType() {
		return getScanningParameters().getScanpathDocument().getModelDocument();
	}
}
