/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Text;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.experiment.api.structure.ExperimentController;
import uk.ac.diamond.daq.experiment.api.structure.ExperimentControllerException;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientSWTElements;

/**
 * Lets the user start and stop their experiment
 */
public class ExperimentManager implements CompositeFactory {

	private final ExperimentController experimentController;

	private Text experimentName;
	private Button startButton;
	private Button stopButton;

	public ExperimentManager(ExperimentController experimentController) {
		this.experimentController = experimentController;
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		Composite composite = ClientSWTElements.createComposite(parent, SWT.NONE);
		Group group = ClientSWTElements.createGroup(composite, 2, ClientMessages.EXPERIMENT);
		ClientSWTElements.createLabel(group, SWT.NONE, ClientMessages.NAME);
		experimentName = ClientSWTElements.createText(group, SWT.NONE, null);
		startButton = ClientSWTElements.createButton(group, SWT.TOGGLE, ClientMessages.START,
				ClientMessages.START_EXPERIMENT);
		stopButton = ClientSWTElements.createButton(group, SWT.TOGGLE, ClientMessages.STOP,
				ClientMessages.STOP_EXPERIMENT);

		attachListeners();
		return composite;
	}

	private void attachListeners() {
		startButton.addListener(SWT.Selection, selectionEvent -> {
			try {
				experimentController.startExperiment(experimentName.getText());
			} catch (ExperimentControllerException e) {
				UIHelper.showError("Cannot start the Experiment", e);
			}
			Display.getDefault().syncExec(() -> toggleEnabledWidgets(true));
		});

		stopButton.addListener(SWT.Selection, selectionEvent -> {
			try {
				experimentController.stopExperiment();
			} catch (ExperimentControllerException e) {
				UIHelper.showError("Cannot stop the Experiment", e);
			}
			Display.getDefault().syncExec(() -> toggleEnabledWidgets(false));
		});

		// set initial state
		toggleEnabledWidgets(false);
	}

	private void toggleEnabledWidgets(boolean experimentRunning) {
		startButton.setEnabled(!experimentRunning);
		stopButton.setEnabled(experimentRunning);
		experimentName.setEnabled(!experimentRunning);
	}

}
