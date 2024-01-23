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
import uk.ac.diamond.daq.mapping.ui.AcquisitionCompositeFactory;
import uk.ac.gda.api.acquisition.AcquisitionKeys;
import uk.ac.gda.api.acquisition.AcquisitionPropertyType;
import uk.ac.gda.api.acquisition.AcquisitionSubType;
import uk.ac.gda.api.acquisition.TrajectoryShape;
import uk.ac.gda.client.composites.AcquisitionCompositeButtonGroupFactoryBuilder;
import uk.ac.gda.ui.tool.ClientMessages;


public class BeamSelectorComposite extends AcquisitionCompositeFactory {

	private BeamSelectorScanControls scanControls;

	private final AcquisitionKeys key = new AcquisitionKeys(AcquisitionPropertyType.DIFFRACTION, AcquisitionSubType.BEAM_SELECTOR, TrajectoryShape.STATIC_POINT);



	public BeamSelectorComposite(Supplier<Composite> buttonsCompositeSupplier) {
		super(buttonsCompositeSupplier);
	}

	@Override
	protected ClientMessages getName() {
		return ClientMessages.BEAM_SELECTOR_ACQUISITION;
	}

	@Override
	protected AcquisitionKeys getKey() {
		return key;
	}

	@Override
	protected Supplier<CompositeFactory> createScanControls() {
		return BeamSelectorScanControls::new;
	}

	@Override
	protected CompositeFactory getButtonControlsFactory() {
		return getAcquistionButtonGroupFactoryBuilder().build();
	}

	private AcquisitionCompositeButtonGroupFactoryBuilder getAcquistionButtonGroupFactoryBuilder() {
		var acquisitionButtonGroup = new AcquisitionCompositeButtonGroupFactoryBuilder();
		acquisitionButtonGroup.addRunSelectionListener(widgetSelectedAdapter(event -> {
			scanControls.resolveScanId();
			submitAcquisition();
		}));
		acquisitionButtonGroup.addSaveSelectionListener(widgetSelectedAdapter(event -> {
			scanControls.resolveScanId();
			saveAcquisition();
		}));
		return acquisitionButtonGroup;
	}

}
