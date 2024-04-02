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

import java.io.IOException;
import java.util.function.Consumer;

import org.apache.commons.csv.CSVRecord;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.observable.IObserver;
import uk.ac.gda.client.viewer.ThreeStateDisplay;

/**
 * Extends a {@link ThreeStateDisplay} to display the position of the Detector Cover and its state
 * depending on whether is in or out according to configured Detector Cover parameters.
 */

public class DetectorCoverDisplay extends ThreeStateDisplay {
	private static final Logger logger = LoggerFactory.getLogger(DetectorCoverDisplay.class);
	private static final String OUT = "Out";
	private static final String IN = "In";

	private double inValue;
	private double outValue;
	private double position;

	private Scannable detectorCover;
	private State state;

	private IObserver handler;

	private enum State {
		OUT("Detector cover is out"),
		UNKNOWN("Detector cover state unknown"),
		IN("Detector cover is in");

		private final String message;

		private State(String message) {
			this.message = message;
		}

		public String getMessage() {
			return message;
		}
	}

	public DetectorCoverDisplay(Composite parent, DetectorCoverParameters displayParams) {
		super(parent, OUT, "Unknown", IN);

		handler = (source, arg) -> handleUpdate();

		Consumer<CSVRecord> consumer = row -> {
			inValue = Double.parseDouble(row.get(IN));
			outValue = Double.parseDouble(row.get(OUT));
		};

		try {
			CsvReader.processCsvFile(displayParams.getDetectorCoverPositionsFile(), consumer);

			detectorCover = Finder.find(displayParams.getScannableName());
			detectorCover.addIObserver(handler);

			logger.debug("DetectorCoverStatus initialised");
			logger.debug("inValue: {}%, outValue: {}%",inValue, outValue);

			setDetectorCoverStatus();

			logger.debug("Initial state: {}", state);

		} catch (IllegalArgumentException | IOException e) {
			logger.error("Error reading CSV file", e);
			setUnknownCoverStatus();
		}
	}

	private void handleUpdate() {
		final State oldState = state;
		setDetectorCoverStatus();
		if (state != oldState) {
			logger.debug("Detector cover state changed from {} to {}", oldState, state);
		}
	}

	private void setUnknownCoverStatus() {
		state = State.UNKNOWN;
		Display.getDefault().asyncExec(this::setDisplay);
	}

	private void setDetectorCoverStatus() {
		try {
			position = (double) detectorCover.getPosition();
			logger.debug("Position: {}%", position);
		} catch(DeviceException e) {
			logger.error("Error getting Detector Cover data", e);
			state = State.UNKNOWN;
		}

		if (position == inValue) {
			state = State.IN;
		} else if(position == outValue) {
			state = State.OUT;
		} else {
			state = State.UNKNOWN;
		}
		Display.getDefault().asyncExec(this::setDisplay);
	}

	private void setDisplay() {
		switch (state) {
			case IN -> setRed();
			case OUT -> setGreen();
			case UNKNOWN -> setYellow();
		}
		setToolTipText(state.getMessage());
	}

	public void dispose() {
		detectorCover.deleteIObserver(handler);
	}

}
