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

package uk.ac.gda.beamline.i14.views.beamlinereadiness;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.SortedMap;
import java.util.TreeMap;
import java.util.function.Consumer;

import org.apache.commons.csv.CSVRecord;
import org.apache.commons.math3.analysis.interpolation.LinearInterpolator;
import org.apache.commons.math3.analysis.polynomials.PolynomialSplineFunction;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Monitor;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.observable.IObserver;
import uk.ac.gda.client.viewer.FourStateDisplay;

/**
 * Extends a {@link FourStateDisplay} to show whether the beamline is ready i.e. whether the beam is in position and the
 * intensity is sufficient.
 */
public class BeamlineReadinessDisplay extends FourStateDisplay {
	private static final Logger logger = LoggerFactory.getLogger(BeamlineReadinessDisplay.class);

	private enum StateSeverity { OK, WARNING, CRITICAL, UNKNOWN }

	private enum ReadinessState {
		READY("Beamline is ready", StateSeverity.OK),
		INTENSITY_ZERO("Beam is off", StateSeverity.CRITICAL),
		INTENSITY_TOO_LOW("Beam intensity is too far from its target", StateSeverity.WARNING),
		SHUTTERS_NOT_OPEN("Shutters are not open", StateSeverity.CRITICAL),
		ION_CHAMBERS_OFF("Beamline state unknown: could not connect to ion chambers", StateSeverity.UNKNOWN),
		INTENSITY_NOT_DEFINED("Beamline state unknown: target intensities have not been defined", StateSeverity.UNKNOWN),
		ENERGY_OUTSIDE_RANGE("Beamline state unknown: energy is outside the calibrated range", StateSeverity.UNKNOWN),
		UNKNOWN("Beamline state unknown - see log for details", StateSeverity.UNKNOWN);

		private final String message;
		private final StateSeverity severity;

		private ReadinessState(String message, StateSeverity severity) {
			this.message = message;
			this.severity = severity;
		}

		public String getMessage() {
			return message;
		}

		public StateSeverity getSeverity() {
			return severity;
		}
	}
	private Monitor intensity;
	private Monitor ringCurrent;
	private List<Scannable> shutters;
	private Scannable energy;

	private boolean ionChambersOn;

	private BeamlineReadinessParameters displayParams;

	private PolynomialSplineFunction beamIntensityFunction;

	private ReadinessState state = ReadinessState.UNKNOWN;

	private IObserver intensityHandler;
	private IObserver handler;

	public BeamlineReadinessDisplay(Composite parent) {
		super(parent, "Ready", "Low intensity", "No beam", "State unknown");

		// Get configuration parameters
		final Map<String, BeamlineReadinessParameters> params = Finder.getLocalFindablesOfType(BeamlineReadinessParameters.class);
		if (params.size() == 0) {
			logger.error("No parameters found for beamline readiness display");
			return;
		} else {
			displayParams = params.values().iterator().next();
		}

		// observers to handle updates
		intensityHandler = (source, arg) -> handleIntensityUpdate();
		handler = (source, arg) -> handleUpdate();

		// Get scannables for the various values we are monitoring
		intensity = Finder.find(displayParams.getIntensity());
		intensity.addIObserver(intensityHandler);

		energy = Finder.find(displayParams.getEnergy());
		energy.addIObserver(handler);

		ringCurrent = Finder.find(displayParams.getRingCurrent());
		ringCurrent.addIObserver(handler);

		final List<String> shutterNames = displayParams.getShutters();
		shutters = new ArrayList<>(shutterNames.size());
		for (String shutterName : shutterNames) {
			final Scannable shutter = Finder.find(shutterName);
			shutter.addIObserver(handler);
			shutters.add(shutter);
		}

		calculateRequiredBeamIntensity();

		logger.debug("BeamlineReadinessDisplay initialised");
		logger.debug("intensityTolerance: {}%", displayParams.getIntensityTolerance());
		logCurrentValues();

		// Set initial state of the readiness indicator
		setReadinessStatus();

		logger.debug("Initial state: {}", state);
	}

