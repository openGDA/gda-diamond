/*
 * This addon will reset Moving Sum plugin for every new scan point
 *  which involves DLD in scan command.
 *
 * -
 * Copyright © 2023 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i09_2.addons;

import java.util.Arrays;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jython.InterfaceProvider;
import gda.observable.IObserver;
import gda.scan.ScanEvent;

public class ResetMovingSumAddon{
	private static final Logger logger = LoggerFactory.getLogger(ResetMovingSumAddon.class);

	private static final String DETECTOR = "dld";
	private static final String COMMAND = "clear_summed_data()";
	private int currentPoint = Integer.MAX_VALUE;

	public ResetMovingSumAddon() {
		configure();
	}

	public void configure() {
		logger.debug("Configuring ResetMovingSumAddon");
		InterfaceProvider.getScanDataPointProvider().addScanEventObserver(serverObserver);
	}

	private IObserver serverObserver = (source, arg) -> {
		if (!(arg instanceof ScanEvent scanEvent)) return;
		if (Arrays.asList(scanEvent.getLatestInformation().getDetectorNames()).stream().filter(s -> s.startsWith(DETECTOR)).toList().isEmpty()) return;
		if (currentPoint == scanEvent.getCurrentPointNumber()) return;
		resetMovSum();
		currentPoint = scanEvent.getCurrentPointNumber();
		if (scanEvent.getLatestStatus().isComplete()) currentPoint = Integer.MAX_VALUE;
	};

	private void resetMovSum() {
		logger.debug("Resetting MovSum");
		InterfaceProvider.getCommandRunner().runCommand(COMMAND);
	}
}
