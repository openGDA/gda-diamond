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

import java.net.URL;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

import org.dawnsci.mapping.ui.IMapClickEvent;
import org.dawnsci.mapping.ui.MappedDataView;
import org.eclipse.dawnsci.plotting.api.IPlottingService;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.rcp.views.AcquisitionCompositeFactoryBuilder;
import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.controller.DiffractionPerspectiveController;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionConfigurationCompositeFactory;
import uk.ac.diamond.daq.beamline.k11.pointandshoot.PointAndShootController;
import uk.ac.diamond.daq.experiment.api.structure.ExperimentController;
import uk.ac.diamond.daq.experiment.api.structure.ExperimentControllerException;
import uk.ac.diamond.daq.mapping.api.document.DetectorDocument;
import uk.ac.diamond.daq.mapping.ui.browser.MapBrowser;
import uk.ac.diamond.daq.mapping.ui.diffraction.base.DiffractionParameterAcquisition;
import uk.ac.diamond.daq.mapping.ui.diffraction.base.DiffractionParameters;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;
import uk.ac.diamond.daq.mapping.ui.experiment.file.FileScanSaver;
import uk.ac.diamond.daq.mapping.ui.experiment.file.SavedScanMetaData;
import uk.ac.diamond.daq.mapping.ui.experiment.saver.PersistenceScanSaver;
import uk.ac.diamond.daq.mapping.ui.experiment.saver.ScanSaver;
import uk.ac.diamond.daq.mapping.ui.properties.DetectorHelper;
import uk.ac.diamond.daq.mapping.ui.properties.DetectorHelper.AcquisitionType;
import uk.ac.diamond.daq.mapping.ui.services.MappingServices;
import uk.ac.gda.api.acquisition.AcquisitionController;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.composites.AcquisitionsBrowserCompositeFactory;
import uk.ac.gda.client.properties.DetectorProperties;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.images.ClientImages;
import uk.ac.gda.ui.tool.spring.SpringApplicationContextProxy;

public class DiffractionScanSelection extends ViewPart {

	public static final String ID = "uk.ac.diamond.daq.beamline.k11.view.DiffractionScanSelection";
	private static final Logger logger = LoggerFactory.getLogger(DiffractionScanSelection.class);

	private AcquisitionController<DiffractionParameterAcquisition> diffController;

	private DiffractionConfigurationCompositeFactory dcf;
	private ScanManagementController smController;
	private PointAndShootController pointAndShootController;
	private ScanSaver scanSaver;
	private Button pointAndShoot;

	private LayoutUtilities layoutUtils = new LayoutUtilities();

	public DiffractionScanSelection() {
		smController = MappingServices.getScanManagementController();
		smController.initialise();
	}

