/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

import java.util.Date;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.epics.connection.EpicsChannelManager;
import gda.epics.connection.EpicsController;
import gda.epics.connection.InitializationListener;
import gda.factory.FactoryException;
import gda.jython.InterfaceProvider;
import gov.aps.jca.CAException;
import gov.aps.jca.Channel;
import gov.aps.jca.TimeoutException;

/**
 * For B18 - this will test the mono temperature at regular points in a scan and will pause until it has colled below
 * some level before resuming.
 */
public class MonoCoolScannable extends ScannableBase implements InitializationListener {

	private static final Logger logger = LoggerFactory.getLogger(MonoCoolScannable.class);

	boolean pauseAtEachPoint = true;
	boolean pauseAtEachLine = true;
	boolean pauseAtScanStart = true;
	double temperatureLimit = 115;
	double temperatureCoolLevel = 100;
	double coolingTimeout = 1800; // in seconds
	String motorTempPV = "";
	EpicsController controller;
	EpicsChannelManager channelManager;
	Channel temperaturePV;

	public MonoCoolScannable() {
		this.setInputNames(new String[0]);
		this.setExtraNames(new String[0]);
		this.setOutputFormat(new String[0]);
	}

	@Override
	public void configure() throws FactoryException {
		if (isConfigured()) {
			return;
		}
		if (motorTempPV == null || motorTempPV.isEmpty()) {
			throw new FactoryException(getName() + " cannot configure as the motorTempPV is not defined.");
		}

		controller = EpicsController.getInstance();
		channelManager = new EpicsChannelManager(this);
		try {
			temperaturePV = channelManager.createChannel(motorTempPV, false);
		} catch (Exception e) {
			throw new FactoryException(getName() + " had CAException during configure", e);
		}
		setConfigured(true);
	}


	@Override
	public void initializationCompleted() {
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		// do nothing
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		return null;
	}

	@Override
	public void atPointStart() throws DeviceException {
		try {
			if (pauseAtEachPoint && temperaturePV != null && temperatureOverLimit()){
				waitUnitTemperatureBelowLimit();
			}
		} catch (Exception e) {
			throw new DeviceException(getName() + " exception in atPointStart",e);
		}
	}


	@Override
	public void atScanLineStart() throws DeviceException {
		try {
			if (pauseAtEachLine && temperaturePV != null && temperatureOverLimit()){
				waitUnitTemperatureBelowLimit();
			}
		} catch (Exception e) {
			throw new DeviceException(getName() + " exception in atScanLineStart",e);
		}

	}

	@Override
	public void atScanStart() throws DeviceException {
		try {
			if (pauseAtScanStart && temperaturePV != null && temperatureOverLimit()){
				waitUnitTemperatureBelowLimit();
			}
		} catch (Exception e) {
			throw new DeviceException(getName() + " exception in atScanStart",e);
		}
	}

	private void waitUnitTemperatureBelowLimit() throws DeviceException {
		try {
			logger.info("bragg motor too hot - waiting for it to cool to " + temperatureCoolLevel +"C...");
			while (getCurrentTemp() > temperatureCoolLevel){
				Long start = new Date().getTime();
				Thread.sleep(10000);
				// stop waiting if Scan has been asked to finish
				if (InterfaceProvider.getCurrentScanController().isFinishEarlyRequested()){
					return;
				}
				if ((new Date().getTime() - start) > (coolingTimeout * 1000)) {
					String message = getName() + " had timeout waiting for motor to cool so will abort scan";
					logger.error(message);
					throw new DeviceException(message);
				}
			}
		} catch (TimeoutException e) {
			logger.error(e.getMessage(),e);
		} catch (CAException e) {
			logger.error(e.getMessage(),e);
		} catch (InterruptedException e) {
			logger.error(e.getMessage(),e);
		}
	}

	private boolean temperatureOverLimit() throws TimeoutException, CAException, InterruptedException {
		return getCurrentTemp() > temperatureLimit;
	}

	private Double getCurrentTemp() throws TimeoutException, CAException, InterruptedException{
		return controller.cagetDouble(temperaturePV);
	}

	public boolean isPauseAtEachPoint() {
		return pauseAtEachPoint;
	}

	public void setPauseAtEachPoint(boolean pauseAtEachPoint) {
		this.pauseAtEachPoint = pauseAtEachPoint;
	}

	public boolean isPauseAtEachLine() {
		return pauseAtEachLine;
	}

	public void setPauseAtEachLine(boolean pauseAtEachLine) {
		this.pauseAtEachLine = pauseAtEachLine;
	}

	public boolean isPauseAtScanStart() {
		return pauseAtScanStart;
	}

	public void setPauseAtScanStart(boolean pauseAtScanStart) {
		this.pauseAtScanStart = pauseAtScanStart;
	}

	public double getTemperatureLimit() {
		return temperatureLimit;
	}

	public void setTemperatureLimit(double temperatureLimit) {
		this.temperatureLimit = temperatureLimit;
	}

	public double getTemperatureCoolLevel() {
		return temperatureCoolLevel;
	}

	public void setTemperatureCoolLevel(double temperatureCoolLevel) {
		this.temperatureCoolLevel = temperatureCoolLevel;
	}

	public double getCoolingTimeout() {
		return coolingTimeout;
	}

	public void setCoolingTimeout(double coolingTimeout) {
		this.coolingTimeout = coolingTimeout;
	}

	public String getMotorTempPV() {
		return motorTempPV;
	}

	public void setMotorTempPV(String motorTempPV) {
		this.motorTempPV = motorTempPV;
	}
}
