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

import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientLabel;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.function.Consumer;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeInterface;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController.RegionPathState;
import uk.ac.gda.api.acquisition.AcquisitionController;
import uk.ac.gda.ui.tool.Reloadable;

/**
 * This Composite allows to edit a {@link ScanningParameters} object.
 *
 * @author Maurizio Nagni
 */
class BeamSelectorScanConfigurationLayoutFactory implements CompositeFactory, Reloadable {

	private static final Logger logger = LoggerFactory.getLogger(BeamSelectorScanConfigurationLayoutFactory.class);

	// ----- Helper ------//
	private AcquisitionController<ScanningAcquisition> controller;
	private Composite mainComposite;

	private RegionAndPathController rapController = PlatformUI.getWorkbench().getService(RegionAndPathController.class);
	private Consumer<RegionPathState> viewUpdater;

	private final List<DiffractionCompositeInterface> components = new ArrayList<>();

	public BeamSelectorScanConfigurationLayoutFactory(AcquisitionController<ScanningAcquisition> controller) {
		this.controller = controller;
	}

	private void dispose() {
		Optional.ofNullable(viewUpdater)
			.ifPresent(rapController::detachViewUpdater);
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		logger.trace("Creating {}", this);
		mainComposite = createClientCompositeWithGridLayout(parent, style, 1);
		createClientGridDataFactory().align(SWT.FILL, SWT.FILL).applyTo(mainComposite);

		createElements(mainComposite, SWT.NONE);

		// Releases resources before dispose
		mainComposite.addDisposeListener(event -> dispose()	);
		return mainComposite;
	}

	@Override
	public void reload() {
		// TBD
//		bindElements();
//		initialiseElements();
		mainComposite.getShell().layout(true, true);
	}

	private void createElements(Composite parent, int labelStyle) {
		createConfiguration(parent, labelStyle);
	}

	private void createConfiguration(Composite parent, int labelStyle) {
		int columns = components.size();
		Composite externalContainer = createClientCompositeWithGridLayout(parent, labelStyle, columns);
		createClientGridDataFactory().align(SWT.FILL, SWT.FILL).applyTo(externalContainer);

		createClientLabel(externalContainer, labelStyle, "TO BE DONE");
	}
}
