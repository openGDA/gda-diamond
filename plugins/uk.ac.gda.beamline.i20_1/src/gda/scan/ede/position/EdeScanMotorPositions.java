/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package gda.scan.ede.position;

import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;

public class EdeScanMotorPositions implements EdeScanPosition {
	private final EdePositionType type;
	private final Map<Scannable, Double> scanablePositions = new HashMap<Scannable, Double>();

	public EdeScanMotorPositions(EdePositionType type, Map<String, Double> positions) throws DeviceException {
		this.type = type;
		for (Entry<String, Double> scannablePositionEntry : positions.entrySet()) {
			Scannable scannable = Finder.getInstance().find(scannablePositionEntry.getKey());
			if (scannable ==null) {
				throw new DeviceException("Unable to find scannable: " + scannablePositionEntry);
			}
			scanablePositions.put(scannable, scannablePositionEntry.getValue());
		}
	}

	@Override
	public void moveIntoPosition() throws DeviceException, InterruptedException {
		for (Entry<Scannable, Double> scannablePositionEntry : scanablePositions.entrySet()) {
			InterfaceProvider.getTerminalPrinter().print("Moving " + scannablePositionEntry.getKey().getName() + " to " + scannablePositionEntry.getValue());
			scannablePositionEntry.getKey().asynchronousMoveTo(scannablePositionEntry.getValue());
		}
		for (Entry<Scannable, Double> scannablePositionEntry : scanablePositions.entrySet()) {
			scannablePositionEntry.getKey().waitWhileBusy();
		}
		InterfaceProvider.getTerminalPrinter().print("Move completed");
	}

	@Override
	public EdePositionType getType() {
		return type;
	}
}
