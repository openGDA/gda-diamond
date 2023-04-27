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

package gda.device.robot;

import java.util.Objects;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.MultiPVScannable;
import gda.device.scannable.ScannableBase;
import gda.factory.FactoryException;

/**
 * Scannable to allow single or multiple angle/pose position of the Meca robot to be moved and used in a scan.
 * Each call to {@link #rawAsynchronousMoveTo(Object)} performs the move by carrying out the following steps :
 * <li> Copy all the current positions/angles to the setpoint (i.e. demand) positions
 * <li> Apply the new setpoint value(s) for the angle/positions to be moved
 * <li> Initiate the move. i.e. move the robot limbs to the current setpoint values.
 *
 * <li>{@link #robotSetpointScannable} is the scannable/group of setpoint PV(s) to be moved each time a position is set
 */
public class MecaRobotMover extends ScannableBase {

	private static final Logger logger = LoggerFactory.getLogger(MecaRobotMover.class);

	/**
	 * Scannable or ScannableGroup of joint or pose setpoint PVs.
	 */
	private Scannable robotSetpointScannable;

	private Scannable startMoveScannable;
	private Scannable copyPositionsScannable;
	private MecaStatusChecker statusChecker;

	private long waitTimeMs = 100;
	private long waitTimeForMotionStart = 500;

	public MecaRobotMover() {
		super();
		setExtraNames(new String[] {});
	}

	@Override
	public void configure() throws FactoryException {
		Objects.requireNonNull(robotSetpointScannable, "Position positionScannableGroup has not been set for "+getName());
		Objects.requireNonNull(startMoveScannable, "'Start move' scannable has not been set for "+getName());
		Objects.requireNonNull(statusChecker, "Status checker has not been set");

		robotSetpointScannable.addIObserver(this::notifyIObservers);

		setConfigured(true);
	}

	@Override
	public void notifyIObservers(Object source, Object arg) {
		try {
			super.notifyIObservers(this, robotSetpointScannable.getPosition());
		} catch (DeviceException e) {
			logger.error("Problem trying to notify observers of {}", getName(), e);
		}
	}

	@Override
	public String[] getOutputFormat() {
		return robotSetpointScannable.getOutputFormat();
	}

	@Override
	public String[] getInputNames() {
		return robotSetpointScannable.getInputNames();
	}

	@Override
	public String[] getExtraNames() {
		return robotSetpointScannable.getExtraNames();
	}

	/**
	 * @return True if robot is busy moving - using {@link MecaStatusChecker#robotIsMoving()}
	 */
	@Override
	public boolean isBusy() throws DeviceException {
		logger.debug("is busy");
		return statusChecker.robotIsMoving();
	}

	/**
	 * Start robot move using the following steps :
	 *
	 * <li> Copy all the readback values to the setpoint values using the 'copyPositions' scannable
	 * (i.e. 'copy readbacks to setpoints' PV).
	 *
	 * <li> Apply the setpoint value(s) using the 'position' scannable
	 * (i.e. setpoint PV for theta1, theta2, pose X, pose Y etc.)
	 *
	 * <li> Start the robot move using 'startMove' scannable
	 * (e.g. 'move joints', 'move pose', or 'move linear' PV)
	 *
	 * A small sleep for {@link #getWaitTimeMs()}ms is done after copying setpoint values and after
	 * applying the new setpoint value to allow Epics records to update.
	 * @param position
	 */
	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		if (copyPositionsScannable != null) {
			logger.info("Copying current readback to demand positions");
			copyPositionsScannable.moveTo(1);
			// Copy all the readback values to the demand values
			waitForCaput();
		}
		logger.info("Setting {} to {}", robotSetpointScannable.getName(), position);
		robotSetpointScannable.moveTo(position);
		waitForCaput();

		logger.info("Starting robot move");
		startMoveScannable.moveTo(1.0);

		logger.info("Waiting {} ms for motion to start", waitTimeForMotionStart);
		waitForCaput(waitTimeForMotionStart);
		logger.info("Finished waiting for motion to start - robot status = {}", statusChecker.getRobotGripperStatusBits());
	}

	/**
	 * Wait for a short time (e.g. after applying value in Epics, to allow records to update).
	 */
	private void waitForCaput() {
		waitForCaput(waitTimeMs);
	}

	private void waitForCaput(long timeMs) {
		try {
			logger.debug("Sleep for {} ms", waitTimeMs);
			Thread.sleep(timeMs);
		} catch (InterruptedException e) {
		    Thread.currentThread().interrupt();
			logger.warn("Interrupted while sleeping", e);
		}
		logger.debug("Sleep finished");
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		if (robotSetpointScannable instanceof MultiPVScannable) {
			return ((MultiPVScannable)robotSetpointScannable).rawGetPosition();
		}
		return robotSetpointScannable.getPosition();
	}

	public Scannable getStartMoveScannable() {
		return startMoveScannable;
	}

	public void setStartMoveScannable(Scannable startMoveScannable) {
		this.startMoveScannable = startMoveScannable;
	}

	public Scannable getCopyPositionsScannable() {
		return copyPositionsScannable;
	}

	public void setCopyPositionsScannable(Scannable copyPositionsScannable) {
		this.copyPositionsScannable = copyPositionsScannable;
	}

	public Scannable getRobotSetpointScannable() {
		return robotSetpointScannable;
	}

	public void setRobotSetpointScannable(Scannable positionScannable) {
		this.robotSetpointScannable = positionScannable;
	}

	public MecaStatusChecker getStatusChecker() {
		return statusChecker;
	}

	/**
	 *
	 * @param statusChecker
	 */
	public void setStatusChecker(MecaStatusChecker statusChecker) {
		this.statusChecker = statusChecker;
	}

	/**
	 * Sleep time to use after applying a value, to allow Epics records time to update.
	 * (i.e. used after setting demand position and after starting robot move in {@link #rawAsynchronousMoveTo(Object)}.
	 * @return
	 */
	public long getWaitTimeMs() {
		return waitTimeMs;
	}

	public void setWaitTimeMs(long waitTimeMs) {
		this.waitTimeMs = waitTimeMs;
	}

	/**
	 * Time after starting the motion in {@link #rawAsynchronousMoveTo(Object)} to wait before continuing execution.
	 * @return
	 */
	public long getWaitTimeForMotionStart() {
		return waitTimeForMotionStart;
	}

	public void setWaitTimeForMotionStart(long waitTimeForMotionStart) {
		this.waitTimeForMotionStart = waitTimeForMotionStart;
	}
}
