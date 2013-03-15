/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package gda.device.scannable;

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.enumpositioner.ValveBase;
import gda.epics.LazyPVFactory;
import gda.epics.ReadOnlyPV;
import gda.factory.FactoryException;
import gda.jython.InterfaceProvider;
import gda.scan.ScanBase;

import java.io.IOException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Zero-in, zero-out scannable intended to be used a default scannable to confirm that the EH shutter is open.
 */
public final class ShutterChecker extends ScannableBase {

	private static final Logger logger = LoggerFactory.getLogger(ShutterChecker.class);

	private final EnumPositioner shutter;
	private ReadOnlyPV<Double> pssState;

	public ShutterChecker(EnumPositioner shutter, String pssPVName) {
		this.shutter = shutter;

		pssState = LazyPVFactory.newReadOnlyDoublePV(pssPVName);

		inputNames = new String[] {};
		extraNames = new String[] {};
		outputFormat = new String[] {};
	}

	@Override
	public void configure() throws FactoryException {
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		return null;
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		// do nothing
	}

	@Override
	public void atScanStart() throws DeviceException {

		// check if shutter open

		String position = (String) shutter.getPosition();
		if (!position.equals(ValveBase.OPEN)) {

			try {
				// if closed, is PSS OK to open it?
				double state = pssState.get();
				// when PSS ready open the shutter
				int attempts = 0;
				while (state != 0) {
					ScanBase.checkForInterrupts();
					// check timeout
					if (attempts > 120) {
						throw new DeviceException(
								"Time out while waiting for the hutch to be searched!\nSearch the hutch, open shutter "
										+ shutter.getName() + ", and restart the scan.");
					}
					updateUser("Experimental shutter closed and hutch not searched. Waiting for search to complete...");
					Thread.sleep(1000);
					state = pssState.get();
				}
				if (attempts > 0) {
					updateUser("Search complete; opening shutter " + shutter.getName());
				} else {
					updateUser("Opening shutter " + shutter.getName());
				}
				shutter.moveTo(ValveBase.RESET);
				shutter.moveTo(ValveBase.OPEN);
				Thread.sleep(100);
				if (!position.equals(ValveBase.OPEN)) {
					throw new DeviceException(
							getName()
									+ " failed to successfully open shutter "
									+ shutter.getName()
									+ ". Aborting scan.\nYou need to check if the shutter is operating properly within GDA."
									+ "\nIf you do not want the shutter to open as you are testing, then run the jython command: remove_default "
									+ shutter.getName());
				}
			} catch (IOException e) {
				logger.error("IOException while checking shutter is open.", e);
				throw new DeviceException("IOException while checking shutter is open.", e);
			} catch (InterruptedException e) {
				logger.error("Interrupted exception while checking shutter is open", e);
				throw new DeviceException("Interrupted exception while checking shutter is open.", e);
			}
		}
	}

	private void updateUser(String message) {
		InterfaceProvider.getTerminalPrinter().print(message);
		logger.info(message);
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

}
