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

package uk.ac.diamond.daq.beamline.k11.diffraction.view;

import java.util.ArrayList;
import java.util.List;
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
import uk.ac.diamond.daq.mapping.ui.BackgroundStateHelper;
import uk.ac.diamond.daq.mapping.ui.LiveStreamBackgroundAction;
import uk.ac.diamond.daq.mapping.ui.browser.MapBrowser;
import uk.ac.diamond.daq.mapping.ui.controller.ScanningAcquisitionController;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;
import uk.ac.diamond.daq.mapping.ui.experiment.controller.ExperimentScanningAcquisitionController;
import uk.ac.diamond.daq.mapping.ui.services.MappingRemoteServices;
import uk.ac.gda.api.acquisition.AcquisitionController;
import uk.ac.gda.client.properties.acquisition.AcquisitionPropertyType;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.AcquisitionConfigurationView;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.document.DocumentFactory;
import uk.ac.gda.ui.tool.selectable.NamedCompositeFactory;
import uk.ac.gda.ui.tool.selectable.SelectableContainedCompositeFactory;

public class DiffractionConfigurationView extends AcquisitionConfigurationView {

	public static final String ID = "uk.ac.diamond.daq.beamline.k11.view.DiffractionConfigurationView";

	private ScanManagementController smController;

	private LiveStreamBackgroundAction liveStreamAction;

	public DiffractionConfigurationView() {
		smController = getMappingRemoteServices().getScanManagementController();
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
		return new SelectableContainedCompositeFactory(initializeConfiguration(controlButtonsContainerSupplier), ClientMessages.ACQUISITIONS);
	}

	@Override
	protected Browser<?> getBrowser() {
		return getAcquisitionController()
			.map(MapBrowser::new)
			.orElseGet(() -> new MapBrowser(null));
	}

	/**
	 * Creates a new {@link ScanningAcquisition} for a diffraction acquisition. Note that the Detectors set by the
	 * {@link ScanningAcquisitionController#createNewAcquisition()}
	 *
	 * @return the new scanning acquisition
	 */
	@Override
	protected Supplier<ScanningAcquisition> newScanningAcquisition() {
		return SpringApplicationContextFacade.getBean(DocumentFactory.class)
				.newScanningAcquisition(AcquisitionPropertyType.DIFFRACTION, AcquisitionTemplateType.TWO_DIMENSION_POINT);
	}

	@Override
	protected AcquisitionController<ScanningAcquisition> createAcquisitionController() {
		return new ExperimentScanningAcquisitionController(AcquisitionPropertyType.DIFFRACTION);
	}

	private List<NamedCompositeFactory> initializeConfiguration(Supplier<Composite> controlButtonsContainerSupplier) {
		List<NamedCompositeFactory> configurations = new ArrayList<>();
		getAcquisitionController()
			.ifPresent(c -> {
				configurations.add(new DiffractionButtonControlledCompositeFactory(c, controlButtonsContainerSupplier));
				configurations.add(new PointAndShootButtonControlledCompositeFactory(c, controlButtonsContainerSupplier));
				configurations.add(new BeamSelectorButtonControlledCompositeFactory(c, controlButtonsContainerSupplier));
			});
		return configurations;
	}

	private static MappingRemoteServices getMappingRemoteServices() {
		return SpringApplicationContextFacade.getBean(MappingRemoteServices.class);
	}
}
