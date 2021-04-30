/*-
 * Copyright © 2016 Diamond Light Source Ltd.
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

import java.io.IOException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.ContinuousParameters;
import gda.device.DeviceException;
import gda.device.trajectoryscancontroller.TrajectoryScanController;
import gda.device.trajectoryscancontroller.TrajectoryScanController.ExecuteState;
import gda.device.trajectoryscancontroller.TrajectoryScanController.ExecuteStatus;
import gda.device.zebra.ZebraGatePulsePreparer;
import gda.device.zebra.controller.Zebra;
import gda.factory.FactoryException;
import gda.jython.InterfaceProvider;
import gda.scan.TrajectoryScanPreparer;
import gda.scan.TurboXasMotorParameters;
import gda.scan.TurboXasParameters;

/**
 * Continuous Scannable for Turbo slit position
 * @since 19/5/2016
 */
public class TurboXasScannable extends ScannableMotor implements ContinuouslyScannable {

	private static final Logger logger = LoggerFactory.getLogger(TurboXasScannable.class);

	private Zebra zebraDevice1;
	private Zebra zebraDevice2;

	private boolean twoWayScan;
	private int sweepNumber = 0;

	private ContinuousParameters continuousParameters;
	private TurboXasMotorParameters motorParameters;

	private enum ScanParametersType { NONE, ERROR, CONTINUOUSPARAMS, TURBOXASMOTORPARAMS };
	private ScanParametersType lastParameterSetType;

	private boolean configZebraDuringPrepare;
	private boolean armZebraAtScanStart;
	private boolean disarmZebraAtScanEnd;

	private TrajectoryScanPreparer trajectoryScanPreparer;
	private ZebraGatePulsePreparer zebraGatePulsePreparer;

	private double motorSpeedBeforeScan;

	private long trajectoryScanInitialWaitTimeMs = 1000;

	private Double rampDistance; /** Motor ramp distance when doing scan based on ContinuousParameters */
	private Double maxMotorSpeed; /** Maximum motor speed when doing scan based on ContinuousParameters */

	public TurboXasScannable() {
	}

	@Override
	public void configure() throws FactoryException {
		if (isConfigured()) {
			return;
		}
		super.configure();
		if (zebraGatePulsePreparer==null && zebraDevice1!=null) {
			zebraGatePulsePreparer=new ZebraGatePulsePreparer(zebraDevice1);
		}
		setConfigured(true);
	}

	/**
	 * Set Continuous parameters and create corresponding TurboXasMotorParameters used for doing scan.
	 */
	@Override
	public void setContinuousParameters(ContinuousParameters continuousParameters) {
		this.continuousParameters = continuousParameters;
		motorParameters = getMotorParametersFromContinuous(continuousParameters);
		lastParameterSetType = ScanParametersType.CONTINUOUSPARAMS;
	}

	@Override
	public ContinuousParameters getContinuousParameters() {
		return continuousParameters;
	}

	public void setMotorParameters(TurboXasMotorParameters motorParameters) {
		this.motorParameters = motorParameters;
		lastParameterSetType = ScanParametersType.TURBOXASMOTORPARAMS;
	}

	public TurboXasMotorParameters getMotorParameters() {
		return motorParameters;
	}

	public Zebra getZebraDevice() {
		return zebraDevice1;
	}

	public void setZebraDevice(Zebra zebraDevice) {
		this.zebraDevice1 = zebraDevice;
	}

	public Zebra getZebraDevice2() {
		return zebraDevice2;
	}

	public void setZebraDevice2(Zebra zebraDevice2) {
		this.zebraDevice2 = zebraDevice2;
	}

	public boolean isTwoWayScan() {
		return twoWayScan;
	}

	public void setTwoWayScan(boolean twoWayScan) {
		this.twoWayScan = twoWayScan;
	}

