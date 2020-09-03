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

import static uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeHelper.acquisitionTypeFromMappingRegion;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.function.Supplier;

import org.eclipse.scanning.api.points.models.AbstractMapModel;
import org.eclipse.scanning.api.points.models.IScanPointGeneratorModel;
import org.eclipse.scanning.api.points.models.TwoAxisGridPointsModel;
import org.eclipse.scanning.api.points.models.TwoAxisLinePointsModel;
import org.eclipse.scanning.api.points.models.TwoAxisPointSingleModel;
import org.eclipse.ui.PlatformUI;
import org.springframework.util.CollectionUtils;

import gda.configuration.properties.LocalProperties;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.diamond.daq.mapping.api.document.helper.ScannableTrackDocumentHelper;
import uk.ac.diamond.daq.mapping.api.document.helper.ScanningParametersHelperBase;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.diamond.daq.mapping.region.CentredRectangleMappingRegion;
import uk.ac.diamond.daq.mapping.region.LineMappingRegion;
import uk.ac.diamond.daq.mapping.region.PointMappingRegion;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;

/**
 * Adapt
 * <ul
 * <li>
 * updates the underlying {@link RegionAndPathController} after loading a {@link ScanningAcquisition}
 * </li>
 * <li>
 * updates the {@link ScanningAcquisition} after a change in the {@link RegionAndPathController} (i.e. the user reshape the region with the mouse)
 * </li>
 * </ul>
 *
 * @author Maurizio Nagni
 */
public class TemplateDataHelper {

	private final ScannableTrackDocumentHelper scannableTrackDocumentHelper;
	private final Supplier<ScanningAcquisition> acquisitionSupplier;

	public TemplateDataHelper(Supplier<ScanningAcquisition> acquisitionSupplier) {
		this.acquisitionSupplier = acquisitionSupplier;
		this.scannableTrackDocumentHelper = new ScannableTrackDocumentHelper(this::getScanningParameters);
	}

	/**
	 * Called when the user moves the ROI on the plotting system, i.e. with the mouse.
	 * Extracts data from the {@link IScanPointGeneratorModel} and update the {@code ScannableTrackDocument} list.
	 * @return {@code true} if the update succeed, {@code false} no update was necessary
	 */
	public boolean updateScannableTracksDocument() {
		Optional<List<ScannableTrackDocument>> scannableDocuments = Optional.empty();
		List<IScanPointGeneratorModel> pathList = getRapController().getScanPathListAndLinkPath();
		AcquisitionTemplateType acquisitionTemplateType = getScanningParameters().getScanpathDocument().getModelDocument();
		switch (acquisitionTemplateType) {
		case TWO_DIMENSION_GRID:
			scannableDocuments = pathList.stream()
				.filter(TwoAxisGridPointsModel.class::isInstance)
				.findFirst()
				.map(c -> extractScannableTrackDocument(TwoAxisGridPointsModel.class.cast(c)));
			break;
		case TWO_DIMENSION_LINE:
			scannableDocuments = pathList.stream()
				.filter(TwoAxisLinePointsModel.class::isInstance)
				.findFirst()
				.map(c -> extractScannableTrackDocument(TwoAxisLinePointsModel.class.cast(c)));
			break;
		case TWO_DIMENSION_POINT:
			scannableDocuments = pathList.stream()
				.filter(TwoAxisPointSingleModel.class::isInstance)
				.findFirst()
				.map(TwoAxisPointSingleModel.class::cast)
				.map(this::extractScannableTrackDocument);
			break;
		default:
			break;
		}

		// Avoids loops between
		List<ScannableTrackDocument> oldDocs = getScanningParameters().getScanpathDocument().getScannableTrackDocuments();
		long count = scannableDocuments
			.orElseGet(ArrayList::new)
			.stream()
			.filter(newDoc -> CollectionUtils.contains(oldDocs.iterator(), newDoc))
			.count();
		if (count == oldDocs.size())
			return false;

		scannableDocuments.ifPresent(this::updateTemplateData);
		return true;
	}

	/**
	 * Called when a ScanningAcquisition is loaded
	 */
	public void updateIMappingScanRegionShape() {
		IMappingScanRegionShape mappingRegionShape = getRapController().getScanRegionShape();
		ScannableTrackDocument trackDocument;
		if (PointMappingRegion.class.isInstance(mappingRegionShape)) {
			PointMappingRegion region = PointMappingRegion.class.cast(rapController.getScanRegionShape());
			trackDocument = getScanningParameters().getScanpathDocument().getScannableTrackDocuments().get(0);
			region.setxPosition(trackDocument.getStart());
			trackDocument = getScanningParameters().getScanpathDocument().getScannableTrackDocuments().get(1);
			region.setyPosition(trackDocument.getStart());
		} else if (LineMappingRegion.class.isInstance(mappingRegionShape)) {
			LineMappingRegion region = LineMappingRegion.class.cast(rapController.getScanRegionShape());
			trackDocument = getScanningParameters().getScanpathDocument().getScannableTrackDocuments().get(0);
			region.setxStart(trackDocument.getStart());
			region.setxStop(trackDocument.getStop());
			trackDocument = getScanningParameters().getScanpathDocument().getScannableTrackDocuments().get(1);
			region.setyStart(trackDocument.getStart());
			region.setyStop(trackDocument.getStop());
		} else if (CentredRectangleMappingRegion.class.isInstance(mappingRegionShape)) {
			CentredRectangleMappingRegion region = CentredRectangleMappingRegion.class.cast(rapController.getScanRegionShape());
			trackDocument = getScanningParameters().getScanpathDocument().getScannableTrackDocuments().get(0);
			double centre = (trackDocument.getStart() + trackDocument.getStop())/2;
			double range = (trackDocument.getStop() - trackDocument.getStart());
			region.setxCentre(centre);
			region.setxRange(range);
			trackDocument = getScanningParameters().getScanpathDocument().getScannableTrackDocuments().get(1);
			centre = (trackDocument.getStart() + trackDocument.getStop())/2;
			range = (trackDocument.getStop() - trackDocument.getStart());
			region.setyCentre(centre);
			region.setyRange(range);
		}
	}

