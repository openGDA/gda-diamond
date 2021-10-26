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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.summary.editor.handler;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.IntBinaryOperator;
import java.util.stream.Collectors;

import org.eclipse.swt.custom.StyledText;

import gda.mscan.element.Mutator;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.summary.editor.AcquisitionSummary;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.summary.editor.SegmentDoubleGroup;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.summary.editor.SegmentGroup;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.summary.editor.SegmentIntGroup;
import uk.ac.diamond.daq.mapping.api.document.helper.ScannableTrackDocumentHelper;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.gda.api.acquisition.parameters.DetectorDocument;
import uk.ac.gda.client.exception.GDAClientException;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientTextFormats;
import uk.ac.gda.ui.tool.controller.AcquisitionController;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;

/**
 * The base class for the summary handlers
 *
 * @author Maurizio Nagni
 */
public abstract class SummaryHandlerBase {

	private static final String PROPERTY_FORMAT = "%s: [%s]";
	private ScannableTrackDocumentHelper scannableTrackDocumentHelper;
	private final AcquisitionSummary segmentUtils;

	/**
	 * Generates a new summary from {@link AcquisitionController#getAcquisition()}
	 *
	 * @param summaryText the widget used as editor. May be {@code null}
	 *
	 * @return a summary text of a scanning acquisition
	 */
	public abstract String typeToString(StyledText summaryText);

	/**
	 * Validate the editor values
	 *
	 * @throws GDAClientException
	 *
	 * @see TwoDimensionGridSummaryHandler
	 */
	public abstract void validate() throws GDAClientException;

	/**
	 * The total points for {@link AcquisitionController#getAcquisition()}
	 *
	 * @return an operator to sum the points
	 */
	protected abstract IntBinaryOperator totalPoints();

	protected SummaryHandlerBase(AcquisitionSummary segmentUtils) {
		this.segmentUtils = segmentUtils;
	}

	protected AcquisitionSummary getSegmentUtils() {
		return segmentUtils;
	}

	protected void title(String title, StyledText summaryText) {
		Optional.ofNullable(summaryText)
			.ifPresent(s -> segmentUtils.titleStyleRange(title));
		segmentUtils.append(title + "\n");
	}

	protected void startToStringNew(StyledText summaryText) {
		getScanningAcquisitionTemporaryHelper()
			.getScanpathDocument()
			.ifPresent(d -> {
				SegmentGroup<double[]> segmentGroup = new SegmentDoubleGroup(getScannableTrackDocumentHelper()::updateScannableTrackDocumentsStarts, true);
				segmentUtils.genericDoubleGroupToString(summaryText, "Start", d.getScannableTrackDocuments(),
						ScannableTrackDocument::getStart, segmentGroup);

				if (summaryText != null) {
					segmentUtils.setStartSegmentGroup(segmentGroup);
				}
			});
	}

	protected void stopToStringNew(StyledText summaryText) {
		getScanningAcquisitionTemporaryHelper()
			.getScanpathDocument()
			.ifPresent(d -> {
				SegmentGroup<double[]> segmentGroup = new SegmentDoubleGroup(getScannableTrackDocumentHelper()::updateScannableTrackDocumentsStops, true);
				segmentUtils.genericDoubleGroupToString(summaryText, "Stop", d.getScannableTrackDocuments(),
						ScannableTrackDocument::getStop, segmentGroup);

				if (summaryText != null) {
					segmentUtils.setStopSegmentGroup(segmentGroup);
				}
			});
	}

	protected void stepsToStringNew(StyledText summaryText) {
		getScanningAcquisitionTemporaryHelper()
			.getScanpathDocument()
			.ifPresent(d -> {
				SegmentGroup<double[]> segmentGroup = new SegmentDoubleGroup(getScannableTrackDocumentHelper()::updateScannableTrackDocumentsSteps, false);
				segmentUtils.genericDoubleGroupToString(summaryText, "Steps", d.getScannableTrackDocuments(),
						ScannableTrackDocument::calculatedStep, segmentGroup);
			});
	}

	protected void pointsToStringNew(StyledText summaryText) {
		getScanningAcquisitionTemporaryHelper()
			.getScanpathDocument()
			.ifPresent(d -> {
				SegmentGroup<int[]> segmentGroup = new SegmentIntGroup(getScannableTrackDocumentHelper()::updateScannableTrackDocumentsPoints, true);
				segmentUtils.genericIntGroupToString(summaryText, "Points", d.getScannableTrackDocuments(),
						ScannableTrackDocument::getPoints, segmentGroup);
			});
	}

	protected String exposureToString() {
		return formatDouble(getExposure(), "Exposure");
	}

	protected String durationToString() {
		return formatDouble(totPoints() * getExposure(), "Duration");
	}

	protected String mutatorToString() {
		 Set<Map.Entry<Mutator, List<Number>>> entries = getScanningAcquisitionTemporaryHelper()
				.getScanpathDocument()
				.map(ScanpathDocument::getMutators)
				.map(Map::entrySet)
				.orElseGet(Collections::emptySet);

		 String content = entries.stream()
			.map(c -> c.getKey().name())
			.collect(Collectors.joining(", "));
		return String.format(PROPERTY_FORMAT, "Mutators", content);
	}

	private int totPoints() {
		return	getScanningAcquisitionTemporaryHelper()
					.getScannableTrackDocuments().stream()
					.filter(d -> d.calculatedStep() > 0)
					.map(ScannableTrackDocument::getPoints)
					.mapToInt(Integer::intValue)
					.reduce(1, totalPoints());
	}

	private String formatDouble(Double value, String name) {
		return Optional.ofNullable(value)
				.map(ClientTextFormats::formatDecimal)
				.map(c -> String.format(PROPERTY_FORMAT + "s", name, c))
				.orElse("");
	}

	private double getExposure() {
		var params = getScanningAcquisitionTemporaryHelper().getScanningParameters();
		if (params.isPresent()) {
			return params.get().getDetectors().stream()
				.map(DetectorDocument::getExposure)
				.max(Double::compare).orElse(0.0);
		}

		return 0.0;

	}

	private ScannableTrackDocumentHelper getScannableTrackDocumentHelper() {
		return Optional.ofNullable(scannableTrackDocumentHelper)
			.orElseGet(() -> {
				this.scannableTrackDocumentHelper = getScanningAcquisitionTemporaryHelper()
						.createScannableTrackDocumentHelper()
						.orElseGet(() -> scannableTrackDocumentHelper);
				return scannableTrackDocumentHelper;
			});
	}

	private ScanningAcquisitionTemporaryHelper getScanningAcquisitionTemporaryHelper() {
		return SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class);
	}
}
