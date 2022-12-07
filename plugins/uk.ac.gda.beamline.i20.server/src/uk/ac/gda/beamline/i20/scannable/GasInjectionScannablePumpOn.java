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

package uk.ac.gda.beamline.i20.scannable;

import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.scannable.ScannableBase;
import gda.epics.CAClient;
import gov.aps.jca.CAException;
import gov.aps.jca.TimeoutException;

public class GasInjectionScannablePumpOn extends ScannableBase {
	private static final Logger logger = LoggerFactory.getLogger(GasInjectionScannablePumpOn.class);
	private CAClient ca_client = new CAClient();

	// valve pvs
	public String v1pv;// Kr
	public String v2pv;// N2
	public String v3pv;// Ar
	public String v4pv;// gas cylinder lines
	public String v5pv;// IC lines

	public String chamberValvepv;// v6, v7, v8, v9

	public String p1pv = "BL20I-EA-GIR-01:P1";// pump

	// pressure gauge pvs
	public String chamberPressurepv;// P2, P3, P4, P5

	// pressure controller pvs
	public String pc1modepv;
	public String pc1targetpv;
	public String pc1currentpv;

	public String pc2modepv;
	public String pc2targetpv;
	public String pc2currentpv;

	public String abortPV;
	public String statusPV;

	public String pumpPV;

	// voltage pvs
	public String readbackPV;
	public String demandPV;
	public String startRampPV;

	public String chamberName;

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {

		if (!(position instanceof List<?>))
			throw new DeviceException("Supplied array must be of type List<String> to move Scannable " + getName());

		List<String> parameters = (List<String>) position;

		String gasType = parameters.get(0);// Kr, N2, Ar
		String pressure = parameters.get(1);

		// before anything check if there is any bias on the ICs. If there is, ramp it down and wait until it is zero
		// before doing anything else
		double i0Voltage = Math.abs(Double.parseDouble(caget(readbackPV)));

		if (i0Voltage > 5) {
			System.out.println("Setting voltage to 0");
			caput(demandPV, "0");
			caput(startRampPV, "1");
			boolean setToZero = true;
			while (setToZero) {
				double voltage = Math.abs(Double.parseDouble(caget(readbackPV)));
				System.out.println("Voltage is currently at " + voltage);
				if (voltage < 5)
					setToZero = false;
				sleep(5000);
			}
		}

		i0Voltage = Math.abs(Double.parseDouble(caget(readbackPV)));

		if (i0Voltage < 5) {
			System.out.println("Filling sequence started");
			System.out.println("Turning on Pump");
			caput(pumpPV, "Open");// turn on pump Bl20I-EA-GIR-01:VACP1:CON 'open'
			System.out.println("Purging cylinder lines for" + gasType);
			purgeCylinderLines(gasType);// purge cylinder lines
			System.out.println("Purging " + chamberName);
			purge();// purge selected chamber this is I0 as an example
			System.out.println("Filling " + chamberName + " with " + gasType + " at " + pressure);
			fill(gasType, pressure);// fill selected chamber this is I0 as an example
			System.out.println("Purging IC lines");
			purgeICLines();// purge IC lines
			System.out.println("Topping up Helium");
			topupHelium();// top up helium for selected chamber this is I0 as an example
			System.out.println("Turning off pump");
			caput(pumpPV, "Close");// turn off pump Bl20I-EA-GIR-01:VACP1:CON 'closed'
		} else
			System.out.println("Voltage is too high at " + i0Voltage);
	}

	// for a given pressure gauge, while pumping is occuring, check pressure every 5 seconds, until the difference
	// between two measurements is less than or equal to 1mbar
	public void pressureCheck(String pv) {
		boolean stable = true;
		while (stable) {
			double pressureOld = Double.parseDouble(caget(pv));
			sleep(5000);
			double pressureNew = Double.parseDouble(caget(pv));
			if (Math.abs(pressureNew - pressureOld) < 1)
				stable = false;
		}
	}

	public boolean isPressureRising(String pv) {
		double pressureOld = Double.parseDouble(caget(pv));
		sleep(5000);
		double pressureNew = Double.parseDouble(caget(pv));
		if (pressureNew - pressureOld > 1)
			return true;
		return false;
	}

