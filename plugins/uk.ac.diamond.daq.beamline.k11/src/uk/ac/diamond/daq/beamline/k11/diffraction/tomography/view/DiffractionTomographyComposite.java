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

public class DiffractionTomographyComposite extends AcquisitionCompositeFactory {

	private static final AcquisitionKeys key = new AcquisitionKeys(AcquisitionPropertyType.DIFFRACTION, AcquisitionSubType.DIFFRACTION_TOMOGRAPHY, TrajectoryShape.TWO_DIMENSION_GRID);

	public DiffractionTomographyComposite(Supplier<Composite> buttonsCompositeSupplier) {
		super(buttonsCompositeSupplier);
	}

	@Override
	public ClientMessages getName() {
		return ClientMessages.DIFFRACTION_TOMOGRAPHY;
	}

	@Override
	protected AcquisitionKeys getKey() {
		return key;
	}

	@Override
	protected Supplier<CompositeFactory> createScanControls() {
		return DiffractionTomographyScanControls::new;
	}

	@Override
	protected CompositeFactory getButtonControlsFactory() {
		var acquisitionButtonGroup = new AcquisitionCompositeButtonGroupFactoryBuilder();
		acquisitionButtonGroup.addRunSelectionListener(widgetSelectedAdapter(event -> submitAcquisition()));
		acquisitionButtonGroup.addSaveSelectionListener(widgetSelectedAdapter(event -> saveAcquisition()));
		return acquisitionButtonGroup.build();
	}

}
