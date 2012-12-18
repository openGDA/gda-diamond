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

	boolean stop = false;

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

	public String getV1pv() {
		return v1pv;
	}

	public void setV1pv(String v1pv) {
		this.v1pv = v1pv;
	}

	public String getV2pv() {
		return v2pv;
	}

	public void setV2pv(String v2pv) {
		this.v2pv = v2pv;
	}

	public String getV3pv() {
		return v3pv;
	}

	public void setV3pv(String v3pv) {
		this.v3pv = v3pv;
	}

	public String getV4pv() {
		return v4pv;
	}

	public void setV4pv(String v4pv) {
		this.v4pv = v4pv;
	}

	public String getV5pv() {
		return v5pv;
	}

	public void setV5pv(String v5pv) {
		this.v5pv = v5pv;
	}

	public String getChamberValvepv() {
		return chamberValvepv;
	}

	public void setChamberValvepv(String chamberValvepv) {
		this.chamberValvepv = chamberValvepv;
	}

	public String getP1pv() {
		return p1pv;
	}

	public void setP1pv(String p1pv) {
		this.p1pv = p1pv;
	}

	public String getChamberPressurepv() {
		return chamberPressurepv;
	}

	public void setChamberPressurepv(String chamberPressurepv) {
		this.chamberPressurepv = chamberPressurepv;
	}

	public String getPc1modepv() {
		return pc1modepv;
	}

	public void setPc1modepv(String pc1modepv) {
		this.pc1modepv = pc1modepv;
	}

	public String getPc1targetpv() {
		return pc1targetpv;
	}

	public void setPc1targetpv(String pc1targetpv) {
		this.pc1targetpv = pc1targetpv;
	}

	public String getPc1currentpv() {
		return pc1currentpv;
	}

	public void setPc1currentpv(String pc1currentpv) {
		this.pc1currentpv = pc1currentpv;
	}

	public String getPc2modepv() {
		return pc2modepv;
	}

	public void setPc2modepv(String pc2modepv) {
		this.pc2modepv = pc2modepv;
	}

	public String getPc2targetpv() {
		return pc2targetpv;
	}

	public void setPc2targetpv(String pc2targetpv) {
		this.pc2targetpv = pc2targetpv;
	}

	public String getPc2currentpv() {
		return pc2currentpv;
	}

	public void setPc2currentpv(String pc2currentpv) {
		this.pc2currentpv = pc2currentpv;
	}

	public String getAbortPV() {
		return abortPV;
	}

	public void setAbortPV(String abortPV) {
		this.abortPV = abortPV;
	}

	public String getStatusPV() {
		return statusPV;
	}

	public void setStatusPV(String statusPV) {
		this.statusPV = statusPV;
	}

	public String getPumpPV() {
		return pumpPV;
	}

	public void setPumpPV(String pumpPV) {
		this.pumpPV = pumpPV;
	}

	public String getReadbackPV() {
		return readbackPV;
	}

	public void setReadbackPV(String readbackPV) {
		this.readbackPV = readbackPV;
	}

	public String getDemandPV() {
		return demandPV;
	}

	public void setDemandPV(String demandPV) {
		this.demandPV = demandPV;
	}

	public String getStartRampPV() {
		return startRampPV;
	}

	public void setStartRampPV(String startRampPV) {
		this.startRampPV = startRampPV;
	}

	@Override
	public void moveTo(Object position) throws DeviceException {
		rawAsynchronousMoveTo(position);
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {

		stop=false;
		
		if (!(position instanceof List<?>))
			throw new DeviceException("Supplied array must be of type List<String> to move Scannable " + getName());

		List<String> parameters = (List<String>) position;

		String gasType = parameters.get(0);// Kr, N2, Ar
		String pressure = parameters.get(1);
		String demandVoltage = parameters.get(2);

		// before anything check if there is any bias on the ICs. If there is, ramp it down and wait until it is zero
		// before doing anything else
		double voltage = Math.abs(Double.parseDouble(caget(readbackPV)));

		if (voltage > 5) {
			log("Setting voltage to 0");
			caput(demandPV, "0");
			sleep(1000);
			caput(startRampPV, "1");
			boolean setToZero = true;
			while (setToZero) {
				voltage = Math.abs(Double.parseDouble(caget(readbackPV)));
				log("Voltage is currently at " + voltage);
				if (voltage < 5)
					setToZero = false;
				sleep(5000);
			}
		}

		voltage = Math.abs(Double.parseDouble(caget(readbackPV)));

		if (voltage < 5) {
			log("------Filling sequence started------");
			log("------Turning on Pump------");
			caput(pumpPV, "Open");// turn on pump Bl20I-EA-GIR-01:VACP1:CON 'open'
			log("------Purging cylinder lines for" + gasType + " ------");
			if (!stop)
				purgeCylinderLines(gasType);// purge cylinder lines
			log("------Purging " + chamberName + "------");
			if (!stop)
				purge();// purge selected chamber this is I0 as an example
			log("------Filling " + chamberName + " with " + gasType + " at " + pressure + " ------");
			if (!stop)
				fill(gasType, pressure);// fill selected chamber this is I0 as an example
			log("------Purging IC lines------");
			if (!stop)
				purgeICLines();// purge IC lines
			log("------Topping up Helium------");
			if (!stop)
				topupHelium();// top up helium for selected chamber this is I0 as an example
			log("------Turning off pump------");
			caput(pumpPV, "Close");// turn off pump Bl20I-EA-GIR-01:VACP1:CON 'closed'
			if (!stop) {
				log("------Ramping voltage to " + demandVoltage + "------");
				caput(demandPV, demandVoltage);
				sleep(1000);
				caput(startRampPV, "1");
			}
		} else
			log("Voltage is too high at " + voltage);
	}

	// for a given pressure gauge, while pumping is occuring, check pressure every 5 seconds, until the difference
	// between two measurements is less than or equal to 1mbar
	public void pressureCheck(String pv) {
		boolean stable = true;
		while (stable && !stop) {
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
		log("Checking that v1, v2, v3 are closed");
		if (caget(v1pv).equals("0") || caget(v2pv).equals("0") || caget(v3pv).equals("0")) {
			log("closing v1, v2, v3");
			caput(v1pv, "Close");
			caput(v2pv, "Close");
			caput(v3pv, "Close");
		}
		// check again. if cannot be closed then show as error and end.
		log("Checking again that v1, v2, v3 are closed");
		if (caget(v1pv).equals("1") || caget(v2pv).equals("1") || caget(v3pv).equals("1")) {
			log("Resetting v4");
			caput(v4pv, "Reset");// reset v4
			sleep(1000);
			log("Opening v4");
			caput(v4pv, "Reset");
			sleep(1000);
			caput(v4pv, "Open");// open v4
			log("Checking p1 is stable");
			pressureCheck(p1pv);// pressure check p1
			log("Closing v4");
			caput(v4pv, "Close");// close v4
			sleep(1000);// sleep so that v4 has finished before other valves start
			if (!stop) {
				if (gas.equals("Kr")) {// if Kr
					log("Kr selected");
					caput(v1pv, "Reset");
					sleep(1000);
					caput(v1pv, "Open");// open v1
					sleep(10000);// wait 10s
					caput(v1pv, "Close");// close v1
				}
				if (gas.equals("N2")) {// if N2
					log("N2 selected");
					caput(v2pv, "Reset");
					sleep(1000);
					caput(v2pv, "Open");// open v2
					sleep(10000);// wait 10s
					caput(v2pv, "Close");// close v2
				}
				if (gas.equals("Ar")) {// if Ar
					log("Ar selected");
					caput(v3pv, "Reset");
					sleep(1000);
					caput(v3pv, "Open");// open v3
					sleep(10000);// wait 10s
					caput(v3pv, "Close");// close v3
				}
			}
			if (!stop) {
				sleep(1000);// sleep so that v4 has finished before other valves start
				caput(v4pv, "Reset");// open v4
				sleep(1000);
				log("Opening v4");
				caput(v4pv, "Reset");
				sleep(1000);
				caput(v4pv, "Open");// open v4
				log("Checking p1 is stable");
				pressureCheck(p1pv);// pressure check p1
				log("Closing v4");
				caput(v4pv, "Close");// close v4
			}
		}
	}

	// I0 is v6 but other ion chambers will differ It=v7, Iref=v8, I1=v9
	// I0 is p2pv but other ion chambers will differ It=p3pv, Iref=p4pv, I1=p5pv
	public void purge() {
		for (int i = 0; i < 3; i++) {
			if (!stop) {
				log("------Purging itteration " + i + " ------");
				log("Opening v5");
				caput(v5pv, "Reset");
				sleep(1000);
				caput(v5pv, "Open");// open v5
				log("Opening chamber valve");
				caput(chamberValvepv, "Reset");
				sleep(1000);
				caput(chamberValvepv, "Open");// open chamber valve
				log("Checking chamber pressure is stable");
				pressureCheck(chamberPressurepv);// pressure check p2
				log("Closing v5");
				caput(v5pv, "Close");// close v5
				log("Setting pc2 to 1bar");
				caput(pc2targetpv, "1000");// set pressure controller 2 to 1bar
				log("Setting p2 to control");
				caput(pc2modepv, "Control");// set pressure controller 2 to control
			}
			if (!stop) {
				sleep(20000);// wait 20s
			}
			if (!stop) {
				log("Setting p2 to Hold");
				caput(pc2modepv, "Hold");// set pressure controller 2 to hold
				log("Closing chamber Valve");
				caput(chamberValvepv, "Close");
			}
		}
	}

	// I0 is v6 but other ion chambers will differ It=v7, Iref=v8, I1=v9
	// I0 is p2pv but other ion chambers will differ It=p3pv, Iref=p4pv, I1=p5pv
	public void fill(String gas, String pressure) {
		log("Opening v5");
		caput(v5pv, "Reset");
		sleep(1000);
		caput(v5pv, "Open");// open v5
		log("Opening chamber valve");
		caput(chamberValvepv, "Reset");
		sleep(1000);
		caput(chamberValvepv, "Open");// open chamber valve
		log("Checking chamber pressure is stable");
		pressureCheck(chamberPressurepv);// pressure check p2
		log("Closing v5");
		caput(v5pv, "Close");// close v5
		log("Setting p1 to " + pressure);
		caput(pc1targetpv, pressure);// set pressure controller 1 to target pressure

		// check v4 is closed
		log("Checking that v4 is closed");
		if (caget(v4pv).equals("Open")) {
			log("v4 is open, now closing");
			caput(v4pv, "Close");// close v4
		}

		if (!stop) {
			if (gas.equals("Kr")) {// if Kr
				log("Kr selected, opening v1");
				caput(v1pv, "Reset");
				sleep(1000);
				caput(v1pv, "Open");// open v1
			}
			if (gas.equals("N2")) {// if N2
				log("N2 selected, opening v2");
				caput(v2pv, "Reset");
				sleep(1000);
				caput(v2pv, "Open");// open v2
			}
			if (gas.equals("Ar")) {// if Ar
				log("Ar selected, opening v3");
				caput(v3pv, "Reset");
				sleep(1000);
				caput(v3pv, "Open");// open v3
			}
		}
		if (!stop) {
			caput(pc1modepv, "Control");// set mode of pressure controller 1 to control

			// if pc1 or p1 rises, close v1, v2 and v3
			log("Checking whether pc1 or pc2 is stable");
			if (isPressureRising(pc1currentpv) || isPressureRising(p1pv)) {
				log("pc1 or pc2 is unstable so closing v1, v2, v3");
				caput(v1pv, "Close");
				caput(v2pv, "Close");
				caput(v3pv, "Close");
			}
		}
		if (!stop) {
			log("Checking chamber pressure is stable");
			pressureCheck(chamberValvepv);
			log("Closing chamber valve");
			caput(chamberValvepv, "Close");// close chamber valve
			log("Setting pc1 to hold");
			caput(pc1modepv, "Hold");// set pressure controller 1 to hold

			if (gas.equals("Kr")) {// if Kr
				log("Closing v1");
				caput(v1pv, "Close");// close v1
			}
			if (gas.equals("N2")) {// if N2
				log("Closing v2");
				caput(v2pv, "Close");// close v2
			}
			if (gas.equals("Ar")) {// if Ar
				log("Closing v3");
				caput(v3pv, "Close");// close v3
			}
		}
	}

	public void purgeICLines() {
		log("Opening v5");
		caput(v5pv, "Reset");
		sleep(1000);
		caput(v5pv, "Open");// open v5
		log("Checking pc2 is stable");
		pressureCheck(pc2currentpv);// pressure check pc2
		log("Closing v5");
		caput(v5pv, "Close");// close v5
		log("Setting pc2 to 1bar");
		caput(pc2targetpv, "1000");// set pc2 to 1bar
		log("Setting pc2 to Control");
		caput(pc2modepv, "Control");// set pc2 to control
		if (!stop)
			sleep(10000);// wait 10s
		if (!stop) {
			log("Setting pc2 to hold");
			caput(pc2modepv, "Hold");// set pc1 to hold
			log("Opening v5");
			caput(v5pv, "Reset");
			sleep(1000);
			caput(v5pv, "Open");// open v5
			log("Checking pc2 is stable");
			pressureCheck(pc2currentpv);// pressure check pc2
			log("Closing v5");
			caput(v5pv, "Close");// close v5
		}
	}

	// I0 is v6 but other ion chambers will differ It=v7, Iref=v8, I1=v9
	public void topupHelium() {
		log("Setting pc2 to 1bar");
		caput(pc2targetpv, "1000");// set pc2 to 1 bar
		log("Setting pc2 to control");
		caput(pc2modepv, "Control");// set pc2 to control
		log("Opening chamber valve");
		caput(chamberValvepv, "Reset");
		sleep(1000);
		caput(chamberValvepv, "Open");// open chamber valve
		if (!stop)
			sleep(20000);// wait 20s
		if (!stop) {
			log("Closing chamber valve");
			caput(chamberValvepv, "Close");// close chamber valve
			log("Setting pc2 to hold");
			caput(pc2modepv, "Hold");// set pc2 to hold
		}
	}

	public void sleep(int time) {
		log("Sleeping for " + time / 1000 + " seconds");
		try {
			Thread.sleep(time);
		} catch (InterruptedException e) {
			logger.error("Thread.sleep failed. Attempted time was " + time, e);
		}
	}

	public void caput(String pv, String value) {
		if (!stop) {
			try {
				ca_client.caput(pv, value);
			} catch (CAException e) {
				logger.error("Could not set " + pv + " to " + value, e);
			} catch (InterruptedException e) {
				logger.error("Could not set " + pv + " to " + value, e);
			}
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
			logger.error("Could not get pv " + pv, e);
		}
		return null;
	}

	@Override
	public void stop() throws DeviceException {

		stop = true;
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

	public void log(String msg) {
		logger.info(msg);
		System.out.println(msg);
	}
}