	@Override
	public void createPartControl(Composite parent) {
		logger.info("{} createPartControl - start", this.getClass());
		Optional<List<DetectorProperties>> dp = DetectorHelper.getAcquistionDetector(AcquisitionType.DIFFRACTION);
		int index = 0; // in future may be parametrised
		if (dp.isPresent()) {
			DetectorDocument dd = new DetectorDocument(dp.get().get(index).getDetectorBean(), 0);
			getTemplateData().setDetector(dd);
		}
		AcquisitionCompositeFactoryBuilder builder = new AcquisitionCompositeFactoryBuilder();
		builder.addTopArea(getTopArea());
		builder.addBottomArea(getBottomArea());
		builder.addSaveSelectionListener(widgetSelectedAdapter(event -> getScanSaver().save()));
		builder.addRunSelectionListener(widgetSelectedAdapter(event -> submit()));
		builder.build().createComposite(parent, SWT.NONE);

		prepareMapEvents();
		MappingServices.updateDetectorParameters();
		logger.info("{} createPartControl - end", this.getClass());
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

	private void buildDiffractionPathComposite(Composite parent) {
		Group group = ClientSWTElements.createGroup(parent, 1, DIFFRACTION_SCAN_PATH);
		controller = getPerspectiveController().getDiffractionAcquisitionController();
		dcf = new DiffractionConfigurationCompositeFactory(controller);
		dcf.createComposite(group, SWT.NONE);
	}

	private CompositeFactory getTopArea() {
		return (parent, style) -> {
			buildDiffractionPathComposite(parent);
			Group group = ClientSWTElements.createGroup(parent, 1, POINT_AND_SHOOT);
			GridLayoutFactory.fillDefaults().applyTo(group);
			GridDataFactory.swtDefaults().align(SWT.BEGINNING, SWT.BEGINNING).applyTo(group);

			pointAndShoot = ClientSWTElements.createButton(group, SWT.NONE, START, START_POINT_AND_SHOOT_TP,
					ClientImages.RUN);
			pointAndShoot.addListener(SWT.Selection, e -> togglePointAndShoot());
			return parent;
		};
	}

	private void buildSavedComposite(Composite parent) {
		Group group = ClientSWTElements.createGroup(parent, 1, SAVED_SCAN_DEFINITION);
		CompositeFactory cf = new AcquisitionsBrowserCompositeFactory<SavedScanMetaData>(
				new MapBrowser(getScanSaver()));
		layoutUtils.fillGrab().applyTo(cf.createComposite(group, SWT.BORDER));
	}

	private CompositeFactory getBottomArea() {
		return (parent, style) -> {
			buildSavedComposite(parent);
			return parent;
		};
	}

	private void submit() {
		if (isPointAndShootActive()) {
			UIHelper.showWarning("Cannot run Acquisition", "Point and Shoot mode is active");
			return;
		}

		if (!getExperimentController().isExperimentInProgress()) {
			UIHelper.showError("Cannot start acquisition", "You must start an experiment first");
			return;
		}

		try {
			URL output = getExperimentController().prepareAcquisition(getAcquisitionName());
			logger.debug(
					controller.getAcquisition().getAcquisitionConfiguration().getAcquisitionParameters().toString());
			smController.submitScan(output, getTemplateData());
		} catch (ExperimentControllerException e) {
			UIHelper.showError("Cannot run acquisition", e);
		}
	}

	private ScanSaver getScanSaver() {
		if (scanSaver == null) {
			if (LocalProperties.isPersistenceServiceAvailable()) {
				scanSaver = new PersistenceScanSaver(dcf::load, smController);
			} else {
				scanSaver = new FileScanSaver(dcf::load, smController);
			}
		}
		return scanSaver;
	}

	private void togglePointAndShoot() {
		IPlottingService plottingService = MappingServices.getPlottingService();
		IPlottingSystem<Object> mapPlottingSystem = plottingService.getPlottingSystem("Map");

		ExperimentController experimentController = getExperimentController();
		if (isPointAndShootActive()) { // end current session
			try {
				pointAndShootController.endSession();
				pointAndShootController = null;
				ClientSWTElements.updateButton(pointAndShoot, START, START_POINT_AND_SHOOT_TP, ClientImages.RUN);
				mapPlottingSystem.setTitle(" ");
			} catch (ExperimentControllerException e) {
				UIHelper.showError("Cannot stop Point and Shoot session", e);
			}

		} else { // start new session
			if (experimentController.isExperimentInProgress()) {
				try {
					pointAndShootController = new PointAndShootController(getAcquisitionName(),
							getExperimentController());
					ClientSWTElements.updateButton(pointAndShoot, STOP, STOP_POINT_AND_SHOOT_TP, ClientImages.STOP);
					mapPlottingSystem.setTitle("Point and Shoot: Ctrl+Click to scan");
				} catch (ExperimentControllerException e) {
					UIHelper.showError(getMessage(CANNOT_START_POINT_AND_SHOOT_SESSION), e);
				}

			} else {
				UIHelper.showError("Cannot start Point and Shoot session", "An experiment must be started first");
			}

		}
	}

	private boolean isPointAndShootActive() {
		return pointAndShootController != null;
	}

	private ExperimentController getExperimentController() {
		return Objects.requireNonNull(SpringApplicationContextProxy.getBean(ExperimentController.class));
	}

	private String getAcquisitionName() {
		return getTemplateData().getName();
	}

	private DiffractionParameters getTemplateData() {
		return getPerspectiveController().getDiffractionAcquisitionController().getAcquisition()
				.getAcquisitionConfiguration().getAcquisitionParameters();
	}

	private AcquisitionController<DiffractionParameterAcquisition> controller;

	private DiffractionPerspectiveController getPerspectiveController() {
		return SpringApplicationContextProxy.getBean(DiffractionPerspectiveController.class);
	}
}
