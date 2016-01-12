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
import gda.device.scannable.ScannableMotor;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;

public class EdeScanMotorPositions implements EdeScanPosition {
	private final EdePositionType type;
	private final Map<Scannable, Double> scannablePositions = new HashMap<Scannable, Double>();

	public EdeScanMotorPositions(EdePositionType type, Map<String, Double> positions) throws DeviceException {
		this.type = type;
		for (Entry<String, Double> scannablePositionEntry : positions.entrySet()) {
			Scannable scannable = Finder.getInstance().find(scannablePositionEntry.getKey());
			if (scannable ==null) {
				throw new DeviceException("Unable to find scannable: " + scannablePositionEntry);
			}
			scannablePositions.put(scannable, scannablePositionEntry.getValue());
		}
	}

	public Map<Scannable, Double> getPositions() {
		return scannablePositions;
	}

	/**
	 * Return an estimate of the time to move all motors from their current position to final position.
	 * @return time to move all motors.
	 * @author Iain Hall
	 * @since 9/10/2015
	 */
	@Override
	public double getTimeToMove()  {
		return getTimeToMove(null);
	}

	/**
	 * Estimate the time to move all motors to their final position.
	 * @param otherMotors another EdeScanMotorPositions object to be used for initial positions (can be null, in which case current motor positions will be used for initial positions).
	 * @return time to move all motors.
	 * @author Iain Hall
	 * @since 9/10/2015
	 */
	public double getTimeToMove( EdeScanMotorPositions otherMotors ) {
		Map<Scannable, Double> intialPositionsMap = null;
		if ( otherMotors != null ) {
			intialPositionsMap = otherMotors.getPositions();
		}
		double maxTimeToMove = 0.0;
		for( Entry<Scannable, Double> positionEntry : scannablePositions.entrySet() )
		{
			try{
				Scannable scanMotor =  positionEntry.getKey();
				double initialPosition = 0;
				if ( intialPositionsMap != null && intialPositionsMap.containsKey( scanMotor ) ) {
					initialPosition = intialPositionsMap.get( scanMotor );
				} else {
					initialPosition = (double) scanMotor.getPosition();
				}

				double motorSpeed = ((ScannableMotor)scanMotor).getSpeed();
				double finalPosition = positionEntry.getValue();
				// Assume constant motor velocity during the move...
				double timeToMove = Math.abs( finalPosition - initialPosition )/motorSpeed;
				maxTimeToMove = Math.max( timeToMove, maxTimeToMove);
			}
			catch (DeviceException e) {
				InterfaceProvider.getTerminalPrinter().print("Problem in getTimeToMove for "+positionEntry.getKey().getName() );
			}
		}
		return maxTimeToMove;
	}

	@Override
	public void moveIntoPosition() throws DeviceException, InterruptedException {
		for (Entry<Scannable, Double> scannablePositionEntry : scannablePositions.entrySet()) {
			InterfaceProvider.getTerminalPrinter().print("Moving " + scannablePositionEntry.getKey().getName() + " to " + scannablePositionEntry.getValue());
			scannablePositionEntry.getKey().asynchronousMoveTo(scannablePositionEntry.getValue());
		}
		for (Entry<Scannable, Double> scannablePositionEntry : scannablePositions.entrySet()) {
			scannablePositionEntry.getKey().waitWhileBusy();
		}
		InterfaceProvider.getTerminalPrinter().print("Move completed");
	}

	@Override
	public EdePositionType getType() {
		return type;
	}
}