	/** Make TurboXasMotorParameters object from ContinousParameters.
	 *
	 * @param continuousParameters
	 * @return TurboXasMotorParameters
	 */
	private TurboXasMotorParameters getMotorParametersFromContinuous(ContinuousParameters continuousParameters) {
		TurboXasParameters scanParams = new TurboXasParameters(continuousParameters);
		TurboXasMotorParameters motorParams = scanParams.getMotorParameters();
		if (rampDistance != null && rampDistance > 0) {
			motorParams.setMotorTimeToVelocity(0.0);
			motorParams.setMotorStabilisationDistance(rampDistance);
		}
		motorParams.setMotorParametersForTimingGroup(0);
		/** Replace the return motor speed calculated by {@link TurboXasMotorParameters#setMotorParametersForTimingGroup} from 'time between spectra' */
		if (maxMotorSpeed != null && maxMotorSpeed > 0) {
			motorParams.setReturnMotorSpeed(maxMotorSpeed);
		}
		return motorParams;
	}

	/**
	 * Configure Arm, Gate, Pulse, Setup parts of Zebra ('PC' part of Zebra edm screen)
	 * @throws Exception
	 */
	public void configureZebra() throws Exception {
		if (twoWayScan && zebraDevice2 != null) {
			// Setup the zebras for bi-directional scan

			// Calculate number of gates for each zebra :
			int numSpectra = motorParameters.getScanParameters().getTotalNumSpectra();
			int numGatesZebra1 = (int) Math.floor(numSpectra/2.0) + numSpectra%2;
			int numGatesZebra2 = numSpectra - numGatesZebra1;

			// Set up zebra1 - like normal scan, exception with reduced number of gates
			zebraGatePulsePreparer.setZebraDevice(zebraDevice1);
			zebraGatePulsePreparer.setFromParameters(motorParameters);
			zebraGatePulsePreparer.setNumGates(numGatesZebra1);
			zebraGatePulsePreparer.configureZebra();

			// Set up zebra2 - like zebra1, except scan start position is scan end position, and scan direction is reversed.
			zebraGatePulsePreparer.setZebraDevice(zebraDevice2);
			// start position for reverse direction is end position of last captured pulse in forwards direction :
			double encoderPositionRange = motorParameters.getNumReadoutsForScan()*motorParameters.getPositionStepsize();
			double reverseStartPosition = motorParameters.getScanStartPosition() + encoderPositionRange;
			zebraGatePulsePreparer.setScanStartMotorPosition(reverseStartPosition);
			zebraGatePulsePreparer.setScanMotorRange(-1.0*encoderPositionRange);
			zebraGatePulsePreparer.setNumGates(numGatesZebra2);
			zebraGatePulsePreparer.configureZebra();
		} else {
			zebraGatePulsePreparer.setZebraDevice(zebraDevice1);
			zebraGatePulsePreparer.setFromParameters(motorParameters);
			zebraGatePulsePreparer.configureZebra();
		}
	}

	public void setConfigZebraDuringPrepare( boolean configZebraDuringPrepare) {
		this.configZebraDuringPrepare = configZebraDuringPrepare;
	}

	public void setArmZebraAtScanStart( boolean armZebraAtScanStart ) {
		this.armZebraAtScanStart = armZebraAtScanStart;
	}

	public void setDisarmZebraAtScanEnd( boolean disarmZebraAtScanEnd ) {
		this.disarmZebraAtScanEnd = disarmZebraAtScanEnd;
	}

	private double getEndPositionForSweep() {
		double position = sweepNumber%2 == 0 ? motorParameters.getStartPosition() : motorParameters.getEndPosition();
		logger.debug("End position for sweep {} = {}", sweepNumber, position);
		return position;
	}

