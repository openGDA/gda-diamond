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

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.eclipse.core.commands.AbstractHandler;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.jface.dialogs.ErrorDialog;
import org.eclipse.scanning.api.ui.auto.IModelDialog;
import org.eclipse.scanning.device.ui.ServiceHolder;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.data.PathConstructor;
import gda.factory.Finder;
import gda.function.ILinearFunction;

public class EditEnergyFocusFunctionHandler extends AbstractHandler {
	private static final String ENERGY_FOCUS_FILE_NAME = "energyFocusFunction.json";
	private static final String DEFAULT_SLOPE_DIVIDEND = "0.0 um";
	private static final String DEFAULT_INTERCEPTION = "0.0 um";
	private static final String DEFAULT_SLOPE_DIVISOR = "1.0 eV";

	private static final Path ENERGY_FOCUS_FUNCTION_FILE_PATH = Paths.get(
			PathConstructor.createFromProperty(LocalProperties.GDA_VAR_DIR),
			ENERGY_FOCUS_FILE_NAME);

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

	/**
	 * Get initial values for the parameters.<br>
	 * These should come from the file read by the server, but if this does not exist, use hard-coded defaults
	 *
	 * @return EnergyFocusConfig object containing the parameters
	 */
	private static EnergyFocusConfig getConfig() {
		if (ENERGY_FOCUS_FUNCTION_FILE_PATH.toFile().exists()) {
			try {
				logger.debug("Attempting to read energy focus parameters from {}", ENERGY_FOCUS_FUNCTION_FILE_PATH);
				final String energyFocusConfigJson = new String(Files.readAllBytes(ENERGY_FOCUS_FUNCTION_FILE_PATH));
				return ServiceHolder.getMarshallerService().unmarshal(energyFocusConfigJson, EnergyFocusConfig.class);
			} catch (Exception e) {
				logger.warn("Could not read energy focus parameters from {}", ENERGY_FOCUS_FUNCTION_FILE_PATH, e);
			}
		}

		logger.debug("Using default values for energy focus function");
		return new EnergyFocusConfig(DEFAULT_SLOPE_DIVIDEND, DEFAULT_INTERCEPTION, DEFAULT_SLOPE_DIVISOR);
	}

	// Save config values to file so they will be restored when the server is restarted
	private static void saveConfig(final EnergyFocusConfig config) {
		try {
			final String energyFocusConfigJson = ServiceHolder.getMarshallerService().marshal(config);
			// save to a file in gda_var so it can be picked up by localStation
			ENERGY_FOCUS_FUNCTION_FILE_PATH.toFile().getParentFile().mkdirs();
			Files.write(ENERGY_FOCUS_FUNCTION_FILE_PATH, energyFocusConfigJson.getBytes());
		} catch (Exception e) {
			logger.error("Error saving function configuration", e);
		}
	}

	// Update energy focus function in running server
	private static void updateServer(final EnergyFocusConfig config) {
		final ILinearFunction energyFocusFunction = Finder.getInstance().find("energyFocusFunction");
		if (energyFocusFunction != null) {
			energyFocusFunction.setSlopeDividend(config.getSlopeDividend());
			energyFocusFunction.setInterception(config.getInterception());
			energyFocusFunction.setSlopeDivisor(config.getSlopeDivisor());
		} else {
			logger.error("Unable to set energyFocusFunction: object not found");
		}
	}
}