	public void purgeCylinderLines(String gas) {
		// only needed if the gas type has changed since the previous fill
		// check that v1, v2, v3 are closed. if open then close.
		System.out.println("Checking that v1, v2, v3 are closed");
		if (caget(v1pv).equals("0") || caget(v2pv).equals("0") || caget(v3pv).equals("0")) {
			System.out.println("closing v1, v2, v3");
			caput(v1pv, "Close");
			caput(v2pv, "Close");
			caput(v3pv, "Close");
		}
		// check again. if cannot be closed then show as error and end.
		System.out.println("Checking again that v1, v2, v3 are closed");
		if (caget(v1pv).equals("1") || caget(v2pv).equals("1") || caget(v3pv).equals("1")) {
			System.out.println("Resetting v4");
			caput(v4pv, "Reset");// reset v4
			sleep(1000);
			System.out.println("Opening v4");
			caput(v4pv, "Open");// open v4
			System.out.println("Checking p1 is stable");
			pressureCheck(p1pv);// pressure check p1
			System.out.println("Closing v4");
			caput(v4pv, "Close");// close v4
			sleep(1000);// sleep so that v4 has finished before other valves start
			if (gas.equals("Kr")) {// if Kr
				System.out.println("Kr selected, opening v1 for a second");
				caput(v1pv, "Open");// open v1
				sleep(10000);// wait 10s
				caput(v1pv, "Close");// close v1
			}
			if (gas.equals("N2")) {// if N2
				System.out.println("N2 selected, opening v2 for a second");
				caput(v2pv, "Open");// open v2
				sleep(10000);// wait 10s
				caput(v2pv, "Close");// close v2
			}
			if (gas.equals("Ar")) {// if Ar
				System.out.println("Ar selected, opening v3 for a second");
				caput(v3pv, "Open");// open v3
				sleep(10000);// wait 10s
				caput(v3pv, "Close");// close v3
			}
			sleep(1000);// sleep so that v4 has finished before other valves start
			System.out.println("Opening v4 for a second");
			caput(v4pv, "Reset");// open v4
			sleep(1000);
			caput(v4pv, "Open");// open v4
			System.out.println("Checking p1 is stable");
			pressureCheck(p1pv);// pressure check p1
			System.out.println("Closing v4");
			caput(v4pv, "Close");// close v4
		}
	}

	// I0 is v6 but other ion chambers will differ It=v7, Iref=v8, I1=v9
	// I0 is p2pv but other ion chambers will differ It=p3pv, Iref=p4pv, I1=p5pv
	public void purge() {
		for (int i = 0; i < 3; i++) {
			System.out.println("Opening v5");
			caput(v5pv, "1");// open v5
			System.out.println("Opening chamber valve");
			caput(chamberValvepv, "1");// open chamber valve
			System.out.println("Checking chamber pressure is stable");
			pressureCheck(chamberPressurepv);// pressure check p2
			System.out.println("Closing v5");
			caput(v5pv, "0");// close v5
			System.out.println("Setting pc2 to 1bar");
			caput(pc2targetpv, "1");// set pressure controller 2 to 1bar
			System.out.println("Setting p2 to control");
			caput(pc2modepv, "control");// set pressure controller 2 to control
			sleep(20000);// wait 20s
			System.out.println("Setting p2 to hold");
			caput(pc2modepv, "hold");// set pressure controller 2 to hold
		}
	}

	// I0 is v6 but other ion chambers will differ It=v7, Iref=v8, I1=v9
	// I0 is p2pv but other ion chambers will differ It=p3pv, Iref=p4pv, I1=p5pv
	public void fill(String gas, String pressure) {
		System.out.println("Opening v5");
		caput(v5pv, "1");// open v5
		System.out.println("Opening chamber valve");
		caput(chamberValvepv, "1");// open chamber valve
		System.out.println("Checking chamber pressure is stable");
		pressureCheck(chamberPressurepv);// pressure check p2
		System.out.println("Closing v5");
		caput(v5pv, "0");// close v5
		System.out.println("Setting p1 to " + pressure);
		caput(pc1targetpv, pressure);// set pressure controller 1 to target pressure

		// check v4 is closed
		System.out.println("Checking that v4 is closed");
		if (caget(v4pv).equals("open")) {
			System.out.println("v4 is open, now closing");
			caput(v4pv, "0");// close v4
		}

		if (gas.equals("Kr"))// if Kr
			System.out.println("Kr selected, opening v1");
			caput(v1pv, "1");// open v1
		if (gas.equals("N2"))// if N2
			System.out.println("N2 selected, opening v2");
			caput(v2pv, "1");// open v2
		if (gas.equals("Ar"))// if Ar
			System.out.println("Ar selected, opening v3");
			caput(v3pv, "1");// open v3
		caput(pc1modepv, "control");// set mode of pressure controller 1 to control

		// if pc1 or p1 rises, close v1, v2 and v3
		System.out.println("Checking whether pc1 or pc2 is stable");
		if (isPressureRising(pc1currentpv) || isPressureRising(p1pv)) {
			System.out.println("pc1 or pc2 is unstable so closing v1, v2, v3");
			caput(v1pv, "0");
			caput(v2pv, "0");
			caput(v3pv, "0");
		}

		System.out.println("Opening chamber valve");
		caput(chamberValvepv, "1");// open chamber valve
		sleep(30000);// wait 30s
		System.out.println("Closing chamber valve");
		caput(chamberValvepv, "0");// close chamber valve
		System.out.println("Setting pc1 to hold");
		caput(pc1modepv, "hold");// set pressure controller 1 to hold

		if (gas.equals("Kr"))// if Kr
			System.out.println("Closing v1");
			caput(v1pv, "0");// close v1
		if (gas.equals("N2"))// if N2
			System.out.println("Closing v2");
			caput(v2pv, "0");// close v2
		if (gas.equals("Ar"))// if Ar
			System.out.println("Closing v3");
			caput(v3pv, "0");// close v3
	}

