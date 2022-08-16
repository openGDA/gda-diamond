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

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

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

	private Monitor xPosition;
	private Monitor yPosition;
	private Monitor intensity;
	private Monitor ringCurrent;
	private List<Scannable> shutters;
	private Scannable energy;

	private BeamlineReadinessParameters displayParams;

	private PolynomialSplineFunction beamIntensityFunction;

	private ReadinessState state = ReadinessState.UNKNOWN;

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

		// Get scannables for the various values we are monitoring
		intensity = Finder.find(displayParams.getIntensity());
		intensity.addIObserver(this::handleUpdate);

		xPosition = Finder.find(displayParams.getxPosition());
		xPosition.addIObserver(this::handleUpdate);

		yPosition = Finder.find(displayParams.getyPosition());
		yPosition.addIObserver(this::handleUpdate);

		energy = Finder.find(displayParams.getEnergy());
		energy.addIObserver(this::handleUpdate);

		ringCurrent = Finder.find(displayParams.getRingCurrent());
		ringCurrent.addIObserver(this::handleUpdate);

		final List<String> shutterNames = displayParams.getShutters();
		shutters = new ArrayList<>(shutterNames.size());
		for (String shutterName : shutterNames) {
			final Scannable shutter = Finder.find(shutterName);
			shutter.addIObserver(this::handleUpdate);
			shutters.add(shutter);
		}

		// Create a function to calculate required beam intensity
		final Map<Double, Double> targetIntensities = displayParams.getTargetIntensities();
		final double[] energies = targetIntensities.entrySet().stream().map(Map.Entry<Double, Double>::getKey).mapToDouble(x -> x).toArray();
		final double[] intensities = targetIntensities.entrySet().stream().map(Map.Entry<Double, Double>::getValue).mapToDouble(x -> x).toArray();
		beamIntensityFunction = new LinearInterpolator().interpolate(energies, intensities);

		logger.debug("BeamlineReadinessDisplay initialised");
		logger.debug("xTolerance: {}%, yTolerance: {}%, intensityTolerance: {}%",
				displayParams.getxTolerance(), displayParams.getyTolerance(), displayParams.getIntensityTolerance());
		logCurrentValues();

		// Set initial state of the readiness indicator
		setReadinessStatus();

		logger.debug("Initial state: {}", state);
	}

	private void logCurrentValues() {
		try {
			logger.debug(
					"intensity: {}, xPosition: {}, yPosition: {}, energy: {}, ringCurrent: {}, targetIntensity: {}",
					getIntensity(), xPosition.getPosition(), yPosition.getPosition(), energy.getPosition(),
					ringCurrent.getPosition(), getTargetIntensity((double) energy.getPosition()));
		} catch (DeviceException e) {
			logger.error("Error getting beamline state", e);
		}
	}

	@SuppressWarnings("unused")
	private void handleUpdate(Object source, Object arg) {
		final ReadinessState oldState = state;
		setReadinessStatus();
		if (state != oldState) {
			logger.debug("Readiness state changed from {} to {}", oldState, state);
			logCurrentValues();
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

	private static boolean isInPosition(double position, double setpoint, double tolerance) {
		return Math.abs((position - setpoint) / position) * 100.0 < tolerance;
	}

	private Double getTargetIntensity(double energy) {
		if (!beamIntensityFunction.isValidPoint(energy)) {
			logger.warn("Energy {} is outside the calibrated range", energy);
			return null;
		}
		double targetIntensity = beamIntensityFunction.value(energy);
		targetIntensity *= (1.0 - (displayParams.getIntensityTolerance() / 100.0));
		return targetIntensity;
	}

	private double getIntensity() throws DeviceException {
		final Object intensityVal = intensity.getPosition();
		if (intensityVal instanceof Double) {
			return (double) intensityVal;
		} else if (intensityVal instanceof double[]) {
			return Arrays.stream((double[]) intensityVal).average().orElse(0);
		}
		return 0.0;
	}


	private void setReadinessStatus() {
		try {
			if (!shuttersAreOpen()) {
				state = ReadinessState.SHUTTERS_NOT_OPEN;
			} else if ((double) ringCurrent.getPosition() < displayParams.getRingCurrentThreshold()) {
				state = ReadinessState.INTENSITY_ZERO;
			} else {
				final Double targetIntensity = getTargetIntensity((double) energy.getPosition());
				if (targetIntensity == null) {
					state = ReadinessState.ENERGY_OUTSIDE_RANGE;
				} else {
					state = (getIntensity() >= targetIntensity) ? ReadinessState.READY : ReadinessState.INTENSITY_TOO_LOW;
				}
			}
		} catch(Exception e) {
			logger.error("Error getting BPM data", e);
			state = ReadinessState.UNKNOWN;
		}
		Display.getDefault().asyncExec(this::setDisplay);
	}

	private void setDisplay() {
		switch(state.getSeverity()) {
			case OK:
				setGreen();
				break;
			case WARNING:
				setYellow();
				break;
			case CRITICAL:
				setRed();
				break;
			case UNKNOWN:
				setGrey();
				break;
		}
		setToolTipText(state.getMessage());
	}

}
