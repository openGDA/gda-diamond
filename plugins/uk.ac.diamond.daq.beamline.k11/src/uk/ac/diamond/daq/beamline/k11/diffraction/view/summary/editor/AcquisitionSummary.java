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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.summary.editor;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.function.ToDoubleFunction;
import java.util.function.ToIntFunction;
import java.util.stream.IntStream;

import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StyleRange;
import org.eclipse.swt.custom.StyledText;

import com.swtdesigner.SWTResourceManager;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.summary.editor.handler.SummaryHandler;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.gda.api.acquisition.AcquisitionController;
import uk.ac.gda.client.exception.GDAClientException;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientResourceManager;
import uk.ac.gda.ui.tool.WidgetUtilities;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;

/**
 * Utilities to create and manage a text segmented based editor for the actual {@link AcquisitionController#getAcquisition()}
 *
 * @author Maurizio Nagni
 */
public class AcquisitionSummary {

	private static final String TEXT_HASH = "TEXT_HASH";

	private final List<StyleRange> styleRanges = new ArrayList<>();
	private final StringBuilder sb = new StringBuilder();
	private final List<Segment<?>> segments = new ArrayList<>();
	private StyleRange boxStyle;

	private SegmentGroup<double[]> startSegmentGroup;
	private SegmentGroup<double[]> stopSegmentGroup;

	private final StyledText summaryText;

	public AcquisitionSummary(StyledText summaryText) {
		this.summaryText = summaryText;
		StyledTextListeners.addStyledTextListeners(this);
	}

	/**
	 * Updates the content of the internal {@link StyledText}
	 */
	public void updateSummary() {
		clearBuffer();
		Optional.of(SummaryHandler.typeToString(null, this))
			.filter(r -> !isSameReport(r, summaryText) && r.length() > 0)
			.ifPresent(r -> updateSummaryText());
	}

	/**
	 *
	 * @param <T> the type of documents belonging to the same data structure
	 * @param <J> the type of data structure
	 * @param summaryText the gui element showing the group element. If {@code null} the generated string is appended only to the internal string buffer
	 * consequently this method can be used also to
	 * @param title the group element name
	 * @param documents the documents composing the data structure
	 * @param getter a method to retrieve the numeric value of a single document
	 * @param segmentGroup the group associated with this editor
	 */
	public <T, J> void genericDoubleGroupToString(StyledText summaryText, String title, List<T> documents,
			ToDoubleFunction<T> getter, SegmentGroup<J> segmentGroup) {
		appendTitle(title, summaryText);
		var oneDimentional = isALine();
		// if is a line should show only one
		int size = oneDimentional ? 1 : documents.size();
		IntStream.range(0, size)
			.forEach(index -> {
				if (index > 0)
					getStringBuilder().append("\s,\s");
				var document = documents.get(index);
				var numericValue = getter.applyAsDouble(document);
				var originalString =  segmentGroup.getDecimalFormat().format(numericValue);

				Optional.ofNullable(summaryText)
					.ifPresent(s -> {
						var segment = new Segment<>(getStringBuilder().length(), numericValue, segmentGroup);
						segments.add(segment);
						segmentGroup.getSegments().add(segment);
					});
				getStringBuilder().append(originalString);
			});
		getStringBuilder().append("\s]");

		if (oneDimentional && !segmentGroup.getSegments().isEmpty()) {
			Segment<J> firstElement = segmentGroup.getSegments().get(0);
			IntStream.range(1, documents.size())
			.forEach(index -> segmentGroup.getSegments().add(firstElement));
		}
	}

	/**
	 * Creates the Segments structure for the summaryText.
	 *
	 * @param <T> the type of documents belonging to the same data structure
	 * @param <J> the type of data structure
	 * @param summaryText the gui element showing the group element. If {@code null} the generated string is appended only to the internal string buffer
	 * consequently this method can be used also to
	 * @param title the group element name
	 * @param documents the documents composing the data structure
	 * @param getter a method to retrieve the numeric value of a single document
	 * @param segmentGroup the group associated with this editor
	 */
	public <T, J> void genericIntGroupToString(StyledText summaryText, String title, List<T> documents,
			ToIntFunction<T> getter, SegmentGroup<J> segmentGroup) {
		appendTitle(title, summaryText);
		// if is a line should show only one
		var oneDimentional = isALine();
		int size = oneDimentional ? 1 : documents.size();
		IntStream.range(0, size)
			.forEach(index -> {
				if (index > 0)
					getStringBuilder().append("\s,\s");
				var document = documents.get(index);
				var numericValue = getter.applyAsInt(document);
				var originalString = segmentGroup.getDecimalFormat().format(numericValue);

				Optional.ofNullable(summaryText)
					.ifPresent(s -> {
						var segment = new Segment<>(getStringBuilder().length(), numericValue, segmentGroup);
						segments.add(segment);
						segmentGroup.getSegments().add(segment);
					});
				getStringBuilder().append(originalString);
			});
		getStringBuilder().append("\s]");

		//
		if (oneDimentional && !segmentGroup.getSegments().isEmpty()) {
			Segment<J> firstElement = segmentGroup.getSegments().get(0);
			// starts from one because we want to replicate size-time the first, already existing, segment
			IntStream.range(1, documents.size())
			.forEach(index -> segmentGroup.getSegments().add(firstElement));
		}
	}

