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

import static uk.ac.diamond.daq.client.gui.camera.CameraConfigurationView.openCameraConfigurationViewButton;
import static uk.ac.diamond.daq.mapping.ui.stage.StagesComposite.buildModeComposite;
import static uk.ac.gda.ui.tool.ClientMessages.CAMERAS;
import static uk.ac.gda.ui.tool.ClientMessages.CONFIGURE_EXPERIMENT_DRIVER;
import static uk.ac.gda.ui.tool.ClientMessages.EXPERIMENT_DRIVER;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientButton;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGroup;

import org.eclipse.jface.wizard.WizardDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Listener;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.client.gui.energy.summary.EnergySummaryComposite;
import uk.ac.diamond.daq.experiment.ui.ExperimentManager;
import uk.ac.diamond.daq.experiment.ui.driver.ExperimentDriverWizard;
import uk.ac.gda.ui.tool.ClientSWTElements;


/**
 * Acquisition dashboard
 *
 * @author Maurizio Nagni
 */
public class PerspectiveDashboardCompositeFactory implements CompositeFactory {

	private Button experimentDriver;

	public PerspectiveDashboardCompositeFactory() {
		super();
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		var container = createClientCompositeWithGridLayout(parent, style, 1);
		ClientSWTElements.createClientGridDataFactory().align(SWT.FILL, SWT.FILL).grab(true, false).applyTo(container);

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
	}

	private void createExperimentManager(Composite parent, int style) {
		var container = createClientCompositeWithGridLayout(parent, style, 1);
		createClientGridDataFactory().align(SWT.FILL, SWT.FILL).grab(true, false).applyTo(container);
		new ExperimentManager().createComposite(container, SWT.NONE);
	}

	private void createStage(Composite parent, int style) {
		var container = createClientCompositeWithGridLayout(parent, style, 1);
		createClientGridDataFactory().align(SWT.FILL, SWT.FILL).grab(true, false).applyTo(container);
		buildModeComposite(container);
	}

	private void createCameraControl(Composite parent, int style) {
		var container = createClientGroup(parent, style, 1, CAMERAS);
		createClientGridDataFactory().align(SWT.FILL, SWT.FILL).grab(true, false).applyTo(container);
		openCameraConfigurationViewButton(container);
	}

	private void createExperimentDriver(Composite parent, int style) {
		var container = createClientCompositeWithGridLayout(parent, style, 1);
		createClientGridDataFactory().align(SWT.FILL, SWT.FILL).applyTo(container);

		experimentDriver = createClientButton(container, SWT.PUSH, EXPERIMENT_DRIVER,
				CONFIGURE_EXPERIMENT_DRIVER);
		createClientGridDataFactory().applyTo(experimentDriver);
	}

	private void createSource(Composite parent, int style) {
		new EnergySummaryComposite().createComposite(parent, style);
	}

	private void bindElements(Composite parent) {
		Listener experimentDriverListener = e -> {
			// FIXME ID: Experiment name? Visit ID?
			var driverWizard = new ExperimentDriverWizard(null);
			var wizardDialog = new WizardDialog(parent.getShell(), driverWizard);
			wizardDialog.setPageSize(driverWizard.getPreferredPageSize());
			wizardDialog.open();
		};
		experimentDriver.addListener(SWT.Selection, experimentDriverListener);
	}
}