	private void calculateRequiredBeamIntensity() {
		SortedMap<Double, Double> targetIntensities = new TreeMap<>();
		Consumer<CSVRecord> consumer = row -> targetIntensities.put(Double.parseDouble(row.get("Energy")), Double.parseDouble(row.get("Intensity")));

		try {
			CsvReader.processCsvFile(displayParams.getTargetIntensitiesFile(), consumer);

			final double[] energies = targetIntensities.entrySet().stream().map(Map.Entry<Double, Double>::getKey).mapToDouble(x -> x).toArray();
			final double[] intensities = targetIntensities.entrySet().stream().map(Map.Entry<Double, Double>::getValue).mapToDouble(x -> x).toArray();

			if (energies.length > 1 && intensities.length > 1) {
				beamIntensityFunction = new LinearInterpolator().interpolate(energies, intensities);
			}
		} catch (IllegalArgumentException | IOException e) {
			logger.error("Error reading CSV file", e);
		}
	}

	private void logCurrentValues() {
		try {
			logger.debug(
					"intensity: {}, energy: {}, ringCurrent: {}, targetIntensity: {}",
					getIntensity(), energy.getPosition(), ringCurrent.getPosition(),
					getTargetIntensity((double) energy.getPosition()));
		} catch (DeviceException e) {
			logger.error("Error getting beamline state", e);
		}
	}


	private void handleIntensityUpdate() {
		ionChambersOn = true;
		handleUpdate();
	}

	private void handleUpdate() {
		final ReadinessState oldState = state;
		setReadinessStatus();
		if (state != oldState) {
			logger.debug("Readiness state changed from {} to {}", oldState, state);
		}
	}

	private boolean shuttersAreOpen() throws DeviceException {
		for (Scannable shutter : shutters) {
			if(shutter.getPosition()==null || !shutter.getPosition().equals("Open")) {
				return false;
			}
		}
		return true;
	}

	private Double getTargetIntensity(double energy) {
		if (beamIntensityFunction != null) {
			if (!beamIntensityFunction.isValidPoint(energy)) {
				logger.warn("Energy {} is outside the calibrated range", energy);
				return null;
			}
			double targetIntensity = beamIntensityFunction.value(energy);
			targetIntensity *= (1.0 - (displayParams.getIntensityTolerance() / 100.0));
			return targetIntensity;
		} else {
			return null;
		}
	}

	private double getIntensity() {
		try {
			final Object intensityPos = intensity.getPosition();
			if (intensityPos instanceof Double) {
				ionChambersOn = true;
				return (double) intensityPos;
			} else if (intensityPos instanceof double[] intensityValue) {
				ionChambersOn = true;
				return Arrays.stream(intensityValue).average().orElse(0);
			}
		} catch (DeviceException e) {
			ionChambersOn = false;
			logger.error(ReadinessState.ION_CHAMBERS_OFF.getMessage(), e);
		}
		return 0.0;
	}


	private void setReadinessStatus() {
		try {
			if (!shuttersAreOpen()) {
				state = ReadinessState.SHUTTERS_NOT_OPEN;
			} else if ((double) ringCurrent.getPosition() < displayParams.getRingCurrentThreshold()) {
				state = ReadinessState.INTENSITY_ZERO;
			} else if(!ionChambersOn) {
				state = ReadinessState.ION_CHAMBERS_OFF;
			} else if (beamIntensityFunction != null) {
				final Double targetIntensity = getTargetIntensity((double) energy.getPosition());
				if (targetIntensity == null) {
					state = ReadinessState.ENERGY_OUTSIDE_RANGE;
				} else {
					state = (getIntensity() >= targetIntensity) ? ReadinessState.READY : ReadinessState.INTENSITY_TOO_LOW;
					logCurrentValues();
				}
			} else {
				state = ReadinessState.INTENSITY_NOT_DEFINED;
			}
		} catch(Exception e) {
			logger.error("Error getting BPM data", e);
			state = ReadinessState.UNKNOWN;
		}
		Display.getDefault().asyncExec(this::setDisplay);
	}

	private void setDisplay() {
		switch (state.getSeverity()) {
			case OK -> setGreen();
			case WARNING -> setYellow();
			case CRITICAL -> setRed();
			case UNKNOWN -> setGrey();
		}
		setToolTipText(state.getMessage());
	}

	public void dispose() {
		intensity.deleteIObserver(intensityHandler);
		energy.deleteIObserver(handler);
		ringCurrent.deleteIObserver(handler);
		shutters.stream().forEach(s -> s.deleteIObserver(handler));
	}

}
