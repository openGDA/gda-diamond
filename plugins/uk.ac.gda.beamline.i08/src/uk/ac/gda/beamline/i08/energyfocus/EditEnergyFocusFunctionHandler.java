/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i08.energyfocus;

import org.eclipse.core.commands.AbstractHandler;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.core.commands.IHandler;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.jface.dialogs.ErrorDialog;
import org.eclipse.scanning.api.stashing.IStashing;
import org.eclipse.scanning.api.ui.auto.IModelDialog;
import org.eclipse.scanning.device.ui.ServiceHolder;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jython.ICommandRunner;
import gda.jython.InterfaceProvider;

public class EditEnergyFocusFunctionHandler extends AbstractHandler implements IHandler {
	private static final String STASH_NAME = "uk.ac.gda.beamline.i08.configuration.energyfocusfunction.json";
	private static final String DEFAULT_SLOPE_DIVIDEND = "0.0 um";
	private static final String DEFAULT_INTERCEPTION = "0.0 um";
	private static final String DEFAULT_SLOPE_DIVISOR = "1.0 eV";

	private static final Logger logger = LoggerFactory.getLogger(EditEnergyFocusFunctionHandler.class);

	@Override
	public Object execute(ExecutionEvent event) throws ExecutionException {
		final Shell activeShell = PlatformUI.getWorkbench().getActiveWorkbenchWindow().getShell();
		try {
			final IModelDialog<EnergyFocusConfig> dialog = ServiceHolder.getInterfaceService().createModelDialog(activeShell);
			dialog.setPreamble("Please define the parameters of the energy to focus mapping function");
			dialog.create();
			dialog.setSize(600, 400);
			dialog.setText("Energy focus mapping");
			dialog.setModel(getConfig());

			final int result = dialog.open();
			if (result == IModelDialog.OK) {
				final EnergyFocusConfig config = dialog.getModel();
				saveConfig(config);
				updateServer(config);
			}
		} catch (Exception e) {
			logger.error("Exception opening editor for energy focus function", e);
			ErrorDialog.openError(activeShell, "Error editing energy focus function",
					"Please contact your support representative.",
					new Status(IStatus.ERROR, "uk.ac.gda.beamline.i08.commandhandlers", e.getMessage(), e));
		}

		return null;
	}

	private static EnergyFocusConfig getConfig() {
		final IStashing stash = ServiceHolder.getStashingService().createStash(STASH_NAME);
		if (stash.isStashed()) {
			try {
				return stash.unstash(EnergyFocusConfig.class);
			} catch (Exception e) {
				logger.warn("Cannot get saved energy focus function parameters: using defaults", e);
			}
		}
		return new EnergyFocusConfig(DEFAULT_SLOPE_DIVIDEND, DEFAULT_INTERCEPTION, DEFAULT_SLOPE_DIVISOR);
	}

	// Save config values to file so they will be restored when the server is restarted
	private static void saveConfig(final EnergyFocusConfig config) {
		final IStashing stash = ServiceHolder.getStashingService().createStash(STASH_NAME);
		try {
			stash.stash(config);
		} catch (Exception e) {
			logger.error("Error saving function configuration", e);
		}
	}

	// Update energy focus function in running server
	private static void updateServer(final EnergyFocusConfig config) {
		final ICommandRunner commandRunner = InterfaceProvider.getCommandRunner();
		final String jythonCommand = String.format("setEnergyFocus('%s', '%s', '%s')",
				config.getSlopeDividend(), config.getInterception(), config.getSlopeDivisor());
		commandRunner.runCommand(jythonCommand);
	}
}
