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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.beamselectorscan;

import static org.eclipse.swt.events.SelectionListener.widgetSelectedAdapter;

import java.util.function.Supplier;

import org.eclipse.swt.widgets.Composite;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.gda.client.composites.AcquisitionCompositeButtonGroupFactoryBuilder;
import uk.ac.gda.client.exception.AcquisitionControllerException;
import uk.ac.gda.client.properties.acquisition.AcquisitionKeys;
import uk.ac.gda.client.properties.acquisition.AcquisitionPropertyType;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;
import uk.ac.gda.ui.tool.selectable.ButtonControlledCompositeTemplate;
import uk.ac.gda.ui.tool.selectable.NamedCompositeFactory;

/**
 * This Composite allows to edit a {@link ScanningParameters} object.
 *
 * @author Maurizio Nagni
 */
public class BeamSelectorButtonControlledCompositeFactory implements NamedCompositeFactory, ButtonControlledCompositeTemplate {

	private final Supplier<Composite> controlButtonsContainerSupplier;

	private CompositeFactory acquistionConfigurationFactory;

	public BeamSelectorButtonControlledCompositeFactory(Supplier<Composite> controlButtonsContainerSupplier) {
		this.controlButtonsContainerSupplier = controlButtonsContainerSupplier;
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		return createButtonControlledComposite(parent, style);
	}

	@Override
	public ClientMessages getName() {
		return ClientMessages.BEAM_SELECTOR_ACQUISITION;
	}

	@Override
	public ClientMessages getTooltip() {
		return ClientMessages.BEAM_SELECTOR_ACQUISITION_TP;
	}

	@Override
	public CompositeFactory getControlledCompositeFactory() {
		if (acquistionConfigurationFactory == null) {
			this.acquistionConfigurationFactory = new BeamSelectorScanControls();
		}
		return acquistionConfigurationFactory;
	}

	@Override
	public CompositeFactory getButtonControlsFactory() {
		return getAcquistionButtonGroupFactoryBuilder().build();
	}

	private AcquisitionCompositeButtonGroupFactoryBuilder getAcquistionButtonGroupFactoryBuilder() {
		var acquisitionButtonGroup = new AcquisitionCompositeButtonGroupFactoryBuilder();
		acquisitionButtonGroup.addRunSelectionListener(widgetSelectedAdapter(event -> getScanningAcquisitionTemporaryHelper().runAcquisition()));
		return acquisitionButtonGroup;
	}

	@Override
	public Supplier<Composite> getButtonControlsContainerSupplier() {
		return controlButtonsContainerSupplier;
	}

	@Override
	public AcquisitionKeys getAcquisitionKeys() {
		return new AcquisitionKeys(AcquisitionPropertyType.BEAM_SELECTOR, AcquisitionTemplateType.STATIC_POINT);
	}

	@Override
	public void createNewAcquisitionInController() throws AcquisitionControllerException {
		getScanningAcquisitionTemporaryHelper()
			.setNewScanningAcquisition(getAcquisitionKeys());
	}

	private ScanningAcquisitionTemporaryHelper getScanningAcquisitionTemporaryHelper() {
		return SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class);
	}
}
