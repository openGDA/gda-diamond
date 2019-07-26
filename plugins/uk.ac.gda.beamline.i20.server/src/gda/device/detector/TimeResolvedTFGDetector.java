/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package gda.device.detector;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.factory.FactoryException;

public class TimeResolvedTFGDetector extends DetectorBase{

	private static final long serialVersionUID = 1L;

	private static final Logger logger = LoggerFactory.getLogger(TimeResolvedTFGDetector.class);

	private DAServer daServer;
	private double laserTriggerTime;
	private double laserDelay;
	private double excitedDelay;
	private double integration;
	private double settleTime;
	private int cycles;
	private int ttlSocket;

	@Override
	public void configure(){
		if (isConfigured()) {
			return;
		}
		try {
			daServer.configure();
		} catch (FactoryException e) {
			logger.error("Error configuring daServer", e);
		}
		setConfigured(true);
	}

	private void switchOnExtTrigger() throws DeviceException {
		daServer.sendCommand("tfg setup-trig start ttl" + ttlSocket);
	}

	private void setTimeFrames() throws DeviceException {
		StringBuffer buffer = new StringBuffer();
		double livePause = (ttlSocket + 8); //
		buffer.append("tfg setup-groups ext-start cycles " + cycles +"\n");
		buffer.append("1 " + laserDelay + " " + laserTriggerTime + " 0 0 0 " + livePause + "\n");
		buffer.append("1 " + excitedDelay + " " + integration + " 0 0 0 0" + "\n");
		buffer.append("1 " + (laserDelay + excitedDelay) + " " + integration +" 0 0 0 " + livePause + "\n");
		buffer.append("1 " + settleTime + " 0.00000001 0 0 0 0" + "\n");
		buffer.append("-1 0 0 0 0 0 0");
		daServer.sendCommand(buffer.toString());
	}

	@Override
	public void collectData() throws DeviceException {
		switchOnExtTrigger();
		setTimeFrames();
		daServer.sendCommand("tfg arm");
	}

	@Override
	public int getStatus() throws DeviceException {
		// TODO Auto-generated method stub
		return 0;
	}

	@Override
	public Object readout() throws DeviceException {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {
		// TODO Auto-generated method stub
		return false;
	}

	public DAServer getDaServer() {
		return daServer;
	}

	public void setDaServer(DAServer daServer) {
		this.daServer = daServer;
	}

	public double getLaserTriggerTime() {
		return laserTriggerTime;
	}

	public void setLaserTriggerTime(double laserTriggerTime) {
		this.laserTriggerTime = laserTriggerTime;
	}

	public double getLaserDelay() {
		return laserDelay;
	}

	public void setLaserDelay(double laserDelay) {
		this.laserDelay = laserDelay;
	}

	public double getExcitedDelay() {
		return excitedDelay;
	}

	public void setExcitedDelay(double excitedDelay) {
		this.excitedDelay = excitedDelay;
	}

	public double getSettleTime() {
		return settleTime;
	}

	public void setSettleTime(double settleTime) {
		this.settleTime = settleTime;
	}

	public int getCycles() {
		return cycles;
	}

	public void setCycles(int cycles) {
		this.cycles = cycles;
	}

	public int getTtlSocket() {
		return ttlSocket;
	}

	public void setTtlSocket(int ttlSocket) {
		this.ttlSocket = ttlSocket;
	}

}
