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
import static uk.ac.gda.ui.tool.ClientSWTElements.STRETCH;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.innerComposite;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;

import gda.factory.Finder;
import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.experiment.ui.ExperimentManager;
import uk.ac.gda.ui.tool.ClientSWTElements;


/**
 * Acquisition dashboard
 *
 * @author Maurizio Nagni
 */
public class PerspectiveDashboardCompositeFactory implements CompositeFactory {

	@Override
	public Composite createComposite(Composite parent, int style) {
		var container = createClientCompositeWithGridLayout(parent, style, 1);
		ClientSWTElements.createClientGridDataFactory().align(SWT.FILL, SWT.FILL).grab(true, false).applyTo(container);

		createElements(container);

		return container;
	}

	private void createElements(Composite parent) {
		createExperimentManager(parent);
		separator(parent);
		createExperimentMode(parent);
		separator(parent);
		createSource(parent);
		createStage(parent);
		createCameraControl(parent);
	}

	private void separator(Composite composite) {
		STRETCH.applyTo(new Label(composite, SWT.HORIZONTAL | SWT.SEPARATOR));
	}

	private void createExperimentManager(Composite parent) {
		new ExperimentManager().createComposite(parent, SWT.NONE);
	}

	private void createExperimentMode(Composite parent) {
		new PerspectiveSwitcher().create(parent);
	}

	private void createStage(Composite parent) {
		new StageControls().create(parent);
	}

	private void createCameraControl(Composite parent) {
		var container = innerComposite(parent, 1, false);
		openCameraConfigurationViewButton(container);
	}

	private void createSource(Composite parent) {
		var composite = innerComposite(parent, 2, true);
		var gridData = GridDataFactory.fillDefaults().align(SWT.FILL, SWT.TOP).grab(true, false);
		gridData.applyTo(composite);

		var beamSelector = new BeamSelectorWidget("beam_selector", "beam_selector_readback").createControls(composite);
		gridData.applyTo(beamSelector);

		var shutters = innerComposite(composite, 1, false);
		STRETCH.copy().align(SWT.FILL, SWT.TOP).applyTo(shutters);
		Finder.listLocalFindablesOfType(ShutterWidgetConfiguration.class).forEach(shutterConfig -> {
			var shutter = new ShutterWidget(shutterConfig).createControls(shutters);
			gridData.applyTo(shutter);
		});
	}
}