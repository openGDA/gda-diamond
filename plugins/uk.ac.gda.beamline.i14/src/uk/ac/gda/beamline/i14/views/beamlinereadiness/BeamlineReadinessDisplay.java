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
import uk.ac.gda.client.viewer.ThreeStateDisplay;

/**
 * Extends a {@link ThreeStateDisplay} to show whether the beamline is ready i.e. whether the beam is in position and the
 * intensity is sufficient.
 */
public class BeamlineReadinessDisplay extends ThreeStateDisplay {
	private static final Logger logger = LoggerFactory.getLogger(BeamlineReadinessDisplay.class);

	private enum ReadinessState {
		OUT_OF_POSITION_X, OUT_OF_POSITION_Y, INTENSITY_ZERO, INTENSITY_TOO_LOW, READY, UNKNOWN
	}

	private static final String BEAM_POSITION_MESSAGE = "Beam %s position is too far from its setpoint";
	private static final String BEAM_OFF_MESSAGE = "Beam is off";
	private static final String BEAM_TOO_LOW_MESSAGE = "Beam intensity is too far from its target";
	private static final String BEAMLINE_READY_MESSAGE = "Beamline is ready";

	private Monitor xPosition;
	private Monitor yPosition;
	private Monitor intensity;
	private Monitor xSetpoint;
	private Monitor ySetpoint;
	private Monitor ringCurrent;
	private List<Scannable> shutters;
	private Scannable energy;

	private BeamlineReadinessParameters displayParams;

	private PolynomialSplineFunction beamIntensityFunction;

	private ReadinessState state = ReadinessState.UNKNOWN;

	public BeamlineReadinessDisplay(Composite parent) {
		super(parent, "Ready", "Low intensity", "No beam");

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

		xSetpoint = Finder.find(displayParams.getxSetpoint());
		ySetpoint = Finder.find(displayParams.getySetpoint());

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
					"intensity: {}, xPosition: {}, yPosition: {}, xSetpoint: {}, ySetpoint: {}, energy: {}, ringCurrent: {}, targetIntensity: {}",
					getIntensity(), xPosition.getPosition(), yPosition.getPosition(), xSetpoint.getPosition(),
					ySetpoint.getPosition(), energy.getPosition(), ringCurrent.getPosition(), getTargetIntensity((double) energy.getPosition()));
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

	private void setReadinessStatus() {
		try {
			if (!shuttersAreOpen() || (double) ringCurrent.getPosition() < displayParams.getRingCurrentThreshold()) {
				state = ReadinessState.INTENSITY_ZERO;
			} else if (!isInPosition((double) xPosition.getPosition(), (double) xSetpoint.getPosition(), displayParams.getxTolerance())) {
				state = ReadinessState.OUT_OF_POSITION_X;
			} else if (!isInPosition((double) yPosition.getPosition(), (double) ySetpoint.getPosition(), displayParams.getyTolerance())) {
				state = ReadinessState.OUT_OF_POSITION_Y;
			} else {
				final double eh2Intensity = getIntensity();
				final double targetIntensity = getTargetIntensity((double) energy.getPosition());
				state = (eh2Intensity >= targetIntensity) ? ReadinessState.READY : ReadinessState.INTENSITY_TOO_LOW;
			}
			Display.getDefault().asyncExec(this::setDisplay);
		} catch (Exception e) {
			logger.error("Error getting BPM data", e);
		}
	}

	private boolean shuttersAreOpen() throws DeviceException {
		for (Scannable shutter : shutters) {
			if (!shutter.getPosition().equals("Open")) {
				return false;
			}
		}
		return true;
	}

	private static boolean isInPosition(double position, double setpoint, double tolerance) {
		return Math.abs((position - setpoint) / position) * 100.0 < tolerance;
	}

	private double getTargetIntensity(double energy) {
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

	private void setDisplay() {
		if (state == ReadinessState.INTENSITY_ZERO) {
			setRed();
			setToolTipText(BEAM_OFF_MESSAGE);
		} else if (state == ReadinessState.OUT_OF_POSITION_X) {
			setRed();
			setToolTipText(String.format(BEAM_POSITION_MESSAGE, "x"));
		} else if (state == ReadinessState.OUT_OF_POSITION_Y) {
			setRed();
			setToolTipText(String.format(BEAM_POSITION_MESSAGE, "y"));
		} else if (state == ReadinessState.INTENSITY_TOO_LOW) {
			setYellow();
			setToolTipText(BEAM_TOO_LOW_MESSAGE);
		} else if (state == ReadinessState.READY) {
			setGreen();
			setToolTipText(BEAMLINE_READY_MESSAGE);
		} else {
			logger.warn("Beamline state unknown");
		}
	}
}
