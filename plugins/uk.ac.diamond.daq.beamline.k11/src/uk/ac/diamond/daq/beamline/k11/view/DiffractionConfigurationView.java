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
import static uk.ac.gda.ui.tool.ClientMessages.CANNOT_START_POINT_AND_SHOOT_SESSION;
import static uk.ac.gda.ui.tool.ClientMessages.DIFFRACTION_SCAN_PATH;
import static uk.ac.gda.ui.tool.ClientMessages.POINT_AND_SHOOT;
import static uk.ac.gda.ui.tool.ClientMessages.SAVED_SCAN_DEFINITION;
import static uk.ac.gda.ui.tool.ClientMessages.START;
import static uk.ac.gda.ui.tool.ClientMessages.START_POINT_AND_SHOOT_TP;
import static uk.ac.gda.ui.tool.ClientMessages.STOP;
import static uk.ac.gda.ui.tool.ClientMessages.STOP_POINT_AND_SHOOT_TP;
import static uk.ac.gda.ui.tool.ClientMessagesUtility.getMessage;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientButton;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGroup;
import static uk.ac.gda.ui.tool.ClientSWTElements.updateButton;

import java.net.URL;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;

import org.dawnsci.mapping.ui.IMapClickEvent;
import org.dawnsci.mapping.ui.MappedDataView;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.rcp.views.AcquisitionCompositeFactoryBuilder;
import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionConfigurationCompositeFactory;
import uk.ac.diamond.daq.beamline.k11.pointandshoot.PointAndShootController;
import uk.ac.diamond.daq.experiment.api.structure.ExperimentController;
import uk.ac.diamond.daq.experiment.api.structure.ExperimentControllerException;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningConfiguration;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.ui.EnableMappingLiveBackgroundAction;
import uk.ac.diamond.daq.mapping.ui.browser.MapBrowser;
import uk.ac.diamond.daq.mapping.ui.controller.ScanningAcquisitionController;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;
import uk.ac.diamond.daq.mapping.ui.properties.DetectorHelper.AcquisitionType;
import uk.ac.diamond.daq.mapping.ui.services.MappingServices;
import uk.ac.gda.api.acquisition.AcquisitionController;
import uk.ac.gda.api.acquisition.AcquisitionControllerException;
import uk.ac.gda.api.acquisition.configuration.ImageCalibration;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.composites.AcquisitionsBrowserCompositeFactory;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.images.ClientImages;
import uk.ac.gda.ui.tool.spring.SpringApplicationContextProxy;

public class DiffractionConfigurationView extends ViewPart {

	public static final String ID = "uk.ac.diamond.daq.beamline.k11.view.DiffractionConfigurationView";
	private static final Logger logger = LoggerFactory.getLogger(DiffractionConfigurationView.class);

	private AcquisitionController<ScanningAcquisition> controller;

	private ScanManagementController smController;
	private PointAndShootController pointAndShootController;
	private Button pointAndShoot;

	private LayoutUtilities layoutUtils = new LayoutUtilities();

	public DiffractionConfigurationView() {
		smController = MappingServices.getScanManagementController();
		smController.initialise();
	}

	@Override
	public void createPartControl(Composite parent) {
		controller = getPerspectiveController();
		controller.setDefaultNewAcquisitionSupplier(newScanningAcquisition());
		controller.createNewAcquisition();

		logger.info("{} createPartControl - start", this.getClass());
		AcquisitionCompositeFactoryBuilder builder = new AcquisitionCompositeFactoryBuilder();
		builder.addTopArea(getTopArea());
		builder.addBottomArea(getBottomArea());
		builder.addNewSelectionListener(widgetSelectedAdapter(event -> controller.createNewAcquisition()));
		builder.addSaveSelectionListener(widgetSelectedAdapter(event -> save()));
		builder.addRunSelectionListener(widgetSelectedAdapter(event -> submitExperiment()));

		Composite container = ClientSWTElements.createClientCompositeWithGridLayout(parent, SWT.NONE, 1);
		ClientSWTElements.createClientGridDataFactory().applyTo(container);

		builder.build().createComposite(container, SWT.NONE);

		prepareMapEvents();
		MappingServices.updateDetectorParameters();

		// Creates camera stream item in the context menu
		EnableMappingLiveBackgroundAction.appendContextMenuAction();

		logger.info("{} createPartControl - end", this.getClass());
	}

