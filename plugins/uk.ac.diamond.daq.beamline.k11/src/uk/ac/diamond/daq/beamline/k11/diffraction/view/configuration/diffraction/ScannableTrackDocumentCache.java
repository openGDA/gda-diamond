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

import java.util.EnumMap;
import java.util.List;
import java.util.Map;

import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.gda.api.acquisition.TrajectoryShape;

public class ScannableTrackDocumentCache {

	private Map<TrajectoryShape, List<ScannableTrackDocument>> scanpathDocuments = new EnumMap<>(TrajectoryShape.class);

	private final List<ScannableTrackDocument> defaultAxesDocuments;

	public ScannableTrackDocumentCache(List<ScannableTrackDocument> defaultAxesDocuments) {
		this.defaultAxesDocuments = defaultAxesDocuments;
	}

	public void cache(TrajectoryShape shape, List<ScannableTrackDocument> document) {
		scanpathDocuments.put(shape, document);
	}

	public List<ScannableTrackDocument> retrieve(TrajectoryShape shape) {
		return scanpathDocuments.computeIfAbsent(shape, s -> defaultAxesDocuments);
	}
}
