/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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

import static gda.device.robot.MecaRobotStatusBits.End_of_Block;
import static gda.device.robot.MecaRobotStatusBits.End_of_Movement;
import static gda.device.robot.MecaRobotStatusBits.Error;

import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableUtils;
import gda.factory.FindableBase;

/**
 * Utility class to interpret Meca 'robot status' and 'gripper status' words to determine the current state.
 * i.e. if moving or in error state etc. - see {@link #robotIsMoving()}, {@link #waitForRobotMove()}, {@link #checkErrorState()}.
 *
 * This class is used in {@link MecaRobotMover} and {@link MecaSampleHolderControl} scannables
 */
public class MecaStatusChecker extends FindableBase {

	private static final Logger logger = LoggerFactory.getLogger(MecaStatusChecker.class);

	private Scannable robotStatus;
	private Scannable gripperStatus;
	private long pollTimeMs = 250;
	private long sleepTimeMs = 500;

	/**
	 * Wait for {@link #getSleepTimeMs()} then wait while the robot is moving
	 * (i.e. until end of movement and end of block bits are both true)
	 * @throws DeviceException
	 */
	public void waitForMove() throws DeviceException {
		try {
			logger.info("Waiting {} ms for motion to start", sleepTimeMs);
			Thread.sleep(sleepTimeMs);
			waitForRobotMove();
			Thread.sleep(sleepTimeMs);
			waitForRobotMove();
		} catch (InterruptedException e) {
			logger.error("Interrupt while waiting for move to finish", e);
			Thread.currentThread().interrupt();
		}
	}

	public void waitForRobotMove() throws InterruptedException, DeviceException {
		logger.info("Waiting motion to finish", sleepTimeMs);
		while(robotIsMoving()) {
			Thread.sleep(pollTimeMs);
		}
	}

	/**
	 * Determine if robot is currently busy moving by examining the robot status word.
	 *
	 * @return True if 'end of block' and 'end of movement' bits are both false
	 * @throws DeviceException
	 */
	public boolean robotIsMoving() throws DeviceException {
		checkErrorState();
		List<MecaRobotStatusBits> statusBits = getRobotStatusBits();
		// Robot is moving if 'end of block' and 'end of movement' bits are not both 1
		return !(statusBits.contains(End_of_Movement) && statusBits.contains(End_of_Block));
	}

	/**
	 * Check error state of the robot and gripper
	 *
	 * @throws DeviceException if robot or gripper status bits contain error state
	 */
	public void checkErrorState() throws DeviceException {
		List<MecaRobotStatusBits> statusBits = getRobotStatusBits();
		logger.debug("Robot status : {}", statusBits);
		String errorMessage = "";
		if (statusBits.contains(Error)) {
			errorMessage += "Robot is in Error state : "+statusBits.toString()+". ";
		}

		List<MecaRobotGripperStatusBits> gripperStatusBits = getRobotGripperStatusBits();
		logger.debug("Gripper status : {}", gripperStatusBits);
		if (gripperStatusBits.contains(MecaRobotGripperStatusBits.Error) ||
				gripperStatusBits.contains(MecaRobotGripperStatusBits.Overload)) {
			errorMessage += "Gripper is in error state : "+gripperStatusBits.toString()+".";
		}
		if (!errorMessage.isEmpty()) {
			throw new DeviceException(errorMessage);
		}
	}

	/**
	 * Create list of {@link MecaRobotStatusBits} corresponding to each bit current set in the 'robot status' word.
	 * @return
	 * @throws DeviceException
	 */
	public List<MecaRobotStatusBits> getRobotStatusBits() throws DeviceException {
		int statusWord = getInteger(robotStatus);
		return Stream.of(MecaRobotStatusBits.values())
				.filter(b -> b.bitIsSet(statusWord))
				.collect(Collectors.toList());
	}

	/**
	 * Create list of {@link MecaRobotGripperStatusBits} corresponding to each bit current set in the 'gripper status' word.
	 * @return
	 * @throws DeviceException
	 */
	public List<MecaRobotGripperStatusBits> getRobotGripperStatusBits() throws DeviceException {
		int statusWord = getInteger(gripperStatus);
		return Stream.of(MecaRobotGripperStatusBits.values())
				.filter(b -> b.bitIsSet(statusWord))
				.collect(Collectors.toList());
	}

	private int getInteger(Scannable scannable) throws DeviceException {
		double[] position = ScannableUtils.getCurrentPositionArray(scannable);
		return (int) Math.floor(position[0]);
	}

	public Scannable getRobotStatus() {
		return robotStatus;
	}

	public void setRobotStatus(Scannable robotStatus) {
		this.robotStatus = robotStatus;
	}

	public Scannable getGripperStatus() {
		return gripperStatus;
	}

	public void setGripperStatus(Scannable gripperStatus) {
		this.gripperStatus = gripperStatus;
	}
	/**
	 * Sleep time to use after setting a value in Epics to allow Epics record to be updated.
	 * @return time (milliseconds)
	 */
	public long getSleepTimeMs() {
		return sleepTimeMs;
	}

	public void setSleepTimeMs(long sleepTimeMs) {
		this.sleepTimeMs = sleepTimeMs;
	}

	/**
	 * Time interval to check robot status when waiting for robot move to finish.
	 * @return time (milliseconds)
	 */
	public long getPollTimeMs() {
		return pollTimeMs;
	}

	public void setPollTimeMs(long pollTimeMs) {
		this.pollTimeMs = pollTimeMs;
	}

}

