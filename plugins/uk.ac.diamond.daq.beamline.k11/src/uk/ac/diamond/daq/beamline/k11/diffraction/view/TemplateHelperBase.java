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

import static uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeHelper.shapeFromMappingRegion;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.function.Supplier;

import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionEvent;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanning.ShapeType;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.gda.ui.tool.spring.SpringApplicationContextProxy;

/**
 * Collection of methods to update a {@link ScanningParameters} instance. Constructor and methods are protected
 * because this class is not supposed to be used alone.
 *
 * @author Maurizio Nagni
 */
public class TemplateHelperBase {

	private static final Logger logger = LoggerFactory.getLogger(TemplateHelperBase.class);

	/**
	 * The acquisition configuration supplier
	 */
	private final Supplier<ScanningAcquisition> acquisitionSupplier;

	/**
	 * @param acquisitionSupplier
	 *            the acquisition configuration
	 */
	protected TemplateHelperBase(Supplier<ScanningAcquisition> acquisitionSupplier) {
		super();
		this.acquisitionSupplier = acquisitionSupplier;
	}

	/**
	 * Used to publish {@link ScanningAcquisitionEvent} when the internal {@code acquisition} has been updated
	 */
	protected void publishAcquisitionChanged() {
		SpringApplicationContextProxy.publishEvent(new ScanningAcquisitionEvent(acquisitionSupplier.get()));
	}

	/**
	 * Builds a list of {@link ScannableTrackDocument} from an array of
	 * {@link uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument.Builder}.
	 *
	 * @param scannableTrackBuilders
	 * @return an array of ScannableTrackDocuments
	 */
	public static final List<ScannableTrackDocument> assembleScannableTracks(
			ScannableTrackDocument.Builder... scannableTrackBuilders) {
		List<ScannableTrackDocument> ret = new ArrayList<>();
		Arrays.stream(scannableTrackBuilders).map(ScannableTrackDocument.Builder::build).forEach(ret::add);
		return Collections.unmodifiableList(ret);
	}

	/**
	 * A {@code ScannableTrackDocument.Builder} which can be used to update a {@link ScannableTrackDocument} from the inner {@link ScanpathDocument}
	 * @param index the {@code ScanpathDocument#getScannableTrackDocuments()} index to retrieve.
	 * @return {@code ScannableTrackDocument.Builder}
	 */
	protected ScannableTrackDocument.Builder getScannableTrackDocumentBuilder(int index) {
		return Optional.ofNullable(getScanningParameters().getScanpathDocument())
				.map(scanpath -> findOrCreateScannableTrackDocument(scanpath, index))
				.orElse(new ScannableTrackDocument.Builder());
	}

	/**
	 * Similar to {@link #getScannableTrackDocumentBuilder(int)} but accept a {@code ScannableTrackDocument}.
	 * @param scanpathDocument from where extract the {@code ScannableTrackDocument}
	 * @param index the position of the required {@code ScannableTrackDocument}
	 * @return a builder or null if the index does not exist
	 */
	private ScannableTrackDocument.Builder findOrCreateScannableTrackDocument(ScanpathDocument scanpathDocument, int index) {
		if (index <= scanpathDocument.getScannableTrackDocuments().size() - 1) {
			return new ScannableTrackDocument.Builder(scanpathDocument.getScannableTrackDocuments().get(index));
		}
		return null;
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

	/**
	 * Replaces the inner {@link ScannableTrackDocument} with the new {@code scannableDocuments}
	 * @param scannableTrackDocuments
	 */
	protected void updateTemplateData(List<ScannableTrackDocument> scannableTrackDocuments) {
		updateTemplate(getBuilder().withScannableTrackDocuments(scannableTrackDocuments));
	}

	/**
	 * @return the inner {@code scanningParameters}
	 * @deprecated use {@link #getScanningParameters()}
	 */
	@Deprecated
	protected ScanningParameters getTemplateData() {
		return acquisitionSupplier.get().getAcquisitionConfiguration().getAcquisitionParameters();
	}

	protected static Logger getLogger() {
		return logger;
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
	 * return
	 */
	protected Optional<ShapeType> getShapeType() {
		//To review is is possible to remove the dependency from {@link getRapController()}
		return shapeFromMappingRegion(getRapController().getScanRegionShape());
	}

	protected ScanningParameters getScanningParameters() {
		return acquisitionSupplier.get().getAcquisitionConfiguration().getAcquisitionParameters();
	}
}