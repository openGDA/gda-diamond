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

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.resource.FontDescriptor;
import org.eclipse.jface.wizard.WizardDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.client.gui.camera.CameraConfigurationView;
import uk.ac.diamond.daq.client.gui.energy.BeamEnergyDialogBuilder;
import uk.ac.diamond.daq.experiment.api.structure.ExperimentController;
import uk.ac.diamond.daq.experiment.ui.driver.ExperimentDriverWizard;
import uk.ac.gda.tomography.stage.IStageController;
import uk.ac.gda.tomography.stage.StagesComposite;
import uk.ac.gda.tomography.stage.enumeration.Position;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientResourceManager;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.images.ClientImages;
import uk.ac.gda.ui.tool.spring.SpringApplicationContextProxy;

/**
 * Tomography dashboard
 *
 * @author Maurizio Nagni
 */
public class PerspectiveDashboardCompositeFactory implements CompositeFactory {

	private static final Logger logger = LoggerFactory.getLogger(PerspectiveDashboardCompositeFactory.class);

	private Group source;
	private Button energyButton;
	private Label energy;
	private Label energyValue;
	private Button shutter;
	private Label shutterLabel;
	private Label shutterValue;
	private Button experimentDriver;

	private final IStageController stageController;

	public PerspectiveDashboardCompositeFactory(IStageController stageController) {
		super();
		this.stageController = stageController;
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		Composite composite = ClientSWTElements.createComposite(parent, style);
		GridLayoutFactory.swtDefaults().margins(ClientSWTElements.defaultCompositeMargin()).applyTo(composite);
		GridDataFactory.swtDefaults().grab(true, true).align(SWT.LEFT, SWT.TOP).applyTo(composite);
		createElements(composite, SWT.NONE);
		bindElements(composite);
		return composite;
	}

	private void createElements(Composite parent, int style) {
		createExperimentManager(ClientSWTElements.createComposite(parent, SWT.NONE));
		headerElements(ClientSWTElements.createComposite(parent, SWT.NONE, 3), style);
		stageCompose(ClientSWTElements.createComposite(parent, SWT.NONE, 1));
		cameraGroupElements(parent);
		experimentDriverButton(parent);
	}

	private void createExperimentManager(Composite parent) {
		new ExperimentManager(getExperimentController()).createComposite(parent, SWT.NONE);
	}

	private void headerElements(Composite parent, int style) {
		createSource(ClientSWTElements.createGroup(parent, 3, ClientMessages.SOURCE), style);
	}

	private void stageCompose(Composite parent) {
		StagesComposite.buildModeComposite(parent, stageController);
	}

	private Button appendOutOfBeamSelectionListener(Composite parent) {
		Button button = ClientSWTElements.createButton(parent, SWT.PUSH, ClientMessages.OUT_OF_BEAM,
				ClientMessages.OUT_OF_BEAM_TP);
		SelectionListener listener = new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				stageController.savePosition(Position.OUT_OF_BEAM);
			}
		};
		button.addSelectionListener(listener);
		return button;
	}

	private void cameraGroupElements(Composite parent) {
		Group cameras = ClientSWTElements.createGroup(parent, 1, ClientMessages.CAMERAS);
		CameraConfigurationView.openCameraConfigurationViewButton(cameras);
	}

	private void experimentDriverButton(Composite parent) {
		experimentDriver = ClientSWTElements.createButton(parent, SWT.PUSH,
				ClientMessages.EXPERIMENT_DRIVER, ClientMessages.CONFIGURE_EXPERIMENT_DRIVER);
	}

	private void createSource(Composite parent, int style) {
		energyButton = ClientSWTElements.createButton(parent, style, ClientMessages.EMPTY_MESSAGE,
				ClientMessages.ENERGY_KEV, ClientImages.BEAM_16);
		energy = ClientSWTElements.createLabel(parent, style, ClientMessages.ENERGY_KEV);
		energyValue = ClientSWTElements.createLabel(parent, style, ClientMessages.NOT_AVAILABLE, null,
				FontDescriptor.createFrom(ClientResourceManager.getInstance().getTextDefaultFont()));

		shutter = ClientSWTElements.createButton(parent, SWT.CHECK, ClientMessages.EMPTY_MESSAGE,
				ClientMessages.SHUTTER_TP);
		shutterLabel = ClientSWTElements.createLabel(parent, style, ClientMessages.SHUTTER);
		shutterValue = ClientSWTElements.createLabel(parent, style, ClientMessages.NOT_AVAILABLE, null,
				FontDescriptor.createFrom(ClientResourceManager.getInstance().getTextDefaultFont()));
	}

	private void bindElements(Composite parent) {
		energyButton.addListener(SWT.Selection, event -> {
			BeamEnergyDialogBuilder builder = new BeamEnergyDialogBuilder();
			builder.addBeamSelector();
			builder.addImagingController();
			builder.addDiffractionController();
			builder.build(parent.getShell()).open();
		});
		appendOutOfBeamSelectionListener(parent);

		experimentDriver.addListener(SWT.Selection, event -> {
			// FIXME ID: Experiment name? Visit ID?
			ExperimentDriverWizard driverWizard = new ExperimentDriverWizard(null);
			WizardDialog wizardDialog = new WizardDialog(parent.getShell(), driverWizard);
			wizardDialog.setPageSize(driverWizard.getPreferredPageSize());
			wizardDialog.open();
		});
	}

	private ExperimentController getExperimentController() {
		return SpringApplicationContextProxy.getBean(ExperimentController.class);
	}
}
