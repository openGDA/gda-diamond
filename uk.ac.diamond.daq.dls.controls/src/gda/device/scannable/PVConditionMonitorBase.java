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

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.epics.connection.EpicsChannelManager;
import gda.epics.connection.EpicsController;
import gda.epics.connection.InitializationListener;
import gov.aps.jca.Channel;
import gov.aps.jca.Channel.ConnectionState;

public abstract class PVConditionMonitorBase extends BeamlineConditionMonitorBase implements InitializationListener {

	private static final Logger logger = LoggerFactory.getLogger(PVConditionMonitorBase.class);
	
	protected EpicsController controller;
	protected Channel theChannel;
	private String thePV = "SR21C-DI-DCCT-01:SIGNAL";
	private EpicsChannelManager channelManager;
	
	
	@Override
	public void configure() {
		this.level = 1;
		if (thePV == null || thePV.isEmpty()) {
			logger.error(getName() + " cannot configure as the PVs are not defined.");
		}

		controller = EpicsController.getInstance();
		channelManager = new EpicsChannelManager(this);
		try {
			theChannel = channelManager.createChannel(thePV, false);
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
	
	protected boolean isConnected() {
		return theChannel.getConnectionState().isEqualTo(ConnectionState.CONNECTED);
	}

	@Override
	public void initializationCompleted() {
	}

	public String getThePV() {
		return thePV;
	}

	public void setThePV(String thePV) {
		this.thePV = thePV;
	}

}