	@Override
	public void prepareForContinuousMove() {
		try {
			if (twoWayScan) {
				if (sweepNumber==0) {
					logger.info("Moving motor to initial run-up position for two way scan : {}", getEndPositionForSweep());
					this.setSpeed(motorParameters.getScanMotorSpeed());
					asynchronousMoveTo(getEndPositionForSweep());
					sweepNumber++;
				}  else {
					double timeForSpectrum = motorParameters.getCurrentTimingGroup().getTimePerSpectrum();
					double timeForRunups = motorParameters.getTotalTimeForScan() - timeForSpectrum;
					double timeBetweenSpectra = motorParameters.getCurrentTimingGroup().getTimeBetweenSpectra();
					double sleepTime = Math.max(0, timeBetweenSpectra - timeForRunups);
					if (sleepTime > 0) {
						logger.info("Sleeping for {} ms before starting next sweep of two way scan", sleepTime*1000);
						Thread.sleep((long)(sleepTime * 1000));
					}
				}
			} else {
				logger.info("Moving motor to initial run-up position : {}", motorParameters.getStartPosition());
				this.setSpeed(motorParameters.getReturnMotorSpeed());
				asynchronousMoveTo(motorParameters.getStartPosition());
			}

			// to help reduce 'dead time', set motor speed just before starting move to final position
			// instead of setting it here after waiting for motor to move to initial position.

			if (configZebraDuringPrepare) {
				logger.info("Configuring zebra gate, pulse parameters ...");
				configureZebra();
			} else
				logger.info("Skipping zebra configure");

		}
		catch(Exception e) {
			logger.warn("Exception in prepareForContinuousMove", e);
		}
	}

	/**
	 * Return number of zebra readouts used for scan.
	 */
	@Override
	public int getNumberOfDataPoints() {
		if (lastParameterSetType==ScanParametersType.CONTINUOUSPARAMS) {
			return continuousParameters.getNumberDataPoints();
		} else {
			return zebraGatePulsePreparer.getNumReadoutsForScan();
		}
	}

	public void armZebra() throws Exception {
		logger.info("Arming Zebra1");
		zebraDevice1.reset();
		zebraDevice1.pcArm();

		if (twoWayScan && zebraDevice2 != null) {
			logger.info("Arming Zebra2");
			zebraDevice2.reset();
			zebraDevice2.pcArm();
		}
	}

	public void disarmZebra() throws Exception {
		logger.info("Disarming Zebra1");
		zebraDevice1.pcDisarm();

		if (twoWayScan && zebraDevice2 != null) {
			logger.info("Disarming Zebra2");
			zebraDevice2.pcDisarm();
		}
	}

	@Override
	public void performContinuousMove() throws DeviceException {
		try {
			if ( armZebraAtScanStart ) {
				logger.info("Arming Zebra(s) at start of scan");
				armZebra();
			} else {
				logger.info("Skipping arm at scan start");
			}

			while (isBusy()) {
				logger.info("Waiting for turbo slit to finish moving to runup position");
				Thread.sleep(20);
			}

			double finalPosition = motorParameters.getEndPosition();
			if (twoWayScan) {
				logger.info("Using final motor position for two way scan (sweep number = {})", sweepNumber);
				finalPosition = getEndPositionForSweep();
				sweepNumber++;
			}

			this.setSpeed(motorParameters.getScanMotorSpeed());
			logger.info("Turbo slit move started : final position = {}", finalPosition);
			asynchronousMoveTo(finalPosition);

		} catch (Exception e) {
			logger.error("Exception in performContinuousMove", e);
			throw new DeviceException(e.getMessage(), e);
		}
	}

	@Override
	public void continuousMoveComplete() throws DeviceException {
		// Use rough estimate of how long motor takes for move for max wait time
		double maxWaitTime = 2.0*motorParameters.getScanPositionRange()/motorParameters.getScanMotorSpeed();
		try {
			logger.info("Waiting for Turbo slit to finish move at end of scan");
			waitWhileBusy(maxWaitTime);
		} catch (DeviceException e) {
			// Timeout
			logger.error("DeviceException while waiting for Turbo slit to finish moving at end of scan "+e+"\n --- Stopping motor" );
			stop();
		} catch (InterruptedException e) {
			// Scan is aborted for some other reason - rethrow as DeviceException
			logger.error("InterruptedException while waiting for Turbo slit to finish moving at end of scan ", e);
			throw new DeviceException(e.getMessage(), e);
		}

		if ( disarmZebraAtScanEnd ) {
			try {
				logger.info("Disarming Zebra(s) at end of scan");
				disarmZebra();
			} catch (Exception e) {
				logger.error("Exception while trying to disarm Zebra at end of scan", e);
				throw new DeviceException(e.getMessage(), e);
			}
		}else {
			logger.info("Skipping disarm at scan end");
		}
	}