	private List<ScannableTrackDocument> extractScannableTrackDocument(TwoAxisGridPointsModel model) {
		ScannableTrackDocument.Builder[] tracks = new ScannableTrackDocument.Builder[2];

		tracks[0] = scannableTrackDocumentHelper.getScannableTrackDocumentBuilder(0);
		Optional.ofNullable(model.getBoundingBox()).ifPresent(b -> {
			tracks[0].withStart(b.getxAxisStart());
			tracks[0].withStop(b.getxAxisEnd());
		});
		tracks[0].withScannable(getScannableX(model));

		tracks[1] = scannableTrackDocumentHelper.getScannableTrackDocumentBuilder(1);
		Optional.ofNullable(model.getBoundingBox()).ifPresent(b -> {
			tracks[1].withStart(b.getyAxisStart());
			tracks[1].withStop(b.getyAxisEnd());
		});
		tracks[1].withScannable(getScannableY(model));

		return ScanningParametersHelperBase.assembleScannableTracks(tracks);
	}

	private List<ScannableTrackDocument> extractScannableTrackDocument(TwoAxisLinePointsModel model) {
		ScannableTrackDocument.Builder[] tracks = new ScannableTrackDocument.Builder[2];

		tracks[0] = scannableTrackDocumentHelper.getScannableTrackDocumentBuilder(0);
		Optional.ofNullable(model.getBoundingLine()).ifPresent(b -> {
			tracks[0].withStart(b.getxStart());
			tracks[0].withStop(Math.cos(b.getAngle()) * b.getLength() + b.getxStart());
		});
		tracks[0].withScannable(getScannableX(model));

		tracks[1] = scannableTrackDocumentHelper.getScannableTrackDocumentBuilder(1);
		Optional.ofNullable(model.getBoundingLine()).ifPresent(b -> {
			tracks[1].withStart(b.getyStart());
			tracks[1].withStop(Math.sin(b.getAngle()) * b.getLength() + b.getyStart());
		});
		tracks[1].withScannable(getScannableY(model));

		return ScanningParametersHelperBase.assembleScannableTracks(tracks);
	}

	private List<ScannableTrackDocument> extractScannableTrackDocument(TwoAxisPointSingleModel model) {
		ScannableTrackDocument.Builder[] tracks = new ScannableTrackDocument.Builder[2];

		tracks[0] = scannableTrackDocumentHelper.getScannableTrackDocumentBuilder(0);
		tracks[0].withStart(model.getX());
		tracks[0].withStop(model.getX());
		tracks[0].withStep(0);
		tracks[0].withScannable(getScannableX(model));

		tracks[1] = scannableTrackDocumentHelper.getScannableTrackDocumentBuilder(1);
		tracks[1].withStart(model.getY());
		tracks[1].withStop(model.getY());
		tracks[1].withStep(0);
		tracks[1].withScannable(getScannableY(model));

		return ScanningParametersHelperBase.assembleScannableTracks(tracks);
	}

	private String getScannableX(AbstractMapModel model) {
		return LocalProperties.get("client.diffraction.scannable.motor.x", model.getxAxisName());
	}

	private String getScannableY(AbstractMapModel model) {
		return LocalProperties.get("client.diffraction.scannable.motor.y", model.getyAxisName());
	}

	private ScanningParameters getScanningParameters() {
		return this.acquisitionSupplier.get().getAcquisitionConfiguration().getAcquisitionParameters();
	}

	protected Optional<AcquisitionTemplateType> getAcquisitionTemplateType() {
		//To review is is possible to remove the dependency from {@link getRapController()}
		return acquisitionTypeFromMappingRegion(getRapController().getScanRegionShape());
	}

	/**
	 * To review and remove. This property does not really fit the purpose of this class
	 */
	private final RegionAndPathController rapController = PlatformUI.getWorkbench()
			.getService(RegionAndPathController.class);

	protected RegionAndPathController getRapController() {
		return rapController;
	}

	/**
	 * Replaces the inner {@link ScannableTrackDocument} with the new {@code scannableDocuments}
	 * @param scannableTrackDocuments
	 */
	protected void updateTemplateData(List<ScannableTrackDocument> scannableTrackDocuments) {
		updateTemplate(getBuilder().withScannableTrackDocuments(scannableTrackDocuments));
	}

	/**
	 * Clones the existing scanpathDocument otherwise creates a new one. A class calling this method, is going to modify
	 * the {@link ScanpathDocument} instance returned by {@code getTemplateData().getScanpathDocument()}, which may
	 * still not exist. Consequently this method return a builder either on the existing {@link ScanpathDocument} or
	 * creates for the request a brand new one.
	 *
	 * @return clones the existing scanpathDocument otherwise creates a new one
	 */
	protected ScanpathDocument.Builder getBuilder() {
		return ScanpathDocument.Builder.cloneScanpathDocument(getScanningParameters().getScanpathDocument());
	}

	/**
	 * Replaces the inner {@link ScanpathDocument} with the one generated by the {@code builder}
	 * @param builder the new, to build, {@code ScanpathDocument}
	 */
	protected void updateTemplate(ScanpathDocument.Builder builder) {
		getScanningParameters().setScanpathDocument(builder.build());
	}
}
