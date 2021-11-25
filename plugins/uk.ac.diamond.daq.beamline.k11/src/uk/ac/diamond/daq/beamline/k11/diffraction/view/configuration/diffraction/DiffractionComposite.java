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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction;

import static org.eclipse.swt.events.SelectionListener.widgetSelectedAdapter;
import static uk.ac.gda.core.tool.spring.SpringApplicationContextFacade.addApplicationListener;

import java.util.Arrays;
import java.util.function.Supplier;

import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.ApplicationListener;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.Activator;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.diamond.daq.mapping.ui.controller.ScanningAcquisitionController;
import uk.ac.gda.api.acquisition.resource.event.AcquisitionConfigurationResourceLoadEvent;
import uk.ac.gda.client.AcquisitionManager;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.composites.AcquisitionCompositeButtonGroupFactoryBuilder;
import uk.ac.gda.client.exception.AcquisitionControllerException;
import uk.ac.gda.client.properties.acquisition.AcquisitionKeys;
import uk.ac.gda.client.properties.acquisition.AcquisitionPropertyType;
import uk.ac.gda.client.properties.acquisition.AcquisitionSubType;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;
import uk.ac.gda.ui.tool.selectable.NamedCompositeFactory;


public class DiffractionComposite implements NamedCompositeFactory {

	private static final Logger logger = LoggerFactory.getLogger(DiffractionComposite.class);
	private final Supplier<Composite> buttonsCompositeSupplier;
	private static final AcquisitionKeys key = new AcquisitionKeys(AcquisitionPropertyType.DIFFRACTION, AcquisitionSubType.STANDARD, AcquisitionTemplateType.TWO_DIMENSION_POINT);

	private DiffractionScanControls scanControls;

	private final LoadListener loadListener;

	/*
	 * TODO
	 * Move AcquisitionManager into ScanningAcquisitionController
	 * when all acquisitions are managed by it
	 */
	private AcquisitionManager acquisitionManager;
	private ScanningAcquisitionController acquisitionController;

	public DiffractionComposite(Supplier<Composite> controlButtonsContainerSupplier) {
		this.buttonsCompositeSupplier = controlButtonsContainerSupplier;

		// instantiate listener but only attach when composite is created
		loadListener = new LoadListener();
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		try {
			initialiseAcquisition();
		} catch (AcquisitionControllerException e) {
			logger.error("Error initialising beam selector acquisition", e);
			var errorComposite = new Composite(parent, SWT.NONE);
			GridLayoutFactory.swtDefaults().applyTo(errorComposite);
			new Label(errorComposite, SWT.NONE).setText("Diffraction scans unavailable (see error log)");
			return errorComposite;
		}

		var controls = getScanControls().createComposite(parent, style);
		var buttonsComposite = buttonsCompositeSupplier.get();
		Arrays.asList(buttonsComposite.getChildren()).forEach(Control::dispose);
		getButtonControlsFactory().createComposite(buttonsComposite, SWT.NONE);
		buttonsComposite.layout(true, true);
		addApplicationListener(loadListener);
		controls.addDisposeListener(dispose -> SpringApplicationContextFacade.removeApplicationListener(loadListener));
		return controls;
	}

	/**
	 * Loads existing instance or new acquisition if none exists
	 */
	private void initialiseAcquisition() throws AcquisitionControllerException {
		var acquisition = getAcquisitionManager().getAcquisition(getAcquisitionKey());
		getAcquisitionController().loadAcquisitionConfiguration(acquisition);
	}

	protected AcquisitionKeys getAcquisitionKey() {
		return key;
	}

	@Override
	public ClientMessages getName() {
		return ClientMessages.DIFFRACTION;
	}

	@Override
	public ClientMessages getTooltip() {
		return ClientMessages.DIFFRACTION_TP;
	}

	protected DiffractionScanControls getScanControls() {
		if (scanControls == null) {
			this.scanControls = new DiffractionScanControls(acquisitionManager);
		}
		return scanControls;
	}

	protected CompositeFactory getButtonControlsFactory() {
		return getAcquistionButtonGroupFacoryBuilder().build();
	}

	public void createNewAcquisitionInController() throws AcquisitionControllerException {
		getScanningAcquisitionTemporaryHelper()
			.setNewScanningAcquisition(getAcquisitionKey());
	}

	private AcquisitionCompositeButtonGroupFactoryBuilder getAcquistionButtonGroupFacoryBuilder() {
		var acquisitionButtonGroup = new AcquisitionCompositeButtonGroupFactoryBuilder();
		acquisitionButtonGroup.addNewSelectionListener(widgetSelectedAdapter(event -> {
			createNewAcquisition();
			scanControls.reload();
		}));
		acquisitionButtonGroup.addSaveSelectionListener(widgetSelectedAdapter(event -> saveAcquisition()));
		acquisitionButtonGroup.addRunSelectionListener(widgetSelectedAdapter(event -> getScanningAcquisitionTemporaryHelper().runAcquisition()));
		return acquisitionButtonGroup;
	}

	protected void saveAcquisition() {
		try {
			getAcquisitionController().saveAcquisitionConfiguration();
		} catch (AcquisitionControllerException e) {
			logger.error("Could not save diffraction acquisition", e);
		}
	}

	protected void createNewAcquisition() {
		boolean confirmed = UIHelper.showConfirm("Create new configuration? The existing one will be discarded");
		if (confirmed) {
			try {
				getAcquisitionController().loadAcquisitionConfiguration(getAcquisitionManager().newAcquisition(getAcquisitionKey()));
			} catch (AcquisitionControllerException e) {
				logger.error("Could not create new diffraction acquisition", e);
			}
		}
	}

	private ScanningAcquisitionController getAcquisitionController() {
		if (acquisitionController == null) {
			acquisitionController = SpringApplicationContextFacade.getBean(ScanningAcquisitionController.class);
		}
		return acquisitionController;
	}

	private AcquisitionManager getAcquisitionManager() {
		if (acquisitionManager == null) {
			acquisitionManager = Activator.getService(AcquisitionManager.class);
		}
		return acquisitionManager;
	}

	private class LoadListener implements ApplicationListener<AcquisitionConfigurationResourceLoadEvent> {

		@Override
		public void onApplicationEvent(AcquisitionConfigurationResourceLoadEvent event) {
			// we are only interested in load events broadcasted by acquisition controller...
			if (!(event.getSource() instanceof ScanningAcquisitionController)) return;
			var controller = (ScanningAcquisitionController) event.getSource();

			// ...relating to diffraction acquisitions
			if (controller.getAcquisitionKeys().getPropertyType().equals(AcquisitionPropertyType.DIFFRACTION)) {
				Display.getDefault().asyncExec(scanControls::reload);
			}
		}
	}

	private ScanningAcquisitionTemporaryHelper getScanningAcquisitionTemporaryHelper() {
		return SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class);
	}
}