/*-
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

package gda.device.robot;

import java.util.Arrays;
import java.util.Objects;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableBase;
import gda.device.scannable.ScannableUtils;
import gda.factory.FactoryException;


public class RotatedXyScannable extends ScannableBase {
	private static final Logger logger = LoggerFactory.getLogger(RotatedXyScannable.class);
	private RotationCalculation calculator = new RotationCalculation();
	private Scannable xyScannable;
	private int componentNumber = 0; // 0 -> labX, 1 -> labY

	@Override
	public void configure() throws FactoryException {
		Objects.requireNonNull(xyScannable, "Scannable to use for XY stage has not been set");
		setInputNames(new String[] {getName()});
		super.configure();
	}

	/**
	 * Demand position is either X or Y value in lab coordinate system.
	 *
	 * @throws DeviceException
	 */
	@Override
	public void asynchronousMoveTo(Object obj) throws DeviceException {
		double demandPosition = ScannableUtils.objectToArray(obj)[0];
		double[] currentLabXY = getCurrentLabXY();
		logger.info("Demand lab position : {}, Current lab(x,y) : {}", demandPosition, Arrays.asList(currentLabXY));
		double[] demandLabXY;
		if (componentNumber == 0) {
			// use demand position for labX, current position for labY
			demandLabXY = new double[] {demandPosition, currentLabXY[1]};
		} else {
			// current lab position for labX, demand position for labY
			demandLabXY = new double[] {currentLabXY[0], demandPosition};
		}
		double[] targetPos = calculator.calcStageXY(demandLabXY[0], demandLabXY[1]);
		logger.info("Final lab(x,y) position : {}, Moving robot to {}", Arrays.asList(demandLabXY), Arrays.asList(targetPos));
		xyScannable.asynchronousMoveTo(targetPos);
	}

	public double[] getCurrentStageXY() throws DeviceException {
		Double[] positionArray = ScannableUtils.objectToArray(xyScannable.getPosition());
		if (positionArray.length != 2) {
			throw new IllegalArgumentException("Position array from "+xyScannable.getName()+" does not have size = 2");
		}
		return new double[] {positionArray[0], positionArray[1]};
	}

	/**
	 * Compute the labXY coordinates from the current robot(x,y) positions
	 * @return
	 * @throws DeviceException
	 */
	public double[] getCurrentLabXY() throws DeviceException {
		double[] stageXY = getCurrentStageXY();
		return calculator.calculateLabXY(stageXY[0], stageXY[1]);
	}

	/**
	 * Compute the lab X Y coordinates for a given stage X, Y coordinate
	 * @param stageX
	 * @param stageY
	 * @return [labX, labY]
	 */
	public double[] getLabXY(double stageX, double stageY) {
		return calculator.calculateLabXY(stageX, stageY);
	}

	/**
	 * Compute the stage X Y coordinates for a given lab X, Y coordinate
	 * @param labX
	 * @param labY
	 * @return [stageX, stageY]
	 */
	public double[] getStageXY(double labX, double labY) {
		return calculator.calcStageXY(labX, labY);
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return xyScannable.isBusy();
	}

	@Override
	public Object getPosition() throws DeviceException {
		return getCurrentLabXY()[componentNumber];
	}

	/**
	 * Set the scannable that should be used to move the robot X,Y axes.
	   The demand and readback positions are expected to be arrays with the x and y values.
	   (e.g. MecaRobotMover instance to move x,y axes, or ScannableGroup with x y scannables).

	 * @param robotXY
	 */
	public void setXYScannable(Scannable robotXY) {
		this.xyScannable = robotXY;
	}

	public int getComponent() {
		return componentNumber;
	}

	/**
	 * Select the lab coordinate system component that will be controlled when making a move :
	 * <li> 0 -> move lab X
	 * <li> 1 -> move lab Y
	 *
	 * @param component
	 */
	public void setComponentNumber(int component) {
		this.componentNumber = component;
	}

	public void setOrigin(double[] origin) {
		if (origin == null || origin.length != 2) {
			throw new IllegalArgumentException("Origin array value must have two elements!");
		}
		calculator.setOrigin(origin[0], origin[1]);
	}

	public double[] getOrigin() {
		return calculator.getOrigin();
	}

	public void setOrigin(double originX, double originY) {
		calculator.setOrigin(originX, originY);
	}

	public void setAngle(double angle) {
		calculator.setAngle(angle);
	}

	public double getAngle() {
		return calculator.getAngle();
	}

	private static class RotationCalculation {
		private double[] origin = {0, 0};
		private double alpha; // angle between robot x axis and 'labX' direction

		/**
		 * Calculate stage(x,y) value for given lab(x,y) value.
		 *
		 * @param labX
		 * @param labY
		 * @return array with [stageX, stageY]
		 */
		public double[] calcStageXY(double labX, double labY) {
			return new double[] {labX*Math.cos(alpha) - labY*Math.sin(alpha) + origin[0],
				   -labY*Math.cos(alpha) - labX*Math.sin(alpha) + origin[1]};
		}

		/**
		 * Calculate lab(x,y) value for given stage(x,y) value
		 * (i.e. inverse calculation to {@link #calcStageXY(double, double)}
		 *
		 * @param stageX
		 * @param stageY
		 * @return array with [labX, labY]
		 */
		public double[] calculateLabXY(double stageX, double stageY) {
			double labY = (origin[0]-stageX)*Math.sin(alpha) + (origin[1]-stageY)*Math.cos(alpha);
			double labX = (stageX - origin[0] + labY*Math.sin(alpha))/Math.cos(alpha);
			return new double[] {labX, labY};
		}

		/**
		 * Set the x,y origin of robot coordinate system
		 *
		 * @param originX
		 * @param originY
		 */
		public void setOrigin(double originX, double originY) {
			origin = new double[] {originX, originY};
		}

		public double[] getOrigin() {
			return origin;
		}

		/**
		 * Set the angle between robot x axis and 'labX' direction
		 *
		 * @param alpha between lab x and robot x axes (degrees)
		 */
		public void setAngle(double alpha) {
			this.alpha = Math.PI*alpha/180.;
		}

		/**
		 *
		 * @return angle (degrees)
		 */
		public double getAngle() {
			return 180*alpha/Math.PI;
		}
	}
}
