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

import static uk.ac.gda.core.tool.spring.SpringApplicationContextFacade.getBean;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientButton;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGroup;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientLabel;

import java.util.Optional;

import org.eclipse.jface.wizard.WizardDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.client.gui.camera.CameraConfigurationView;
import uk.ac.diamond.daq.client.gui.energy.BeamEnergyDialogBuilder;
import uk.ac.diamond.daq.experiment.ui.driver.ExperimentDriverWizard;
import uk.ac.diamond.daq.mapping.ui.controller.StageController;
import uk.ac.diamond.daq.mapping.ui.stage.StagesComposite;
import uk.ac.diamond.daq.mapping.ui.stage.enumeration.Position;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.images.ClientImages;

/**
 * Acquisition dashboard
 *
 * @author Maurizio Nagni
 */
public class PerspectiveDashboardCompositeFactory implements CompositeFactory {

	private Button energyButton;
	private Label energy;
	private Label energyValue;
	private Button shutter;
	private Label shutterLabel;
	private Label shutterValue;
	private Button experimentDriver;
	private Button outOfBeam;

	public PerspectiveDashboardCompositeFactory() {
		super();
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		Composite container = createClientCompositeWithGridLayout(parent, style, 1);
		ClientSWTElements.createClientGridDataFactory().align(SWT.FILL, SWT.FILL).grab(true, true).applyTo(container);

		createElements(container, SWT.NONE);
		bindElements(container);
		return container;
	}

	private void createElements(Composite parent, int style) {
		createExperimentManager(parent, style);
		createSource(parent, style);
		createStage(parent, style);
		createCameraControl(parent, style);
		createExperimentDriver(parent, style);
		createOutOfBeam(parent, style);
	}

	private void createExperimentManager(Composite parent, int style) {
		Composite container = createClientCompositeWithGridLayout(parent, style, 1);
		ClientSWTElements.createClientGridDataFactory().align(SWT.FILL, SWT.FILL).grab(true, false).applyTo(container);

		new ExperimentManager().createComposite(container, SWT.NONE);
	}

	private void createStage(Composite parent, int style) {
		Composite container = createClientCompositeWithGridLayout(parent, style, 1);
		ClientSWTElements.createClientGridDataFactory().align(SWT.FILL, SWT.FILL).grab(true, false).applyTo(container);

		StagesComposite.buildModeComposite(container);
	}

	private Button createOutOfBeam(Composite parent, int style) {
		Composite container = createClientCompositeWithGridLayout(parent, style, 1);
		ClientSWTElements.createClientGridDataFactory().align(SWT.FILL, SWT.FILL).grab(true, false).applyTo(container);

		outOfBeam = createClientButton(container, SWT.PUSH, ClientMessages.OUT_OF_BEAM, ClientMessages.OUT_OF_BEAM_TP);
		return outOfBeam;
	}

	private void createCameraControl(Composite parent, int style) {
		Group container = createClientGroup(parent, style, 1, ClientMessages.CAMERAS);
		ClientSWTElements.createClientGridDataFactory().align(SWT.FILL, SWT.FILL).grab(true, false).applyTo(container);

		CameraConfigurationView.openCameraConfigurationViewButton(container);
	}

	private void createExperimentDriver(Composite parent, int style) {
		Composite container = createClientCompositeWithGridLayout(parent, style, 1);
		ClientSWTElements.createClientGridDataFactory().align(SWT.FILL, SWT.FILL).grab(true, false).applyTo(container);

		experimentDriver = createClientButton(container, SWT.PUSH, ClientMessages.EXPERIMENT_DRIVER,
				ClientMessages.CONFIGURE_EXPERIMENT_DRIVER);
	}

	private void createSource(Composite parent, int style) {
		Group container = createClientGroup(parent, style, 3, ClientMessages.SOURCE);
		ClientSWTElements.createClientGridDataFactory().align(SWT.FILL, SWT.FILL).grab(true, false).applyTo(container);

		energyButton = createClientButton(container, style, ClientMessages.EMPTY_MESSAGE, ClientMessages.ENERGY_KEV,
				ClientImages.BEAM_16);
		ClientSWTElements.createClientGridDataFactory().applyTo(energyButton);

		energy = createClientLabel(container, style, ClientMessages.ENERGY_KEV);
		ClientSWTElements.createClientGridDataFactory().applyTo(energy);

		energyValue = createClientLabel(container, style, ClientMessages.NOT_AVAILABLE);
		ClientSWTElements.createClientGridDataFactory().applyTo(energyValue);

		shutter = createClientButton(container, SWT.CHECK, ClientMessages.EMPTY_MESSAGE, ClientMessages.SHUTTER_TP);
		ClientSWTElements.createClientGridDataFactory().applyTo(shutter);

		shutterLabel = createClientLabel(container, style, ClientMessages.SHUTTER);
		ClientSWTElements.createClientGridDataFactory().applyTo(shutterLabel);

		shutterValue = createClientLabel(container, style, ClientMessages.NOT_AVAILABLE);
		ClientSWTElements.createClientGridDataFactory().applyTo(shutterValue);
	}

	private void bindElements(Composite parent) {
		Listener outOfBeamListener = e -> Optional.ofNullable(getBean(StageController.class))
				.ifPresent(c -> c.savePosition(Position.OUT_OF_BEAM));
		outOfBeam.addListener(SWT.Selection, outOfBeamListener);

		Listener energyButtonListener = e -> {
			BeamEnergyDialogBuilder builder = new BeamEnergyDialogBuilder();
			builder.addImagingController();
			builder.addDiffractionController();
			builder.build(parent.getShell()).open();
		};
		energyButton.addListener(SWT.Selection, energyButtonListener);

		Listener experimentDriverListener = e -> {
			// FIXME ID: Experiment name? Visit ID?
			ExperimentDriverWizard driverWizard = new ExperimentDriverWizard(null);
			WizardDialog wizardDialog = new WizardDialog(parent.getShell(), driverWizard);
			wizardDialog.setPageSize(driverWizard.getPreferredPageSize());
			wizardDialog.open();
		};
		experimentDriver.addListener(SWT.Selection, experimentDriverListener);
	}
}