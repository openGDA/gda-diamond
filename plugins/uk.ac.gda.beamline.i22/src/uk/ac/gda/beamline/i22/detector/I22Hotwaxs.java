/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i22.detector;

import gda.device.DeviceException;
import gda.epics.connection.EpicsController;
import gda.factory.FactoryException;
import gda.factory.corba.util.CorbaAdapterClass;
import gda.factory.corba.util.CorbaImplClass;
import gda.jython.InterfaceProvider;
import gov.aps.jca.Channel;
import gov.aps.jca.dbr.DBR;
import gov.aps.jca.dbr.DBR_Double;
import gov.aps.jca.dbr.DBR_Int;
import gov.aps.jca.event.MonitorEvent;
import gov.aps.jca.event.MonitorListener;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.server.ncd.subdetector.NcdWireDetector;
import uk.ac.gda.server.ncd.subdetector.corba.impl.SubdetectorAdapter;
import uk.ac.gda.server.ncd.subdetector.corba.impl.SubdetectorImpl;

@CorbaAdapterClass(SubdetectorAdapter.class)
@CorbaImplClass(SubdetectorImpl.class)
public class I22Hotwaxs extends NcdWireDetector implements MonitorListener {
	
	private class GasFlowException extends DeviceException {
		public GasFlowException(String message) {
			super(message);
		}
	}
	private class SupplyException extends DeviceException {
		public SupplyException(String message) {
			super(message);
		}
	}
	
	private static final Logger logger = LoggerFactory.getLogger(I22Hotwaxs.class);  		

	private EpicsController ec;
	private String flowPVName, caenPVbase;
	private int restarts = 0;
	private boolean inAScan = false;
	private double gasFlow = 0;
	private SupplyState[] supplyState = new SupplyState[4];
	private DeviceException whatswrong = new DeviceException("uninitialised");
	private Channel[] supplyChannels = new Channel[4];
	
	enum SupplyState {
		ON, OFF, TRIPPED
	}
	
	@Override
	public void configure() throws FactoryException {
		super.configure();
		
		ec = EpicsController.getInstance();
		
		try {
			Channel channel = ec.createChannel(flowPVName);
			ec.setMonitor(channel, this);
			for (int i = 0; i < 3; i++) {
				supplyChannels[i] = ec.createChannel(String.format("%s:STAT%d:RBV", caenPVbase, i));
				ec.setMonitor(supplyChannels[i], this);
			}
		} catch (Exception e) {
			throw new FactoryException("error connecting to PVs for "+getName(), e);
		}
		
		
	}
	
	@Override
	public void atScanStart() throws DeviceException {
		if (whatswrong != null) throw whatswrong;
		super.atScanStart();
		inAScan = true;
		restarts = 0;
	}
	
	@Override
	public void atScanEnd() throws DeviceException {
		inAScan = false;
		super.atScanEnd();
	}
	
	
	private DeviceException checkGas() {
		double targetGasFlow = 100;
		double gasFlowSpread = 1;
		
		if (gasFlow < targetGasFlow-gasFlowSpread || gasFlow > targetGasFlow+gasFlowSpread)
			return new GasFlowException("Gas flow not in acceptable range. Contact beamline staff for help with "+getName());
		
		return null;
	}
	
	private DeviceException checkSupplies() {
		DeviceException de = null;
		for (int i = 0; i < 3; i++) {
			if (supplyState[i] == SupplyState.OFF) {
				return new SupplyException(String.format("Channel %d of HV supplies is OFF. Contact beamline staff to start up %s.", i, getName()));
			}
			if (supplyState[i] == SupplyState.TRIPPED) {
				if (!inAScan) 
					return new SupplyException(String.format("Channel %d of HV supplies has tripped on %s.", i, getName()));
				restarts++;
				if (restarts < 12) {
					de = new SupplyException(String.format("Channel %d of HV supplies has tripped. %s is trying to recover that for you.", i, getName()));
					try {
						ec.caput(ec.createChannel(String.format("%s:ON%d", caenPVbase, i)), 1);
					} catch (Exception e) {
						logger.error("cannot restart HV supply", e);
					}
				} else {
					return new SupplyException(String.format("Channel %d of HV supplies has tripped an excessive number of times. Contact beamline staff to reanimate %s.", i, getName()));
				}
			}
		}
		
		return de;
	}

	private SupplyState supplyStateFromInt(int value) {
		if ((value & 1<<7) == 1<<7) {
			return SupplyState.TRIPPED;
		}
		if ((value & 1<<0) == 1<<0) {
			return SupplyState.ON;
		}
		return SupplyState.OFF;
	}
	
	
	@Override
	public void monitorChanged(MonitorEvent mev) {
		
		// FIXME check for disconnects in case the IOC goes down
		
		try { 
			final DeviceException oldError = whatswrong;
			
			DBR dbr = mev.getDBR();
			
			if (dbr instanceof DBR_Double) {
				gasFlow = ((DBR_Double) dbr).getDoubleValue()[0];
			
				whatswrong = checkGas();
			} else if (dbr instanceof DBR_Int){
				for (int i = 0; i < 3; i++) {
					if (mev.getSource().equals(supplyChannels[i])) {
						supplyState[i] = supplyStateFromInt(((DBR_Int) dbr).getIntValue()[0]);
						break;
					}
				}
			}

			new Thread(new Runnable() {
				@Override
				public void run() {
					processNewState(oldError);
				}
			}).start();
			
		} catch (Exception e) {
			logger.error("unexpected problems processing monitor updates on gain PV", e);
		}
	}

	private void processNewState(DeviceException oldError) {
		if (whatswrong == null) 
			whatswrong = checkSupplies();
		
		if (inAScan) {
			if (whatswrong != null && oldError == null) {
				InterfaceProvider.getTerminalPrinter().print(whatswrong.getMessage());
			}
			if (oldError != null && whatswrong == null) {
				InterfaceProvider.getTerminalPrinter().print(getName()+" has recovered");
			}
			if (oldError != null && whatswrong != null && !oldError.getMessage().equals(whatswrong.getMessage())) {
				InterfaceProvider.getTerminalPrinter().print(whatswrong.getMessage());
			}
		}
	}
	
	public String getFlowPVName() {
		return flowPVName;
	}

	public void setFlowPVName(String flowPVName) {
		this.flowPVName = flowPVName;
	}

	public String getCaenPVbase() {
		return caenPVbase;
	}

	public void setCaenPVbase(String caenPVbase) {
		this.caenPVbase = caenPVbase;
	}
}