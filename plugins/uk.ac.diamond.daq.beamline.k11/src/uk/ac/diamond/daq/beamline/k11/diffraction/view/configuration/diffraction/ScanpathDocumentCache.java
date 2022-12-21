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
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument.Axis;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.gda.api.acquisition.AcquisitionTemplateType;

public class ScanpathDocumentCache {


	private Map<AcquisitionTemplateType, ScanpathDocument> scanpathDocuments = new EnumMap<>(AcquisitionTemplateType.class);

	public void cache(ScanpathDocument document) {
		scanpathDocuments.put(getInnerShape(document), document);
	}

	private AcquisitionTemplateType getInnerShape(ScanpathDocument document) {
		var shape = document.getModelDocument();

		if (shape == AcquisitionTemplateType.DIFFRACTION_TOMOGRAPHY) {
			// I can't handle the outer dimension, so I'll assume you want a grid
			shape = AcquisitionTemplateType.TWO_DIMENSION_GRID;
		}

		return shape;
	}

	public ScanpathDocument cacheAndChangeShape(ScanpathDocument document, AcquisitionTemplateType shape) {
		cache(document);
		var swapped = scanpathDocuments.computeIfAbsent(shape, s -> defaultDocument(document, shape));

		return new ScanpathDocument(swapped.getModelDocument(), ScanningParametersUtils.updateAxes(document, swapped.getScannableTrackDocuments()));
	}

	private ScanpathDocument defaultDocument(ScanpathDocument document, AcquisitionTemplateType shape) {
		List<ScannableTrackDocument> tracks = List.of(
				createTrack(Axis.X, getXAxisName(document), 0, 5, 5),
				createTrack(Axis.Y, getYAxisName(document), 0, 5, 5));

		return new ScanpathDocument(shape, tracks);
	}

	private String getXAxisName(ScanpathDocument document) {
		return getAxisName(document, Axis.X);
	}

	private String getYAxisName(ScanpathDocument document) {
		return getAxisName(document, Axis.Y);
	}

	private String getAxisName(ScanpathDocument document, Axis axis) {
		return document.getScannableTrackDocuments().stream()
				.filter(track -> track.getAxis() == axis)
				.map(ScannableTrackDocument::getScannable).findFirst().orElseThrow();
	}

	private ScannableTrackDocument createTrack(Axis axis, String axisName, double start, double stop, int points) {
		var track = new ScannableTrackDocument();
		track.setAxis(axis);
		track.setScannable(axisName);
		track.setStart(start);
		track.setStop(stop);
		track.setPoints(points);
		track.setAlternating(true);
		track.setContinuous(true);
		return track;
	}
}