	public void applyStyleRanges(StyledText summaryText) {
		Collections.sort(styleRanges, (o1, o2) -> o1.start - o2.start);
		summaryText.setStyleRanges(styleRanges.toArray(new StyleRange[0]));
	}

	public void updateStyleRanges(Segment<?> segment, int delta) {
		getStyleRanges().stream()
			.filter(style -> style.start > segment.getStart())
			.forEach(style -> style.start = style.start + delta);
	}

	public void drawBox(Segment<?> segment) {
		getStyleRanges().remove(boxStyle);
		boxStyle = new StyleRange();
		boxStyle.borderColor = SWTResourceManager.getColor(SWT.COLOR_RED);
		boxStyle.borderStyle = SWT.BORDER_SOLID;
		boxStyle.start = segment.getStart();
		boxStyle.length = segment.getActualString().length();
		getStyleRanges().add(boxStyle);
	}

	public void removeBox() {
		getStyleRanges().remove(boxStyle);
	}

	public void append(String newText) {
		getStringBuilder().append(newText);
	}

	public Optional<Segment<?>> segmentAtTextPosition(int position) {
		return segments.stream()
				.filter(s -> s.contains(position))
				.findFirst();
	}

	public void validateGridRange() throws GDAClientException {
		double[] starts = startSegmentGroup.getValues();
		double[] stops = stopSegmentGroup.getValues();

		for (var index = 0 ; index < starts.length ; index++) {
			if (stops[index] < starts[index]) {
				if (index == 0) {
					throw new GDAClientException("Start greater than stop");
				} else {
					throw new GDAClientException("Stop smaller than start");
				}
			}
		}
	}

	public void setStartSegmentGroup(SegmentGroup<double[]> startSegmentGroup) {
		this.startSegmentGroup = startSegmentGroup;
	}

	public void setStopSegmentGroup(SegmentGroup<double[]> stopSegmentGroup) {
		this.stopSegmentGroup = stopSegmentGroup;
	}

	public void titleStyleRange(String type) {
		var styleRange = new StyleRange();
		styleRange.start = getStringBuilder().length();
		styleRange.length = type.length();
		styleRange.font = ClientResourceManager.getInstance().getGroupDefaultFont();
		getStyleRanges().add(styleRange);
	}

	/**
	 * Compares the hash of a new report with the hash of a previous one.
	 *
	 * @param summaryText
	 * @param report
	 * @return {@code true} if the report is equivalent to the one stored in summaryText, otherwise {@code false}
	 */
	private boolean isSameReport(String report, StyledText summaryText) {
		return Optional.ofNullable(WidgetUtilities.getDataObject(summaryText, Integer.class, TEXT_HASH))
				.filter(h -> h == report.hashCode())
				.isPresent();
	}

	private void clearSegment() {
		clearBuffer();
		segments.clear();
		getStyleRanges().clear();
	}

	private void clearBuffer() {
		getStringBuilder().delete(0, getStringBuilder().length());
	}

	private StringBuilder getStringBuilder() {
		return sb;
	}

	private void appendTitle(String title, StyledText summaryText) {
		Optional.ofNullable(summaryText)
			.ifPresent(s -> titleStyleRange(title));
		getStringBuilder().append(title);
		getStringBuilder().append(":\s[\s");
	}

	private void updateSummaryTextAndApplyStyleRanges(String report, StyledText summaryText) {
		summaryText.setText(report);
		summaryText.setData(TEXT_HASH, report.hashCode());
		applyStyleRanges(summaryText);
	}

	private List<StyleRange> getStyleRanges() {
		return styleRanges;
	}

	/**
	 * A line may be two or more dimensional and consequently have the same number or points in all the axes.
	 * However the coordinate system based on-the-line is one dimensional and this simplifies the editor as instead to keep replicas of all the points
	 * it just edit a single value, that is a single number of points. This flag defines when the data structure has to be considered as the latter case.
	 *
	 * @return {@code true} if the acquisition type is {@link AcquisitionTemplateType#TWO_DIMENSION_LINE}, otherwise {@code false}.
	 */
	private boolean isALine() {
		return getScanningAcquisitionTemporaryHelper()
				.getSelectedAcquisitionTemplateType()
				.filter(AcquisitionTemplateType.TWO_DIMENSION_LINE::equals)
				.isPresent();
	}

	@Override
	public String toString() {
		return sb.toString();
	}

	public StyledText getSummaryText() {
		return summaryText;
	}

	private void updateSummaryText() {
		clearSegment();
		Optional.ofNullable(SummaryHandler.typeToString(summaryText, this))
			.ifPresent(report -> {
				updateSummaryTextAndApplyStyleRanges(report, summaryText);
			});
	}

	private ScanningAcquisitionTemporaryHelper getScanningAcquisitionTemporaryHelper() {
		return SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class);
	}
}
