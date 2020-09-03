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
import java.util.function.Supplier;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.gda.api.acquisition.parameters.DetectorDocument;
import uk.ac.gda.client.UIHelper;

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

	protected static final Logger logger = LoggerFactory.getLogger(AcquisitionTemplateTypeSummaryBase.class);
	private final Supplier<ScanningAcquisition> acquisitionSupplier;

	public AcquisitionTemplateTypeSummaryBase(Supplier<ScanningAcquisition> acquisitionSupplier) {
		this.acquisitionSupplier = acquisitionSupplier;
	}

	protected ScanningAcquisition getAcquisition() {
		return acquisitionSupplier.get();
	}

	protected double getExposure() {
		Optional<Double> exposure = Optional.ofNullable(getScanningParameters().getDetector())
				.map(DetectorDocument::getExposure);
		if (exposure.isPresent()) {
			return exposure.get();
		}
		UIHelper.showWarning("Exposure is zero", "No DetectorDocument is defined");
		return 0d;
	}

	protected String startToString() {
		DecimalFormat df = new DecimalFormat("#0.00");
		String content = getScanningParameters().getScanpathDocument().getScannableTrackDocuments().stream()
			.map(ScannableTrackDocument::getStart)
			.map(df::format)
			.collect(Collectors.joining(", "));
		return String.format("%s: [%s]", "Start", content);
	}

	protected String stopToString() {
		DecimalFormat df = new DecimalFormat("#0.00");
		String content = getScanningParameters().getScanpathDocument().getScannableTrackDocuments().stream()
			.map(ScannableTrackDocument::getStop)
			.map(df::format)
			.collect(Collectors.joining(", "));
		return String.format("%s: [%s]", "Stop", content);
	}

	protected String pointsToString() {
		DecimalFormat df = new DecimalFormat("#");
		String content = getScanningParameters().getScanpathDocument().getScannableTrackDocuments().stream()
			.map(ScannableTrackDocument::getPoints)
			.map(df::format)
			.collect(Collectors.joining(", "));
		return String.format("%s: [%s]", "Points", content);
	}

	protected String stepToString() {
		DecimalFormat df = new DecimalFormat("#0.00");
		String content = getScanningParameters().getScanpathDocument().getScannableTrackDocuments().stream()
			.map(c -> Math.sqrt(Math.pow(c.getStop() - c.getStop(), 2) / c.getPoints()))
			.map(df::format)
			.collect(Collectors.joining(", "));
		return String.format("%s: [%s]", "Steps", content);
	}

	protected String durationToString() {
		return String.format("%s: [%s]s", "Duration", totPoints() * getExposure());
	}

	protected String lineDurationToString() {
		// divide by two because the totPoints are counted on all the axes (for now, no more than 2)
		return String.format("%s: [%s]s", "Duration", (totPoints() * getExposure())
				/  getScanningParameters().getScanpathDocument().getScannableTrackDocuments().size());
	}

	private int totPoints() {
		return getScanningParameters().getScanpathDocument().getScannableTrackDocuments().stream()
				.map(ScannableTrackDocument::getPoints)
				.mapToInt(Integer::intValue)
				.sum();
	}

	protected String mutatorToString() {
		String content = getScanningParameters().getScanpathDocument().getMutators().entrySet().stream()
			.map(c -> c.getKey().name())
			.collect(Collectors.joining(", "));
		return String.format("%s: [%s]", "Mutators", content);
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

	private String pointToString() {
		return String.format("Point%n%s, %s%n%s", startToString(), lineDurationToString(), mutatorToString());
	}

	private String lineToString() {
		return String.format("Line%n%s, %s%n%s, %s%n%s, %s", startToString(), stopToString(),
				pointsToString(), stepToString(), lineDurationToString(), mutatorToString());
	}

	private String rectangleToString() {
		return String.format("Rectangle%n%s, %s%n%s%n%s %s%n%s", startToString(), stopToString(),
				pointsToString(), stepToString(), durationToString(), mutatorToString());
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
