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

import java.util.function.IntBinaryOperator;

import org.eclipse.swt.custom.StyledText;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.summary.editor.AcquisitionSummary;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.gda.client.exception.GDAClientException;

/**
 * The summary handler for {@link AcquisitionTemplateType#TWO_DIMENSION_POINT} type
 *
 * @author Maurizio Nagni
 */
public class TwoDimensionPointSummaryHandler extends SummaryHandlerBase {

	public TwoDimensionPointSummaryHandler(AcquisitionSummary segmentUtils) {
		super(segmentUtils);
	}

	@Override
	public String typeToString(StyledText summaryText) {
		title("Point", summaryText);
		startToStringNew(summaryText);
		getSegmentUtils().append(String.format("%n%s %s%n%s",
				exposureToString(), durationToString(), mutatorToString()));
		return getSegmentUtils().toString();
	}

	@Override
	protected IntBinaryOperator totalPoints() {
		// A Single point
		return (a, b) -> 1;
	}

	@Override
	public void validate() throws GDAClientException {
		// no validation
	}
}
