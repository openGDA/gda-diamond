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

import static org.eclipse.swt.events.SelectionListener.widgetSelectedAdapter;
import static uk.ac.gda.ui.tool.ClientMessages.SAVED_SCAN_DEFINITION;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGroup;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;

import org.dawnsci.mapping.ui.IMapClickEvent;
import org.dawnsci.mapping.ui.MappedDataView;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.swtdesigner.SWTResourceManager;

import gda.rcp.views.AcquisitionCompositeFactoryBuilder;
import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.DiffractionAcquisitionTypeProperties;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.BeamSelectorConfigurationCompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionConfigurationCompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.PointAndShootConfigurationCompositeFactory;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningConfiguration;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.diamond.daq.mapping.ui.EnableMappingLiveBackgroundAction;
import uk.ac.diamond.daq.mapping.ui.browser.MapBrowser;
import uk.ac.diamond.daq.mapping.ui.controller.ScanningAcquisitionController;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;
import uk.ac.diamond.daq.mapping.ui.properties.AcquisitionsPropertiesHelper;
import uk.ac.diamond.daq.mapping.ui.services.MappingServices;
import uk.ac.gda.api.acquisition.AcquisitionController;
import uk.ac.gda.api.acquisition.AcquisitionControllerException;
import uk.ac.gda.api.acquisition.configuration.ImageCalibration;
import uk.ac.gda.api.acquisition.configuration.MultipleScans;
import uk.ac.gda.api.acquisition.configuration.MultipleScansType;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.composites.AcquisitionsBrowserCompositeFactory;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.selectable.NamedComposite;
import uk.ac.gda.ui.tool.selectable.SelectableContainedCompositeFactory;

public class DiffractionConfigurationView extends ViewPart {

	public static final String ID = "uk.ac.diamond.daq.beamline.k11.view.DiffractionConfigurationView";
	private static final Logger logger = LoggerFactory.getLogger(DiffractionConfigurationView.class);

	private AcquisitionController<ScanningAcquisition> acquisitionController;

	private ScanManagementController smController;

	private LayoutUtilities layoutUtils = new LayoutUtilities();

	public DiffractionConfigurationView() {
		smController = MappingServices.getScanManagementController();
		smController.initialise();
	}

	@Override
	public void createPartControl(Composite parent) {
		logger.trace("Creating {}", this);
		// The overall container
		Composite container = createClientCompositeWithGridLayout(parent, SWT.NONE, 1);
		createClientGridDataFactory().applyTo(container);
		container.setBackground(SWTResourceManager.getColor(SWT.COLOR_WIDGET_BACKGROUND));

		getAcquisitionController().setDefaultNewAcquisitionSupplier(newScanningAcquisition());
		getAcquisitionController().createNewAcquisition();

		AcquisitionCompositeFactoryBuilder builder = new AcquisitionCompositeFactoryBuilder();
		builder.addTopArea(getTopArea());
		builder.addBottomArea(getBottomArea());
		builder.addNewSelectionListener(widgetSelectedAdapter(event -> getAcquisitionController().createNewAcquisition()));
		builder.addSaveSelectionListener(widgetSelectedAdapter(event -> save()));
		builder.addRunSelectionListener(widgetSelectedAdapter(event -> submitExperiment()));
		builder.build().createComposite(container, SWT.NONE);
		logger.trace("Created {}", this);

		prepareMapEvents();
		MappingServices.updateDetectorParameters();

		// Creates camera stream item in the context menu
		EnableMappingLiveBackgroundAction.appendContextMenuAction();
	}

	@Override
	public void dispose() {
		getAcquisitionController().releaseResources();
		super.dispose();
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
	public void setFocus() {
		// Do not necessary
	}

	private CompositeFactory getTopArea() {
		// Theses are the on-demand composites for the specific acquisition configurations
		List<NamedComposite> configurations = new ArrayList<>();
		configurations.add(new DiffractionConfigurationCompositeFactory(getAcquisitionController()));
		configurations.add(new PointAndShootConfigurationCompositeFactory(getAcquisitionController()));
		configurations.add(new BeamSelectorConfigurationCompositeFactory(getAcquisitionController()));

		return new SelectableContainedCompositeFactory(configurations, ClientMessages.ACQUISITIONS);
	}

	private void buildSavedComposite(Composite parent) {
		Group group = createClientGroup(parent, SWT.NONE, 1, SAVED_SCAN_DEFINITION);
		createClientGridDataFactory().applyTo(group);

		CompositeFactory cf = new AcquisitionsBrowserCompositeFactory<>(new MapBrowser(getAcquisitionController()));
		layoutUtils.fillGrab().applyTo(cf.createComposite(group, SWT.BORDER));
	}

	private CompositeFactory getBottomArea() {
		return (parent, style) -> {
			buildSavedComposite(parent);
			return parent;
		};
	}

	private void save() {
		try {
			getAcquisitionController().saveAcquisitionConfiguration();
		} catch (AcquisitionControllerException e) {
			UIHelper.showError("Cannot save acquisition", e, logger);
		}
	}

	private void submitExperiment() {
		try {
			getAcquisitionController().runAcquisition();
		} catch (AcquisitionControllerException e) {
			UIHelper.showError(e.getMessage(), e.getCause().getMessage());
		}
	}

	/**
	 * Creates a new {@link ScanningAcquisition} for a diffraction acquisition. Note that the Detectors set by the
	 * {@link ScanningAcquisitionController#createNewAcquisition()}
	 *
	 * @return
	 */
	private Supplier<ScanningAcquisition> newScanningAcquisition() {
		return () -> {
			ScanningAcquisition newConfiguration = new ScanningAcquisition();
			newConfiguration.setUuid(UUID.randomUUID());
			ScanningConfiguration configuration = new ScanningConfiguration();
			newConfiguration.setAcquisitionConfiguration(configuration);

			newConfiguration.setName("Default name");
			ScanningParameters acquisitionParameters = new ScanningParameters();
			configuration.setImageCalibration(new ImageCalibration.Builder().build());

			// When a new acquisitionType is selected, replaces the acquisition scanPathDocument
			ScanpathDocument.Builder scanpathBuilder = Optional.ofNullable(AcquisitionTemplateType.TWO_DIMENSION_POINT)
				.map(DiffractionAcquisitionTypeProperties::createScanpathDocument)
				.orElseGet(ScanpathDocument.Builder::new);
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

	private AcquisitionController<ScanningAcquisition> getAcquisitionController() {
		if (acquisitionController == null) {
			acquisitionController = new ExperimentScanningAcquisitionController(AcquisitionsPropertiesHelper.AcquisitionPropertyType.DIFFRACTION);
		}
		return acquisitionController;
	}
}