	@Override
	public double calculateEnergy(int frameIndex) throws DeviceException {
		double position = calculateEnergy(frameIndex);
		if (motorParameters.getScanParameters().isUsePositionsForScan()) {
			return position;
		}
		return motorParameters.getEnergyForPosition(position);
	}

	public double calculatePosition(int frameIndex) {
		if (motorParameters.getScanPositionRange() < 0) {
			frameIndex *= -1;
		}
		return motorParameters.getScanStartPosition() + frameIndex*motorParameters.getPositionStepsize();
	}

	/**
	 *  Reset Zebra arm, disarm and configure parameters to default values (i.e. all true)
	 */
	public void resetZebraArmConfigFlags() {
		armZebraAtScanStart = true;
		disarmZebraAtScanEnd = true;
		configZebraDuringPrepare = true;
	}

	public ZebraGatePulsePreparer makeDefaultZebraGatePulsePreparer() {
		ZebraGatePulsePreparer preparer = new ZebraGatePulsePreparer(zebraDevice1);
		preparer.setMotorStabilisationDistance(0.1);
		preparer.setPositionTriggerEncoder(Zebra.PC_ENC_ENC3);
		preparer.setTtlOutputPort(31); // set TTL output 1 to 'PC_PULSE'
		preparer.setPositionTriggerTimeUnits(Zebra.PC_TIMEUNIT_SEC);
		preparer.setPulseWidthFraction(0.5);
		return preparer;
	}


	@Override
	public void atScanStart() {
		resetZebraArmConfigFlags();
		sweepNumber = 0;
		try {
			motorSpeedBeforeScan = this.getSpeed();
		} catch (DeviceException e) {
			logger.error("Problem saving motor speed at scan start", e);
		}

		// Create default zebra gate/pulse settings preparer if one has not already been set.
		if (zebraGatePulsePreparer==null) {
			logger.info("Creating default ZebraGatePulsePreparer");
			zebraGatePulsePreparer = new ZebraGatePulsePreparer(zebraDevice1);
		}
	}

	@Override
	public void atScanEnd() {
		try {
			logger.info("Disarming Zebra(s) at end of scan");
			disarmZebra();
		} catch (Exception e) {
			logger.error("Problem disarming zebra at scan end", e);
		}

		if (motorSpeedBeforeScan > 0) {
			try {
				this.setSpeed(motorSpeedBeforeScan);
			} catch (DeviceException e) {
				logger.error("Problem changing motor speed back to original value at scan end", e);
			}
		}

		resetZebraArmConfigFlags();
	}

	@Override
	public void atCommandFailure() {
		atScanEnd();
	}

	@Override
	public void stop() throws DeviceException {
		super.stop();
		atScanEnd();
	}

	public ZebraGatePulsePreparer getZebraGatePulsePreparer() {
		return zebraGatePulsePreparer;
	}

	public void setZebraGatePulsePreparer(ZebraGatePulsePreparer zebraTriggerPreparer) {
		this.zebraGatePulsePreparer = zebraTriggerPreparer;
	}

	public TrajectoryScanPreparer getTrajectoryScanPreparer() {
		return trajectoryScanPreparer;
	}

	public void setTrajectoryScanPreparer(TrajectoryScanPreparer trajectoryScanPrepaper) {
		this.trajectoryScanPreparer = trajectoryScanPrepaper;
	}

