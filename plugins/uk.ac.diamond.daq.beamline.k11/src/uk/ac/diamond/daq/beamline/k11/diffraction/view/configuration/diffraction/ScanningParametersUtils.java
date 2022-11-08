/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument.Axis;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;

public class ScanningParametersUtils {

	private ScanningParametersUtils() {
		// static utils
	}

	/**
	 * Compiles the axis documents from the given {@code updatedAxes}
	 * and any other not updated axis from the given {@code document}
	 */
	public static List<ScannableTrackDocument> updateAxes(ScanpathDocument document, List<ScannableTrackDocument> updatedAxes) {
		// axis labels for new document
		var axesToUpdate = getAxesLabels(updatedAxes);

		// modifiable list of axes in old document...
		var axes = new ArrayList<>(document.getScannableTrackDocuments());

		// ...remove those to be updated
		axes.removeIf(doc -> axesToUpdate.contains(doc.getAxis()));

		// ...and add the axes in new document
		axes.addAll(updatedAxes);

		return axes;
	}

	/**
	 * Reduce the {@link ScannableTrackDocument}s in the list to their axis label e.g. "x"
	 */
	private static List<Axis> getAxesLabels(List<ScannableTrackDocument> axesDocuments) {
		return axesDocuments.stream().map(ScannableTrackDocument::getAxis).collect(Collectors.toList());
	}

}
