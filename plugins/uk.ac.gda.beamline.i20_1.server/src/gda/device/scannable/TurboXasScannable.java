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

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.ContinuousParameters;
import gda.device.DeviceException;
import gda.device.zebra.ZebraAreaDetectorPreparer;
import gda.device.zebra.ZebraGatePulsePreparer;
import gda.device.zebra.controller.Zebra;
import gda.factory.FactoryException;
import gda.scan.TrajectoryScanPreparer;
import gda.scan.TurboXasMotorParameters;
import gda.scan.TurboXasParameters;

/**
 * Continuous Scannable for Turbo slit position
 * @since 19/5/2016
 */
public class TurboXasScannable extends ScannableMotor implements ContinuouslyScannable {

	private static final Logger logger = LoggerFactory.getLogger(TurboXasScannable.class);

	private Zebra zebraDevice;

	private ContinuousParameters continuousParameters;
	private TurboXasMotorParameters motorParameters;

	private enum ScanParametersType { NONE, ERROR, CONTINUOUSPARAMS, TURBOXASMOTORPARAMS };
	private ScanParametersType lastParameterSetType;

	private boolean configZebraDuringPrepare;
	private boolean armZebraAtScanStart;
	private boolean disarmZebraAtScanEnd;

	private boolean useAreaDetector = false;
	private ZebraAreaDetectorPreparer zebraAreaDetectorPreparer;
	private TrajectoryScanPreparer trajectoryScanPreparer;

	private ZebraGatePulsePreparer zebraGatePulsePreparer;
	private double motorSpeedBeforeScan;

	public TurboXasScannable() {
	}

	@Override
	public void configure() throws FactoryException {
		super.configure();
		if (zebraGatePulsePreparer==null && zebraDevice!=null) {
			zebraGatePulsePreparer=new ZebraGatePulsePreparer(zebraDevice);
		}
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
		return zebraDevice;
	}

	public void setZebraDevice(Zebra zebraDevice) {
		this.zebraDevice = zebraDevice;
	}

	/** Make TurboXasMotorParameters object from ContinousParameters.
	 *
	 * @param continuousParameters
	 * @return TurboXasMotorParameters
	 */
	private TurboXasMotorParameters getMotorParametersFromContinuous(ContinuousParameters continuousParameters) {
		TurboXasParameters scanParams = new TurboXasParameters(continuousParameters);
		TurboXasMotorParameters motorParams = scanParams.getMotorParameters();
		motorParams.setMotorParametersForTimingGroup(0);
		return motorParams;
	}

	/**
	 * Configure Arm, Gate, Pulse, Setup parts of Zebra ('PC' part of Zebra edm screen)
	 * @throws Exception
	 */
	public void configureZebra() throws Exception {
		zebraGatePulsePreparer.setZebraDevice(zebraDevice);
		zebraGatePulsePreparer.setFromParameters(motorParameters);
		zebraGatePulsePreparer.configureZebra();

		// Configure the area detector settings
		if (useAreaDetector && zebraAreaDetectorPreparer != null) {
			int totNumReadoutsForScan = zebraGatePulsePreparer.getNumReadoutsForScan() * zebraGatePulsePreparer.getNumGates();
			zebraAreaDetectorPreparer.configure(totNumReadoutsForScan);
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

	@Override
	public void prepareForContinuousMove() {
		try {
			logger.info("Moving motor to initial run-up position ("+motorParameters.getStartPosition()+")");
			this.setSpeed(motorParameters.getReturnMotorSpeed());
			asynchronousMoveTo(motorParameters.getStartPosition());
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
		return zebraGatePulsePreparer.getNumReadoutsForScan();
	}


	@Override
	public void performContinuousMove() throws DeviceException {
		try {
			if ( armZebraAtScanStart ) {
				logger.info("Arming Zebra");
				zebraDevice.reset();
				zebraDevice.pcArm(); // should wait until armed, but seems to wait for ever

				// Arm the area detector
				if (useAreaDetector && zebraAreaDetectorPreparer != null) {
					zebraAreaDetectorPreparer.arm();
				}

			} else
				logger.info("Skipping arm at scan start");

			while (isBusy()) {
				logger.info("Waiting for turbo slit to finish moving to runup position");
				Thread.sleep(20);
			}

			logger.info("Turbo slit move started (final position = "+motorParameters.getEndPosition()+")");
			this.setSpeed(motorParameters.getScanMotorSpeed());
			asynchronousMoveTo(motorParameters.getEndPosition() );

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
				logger.info("Disarming Zebra at end of scan");
				zebraDevice.pcDisarm();
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
		return motorParameters.getEnergyForPosition(calculatePosition(frameIndex));
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
		ZebraGatePulsePreparer preparer = new ZebraGatePulsePreparer(zebraDevice);
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

		try {
			motorSpeedBeforeScan = this.getSpeed();
		} catch (DeviceException e) {
			logger.error("Problem saving motor speed at scan start", e);
		}

		// Create default zebra gate/pulse settings preparer if one has not already been set.
		if (zebraGatePulsePreparer==null) {
			logger.info("Creating default ZebraGatePulsePreparer");
			zebraGatePulsePreparer = new ZebraGatePulsePreparer(zebraDevice);
		}
	}

	@Override
	public void atScanEnd() {
		try {
			logger.info("Disarming Zebra at end of scan");
			zebraDevice.pcDisarm();
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

	public void setUseAreaDetector(boolean useAreaDetector) throws Exception {
		this.useAreaDetector = useAreaDetector;
		if (useAreaDetector) {
			zebraAreaDetectorPreparer = makeZebraAreaDetectorPreparer();
		} else
			zebraAreaDetectorPreparer = null;
	}

	public void setAreaDetectorPreparer(ZebraAreaDetectorPreparer preparer) {
		zebraAreaDetectorPreparer = preparer;
		if (preparer != null) {
			useAreaDetector = true;
		} else {
			useAreaDetector = false;
		}
	}

	public ZebraAreaDetectorPreparer getAreaDetectorPreparer() {
		return zebraAreaDetectorPreparer;
	}

	/** Make default area detector preparer for i20-1 zebra
	 * This is is for testing purposes only, so set hdf file path to the tmp directory.
	 * To change how it's set up (e.g. in script), just make
	 * a new ZebraAreaDector object and pass it in via. {@link #setAreaDetectorPreparer(ZebraAreaDetectorPreparer)}.
	 */
	private ZebraAreaDetectorPreparer makeZebraAreaDetectorPreparer() throws Exception {
		String zebraPv = zebraDevice.getZebraPrefix();
		String dataDir = "/dls/i20-1/data/2016/cm14479-4/tmp/";
		String fileName = "test";
		ZebraAreaDetectorPreparer preparer = new ZebraAreaDetectorPreparer(zebraPv);
		preparer.setFileDirectory(dataDir);
		preparer.setFilename(fileName);
		preparer.setCamPvSuffix(""); // Normal area detectors use "CAM:"
		preparer.setHdfPvSuffix("HDF:"); // NB Normal area detectors use "HDF5:"
		preparer.setFilenameTemplate("%s%s%d.hdf");
		return preparer;
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
}
