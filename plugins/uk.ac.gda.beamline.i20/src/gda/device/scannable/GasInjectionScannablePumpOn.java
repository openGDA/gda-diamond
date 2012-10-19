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

package gda.device.scannable;

import java.util.List;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.epics.CAClient;
import gov.aps.jca.CAException;
import gov.aps.jca.TimeoutException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GasInjectionScannablePumpOn extends ScannableBase implements Scannable {

	private static final Logger logger = LoggerFactory.getLogger(GasInjectionScannablePumpOn.class);
	CAClient ca_client = new CAClient();

	// valve pvs
	private String v1pv;
	private String v2pv;
	private String v3pv;
	private String v4pv;
	private String v5pv;
	private String v6pv;
	private String v7pv;
	private String v8pv;
	private String v9pv;

	// pressure gauge pvs
	private String p1pv;
	private String p2pv;
	private String p3pv;
	private String p4pv;
	private String p5pv;

	// pressure controller pvs
	private String pc1modepv;
	private String pc1targetpv;
	private String pc2modepv;
	private String pc2targetpv;
	
	private String abortPV;
	
	private String statusPV;
	
	private String pumpPV;
	
	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		
		if (!(position instanceof List<?>))
			throw new DeviceException("Supplied array must be of type List<String> to move Scannable " + getName());
		
		List<String> parameters = (List<String>) position;
		
		String gasType = parameters.get(0);
		String pressure = parameters.get(1);
		
		caput(pumpPV, "open");// turn on pump Bl20I-EA-GIR-01:VACP1:CON 'open'
		purgeCylinderLines(gasType);// purge cylinder lines
		purgeI0();// purge I0
		fillI0(gasType, pressure);// fill I0
		purgeIC();// purge IC lines
		topupHelium();// top up helium
		caput(pumpPV, "closed");// turn off pump Bl20I-EA-GIR-01:VACP1:CON 'closed'
	}
	
	private void pressureCheck(String pv) {
		// for a given pressure gauge, while pumping is occuring, check pressure every 5 seconds, until the difference
		// between two measurements is less than or equal to 1mbar
		// before anything check if there is any bias on the ICs. If there is, ramp it down and wait until it is zero before
		// doing anything else
		// pump is left on all the time that pumping/purging sequences are being run
	}

	private void purgeCylinderLines(String gas) {
		// only needed if the gas type has changed since the previous fill
		// check that v1, v2, v3 are closed
		caput(v4pv, "0");// open v4
		// pressure check p1
		caput(v4pv, "0");// close v4
		if (gas.equals("Kr")) {// if Kr
			caput(v1pv, "0");// open v1
			sleep(10000);// wait 10s
			caput(v1pv, "0");// close v1
		}
		if (gas.equals("N2")) {// if N2
			caput(v2pv, "0");// open v2
			sleep(10000);// wait 10s
			caput(v2pv, "0");// close v2
		}
		if (gas.equals("Ar")) {// if Ar
			caput(v3pv, "0");// open v3
			sleep(10000);// wait 10s
			caput(v3pv, "0");// close v3
		}
		caput(v4pv, "0");// open v4
		sleep(30000);// wait 30s
		caput(v4pv, "0");// close v4
	}

	private void purgeI0() {
		for (int i = 0; i < 3; i++) {
			caput(v5pv, "1");// open v5
			caput(v6pv, "1");// open v6
			// pressure check p2
			caput(v5pv, "0");// close v5
			caput(pc2targetpv, "1");// set pressure controller 2 to 1bar
			caput(pc2modepv, "control");// set pressure controller 2 to control
			sleep(20000);// wait 20s
			caput(pc2modepv, "hold");// set pressure controller 2 to hold
		}
	}

	private void fillI0(String gas, String pressure) {
		caput(v5pv, "1");// open v5
		caput(v6pv, "1");// open v6
		// pressure check p2
		caput(v5pv, "0");// close v5
		caput(pc1targetpv, pressure);// set pressure controller 1 to target pressure
		
		// check v4 is closed
		if(caget(v4pv).equals("closed")){
			
		}
		
		if (gas.equals("Kr"))// if Kr
			caput(v1pv, "1");// open v1
		if (gas.equals("N2"))// if N2
			caput(v2pv, "1");// open v2
		if (gas.equals("Ar"))// if Ar
			caput(v3pv, "1");// open v3
		caput(pc1modepv, "control");// set mode of pressure controller 1 to control
		// if cp1 or p1 rises, close v1, v2 and v3
		caput(v6pv, "1");// open v6
		caput(pc1modepv, "hold");// set pressure controller 1 to hold
		if (gas.equals("Kr"))// if Kr
			caput(v1pv, "0");// close v1
		if (gas.equals("N2"))// if N2
			caput(v2pv, "0");// close v2
		if (gas.equals("Ar"))// if Ar
			caput(v3pv, "0");// close v3
	}

	private void purgeIC() {
		caput(v5pv, "1");// open v5
		// pressure check pc2
		caput(v5pv, "0");// close v5
		caput(pc2targetpv, "1");// set pc2 to 1bar
		caput(pc1modepv, "control");// set pc1 to control
		sleep(10000);// wait 10s
		caput(pc1modepv, "hold");// set pc1 to hold
		caput(v5pv, "1");// open v5
		// pressure check pc2
		caput(v5pv, "0");// close v5
	}

	private void topupHelium() {
		caput(pc2targetpv, "1");// set pc2 to 1 bar pc1targetpv
		caput(pc2modepv, "control");// set pc2 to control pc1modepv
		caput(v6pv, "1");// open v6
		sleep(20000);// wait 20s
		caput(v6pv, "0");// close v6
		caput(pc2modepv, "hold");// set pc2 to hold
	}
	
	private void sleep(int time) {
		try {
			Thread.sleep(time);
		} catch (InterruptedException e) {
			logger.error("Thread.sleep failed. Attempted time was " + time, e);
		}
	}

	private void caput(String pv, String value) {
		try {
			ca_client.caput(pv, 1);
		} catch (CAException e) {
			logger.error("Could not set " + pv + " to " + value, e);
		} catch (InterruptedException e) {
			logger.error("Could not set " + pv + " to " + value, e);
		}
	}
	
	private String caget(String pv){
		try {
			return ca_client.caget(pv);
		} catch (CAException e) {
			logger.error("Could not get pv "+pv, e);
		} catch (TimeoutException e) {
			logger.error("Could not get pv "+pv, e);
		} catch (InterruptedException e) {
			logger.error("Could not get pv "+pv, e);
		}
		return null;
	}
	
	@Override
	public void stop() throws DeviceException{
		CAClient ca_client = new CAClient();
		try {
			ca_client.caput(abortPV, 1);
		} catch (CAException e) {
			logger.error("Could not abort gas filling", e);
		} catch (InterruptedException e) {
			logger.error("Could not abort gas filling", e);
		}
	}
	
	@Override
	public boolean isBusy() throws DeviceException {
		if(getFillStatus().equals("0"))
			return false;
		return true;
	}
	
	private String getFillStatus() {
		String status = null;
		try {
			status = caget(statusPV);
		} catch (NumberFormatException e) {
			e.printStackTrace();
		}
		if (status.equals('0'))
			return "idle";
		else if (status.equals("4"))
			return "purging gas";
		else if (status.equals("8"))
			return "filling gas";
		else if (status.equals("16"))
			return "purging helium";
		else if (status.equals("32"))
			return "filling helium";
		else if (status.equals("256"))
			return "timeout";
		else if (status.equals("512"))
			return "aborted";
		return null;
	}
	
	@Override
	public Object rawGetPosition() {
		return getFillStatus();
	}
}
