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

package uk.ac.gda.beamline.i14.views.beamlinereadiness;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.observable.IObserver;
import uk.ac.diamond.daq.mapping.ui.experiment.StateReporter;

/**
 * Class that implements {@link StateReporter} interface
 * Finds the list of shutters as specified in {@link BeamlineReadinessParameters},
 * that will be observed. If their state changes, it will report this to the consumer
 */
public class ShuttersStateListener implements StateReporter {

	private static final Logger logger = LoggerFactory.getLogger(ShuttersStateListener.class);

	private IObserver handler;

	private List<Scannable> shutters;
	private Consumer<StateReport> stateConsumer;

	@Override
	public void initialize(Consumer<StateReport> stateConsumer) {
		this.stateConsumer = stateConsumer;
		setShuttersListeners();
	}

	private void setShuttersListeners() {
		final Map<String, BeamlineReadinessParameters> displayParams = Finder.getLocalFindablesOfType(BeamlineReadinessParameters.class);
		if (displayParams.isEmpty()) {
			logger.error("No parameters found for beamline readiness display");
		} else {
			List<String> shutterNames = displayParams.values().iterator().next().getShutters();
			shutters = new ArrayList<>(shutterNames.size());
			for (String shutterName : shutterNames) {
				final Scannable shutter = Finder.find(shutterName);
				handler = (source, arg) -> reportShuttersState();
				shutter.addIObserver(handler);
				shutters.add(shutter);
			}
			reportShuttersState();
		}
	}

	private boolean shuttersAreOpen() {
		for (Scannable shutter : shutters) {
			try {
				if(!shutter.getPosition().equals("Open")) {
					return false;
				}
			} catch(DeviceException e) {
				logger.error("Error getting shutter position", e);
			}
		}
		return true;
	}

	private void reportShuttersState() {
		if (shuttersAreOpen()) {
			stateConsumer.accept(new StateReport(State.GOOD, ""));
		} else {
			stateConsumer.accept(new StateReport(State.BAD, "Shutters are not open"));
		}
	}

	@Override
	public void dispose() {
		shutters.stream().forEach(shutter -> shutter.deleteIObserver(handler));
	}
}
