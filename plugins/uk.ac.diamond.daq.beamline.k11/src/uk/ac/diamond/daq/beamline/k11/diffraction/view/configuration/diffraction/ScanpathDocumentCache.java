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

import java.util.Collections;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

import gda.mscan.element.Mutator;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;

public class ScanpathDocumentCache {


	private Map<AcquisitionTemplateType, ScanpathDocument> scanpathDocuments = new EnumMap<>(AcquisitionTemplateType.class);

	public void cache(ScanpathDocument document) {
		scanpathDocuments.put(document.getModelDocument(), document);
	}

	public ScanpathDocument cacheAndChangeShape(ScanpathDocument document, AcquisitionTemplateType shape) {
		scanpathDocuments.put(document.getModelDocument(), document);
		return scanpathDocuments.computeIfAbsent(shape, s -> defaultDocument(document, shape));
	}

	private ScanpathDocument defaultDocument(ScanpathDocument document, AcquisitionTemplateType shape) {
		List<ScannableTrackDocument> tracks = List.of(
				createTrack("x", getXAxisName(document), 0, 5, 5),
				createTrack("y", getYAxisName(document), 0, 5, 5));

		Map<Mutator, List<Number>> mutators = new EnumMap<>(Mutator.class);

		switch (shape) {
		case TWO_DIMENSION_GRID:
			mutators.put(Mutator.CONTINUOUS, Collections.emptyList());
			mutators.put(Mutator.ALTERNATING, Collections.emptyList());
			break;
		case TWO_DIMENSION_LINE:
			mutators.put(Mutator.CONTINUOUS, Collections.emptyList());
			break;
		case TWO_DIMENSION_POINT:
			break;
		default:
			throw new IllegalArgumentException("Unsupported type: " + shape.toString());
		}

		return new ScanpathDocument(shape, tracks, mutators);
	}

	private String getXAxisName(ScanpathDocument document) {
		return getAxisName(document, "x");
	}

	private String getYAxisName(ScanpathDocument document) {
		return getAxisName(document, "y");
	}

	private String getAxisName(ScanpathDocument document, String axis) {
		return document.getScannableTrackDocuments().stream()
				.filter(track -> track.getAxis().equalsIgnoreCase(axis))
				.map(ScannableTrackDocument::getScannable).findFirst().orElseThrow();
	}

	private ScannableTrackDocument createTrack(String axis, String axisName, double start, double stop, int points) {
		return new ScannableTrackDocument.Builder()
				.withAxis(axis)
				.withScannable(axisName)
				.withStart(start)
				.withStop(stop)
				.withPoints(points)
				.build();
	}
}
