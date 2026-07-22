/*-
 * Copyright © 2026 Diamond Light Source Ltd.
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

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.MotorStatus;
import gda.jython.InterfaceProvider;
import gda.jython.JythonServerFacade;
import uk.ac.diamond.daq.concurrent.Async;

public class ScannableMotorTimeoutRetry extends ScannableMotor {

	/** how long to wait for a motor move to complete before retrying the move */
	private double timeoutSecs = 120.0;

	/** Maximum number of attempts to make to move a motor */
	private int numRetries = 5;

	private double pollIntervalSecs = 0.2;

	private volatile boolean motorMoveLoopRunning = false;
	private Exception motorMoveLoopException = null;

	private static final Logger logger = LoggerFactory.getLogger(ScannableMotorTimeoutRetry.class);

	public ScannableMotorTimeoutRetry() {
	}

	public boolean isScanRunning() {
		return JythonServerFacade.getInstance().isScanRunning();
	}

	private long getCurrentTime() {
		return System.currentTimeMillis();
	}

	/**
	 * Run motor move loop in background thread, store any exception that gets thrown
	 * and re-throw in isBusy or waitWhileBusy.
	 *
	 * @param demandPosition
	 * @throws DeviceException
	 */
	private void runMotorMoveLoop(double demandPosition) throws DeviceException {

		if (motorMoveLoopRunning) {
			throw new DeviceException("Motor move loop is already running - can't run it again!");
		}

		logger.info("Starting thread to move motor to {}", demandPosition);

		motorMoveLoopRunning = true;
		motorMoveLoopException = null;

		// Run move-retry in background thread, store any exception that gets thrown,
		// so it can be re-thrown in 'isBusy' or 'waitWhileBusy'
		Async.execute(() -> {
			try {
				motorMoveLoopRunning = true;
				motorMoveLoop(demandPosition);
			} catch (DeviceException e) {
				logger.error("Problem running motor move-retry loop", e);
				motorMoveLoopException = e;
			} catch (InterruptedException e) {
				Thread.currentThread().interrupt();
				logger.error("Thread interrupted running motor move-retry loop", e);
				motorMoveLoopException = e;
			} finally {
				motorMoveLoopRunning = false;
			}
		});
	}

	/**
	 * Move motor to requested demandPosition.
	 * If the motor move takes more than {@link #timeoutSecs} seconds to complete, the move move will be stopped and tried again.
	 * This is repeated up to {@link #numRetries} times. If the move not complete after the retries, then a DeviceException
	 * is raised.
	 *
	 * @param demandPosition to move the motor to
	 * @throws DeviceException
	 * @throws InterruptedException
	 */
	private void motorMoveLoop(double demandPosition) throws DeviceException, InterruptedException {

		motorMoveLoopRunning = true;
		String timeoutMsg = String.format("%s motor move timeout after %.1f secs", getName(), timeoutSecs);
		boolean motorMoveFinished = false;
		int retryCount = 0;

		while (retryCount < numRetries && !motorMoveFinished) {
			retryCount += 1;

			// Stop the motor before trying to move it
			if (getMotor().getStatus() != MotorStatus.READY) {
				logger.debug("Stopping motor before next move");
				stop();
				logger.debug("Waiting for motor to stop");
				getMotor().waitWhileStatusBusy();
			}

			long moveStartTime = getCurrentTime();
			logger.debug("Moving {} to {} mm. Current position = {} mm", getName(), demandPosition, getPosition());

			getMotor().moveTo(demandPosition);
			motorMoveFinished = waitWhileMotorBusy(moveStartTime);

			logger.debug("Move finished. Current position = {}", getPosition());

			if (!motorMoveFinished) {
				String retryMsg = String.format("(attempt %d of %d)", retryCount, numRetries);
				String stateMsg = String.format("Current position = %.5f mm, demand position = %.5f mm", getPosition(), demandPosition);
				logger.warn("{} ({}). {}", timeoutMsg, retryMsg, stateMsg);
				InterfaceProvider.getTerminalPrinter().print(String.format("\tWarning : t%s. %s.%n\t%s", timeoutMsg, retryMsg, stateMsg));
			}
		}

		// Throw exception if number motor didn't complete successfully
		if (!motorMoveFinished) {
			throw new DeviceException(String.format("%s. Maximum number of retries reached (%s).", timeoutMsg, numRetries));
		}
	}

	/**
	 * Wait for motor move to finish, up to timeout limit.
	 * @param moveStartTime start time of motor move
	 * @return true if move completed successfully, false if move timeout out
	 * @throws InterruptedException
	 * @throws DeviceException
	 */
	private boolean waitWhileMotorBusy(long moveStartTime) throws InterruptedException, DeviceException {
		while (getMotor().getStatus() == MotorStatus.BUSY) {
			if (isScanRunning() && getCurrentTime() - moveStartTime > timeoutSecs * 1000L) {
				return false;
			}
			Thread.sleep((long) (pollIntervalSecs * 1000));
		}
		// move finished ok
		return true;
	}

	@Override
	public boolean isBusy() throws DeviceException {
		raiseExceptionIfPresent();
		return motorMoveLoopRunning;
	}

	@Override
	public void waitWhileBusy() throws InterruptedException, DeviceException {
		logger.debug("Waiting for {} motor move loop to complete", getName());
		while (isBusy()) {
			Thread.sleep((long) (pollIntervalSecs * 1000));
		}
		raiseExceptionIfPresent();
		super.waitWhileBusy();
	}

	private void raiseExceptionIfPresent() throws DeviceException {
		if (motorMoveLoopException != null) {
			throw new DeviceException("Problem running motor move loop", motorMoveLoopException.getMessage(),
					motorMoveLoopException);
		}
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		double demandPosition = ScannableUtils.objectToArray(position)[0];;
		logger.debug("Moving {} to {}. Current position = {}", getName(), demandPosition, getPosition());
		runMotorMoveLoop(demandPosition);
	}

	public double getTimeoutSecs() {
		return timeoutSecs;
	}

	public void setTimeoutSecs(double timeoutSecs) {
		this.timeoutSecs = timeoutSecs;
	}

	public double getPollIntervalSecs() {
		return pollIntervalSecs;
	}

	public void setPollIntervalSecs(double pollIntervalSecs) {
		this.pollIntervalSecs = pollIntervalSecs;
	}

	public int getNumRetries() {
		return numRetries;
	}

	public void setNumRetries(int numRetries) {
		this.numRetries = numRetries;
	}
}
