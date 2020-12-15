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

import java.util.Optional;

import org.eclipse.swt.widgets.Composite;

import uk.ac.diamond.daq.mapping.api.IMappingExperimentBean;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.gda.api.acquisition.AcquisitionController;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.selectable.NamedComposite;

/**
 * This Composite allows to edit a {@link ScanningParameters} object.
 *
 * @author Maurizio Nagni
 */
public class BeamSelectorConfigurationCompositeFactory implements NamedComposite {

	private final DiffractionConfigurationCompositeBaseFactory diffractionBase;
	public BeamSelectorConfigurationCompositeFactory(AcquisitionController<ScanningAcquisition> controller) {
		diffractionBase = new DiffractionConfigurationCompositeBaseFactory(controller);
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		return diffractionBase.createComposite(parent, style);
	}

	/**
	 * Loads the content of the file identified by the fully qualified filename parameter into the mapping bean and
	 * refreshes the UI to dispay the changes. An update of any linked UIs will also be triggered by the controllers
	 *
	 */
	public void load(Optional<IMappingExperimentBean> bean) {
		diffractionBase.load(bean);
	}

	@Override
	public ClientMessages getName() {
		return ClientMessages.BEAM_SELECTOR_ACQUISITION;
	}

	@Override
	public ClientMessages getTooltip() {
		return ClientMessages.BEAM_SELECTOR_ACQUISITION_TP;
	}
}
