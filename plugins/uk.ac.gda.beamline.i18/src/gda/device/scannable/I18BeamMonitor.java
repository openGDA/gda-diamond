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

package gda.device.scannable;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.epics.connection.EpicsChannelManager;
import gda.epics.connection.EpicsController;
import gda.epics.connection.InitializationListener;
import gda.jython.commands.ScannableCommands;
import gov.aps.jca.Channel;
import gov.aps.jca.Channel.ConnectionState;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * I18 specific.
 * <p>
 * This will pause scans if the ring current goes below 1mA or if the front-end shutter is closed.
 * <p>
 * When the beam comes back it moves the energy scannable to its current position so that the ID gap is definitely at the right place.
 */
public class I18BeamMonitor extends BeamlineConditionMonitorBase implements InitializationListener {
	private static final Logger logger = LoggerFactory.getLogger(I18BeamMonitor.class);

	private String ringCurrentPV = "SR21C-DI-DCCT-01:SIGNAL";
	private String shutterPV = "FE18I-RS-ABSB-02:STA";
	private String[] modesToIgnore = new String[] { "Mach. Dev.", "Shutdown" };

	private EpicsController controller;
	private EpicsChannelManager channelManager;
	private Channel machineMode;
	private Channel portShutter;
	private Channel ringCurrent;

	private Scannable beamlineEnergyWithGapScannable;

	public I18BeamMonitor(Scannable beamlineEnergyWithGapScannable) {
		super();
		this.beamlineEnergyWithGapScannable = beamlineEnergyWithGapScannable;
	}

	@Override
	public void configure() {
		this.level = 1;
		if (shutterPV == null || shutterPV.isEmpty()
				|| ringCurrentPV == null || ringCurrentPV.isEmpty()) {
			logger.error(getName() + " cannot configure as the PVs are not defined.");
		}

		controller = EpicsController.getInstance();
		channelManager = new EpicsChannelManager(this);
		try {
			portShutter = channelManager.createChannel(shutterPV, false);
			ringCurrent = channelManager.createChannel(ringCurrentPV, false);
		} catch (Exception e) {
			logger.error(getName() + " Beam monitor failed to configure.", e);
		}
	}

	@Override
	public void atScanStart() throws DeviceException {
		// if not connected then try to connect again at the start of every scan
		if (!isConnected()) {
			configure();
		}
	}

	@Override
	public void atScanEnd() throws DeviceException {
		ScannableCommands.remove_default(this);
	}

	@Override
	public void atCommandFailure() {
		ScannableCommands.remove_default(this);
	}

	protected boolean isConnected() {
		return machineMode.getConnectionState().isEqualTo(ConnectionState.CONNECTED)
				&& portShutter.getConnectionState().isEqualTo(ConnectionState.CONNECTED)
				&& ringCurrent.getConnectionState().isEqualTo(ConnectionState.CONNECTED);
	}

	protected String getNotConnectedMessage() {
		return getName()
				+ " could not run its test as its channels to Epics are not connected. The scan is not protected by this scannable";
	}

	@Override
	protected void testShouldPause() throws DeviceException {

		if (!isConnected()) {
			logger.error(getNotConnectedMessage());
		}

		if (!machineIsRunning()) {
			return;
		}

		while (!machineHasCurrent()) {
			try {
				sendAndPrintMessage("Ring has no current : pausing until it has returned");
				Thread.sleep(60000);
			} catch (InterruptedException e) {
				// someone trying to kill the thread so re-throw to kill any scan
				throw new DeviceException(e.getMessage(), e);
			}
		}

		while (!portShutterOpen()) {
			try {
				sendAndPrintMessage("Port shutter closed : pausing until it is opened");
				Thread.sleep(60000);
			} catch (InterruptedException e) {
				// someone trying to kill the thread so re-throw to kill any scan
				throw new DeviceException(e.getMessage(), e);
			}
		}

		// set energy to same value so idgap goes to correct position.
		Double beamlineEnergy = (Double) beamlineEnergyWithGapScannable.getPosition();
		beamlineEnergyWithGapScannable.moveTo(beamlineEnergy);
	}

	protected boolean portShutterOpen() {
		try {
			String value = controller.cagetString(portShutter);
			return value.equals("Open");
		} catch (Exception e) {
			logger.error(e.getMessage(), e);
			return true;
		}
	}

	protected boolean machineHasCurrent() {
		try {
			Double current = controller.cagetDouble(ringCurrent);
			return current > 1.0;
		} catch (Exception e) {
			logger.error(e.getMessage(), e);
			return true;
		}
	}

	@Override
	public void initializationCompleted() {
	}

	public String getShutterPV() {
		return shutterPV;
	}

	public void setShutterPV(String shutterPV) {
		this.shutterPV = shutterPV;
	}

	public String[] getModesToIgnore() {
		return modesToIgnore;
	}

	public void setModesToIgnore(String[] modesToIgnore) {
		this.modesToIgnore = modesToIgnore;
	}

	public void setRingCurrentPV(String ringCurrentPV) {
		this.ringCurrentPV = ringCurrentPV;
	}

	public String getRingCurrentPV() {
		return ringCurrentPV;
	}
}
