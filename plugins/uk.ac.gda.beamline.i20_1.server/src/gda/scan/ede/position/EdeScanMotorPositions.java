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

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.dawnsci.ede.EdePositionType;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableMotor;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.scan.ede.TimeResolvedExperimentParameters;

@JsonInclude(Include.NON_NULL)
public class EdeScanMotorPositions implements EdeScanPosition {
	private final EdePositionType type;
	private final Map<Scannable, Double> scannablePositions = new HashMap<Scannable, Double>();

	@JsonSerialize(using = TimeResolvedExperimentParameters.MapSerializerStringDouble.class)
	@JsonDeserialize(using = TimeResolvedExperimentParameters.MapDeserializerStringDouble.class)
	private final Map<String, Double> positionMap;

	private Scannable scannableToMoveDuringScan;
	private String nameOfScannableToMoveDuringScan;
	private List<Object> motorPositionsDuringScan = new ArrayList<>();

	/**
	 * No-args constructor (added for serialisation)
	 */
	public EdeScanMotorPositions() {
		type = null;
		positionMap = null;
	}
	public EdeScanMotorPositions(EdePositionType type, Map<String, Double> positions) throws DeviceException {
		this.type = type;
		this.positionMap = positions;
		setupScannablePositionMap();
	}

	public void setupScannablePositionMap() throws DeviceException {
		if (positionMap==null) {
			return;
		}
		for (Entry<String, Double> scannablePositionEntry : positionMap.entrySet()) {
			Scannable scannable = Finder.find(scannablePositionEntry.getKey());
			if (scannable ==null) {
				throw new DeviceException("Unable to find scannable: " + scannablePositionEntry);
			}
			scannablePositions.put(scannable, scannablePositionEntry.getValue());
		}
	}

	public void setScannableToMoveDuringScan(Scannable scannableToMoveDuringScan) {
		this.scannableToMoveDuringScan = scannableToMoveDuringScan;
		nameOfScannableToMoveDuringScan = scannableToMoveDuringScan.getName();
	}

	@JsonIgnore
	public Scannable getScannableToMoveDuringScan() {
		if (scannableToMoveDuringScan==null && nameOfScannableToMoveDuringScan!=null) {
			scannableToMoveDuringScan=Finder.find(nameOfScannableToMoveDuringScan);
		}
		return scannableToMoveDuringScan;
	}

	public void setMotorPositionsDuringScan(List<Object> motorPositionsDuringScan) {
		this.motorPositionsDuringScan = motorPositionsDuringScan;
	}

	@JsonIgnore
	public List<Object> getMotorPositionsDuringScan() {
		return motorPositionsDuringScan;
	}

	public void setMotorPositionsDuringScan(double startPos, double endPos, int numPoints) {
		if (numPoints<2) {
			numPoints=2;
		}
		double stepSize = (endPos-startPos)/(numPoints-1);

		motorPositionsDuringScan.clear();
		int count = 0;
		while(count < numPoints) {
			double posToAdd = startPos + count*stepSize;
			motorPositionsDuringScan.add(posToAdd);
			count++;
		}
	}

	@JsonIgnore
	public Map<Scannable, Double> getPositions() {
		return scannablePositions;
	}

	public Map<String, Double> getPositionMap() {
		return positionMap;
	}

	/**
	 * Return an estimate of the time to move all motors from their current position to final position.
	 * @return time to move all motors.
	 * @author Iain Hall
	 * @since 9/10/2015
	 */
	@JsonIgnore
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
				printMessage("Problem in getTimeToMove for "+positionEntry.getKey().getName() );
			}
		}
		return maxTimeToMove;
	}

	private double moveTolerance = 1e-3;

	/**
	 * Test whether current position of scannable is within tolerance of a position
	 * @param scn
	 * @param newPosition
	 * @return true if scn position is within {@link #moveTolerance} of newPosition
	 * @throws DeviceException
	 */
	private boolean doMove(Scannable scn, Double newPosition) throws DeviceException {
		double currentPos = (double) scn.getPosition();
		return Math.abs(newPosition - currentPos) > moveTolerance;
	}

	@Override
	public void moveIntoPosition() throws DeviceException, InterruptedException {
		List<Scannable> scannablesToWaitFor = new ArrayList<>();

		for (Entry<Scannable, Double> scannablePositionEntry : scannablePositions.entrySet()) {
			Scannable scn = scannablePositionEntry.getKey();
			double newPosition = scannablePositionEntry.getValue();
			if (doMove(scn, newPosition)) {
				printMessage("Moving " + scn.getName() + " to " + newPosition);
				scn.asynchronousMoveTo(newPosition);
				scannablesToWaitFor.add(scn);
			} else {
				printMessage(scn.getName() + " is already at required position " + newPosition);
			}
		}
		for (Scannable scn : scannablesToWaitFor) {
			scn.waitWhileBusy();
		}
		printMessage("Move completed");
	}

	@Override
	public EdePositionType getType() {
		return type;
	}

	private void printMessage(String msg) {
		InterfaceProvider.getTerminalPrinter().print(msg);
	}

	public double getMoveTolerance() {
		return moveTolerance;
	}

	public void setMoveTolerance(double moveTolerance) {
		this.moveTolerance = moveTolerance;
	}
}
