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

import gda.device.DeviceException;
import gda.epics.connection.EpicsChannelManager;
import gda.epics.connection.EpicsController;
import gda.epics.connection.InitializationListener;
import gov.aps.jca.Channel;
import gov.aps.jca.Channel.ConnectionState;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Looks at a shutter (such as the beamline's port shutter) during scans to see if its open. Will stop the scan if
 * theres no beam.
 * <p>
 * Will not do this if the machine is not running.
 */
public class BeamMonitorScannable extends TopupScannable implements InitializationListener {

	private static final Logger logger = LoggerFactory.getLogger(BeamMonitorScannable.class);

	private String machineModePV = "CS-CS-MSTAT-01:MODE";
	private String shutterPV = "FE18B-RS-ABSB-02:STA";
	private String[] modesToIgnore = new String[] { "Mach. Dev." };

	private EpicsController controller;

	private EpicsChannelManager channelManager;

	private Channel machineMode;
	private Channel portShutter;

	public BeamMonitorScannable() {
		super();
	}

	@Override
	public void configure() {
		this.level = 1;
		if (machineModePV == null || machineModePV.isEmpty() || shutterPV == null || shutterPV.isEmpty()) {
			logger.error(getName() + " cannot configure as the PVs are not defined.");
		}

		controller = EpicsController.getInstance();
		channelManager = new EpicsChannelManager(this);
		try {
			machineMode = channelManager.createChannel(machineModePV, false);
			portShutter = channelManager.createChannel(shutterPV, false);
		} catch (Exception e) {
			logger.error(getName() + " had Exception during configure. Scans will not be protected by this Scannable.",
					e);
		}
	}

	@Override
	public void atScanStart() throws DeviceException {
		// if not connected then try to connect again at the start of every scan
		if (!isConnected()) {
			configure();
		}
	}

	private boolean isConnected() {
		return machineMode.getConnectionState().isEqualTo(ConnectionState.CONNECTED)
				&& portShutter.getConnectionState().isEqualTo(ConnectionState.CONNECTED);
	}

	private String getNotConnectedMessage() {
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

		if (!beamAvailable()) {
			throw new DeviceException(
					"Scan should not run as port shutter closed! If you do not want this protection for scans type: \"remove_default "
							+ getName() + "\"");
		}
	}

	private boolean beamAvailable() {
		String value;
		try {
			value = controller.cagetString(portShutter);
			return value.equals("Open");
		} catch (Exception e) {
			logger.error(e.getMessage(), e);
			return true;
		}
	}

	/**
	 * Returns false if not in a real running mode.
	 * 
	 * @return true if user mode, so this object should operate.
	 */
	private boolean machineIsRunning() {

		if (machineModePV == null || machineModePV.isEmpty()) {
			return true;
		}

		String value;
		try {
			value = controller.cagetString(machineMode);
		} catch (Exception e) {
			logger.error(e.getMessage(), e);
			return true;
		}

		for (String modeToIgnore : modesToIgnore) {
			if (modeToIgnore.equals(value)) {
				return false;
			}
		}

		// current mode not listed in modes to ignore
		return true;
	}

	public String getMachineModePV() {
		return machineModePV;
	}

	public void setMachineModePV(String machineModePV) {
		this.machineModePV = machineModePV;
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

	@Override
	public void initializationCompleted() {
	}

}
