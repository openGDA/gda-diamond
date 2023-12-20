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

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jython.InterfaceProvider;
import gda.jython.commandinfo.CommandThreadEvent;
import gda.jython.commandinfo.CommandThreadEventType;
import gda.jython.commandinfo.ICommandThreadObserver;
import gda.observable.IObserver;
import gda.scan.ScanEvent;

public class ResetMovingSumAddon{
	private static final Logger logger = LoggerFactory.getLogger(ResetMovingSumAddon.class);

	private static final String DETECTOR = "dld";
	private static final String COMMAND = "clear_summed_data()";

	private String scanCommand;
	private boolean scanIsRunning = false;
	private int currentPoint = -1;

	public ResetMovingSumAddon() {
		configure();
	}

	public void configure() {
		logger.debug("Configuring ResetMovingSumAddon");
		InterfaceProvider.getCommandThreadInfoProvider().addCommandThreadObserver(commandThreadObserver);
		InterfaceProvider.getScanDataPointProvider().addScanEventObserver(serverObserver);
	}

	private ICommandThreadObserver commandThreadObserver = (source, arg) -> {
		if (arg instanceof CommandThreadEvent event &&  (event.getEventType()==CommandThreadEventType.START)) {
				scanCommand = event.getInfo().getCommand();
				if (!(scanCommand.contains(DETECTOR))) return;
				scanIsRunning = true;
				resetMovSum();
				logger.debug("CommandThreadObserver got scan command {}",scanCommand);
		}
	};

	private IObserver serverObserver = (source, arg) -> {
		if (!(arg instanceof ScanEvent scanEvent) || (!scanIsRunning)) return;
		if (scanEvent.getLatestStatus().isComplete()) {
			scanIsRunning = false;
			currentPoint = -1;
			return;
		}
		if (scanEvent.getCurrentPointNumber()==currentPoint) return;
		resetMovSum();
		currentPoint = scanEvent.getCurrentPointNumber();
	};

	private void resetMovSum() {
		logger.debug("Resetting MovSum");
		InterfaceProvider.getCommandRunner().runCommand(COMMAND);
	}
}
