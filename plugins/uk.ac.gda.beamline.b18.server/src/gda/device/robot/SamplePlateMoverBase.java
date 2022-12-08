/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.scannable.ScannableBase;
import gda.factory.FactoryException;
import gda.jython.InterfaceProvider;
import uk.ac.diamond.daq.concurrent.Async;

public abstract class SamplePlateMoverBase extends ScannableBase implements SamplePlateMover  {

	private static final Logger logger = LoggerFactory.getLogger(SamplePlateMoverBase.class);

	private volatile MotionState motionState;
	private volatile MotorSequence currentMotorSequence;

	/** State of the gripper used to hold sample plate */
	public enum GripperState {OPEN, CLOSE}

	/** State during and after a {@link MotorSequence} has run */
	public enum MotionState {IDLE, IN_PROGRESS, ERROR}

	/** Types of motor move sequences that can take place */
	public enum MotorSequence {LOAD_SAMPLE, UNLOAD_SAMPLE, MOVE_TO_BEAM}

	private volatile Optional<DeviceException> moveException = Optional.empty();

	@Override
	public void configure() throws FactoryException {
		if (!isConfigured()) {
			inputNames = new String[] {};
		}
		super.configure();
	}

	@Override
	public void performMotion(MotorSequence motion, String samplePlateName) throws DeviceException {
		if (motionState == MotionState.IN_PROGRESS) {
			logger.warn("Cannot run performMotion again - motion {} already in progress", currentMotorSequence);
			return;
		}
		runMotion(motion, samplePlateName);
	}

	private void runMotion(MotorSequence motion, String samplePlateName) throws DeviceException {
		try {
			logger.info("Starting to run {} motion", motion);
			currentMotorSequence = motion;
			motionState = MotionState.IN_PROGRESS;
			switch(motion) {
			case LOAD_SAMPLE :
				loadPlate(samplePlateName);
				break;
			case UNLOAD_SAMPLE :
				unloadPlate();
				break;
			case MOVE_TO_BEAM :
				moveToBeam();
				break;
			}
			motionState = MotionState.IDLE;
		} catch (DeviceException e) {
			motionState = MotionState.ERROR;
			throw e;
		}
	}

	@Override
	public void asynchronousMoveTo(Object position) throws DeviceException {
		if (motionState == MotionState.IN_PROGRESS) {
			logger.warn("Cannot load sample plate {} - motion {} already in progress", position.toString(), currentMotorSequence);
			return;
		}

		// make sure in_progress is set, so isBusy returns true *before* starting the run thread (to avoid race condition)
		// and ensure isBusy returns true immediately in parent moveTo method.
		motionState = MotionState.IN_PROGRESS;

		moveException = Optional.empty();
		Async.execute(() -> {
			try {
				String samplePlateName = position.toString();
				runMotion(MotorSequence.LOAD_SAMPLE, samplePlateName);
				performMotion(MotorSequence.MOVE_TO_BEAM, samplePlateName);
			} catch (DeviceException e) {
				logger.error("Problem performing {} motion : {}", currentMotorSequence, e.getMessage());
				printConsoleMessage("Problem performing "+currentMotorSequence+" motion : "+e.getMessage());
				// Store the exception so it can be rethrown in the main thread by 'isBusy' method
				moveException = Optional.of(e);
			}
		});
	}

	@Override
	public boolean isBusy() throws DeviceException {
		if (moveException.isPresent()) {
			throw moveException.get();
		}
		return getMotionState() == MotionState.IN_PROGRESS;
	}

	/**
	 * The last motor sequence that was run - one of the values in {@link MotorSequence} enum.
	 * @return
	 */
	public MotorSequence getMotorSequence() {
		return currentMotorSequence;
	}

	/**
	 * Current state of motion - one of {@link MotionState} (i.e. in progress, completed or error).
	 * @return
	 */
	public MotionState getMotionState() {
		return motionState;
	}

	protected void printConsoleMessage(String message) {
		InterfaceProvider.getTerminalPrinter().print(message);
	}
}
