/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.view;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;

import org.dawnsci.mapping.ui.IMapClickEvent;
import org.dawnsci.mapping.ui.MappedDataView;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.IWorkbenchPage;

import gda.rcp.views.Browser;
import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.beamselectorscan.BeamSelectorButtonControlledCompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.DiffractionButtonControlledCompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.pointandshoot.PointAndShootButtonControlledCompositeFactory;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningConfiguration;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.diamond.daq.mapping.ui.BackgroundStateHelper;
import uk.ac.diamond.daq.mapping.ui.LiveStreamBackgroundAction;
import uk.ac.diamond.daq.mapping.ui.browser.MapBrowser;
import uk.ac.diamond.daq.mapping.ui.controller.ScanningAcquisitionController;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;
import uk.ac.diamond.daq.mapping.ui.experiment.controller.ExperimentScanningAcquisitionController;
import uk.ac.diamond.daq.mapping.ui.properties.AcquisitionTypeProperties;
import uk.ac.diamond.daq.mapping.ui.properties.AcquisitionsPropertiesHelper;
import uk.ac.diamond.daq.mapping.ui.services.MappingServices;
import uk.ac.gda.api.acquisition.AcquisitionController;
import uk.ac.gda.api.acquisition.configuration.ImageCalibration;
import uk.ac.gda.api.acquisition.configuration.MultipleScans;
import uk.ac.gda.api.acquisition.configuration.MultipleScansType;
import uk.ac.gda.ui.tool.AcquisitionConfigurationView;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.selectable.NamedCompositeFactory;
import uk.ac.gda.ui.tool.selectable.SelectableContainedCompositeFactory;

public class DiffractionConfigurationView extends AcquisitionConfigurationView {

	public static final String ID = "uk.ac.diamond.daq.beamline.k11.view.DiffractionConfigurationView";

	private AcquisitionController<ScanningAcquisition> acquisitionController;

	private ScanManagementController smController;

	private LiveStreamBackgroundAction liveStreamAction;

	public DiffractionConfigurationView() {
		smController = MappingServices.getScanManagementController();
		smController.initialise();
	}

	@Override
	public void createPartControl(Composite parent) {
		super.createPartControl(parent);
		prepareMapEvents();
		MappingServices.updateDetectorParameters();
		// Creates camera stream item in the context menu
		liveStreamAction = new LiveStreamBackgroundAction(new BackgroundStateHelper());
		//EnableMappingLiveBackgroundAction.appendContextMenuAction();
	}

	/**
	 * Point&Shoot depends on {@link IMapClickEvent}s firing when users click on the map. The producer of these is
	 * registered once the {@link MappedDataView} is created; here Eclipse finds it, creating it and registering all the
	 * required components.
	 */
	private void prepareMapEvents() {
		final IWorkbenchPage page = getSite().getPage();
		page.findView(MappedDataView.ID);
	}

	@Override
	protected CompositeFactory getTopArea(Supplier<Composite> controlButtonsContainerSupplier) {
		// Theses are the on-demand composites for the specific acquisition configurations
		List<NamedCompositeFactory> configurations = new ArrayList<>();
		configurations.add(new DiffractionButtonControlledCompositeFactory(getAcquisitionController(), controlButtonsContainerSupplier));
		configurations.add(new PointAndShootButtonControlledCompositeFactory(getAcquisitionController(), controlButtonsContainerSupplier));
		configurations.add(new BeamSelectorButtonControlledCompositeFactory(getAcquisitionController(), controlButtonsContainerSupplier));
		return new SelectableContainedCompositeFactory(configurations, ClientMessages.ACQUISITIONS);
	}

	@Override
	protected Browser<?> getBrowser() {
		return new MapBrowser(getAcquisitionController());
	}

	/**
	 * Creates a new {@link ScanningAcquisition} for a diffraction acquisition. Note that the Detectors set by the
	 * {@link ScanningAcquisitionController#createNewAcquisition()}
	 *
	 * @return the new scanning acquisition
	 */
	@Override
	protected Supplier<ScanningAcquisition> newScanningAcquisition() {
		return () -> {
			ScanningAcquisition newConfiguration = new ScanningAcquisition();
			newConfiguration.setUuid(UUID.randomUUID());
			ScanningConfiguration configuration = new ScanningConfiguration();
			newConfiguration.setAcquisitionConfiguration(configuration);

			newConfiguration.setName("Default name");
			ScanningParameters acquisitionParameters = new ScanningParameters();
			configuration.setImageCalibration(new ImageCalibration.Builder().build());

			// When a new acquisitionType is selected, replaces the acquisition scanPathDocument
			String acquisitionType = "diffraction";
			ScanpathDocument.Builder scanpathBuilder =
					AcquisitionTypeProperties.getAcquisitionProperties(acquisitionType)
					.buildScanpathBuilder(AcquisitionTemplateType.TWO_DIMENSION_POINT);
			// *-------------------------------
//			ScannableTrackDocument.Builder scannableTrackBuilder = new ScannableTrackDocument.Builder();
//			scannableTrackBuilder.withPoints(1);
//			IScannableMotor ism = getStageController().getStageDescription().getMotors()
//					.get(StageDevice.MOTOR_STAGE_ROT_Y);
//			scannableTrackBuilder.withScannable(ism.getName());
//			List<ScannableTrackDocument> scannableTrackDocuments = new ArrayList<>();
//			scannableTrackDocuments.add(scannableTrackBuilder.build());
//			scanpathBuilder.withScannableTrackDocuments(scannableTrackDocuments);
			acquisitionParameters.setScanpathDocument(scanpathBuilder.build());

			MultipleScans.Builder multipleScanBuilder = new MultipleScans.Builder();
			multipleScanBuilder.withMultipleScansType(MultipleScansType.REPEAT_SCAN);
			multipleScanBuilder.withNumberRepetitions(1);
			multipleScanBuilder.withWaitingTime(0);
			configuration.setMultipleScans(multipleScanBuilder.build());
			newConfiguration.getAcquisitionConfiguration().setAcquisitionParameters(acquisitionParameters);

			// --- NOTE---
			// The creation of the acquisition engine and the used detectors documents are delegated to the ScanningAcquisitionController
			// --- NOTE---

			return newConfiguration;
		};
	}

	@Override
	protected AcquisitionController<ScanningAcquisition> getAcquisitionController() {
		if (acquisitionController == null) {
			acquisitionController = new ExperimentScanningAcquisitionController(AcquisitionsPropertiesHelper.AcquisitionPropertyType.DIFFRACTION);
		}
		return acquisitionController;
	}
}