	@Override
	public void dispose() {
		Optional.ofNullable(controller).ifPresent(AcquisitionController::releaseResources);
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

	@SuppressWarnings("unchecked")
	private AcquisitionController<ScanningAcquisition> getPerspectiveController() {
		return (AcquisitionController<ScanningAcquisition>) SpringApplicationContextProxy
				.getBean("scanningAcquisitionController", AcquisitionType.DIFFRACTION);
	}

	private void buildDiffractionPathComposite(Composite parent) {
		Group group = createClientGroup(parent, SWT.NONE, 1, DIFFRACTION_SCAN_PATH);
		createClientGridDataFactory().grab(true, false).applyTo(group);

		DiffractionConfigurationCompositeFactory factory = new DiffractionConfigurationCompositeFactory(controller);
		factory.createComposite(group, SWT.NONE);
	}

	private CompositeFactory getTopArea() {
		return (parent, style) -> {
			buildDiffractionPathComposite(parent);
			Group group = createClientGroup(parent, SWT.NONE, 1, POINT_AND_SHOOT);
			createClientGridDataFactory().applyTo(group);

			pointAndShoot = createClientButton(group, SWT.NONE, START, START_POINT_AND_SHOOT_TP, ClientImages.RUN);
			createClientGridDataFactory().applyTo(pointAndShoot);

			pointAndShoot.addListener(SWT.Selection, e -> togglePointAndShoot());
			return parent;
		};
	}

	private void buildSavedComposite(Composite parent) {
		Group group = createClientGroup(parent, SWT.NONE, 1, SAVED_SCAN_DEFINITION);
		createClientGridDataFactory().applyTo(group);

		CompositeFactory cf = new AcquisitionsBrowserCompositeFactory<>(new MapBrowser(controller));
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
			controller.saveAcquisitionConfiguration();
		} catch (AcquisitionControllerException e) {
			UIHelper.showError("Cannot save acquisition", e, logger);
		}
	}

	private void submitExperiment() {
		if (isPointAndShootActive()) {
			UIHelper.showWarning("Cannot run Acquisition", "Point and Shoot mode is active");
			return;
		}

		if (getExperimentController().isPresent()) {
			validateExperimentRequest(getExperimentController().get());
		} else {
			UIHelper.showError("Cannot start acquisition", "Experiment Controller not present");
		}
	}

	private void validateExperimentRequest(ExperimentController experimentController) {
		if (!experimentController.isExperimentInProgress()) {
			UIHelper.showError("Cannot start acquisition", "You must start an experiment first");
			return;
		}

		try {
			submit(experimentController.prepareAcquisition(getAcquisitionName()));
		} catch (ExperimentControllerException | AcquisitionControllerException e) {
			UIHelper.showError("Cannot run acquisition", e);
		}
	}

	private void submit(URL acquisitionOutput) throws AcquisitionControllerException {
		getAcquisition().setAcquisitionLocation(acquisitionOutput);
		controller.runAcquisition();
	}

	private void togglePointAndShoot() {
		if (isPointAndShootActive()) {
			// end current session
			endPointAndShootSession();
		} else {
			// start new session
			getExperimentController().ifPresent(this::startPointAndShootSession);
		}
	}

	private IPlottingSystem<Object> getMapPlottingSystem() {
		return MappingServices.getPlottingService().getPlottingSystem("Map");
	}

	private void startPointAndShootSession(ExperimentController experimentController) {
		if (experimentController.isExperimentInProgress()) {
			try {
				pointAndShootController = new PointAndShootController(getAcquisitionName(), experimentController);
				updateButton(pointAndShoot, STOP, STOP_POINT_AND_SHOOT_TP, ClientImages.STOP);
				getMapPlottingSystem().setTitle("Point and Shoot: Ctrl+Click to scan");
			} catch (ExperimentControllerException e) {
				UIHelper.showError(getMessage(CANNOT_START_POINT_AND_SHOOT_SESSION), e);
			}
		} else {
			UIHelper.showError("Cannot start Point and Shoot session", "An experiment must be started first");
		}
	}

	private void endPointAndShootSession() {
		try {
			pointAndShootController.endSession();
			pointAndShootController = null;
			updateButton(pointAndShoot, START, START_POINT_AND_SHOOT_TP, ClientImages.RUN);
			getMapPlottingSystem().setTitle(" ");
		} catch (ExperimentControllerException e) {
			UIHelper.showError("Cannot stop Point and Shoot session", e);
		}
	}

	private boolean isPointAndShootActive() {
		return pointAndShootController != null;
	}

	private String getAcquisitionName() {
		return getAcquisition().getName();
	}

	private ScanningAcquisition getAcquisition() {
		return getController().getAcquisition();
	}

	private AcquisitionController<ScanningAcquisition> getController() {
		return controller;
	}

	private Optional<ExperimentController> getExperimentController() {
		return SpringApplicationContextProxy.getOptionalBean(ExperimentController.class);
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
			// Diffraction detectors are set by the controller
			configuration.setImageCalibration(new ImageCalibration());
			// *-------------------------------

			newConfiguration.getAcquisitionConfiguration().setAcquisitionParameters(acquisitionParameters);
			return newConfiguration;
		};
	}
}
