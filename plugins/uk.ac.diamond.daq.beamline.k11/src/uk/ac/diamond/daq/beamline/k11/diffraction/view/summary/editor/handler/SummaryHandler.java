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

import java.util.Optional;

import org.eclipse.swt.custom.StyledText;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.summary.editor.AcquisitionSummary;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.gda.client.exception.GDAClientException;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;

/**
 * Handler manager for various acquisition type summaries.
 *
 * This class should be better refactored to a real chain of responsibility pattern
 *
 *  @author Maurizio Nagni
 */
public class SummaryHandler {

	private SummaryHandler() {
		super();
	}

	/**
	 * Returns the summary string associated with the actual acquisition
	 *
	 * @param summaryText
	 * @param segmentUtils
	 * @return the summary report, an {@code empty} string otherwise
	 */
	public static String typeToString(StyledText summaryText, AcquisitionSummary segmentUtils) {
		return getHandler(segmentUtils)
			.map(h -> h.typeToString(summaryText))
			.orElseGet(() -> "");
	}

	/**
	 * Returns the summary string associated with the actual acquisition
	 *
	 * @param segmentUtils
	 * @throws GDAClientException
	 */
	public static void validate(AcquisitionSummary segmentUtils) throws GDAClientException {
		Optional<SummaryHandlerBase> handler = getHandler(segmentUtils);
		if (handler.isPresent()) {
			handler.get().validate();
		}
	}

	/**
	 * Returns the summary string associated with the actual acquisition
	 *
	 * @param templateType
	 * @param summaryText
	 * @param segmentUtils
	 * @return the summary report, an {@code empty} string otherwise
	 */
	private static Optional<SummaryHandlerBase> getHandler(AcquisitionSummary segmentUtils) {
		AcquisitionTemplateType templateType = getScanningAcquisitionTemporaryHelper()
			.getSelectedAcquisitionTemplateType()
			.orElseGet(null);
		switch (templateType) {
		case TWO_DIMENSION_POINT:
			return Optional.ofNullable(new TwoDimensionPointSummaryHandler(segmentUtils));
		case TWO_DIMENSION_LINE:
			return Optional.ofNullable(new TwoDimensionLineSummaryHandler(segmentUtils));
		case TWO_DIMENSION_GRID:
			return Optional.ofNullable(new TwoDimensionGridSummaryHandler(segmentUtils));
		default:
			return Optional.empty();
		}
	}

	private static ScanningAcquisitionTemporaryHelper getScanningAcquisitionTemporaryHelper() {
		return SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class);
	}
}
