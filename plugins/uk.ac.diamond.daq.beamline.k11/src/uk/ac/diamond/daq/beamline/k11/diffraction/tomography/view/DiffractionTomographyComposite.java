/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.tomography.view;

import static org.eclipse.swt.events.SelectionListener.widgetSelectedAdapter;

import java.util.Arrays;
import java.util.function.Supplier;

import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.mapping.ui.controller.AcquisitionUiReloader;
import uk.ac.diamond.daq.mapping.ui.controller.ScanningAcquisitionController;
import uk.ac.gda.api.acquisition.AcquisitionKeys;
import uk.ac.gda.api.acquisition.AcquisitionPropertyType;
import uk.ac.gda.api.acquisition.AcquisitionSubType;
import uk.ac.gda.api.acquisition.TrajectoryShape;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.composites.AcquisitionCompositeButtonGroupFactoryBuilder;
import uk.ac.gda.client.exception.AcquisitionControllerException;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;
import uk.ac.gda.ui.tool.selectable.NamedCompositeFactory;

public class DiffractionTomographyComposite implements NamedCompositeFactory {

	private static final AcquisitionKeys key = new AcquisitionKeys(AcquisitionPropertyType.DIFFRACTION, AcquisitionSubType.DIFFRACTION_TOMOGRAPHY, TrajectoryShape.TWO_DIMENSION_GRID);
	private static final Logger logger = LoggerFactory.getLogger(DiffractionTomographyComposite.class);

	private final Supplier<Composite> buttonsCompositeSupplier;

	private DiffractionTomographyScanControls scanControls;
	private ScanningAcquisitionController acquisitionController;


	public DiffractionTomographyComposite(Supplier<Composite> buttonsCompositeSupplier) {
		this.buttonsCompositeSupplier = buttonsCompositeSupplier;
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		try {
			getAcquisitionController().initialise(key);
		} catch (AcquisitionControllerException e) {
			logger.error("Error initialising beam selector acquisition", e);
			var errorComposite = new Composite(parent, SWT.NONE);
			GridLayoutFactory.swtDefaults().applyTo(errorComposite);
			new Label(errorComposite, SWT.NONE).setText("Beam selector scans unavailable (see error log)");
			return errorComposite;
		}

		var controls = createScanControls().createComposite(parent, style);
		var buttonsComposite = buttonsCompositeSupplier.get();
		Arrays.asList(buttonsComposite.getChildren()).forEach(Control::dispose);
		getButtonControlsFactory().createComposite(buttonsComposite, SWT.NONE);
		buttonsComposite.layout(true, true);
		var loadListener = new AcquisitionUiReloader(key, scanControls);
		SpringApplicationContextFacade.addApplicationListener(loadListener);
		controls.addDisposeListener(dispose -> SpringApplicationContextFacade.removeApplicationListener(loadListener));
		return controls;
	}

	@Override
	public ClientMessages getName() {
		return ClientMessages.DIFFRACTION_TOMOGRAPHY;
	}

	@Override
	public ClientMessages getTooltip() {
		return ClientMessages.DIFFRACTION_TOMOGRAPHY;
	}

	private DiffractionTomographyScanControls createScanControls() {
		this.scanControls = new DiffractionTomographyScanControls();
		return scanControls;
	}

	private CompositeFactory getButtonControlsFactory() {
		return getAcquistionButtonGroupFactoryBuilder().build();
	}

	private AcquisitionCompositeButtonGroupFactoryBuilder getAcquistionButtonGroupFactoryBuilder() {
		var acquisitionButtonGroup = new AcquisitionCompositeButtonGroupFactoryBuilder();
		acquisitionButtonGroup.addNewSelectionListener(widgetSelectedAdapter(event -> {
			createNewAcquisition();
			scanControls.reload();
		}));
		acquisitionButtonGroup.addRunSelectionListener(widgetSelectedAdapter(event -> getScanningAcquisitionTemporaryHelper().runAcquisition()));
		acquisitionButtonGroup.addSaveSelectionListener(widgetSelectedAdapter(event -> saveAcquisition()));
		return acquisitionButtonGroup;
	}

	private void createNewAcquisition() {
		boolean confirmed = UIHelper.showConfirm("Create new configuration? The existing one will be discarded");
		if (confirmed) {
			try {
				getAcquisitionController().newScanningAcquisition(key);
			} catch (AcquisitionControllerException e) {
				logger.error("Could not create new beam selector acquisition", e);
			}
		}
	}

	private void saveAcquisition() {
		try {
			getAcquisitionController().saveAcquisitionConfiguration();
		} catch (AcquisitionControllerException e) {
			logger.error("Could not save beam selector acquisition", e);
		}
	}

	private ScanningAcquisitionController getAcquisitionController() {
		if (acquisitionController == null) {
			acquisitionController = SpringApplicationContextFacade.getBean(ScanningAcquisitionController.class);
		}
		return acquisitionController;
	}

	private ScanningAcquisitionTemporaryHelper getScanningAcquisitionTemporaryHelper() {
		return SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class);
	}

}