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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.density;

import java.util.EnumMap;
import java.util.Map;
import java.util.Optional;
import java.util.function.Supplier;
import java.util.stream.IntStream;

import org.springframework.context.ApplicationListener;

import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.gda.api.acquisition.resource.event.AcquisitionConfigurationResourceLoadEvent;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.WidgetUtilities;

/**
 * Listens to {@link ScanningAcquisitionChangeEvent} published by any components updating the active {@link ScanningAcquisition}
 * and update the underlying {@link RegionAndPathController}
 *
 * @author Maurizio Nagni
 */
public class RegionAndPathControllerUpdater {

	/**
	 * Maps, for each AcquisitionTemplateType, the relevant density properties for the associated IScanPointGeneratorModel class
	 */
	private static final Map<AcquisitionTemplateType, String[]> acquisitionTemplateTypeProperties = new EnumMap<>(AcquisitionTemplateType.class);

	static {
		acquisitionTemplateTypeProperties.put(AcquisitionTemplateType.TWO_DIMENSION_POINT, new String[] {});
		acquisitionTemplateTypeProperties.put(AcquisitionTemplateType.TWO_DIMENSION_LINE, new String[] { "points" });
		acquisitionTemplateTypeProperties.put(AcquisitionTemplateType.TWO_DIMENSION_GRID, new String[] { "xAxisPoints", "yAxisPoints" });
	}

	private final Supplier<ScanningAcquisition> acquisitionSupplier;
	private final RegionAndPathController rapController;

	public RegionAndPathControllerUpdater(Supplier<ScanningAcquisition> acquisitionSupplier, RegionAndPathController rapController) {
		super();
		this.acquisitionSupplier = acquisitionSupplier;
		this.rapController = rapController;
		SpringApplicationContextFacade.addDisposableApplicationListener(this, listenToScanningAcquisitionChanges);
		SpringApplicationContextFacade.addDisposableApplicationListener(this, listenToAcquisitionConfigurationResourceLoadEvent);

	}

	// At the moment is not possible to use anonymous lambda expression because it
	// generates a class cast exception
	private ApplicationListener<ScanningAcquisitionChangeEvent> listenToScanningAcquisitionChanges = new ApplicationListener<ScanningAcquisitionChangeEvent>() {
		@Override
		public void onApplicationEvent(ScanningAcquisitionChangeEvent event) {
			updateRap();
		}

		private AcquisitionTemplateType getSelectedAcquisitionTemplateType() {
			return Optional.ofNullable(getScanningParameters())
					.map(ScanningParameters::getScanpathDocument)
					.map(ScanpathDocument::getModelDocument)
					.orElse(null);
		}

		private Optional<Integer> getPoints(int index) {
			return Optional.ofNullable(getScannableTrackDocument(index))
				.map(ScannableTrackDocument::getPoints);
		}

		private ScannableTrackDocument getScannableTrackDocument(int index) {
			return Optional.ofNullable(getScanningParameters())
				.map(ScanningParameters::getScanpathDocument)
				.map(ScanpathDocument::getScannableTrackDocuments)
				.filter(l -> !l.isEmpty())
				.map(l -> l.get(index))
				.orElseGet(() -> null);
		}

		private ScanningParameters getScanningParameters() {
			return getScanningAcquisition().getAcquisitionConfiguration().getAcquisitionParameters();
		}

		private ScanningAcquisition getScanningAcquisition() {
			return acquisitionSupplier.get();
		}

		private void updateRap() {
			String[] properties = Optional.ofNullable(getSelectedAcquisitionTemplateType())
				.map(acquisitionTemplateTypeProperties::get)
				.orElseGet(() -> new String[0]);
//			String[] properties = acquisitionTemplateTypeProperties.get(getSelectedAcquisitionTemplateType());
			IntStream.range(0, properties.length)
			.forEach(index -> {
				if (WidgetUtilities.isWritableProperty(rapController.getScanPathModel(), properties[index])) {
					getPoints(index).ifPresent(iPoints -> WidgetUtilities.setPropertyValue(rapController.getScanPathModel(), properties[index], iPoints));
				}
			});
			rapController.updatePoints();
		}
	};

	// At the moment is not possible to use anonymous lambda expression because it
	// generates a class cast exception
	private ApplicationListener<AcquisitionConfigurationResourceLoadEvent> listenToAcquisitionConfigurationResourceLoadEvent = new ApplicationListener<AcquisitionConfigurationResourceLoadEvent>() {
		@Override
		public void onApplicationEvent(AcquisitionConfigurationResourceLoadEvent event) {
			updateRap();
		}

		private AcquisitionTemplateType getSelectedAcquisitionTemplateType() {
			return Optional.ofNullable(getScanningParameters())
					.map(ScanningParameters::getScanpathDocument)
					.map(ScanpathDocument::getModelDocument)
					.orElse(null);
		}

		private Optional<Integer> getPoints(int index) {
			return Optional.ofNullable(getScannableTrackDocument(index))
				.map(ScannableTrackDocument::getPoints);
		}

		private ScannableTrackDocument getScannableTrackDocument(int index) {
			return Optional.ofNullable(getScanningParameters())
				.map(ScanningParameters::getScanpathDocument)
				.map(ScanpathDocument::getScannableTrackDocuments)
				.filter(l -> !l.isEmpty())
				.map(l -> l.get(index))
				.orElseGet(() -> null);
		}

		private ScanningParameters getScanningParameters() {
			return getScanningAcquisition().getAcquisitionConfiguration().getAcquisitionParameters();
		}

		private ScanningAcquisition getScanningAcquisition() {
			return acquisitionSupplier.get();
		}

		private void updateRap() {
			String[] properties = Optional.ofNullable(getSelectedAcquisitionTemplateType())
					.map(acquisitionTemplateTypeProperties::get)
					.orElseGet(() -> new String[0]);
			IntStream.range(0, properties.length)
			.forEach(index -> {
				if (WidgetUtilities.isWritableProperty(rapController.getScanPathModel(), properties[index])) {
					getPoints(index).ifPresent(iPoints -> WidgetUtilities.setPropertyValue(rapController.getScanPathModel(), properties[index], iPoints));
				}
			});
			rapController.updatePoints();
		}
	};
}