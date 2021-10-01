/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.Finder;
import uk.ac.gda.client.viewer.ThreeStateDisplay;

/**
 * Extends a {@link ThreeStateDisplay} to display the position of the Detector Cover and its state
 * depending on whether is in or out according to configured Detector Cover parameters.
 */

public class DetectorCoverDisplay extends ThreeStateDisplay {

	private static final Logger logger = LoggerFactory.getLogger(DetectorCoverDisplay.class);

	private double inValue;
	private double outValue;
	private double position;

	private Scannable detectorCover;
	private DetectorCoverState state;


	private enum DetectorCoverState {
		OUT("Detector cover is out"),
		UNKNOWN("Detector cover state unknown"),
		IN("Detector cover is in");

		private final String message;

		private DetectorCoverState(String message) {
			this.message = message;
		}

		public String getMessage() {
			return message;
		}
	}


	public DetectorCoverDisplay(Composite parent, DetectorCoverParameters displayParams) {
		super(parent, "Out", "Unknown", "In");

		inValue = displayParams.getInValue();
		outValue = displayParams.getOutValue();

		detectorCover = Finder.find(displayParams.getScannableName());
		detectorCover.addIObserver(this::handleUpdate);

		logger.debug("DetectorCoverStatus initialised");
		logger.debug("inValue: {}%, outValue: {}%",displayParams.getInValue(), displayParams.getOutValue());

		setDetectorCoverStatus();

		logger.debug("Initial state: {}", state);
	}

	@SuppressWarnings("unused")
	private void handleUpdate(Object source, Object arg) {
		final DetectorCoverState oldState = state;
		setDetectorCoverStatus();
		if (state != oldState) {
			logger.debug("Detector cover state changed from {} to {}", oldState, state);
		}
	}

	private DetectorCoverState setDetectorCoverStatus() {

		try {
			position = (double) detectorCover.getPosition();
			logger.debug("Position: {}%", position);

		} catch(DeviceException e) {
			logger.error("Error getting Detector Cover data", e);
			state = DetectorCoverState.UNKNOWN;
		}

		if (position == inValue) {
			state = DetectorCoverState.IN;
		} else if(position == outValue) {
			state = DetectorCoverState.OUT;
		} else {
			state = DetectorCoverState.UNKNOWN;
		}

		Display.getDefault().asyncExec(this::setDisplay);

		return state;
	}

	private void setDisplay() {
		if (state == DetectorCoverState.IN) {
			setRed();
		} else if (state == DetectorCoverState.OUT) {
			setGreen();
		} else if (state == DetectorCoverState.UNKNOWN) {
			setYellow();
		}
		setToolTipText(state.getMessage());
	}

}