	public void purgeICLines() {
		System.out.println("Opening v5");
		caput(v5pv, "1");// open v5
		System.out.println("Checking pc2 is stable");
		pressureCheck(pc2currentpv);// pressure check pc2
		System.out.println("Closing v5");
		caput(v5pv, "0");// close v5
		System.out.println("Setting pc2 to 1bar");
		caput(pc2targetpv, "1");// set pc2 to 1bar
		System.out.println("Setting pc1 to control");
		caput(pc1modepv, "control");// set pc1 to control
		sleep(10000);// wait 10s
		System.out.println("Setting pc1 to hold");
		caput(pc1modepv, "hold");// set pc1 to hold
		System.out.println("Opening v5");
		caput(v5pv, "1");// open v5
		System.out.println("Checking pc2 is stable");
		pressureCheck(pc2currentpv);// pressure check pc2
		System.out.println("Closing v5");
		caput(v5pv, "0");// close v5
	}

	// I0 is v6 but other ion chambers will differ It=v7, Iref=v8, I1=v9
	public void topupHelium() {
		System.out.println("Setting pc2 to 1bar");
		caput(pc2targetpv, "1");// set pc2 to 1 bar
		System.out.println("Setting pc2 to control");
		caput(pc2modepv, "control");// set pc2 to control
		System.out.println("Opening chamber valve");
		caput(chamberValvepv, "1");// open chamber valve
		sleep(20000);// wait 20s
		System.out.println("Closing chamber valve");
		caput(chamberValvepv, "0");// close chamber valve
		System.out.println("Setting pc2 to hold");
		caput(pc2modepv, "hold");// set pc2 to hold
	}

	public void sleep(int time) {
		System.out.println("Sleeping for " + time + " seconds");
		try {
			Thread.sleep(time);
		} catch (InterruptedException e) {
			// Reset interrupt status
			Thread.currentThread().interrupt();
			logger.error("Thread.sleep failed. Attempted time was " + time, e);
		}
	}

	public void caput(String pv, String value) {
		try {
			ca_client.caput(pv, value);
		} catch (CAException e) {
			logger.error("Could not set " + pv + " to " + value, e);
		} catch (InterruptedException e) {
			// Reset interrupt status
			Thread.currentThread().interrupt();
			logger.error("Could not set " + pv + " to " + value, e);
		}
	}

	public String caget(String pv) {
		try {
			return ca_client.caget(pv);
		} catch (CAException e) {
			logger.error("Could not get pv " + pv, e);
		} catch (TimeoutException e) {
			logger.error("Could not get pv " + pv, e);
		} catch (InterruptedException e) {
			// Reset interrupt status
			Thread.currentThread().interrupt();
			logger.error("Could not get pv " + pv, e);
		}
		return null;
	}

	@Override
	public void stop() throws DeviceException {
		CAClient ca_client = new CAClient();
		try {
			ca_client.caput(abortPV, 1);
		} catch (CAException e) {
			logger.error("Could not abort gas filling", e);
		} catch (InterruptedException e) {
			// Reset interrupt status
			Thread.currentThread().interrupt();
			logger.error("Could not abort gas filling", e);
		}
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	@Override
	public Object rawGetPosition() {
		return null;
	}

	public String getChamberName() {
		return chamberName;
	}

	public void setChamberName(String chamberName) {
		this.chamberName = chamberName;
	}

}