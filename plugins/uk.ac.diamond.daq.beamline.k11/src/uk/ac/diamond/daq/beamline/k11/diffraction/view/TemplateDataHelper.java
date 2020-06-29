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

package uk.ac.diamond.daq.beamline.k11.diffraction.view;

import java.util.List;
import java.util.Optional;

import org.eclipse.scanning.api.points.models.AbstractMapModel;
import org.eclipse.scanning.api.points.models.IScanPointGeneratorModel;
import org.eclipse.scanning.api.points.models.TwoAxisGridPointsModel;
import org.eclipse.scanning.api.points.models.TwoAxisLinePointsModel;
import org.eclipse.scanning.api.points.models.TwoAxisPointSingleModel;

import gda.configuration.properties.LocalProperties;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanning.ShapeType;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;

public class TemplateDataHelper extends TemplateHelperBase {

	public TemplateDataHelper(ScanningParameters templateData) {
		super(templateData);
	}

	public void updateTemplateData() {
		getShapeType().ifPresent(this::updateTemplateData);
		if (getLogger().isDebugEnabled()) {
			getLogger().debug(getTemplateData().toString());
		}
	}

	private void updateTemplateData(ShapeType shapeType) {
		Optional<List<ScannableTrackDocument>> scannableDocuments = Optional.empty();
		List<IScanPointGeneratorModel> pathList = getRapController().getScanPathListAndLinkPath();
		switch (shapeType) {
		case CENTRED_RECTANGLE:
			scannableDocuments = pathList.stream().filter(TwoAxisGridPointsModel.class::isInstance).findFirst()
					.map(c -> extractScannableTrackDocument(TwoAxisGridPointsModel.class.cast(c)));
			break;
		case LINE:
			scannableDocuments = pathList.stream().filter(TwoAxisLinePointsModel.class::isInstance).findFirst()
					.map(c -> extractScannableTrackDocument(TwoAxisLinePointsModel.class.cast(c)));
			break;
		case POINT:
			scannableDocuments = pathList.stream().filter(TwoAxisPointSingleModel.class::isInstance).findFirst()
					.map(c -> extractScannableTrackDocument(TwoAxisPointSingleModel.class.cast(c)));
			break;
		default:
			break;
		}
		scannableDocuments.ifPresent(this::updateTemplateData);
	}

	private List<ScannableTrackDocument> extractScannableTrackDocument(TwoAxisGridPointsModel model) {
		ScannableTrackDocument.Builder scannableTrackOneBuilder = getScannableTrackDocumentBuilder(0);

		Optional.ofNullable(model.getBoundingBox()).ifPresent(b -> {
			scannableTrackOneBuilder.withStart(b.getxAxisStart());
			scannableTrackOneBuilder.withStop(b.getxAxisEnd());
		});
		scannableTrackOneBuilder.withScannable(getScannableX(model));

		ScannableTrackDocument.Builder scannableTrackTwoBuilder = getScannableTrackDocumentBuilder(1);
		Optional.ofNullable(model.getBoundingBox()).ifPresent(b -> {
			scannableTrackTwoBuilder.withStart(b.getyAxisStart());
			scannableTrackTwoBuilder.withStop(b.getyAxisEnd());
		});
		scannableTrackTwoBuilder.withScannable(getScannableY(model));

		return assembleScannableTracks(scannableTrackOneBuilder, scannableTrackTwoBuilder);
	}

	private List<ScannableTrackDocument> extractScannableTrackDocument(TwoAxisLinePointsModel model) {
		ScannableTrackDocument.Builder scannableTrackOneBuilder = getScannableTrackDocumentBuilder(0);
		Optional.ofNullable(model.getBoundingLine()).ifPresent(b -> {
			scannableTrackOneBuilder.withStart(b.getxStart());
			scannableTrackOneBuilder.withStop(Math.cos(b.getAngle()) * b.getLength() + b.getxStart());
		});
		scannableTrackOneBuilder.withScannable(getScannableX(model));

		ScannableTrackDocument.Builder scannableTrackTwoBuilder = getScannableTrackDocumentBuilder(1);
		Optional.ofNullable(model.getBoundingLine()).ifPresent(b -> {
			scannableTrackTwoBuilder.withStart(b.getyStart());
			scannableTrackTwoBuilder.withStop(Math.sin(b.getAngle()) * b.getLength() + b.getyStart());
		});
		scannableTrackTwoBuilder.withScannable(getScannableY(model));

		return assembleScannableTracks(scannableTrackOneBuilder, scannableTrackTwoBuilder);
	}

	private List<ScannableTrackDocument> extractScannableTrackDocument(TwoAxisPointSingleModel model) {
		ScannableTrackDocument.Builder scannableTrackOneBuilder = getScannableTrackDocumentBuilder(0);
		scannableTrackOneBuilder.withStart(model.getX());
		scannableTrackOneBuilder.withStop(model.getX());
		scannableTrackOneBuilder.withStep(0);
		scannableTrackOneBuilder.withScannable(getScannableX(model));

		ScannableTrackDocument.Builder scannableTrackTwoBuilder= getScannableTrackDocumentBuilder(1);
		scannableTrackTwoBuilder.withStart(model.getY());
		scannableTrackTwoBuilder.withStop(model.getY());
		scannableTrackTwoBuilder.withStep(0);
		scannableTrackTwoBuilder.withScannable(getScannableY(model));

		return assembleScannableTracks(scannableTrackOneBuilder, scannableTrackTwoBuilder);
	}



	private String getScannableX(AbstractMapModel model) {
		return LocalProperties.get("client.diffraction.scannable.motor.x", model.getxAxisName());
	}

	private String getScannableY(AbstractMapModel model) {
		return LocalProperties.get("client.diffraction.scannable.motor.y", model.getyAxisName());
	}
}