	/**
	 * Move motor to a position by doing a trajectory scan with a single point in the profile.
	 * @param position
	 * @param timeForMove
	 * @throws Exception
	 */
	public void moveWithTrajectoryScan(double position, double timeForMove) throws Exception {
		trajectoryScanPreparer.setDefaults();
		trajectoryScanPreparer.clearTrajectoryLists();
		trajectoryScanPreparer.addPointToTrajectory(position, timeForMove, 3);
		trajectoryScanPreparer.sendProfileValues();
		trajectoryScanPreparer.setBuildProfile();
		trajectoryScanPreparer.setExecuteProfile();
	}

	/**
	 * Wait for a trajectory scan to execute.
	 * @return false if trajectory scan failed to execute successfully (i.e. if execute status != 'success' after scan finishes)
	 * @param controller
	 * @throws IOException
	 * @throws InterruptedException
	 */
	public boolean waitForTrajectoryScan() throws IOException, InterruptedException {
		logger.debug("Waiting for trajectory scan to execute");
		TrajectoryScanController controller = trajectoryScanPreparer.getTrajectoryScanController();

		// Give it at least a second (in case trajectory hasn't quite started yet)...
		Thread.sleep(trajectoryScanInitialWaitTimeMs);

		// Wait while trajectory scan runs...
		while (controller.getExecuteState() == ExecuteState.EXECUTING) {
			Thread.sleep(500);
		}

		// Output some info on trajectory scan final execution state
		logger.debug("Trajectory scan finished. Execute state = {}, percent complete = {}",
				controller.getExecuteState(), controller.getScanPercentComplete());

		if (controller.getScanPercentComplete() < 100 && controller.getExecuteStatus() != ExecuteStatus.SUCCESS) {
			String message = "\nTrajectory scan failed to execute correctly. Check Edm screen for more information";
			logger.warn(message);
			InterfaceProvider.getTerminalPrinter().print(message);
			return false;
		}
		return true;
	}

	/**
	 * Build a trajectory scan by building profile points from the currently stored timing groups and motor parameters.
	 * Calls {@link TrajectoryScanPreparer#addPointsForTimingGroups(TurboXasMotorParameters)}.
	 * @throws Exception
	 */
	public void prepareTrajectoryScan() throws Exception {
		trajectoryScanPreparer.setDefaults();
		trajectoryScanPreparer.setTwoWayScan(twoWayScan);
		trajectoryScanPreparer.addPointsForTimingGroups(motorParameters);

		// send profile points to Epics trajectory scan, building and appending as necessary
		TrajectoryScanController controller = trajectoryScanPreparer.getTrajectoryScanController();
		if (controller.getExecuteState() != ExecuteState.DONE) {
			throw new Exception("Problem building trajectory scan profile - scan is already runninng!");
		}
		trajectoryScanPreparer.sendAppendProfileValues();
	}

	/**
	 * Execute the currently built trajectory scan
	 * @throws Exception
	 */
	public void executeTrajectoryScan() throws Exception {
		trajectoryScanPreparer.getTrajectoryScanController().setExecuteProfile();
	}

	public long getTrajectoryScanInitialWaitTimeMs() {
		return trajectoryScanInitialWaitTimeMs;
	}

	/**
	 * Set initial wait time used in {@link #waitForTrajectoryScan()} before looking at PVs to determine trajectory scan state.
	 * @param trajectoryScanExtraWaitTime wait time (milliseconds)
 	 */
	public void setTrajectoryScanInitialWaitTimeMs(long trajectoryScanInitialWaitTimeMs) {
		this.trajectoryScanInitialWaitTimeMs = trajectoryScanInitialWaitTimeMs;
	}

	public double getRampDistance() {
		return rampDistance;
	}

	/** Motor runup distance to use for scans based on ContinuousParameters */
	public void setRampDistance(double rampDistance) {
		this.rampDistance = rampDistance;
	}

	public double getMaxMotorSpeed() {
		return maxMotorSpeed;
	}

	/** Maximum motor speed for scans based on ContinuousParameters (used when moving to scan runup postion)*/
	public void setMaxMotorSpeed(double maxMotorSpeed) {
		this.maxMotorSpeed = maxMotorSpeed;
	}
}
