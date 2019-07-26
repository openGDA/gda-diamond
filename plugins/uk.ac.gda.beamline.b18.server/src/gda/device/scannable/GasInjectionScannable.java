/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.FactoryException;
import gda.jython.JythonServerFacade;

public class GasInjectionScannable extends ScannableBase {

	private Scannable purge_pressure;
	private Scannable purge_period;
	private Scannable purge_timeout;
	private Scannable gas_fill1_pressure;
	private Scannable gas_fill1_period;
	private Scannable gas_fill1_timeout;
	private Scannable gas_fill2_pressure;
	private Scannable gas_fill2_period;
	private Scannable gas_fill2_timeout;
	private Scannable gas_fill_start;
	private Scannable gas_select;
	private Scannable control_select;  // the combo box in the Gas Injection Rig screen. Use to abort.
	private Scannable ion_chamber_select;
	private Scannable gas_injection_status;
	private Scannable power_supply;
	private Scannable base_pressure;
	private Scannable hvStatusScannable;

	private String ion_chamber;

	private static final Logger logger = LoggerFactory.getLogger(GasInjectionScannable.class);

	private double purge_pressure_val;
	private double purge_period_val;
	private double gas_fill1_pressure_val;
	private double gas_fill1_period_val;
	private double gas_fill2_pressure_val;
	private double gas_fill2_period_val;
	private double base_pressure_val;
	private int gas_select_val;
	private String hvstatus;
	private double original_voltage;
	private boolean abortPurgeAndFillSequence;
	private boolean runningPurgeAndFillSequence;

	@Override
	public boolean isBusy() {
		return runningPurgeAndFillSequence;
	}

	public void log(String msg) {
		logger.info(msg);
		JythonServerFacade.getInstance().print(msg);
	}

	@Override
	public void configure() throws FactoryException {
		if (isConfigured()) {
			return;
		}
		super.configure();
		this.inputNames = new String[] { "purge_pressure", "purge_period", "gas_fill1_pressure", "gas_fill1_period",
				"gas_fill2_pressure", "gas_fill2_period", "gas_select" };
		this.outputFormat = new String[] { "%2d", "%2d", "%2d", "%2d", "%2d", "%2d", "%s", "%s" };
		this.extraNames = new String[] { "status" };
		setConfigured(true);
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		abortPurgeAndFillSequence = false;
		runningPurgeAndFillSequence = true;

		try {
			// before any operations, check that it is not in an aborted state, if it is then do an Abort to reset the hardware
			double currentStatus = Double.parseDouble(gas_injection_status.getPosition().toString());
			if (currentStatus > 128.0){
				// this is the ABORT option in the Control combo box in the EDM screen
				control_select.moveTo(1);
			}

			String ionc = "";
			if (ion_chamber.equals("0"))
				ionc = "I0";
			else if (ion_chamber.equals("1"))
				ionc = "It";
			else if (ion_chamber.equals("2"))
				ionc = "Iref";
			log("Gas filling of " + ionc + " started");

			if (!(position instanceof List<?>)) {
				throw new DeviceException("Supplied array must be of type List<String> to move Scannable " + getName());
			}

			@SuppressWarnings("unchecked")
			List<String> parameters = (List<String>) position;

			String flush = parameters.get(7);

			original_voltage = Double.parseDouble(power_supply.getPosition().toString());

			// pos ionc1_gas_injector ["2.0","1","0.024377","100.0","1.975623","100.0","2","True"]

			// check if voltage is below 5v.
			if (checkVoltageInRange(-5, 5)) {
				configurePurgeAndFill(parameters);
				if (Boolean.parseBoolean(flush))
					flush();
				gas_fill2_pressure.moveTo(gas_fill2_pressure_val);
				performFill((int) (purge_period_val + gas_fill1_period_val + gas_fill2_period_val));
			}

			else {
				log("Voltage is too high to fill gas");

				if (getFillStatus().equals("idle")) {
					log("Setting voltage to 0V.");
					setVoltage(0);// lower voltage to 0v
					int voltageTimeout = 300;
					while ((!checkVoltageInRange(-5, 5)) && voltageTimeout > 0) {
						try {
							Thread.sleep(1000);
						} catch (InterruptedException e) {
							e.printStackTrace();
						}
						voltageTimeout--;
					}
					purge_pressure_val = Double.parseDouble(parameters.get(0));
					gas_fill1_pressure_val = Double.parseDouble(parameters.get(2));

					if (gas_fill1_pressure_val + purge_pressure_val < 1100) {
						// check if voltage is below 5v.
						if (checkVoltageInRange(-5, 5)) {
							configurePurgeAndFill(parameters);
							if (Boolean.parseBoolean(flush))
								flush();
							gas_fill2_pressure.moveTo(gas_fill2_pressure_val);
							performFill((int) (purge_period_val + gas_fill1_period_val + gas_fill2_period_val));
						}
					} else
						log("Cannot fill gas because pressure is too high");
				} else
					log("Cannot change voltage unless gas filling is idle");
			}
		} finally {
			runningPurgeAndFillSequence = false;
			log("Gas filling finished");
		}
	}

	public void configurePurgeAndFill(List<String> parameters) throws NumberFormatException, DeviceException {
		purge_pressure_val = Double.parseDouble(parameters.get(0));
		purge_period_val = Double.parseDouble(parameters.get(1));
		gas_fill1_period_val = Double.parseDouble(parameters.get(3));
		gas_fill2_pressure_val = Double.parseDouble(parameters.get(4));
		gas_fill2_period_val = Double.parseDouble(parameters.get(5));
		gas_select_val = Integer.parseInt(parameters.get(6));
		gas_fill1_pressure_val = Double.parseDouble(parameters.get(2));

		// set ion chamber
		isAborted();
		ion_chamber_select.moveTo(Integer.parseInt(ion_chamber));
		// set purge parameters
		isAborted();
		purge_pressure.moveTo(purge_pressure_val);
		isAborted();
		purge_period.moveTo(purge_period_val);
		isAborted();
		purge_timeout.moveTo(purge_period_val + 10);
		// set gas
		// set gas fill 1 parameters
		if (gas_select_val != -1) {
			isAborted();
			gas_select.moveTo(gas_select_val);
			// gas_fill1_pressure.moveTo(gas_fill1_pressure_val + purge_pressure_val);
			isAborted();
			gas_fill1_period.moveTo(gas_fill1_period_val);
			isAborted();
			gas_fill1_timeout.moveTo(gas_fill1_period_val + 10);
		}
		// set gas fill 2 parameters
		isAborted();
		gas_fill2_period.moveTo(gas_fill2_period_val);
		isAborted();
		gas_fill2_timeout.moveTo(gas_fill2_period_val + 10);
		// set control to purge & fill
		// control_select.moveTo(0);

		try {
			isAborted();
			Thread.sleep(2000);
		} catch (InterruptedException e) {
			throw new DeviceException("Gas Purge and Fill interrupted.");
		}
	}

	private void isAborted() throws DeviceException {
		if (abortPurgeAndFillSequence) {
			throw new DeviceException("Gas Purge and Fill aborted.");
		}
	}

	@Override
	public void stop() throws DeviceException {
		// simply do no more work after the current operation has completed.
		abortPurgeAndFillSequence = true;
	}

	public void flush() {
		log("Flushing");
		try {
			control_select.moveTo(2);// Purge1
			gas_fill_start.moveTo(1);
		} catch (DeviceException e) {
			logger.error("Purge 1 Failed. Possibly a timeout waiting for pressure to reach target purge value.", e);
		}
		waitUntilIdle(300);
		try {
			gas_fill2_pressure.moveTo(500);
			control_select.moveTo(5);// Fill 2
			gas_fill_start.moveTo(1);
		} catch (DeviceException e) {
			logger.error("Gas fill 2 failed. Possibly a timeout.", e);
		}// Gas Fill 2 = 500
		waitUntilIdle(100);
		log("Flushing finished");
	}

	public void performFill(int totalFillPeriod) {
		try {
			log("Filling gas. Voltage = " + power_supply.getPosition());

			try {
				Thread.sleep(1000);
			} catch (InterruptedException e1) {
				e1.printStackTrace();
			}

			int extraTime = 10;
			int fillTimeout = totalFillPeriod + extraTime;

			waitUntilIdle(fillTimeout);

			log("Waiting for pressure to stabilise");
			try {
				Thread.sleep(5000);
			} catch (InterruptedException e1) {
				e1.printStackTrace();
			}

			if (checkVoltageInRange(-5, 5)) {
				checkForAbort();

				log("Purge 1");
				control_select.moveTo(2);
				checkForAbort();
				gas_fill_start.moveTo(1);// purge 1
				checkForAbort();
				waitUntilIdle(300);

				// -1 means He only so skip the filling 1 and second purge
				if (gas_select_val != -1) {
					base_pressure_val = Double.parseDouble(base_pressure.getPosition().toString());
					gas_fill1_pressure.moveTo(gas_fill1_pressure_val + base_pressure_val);

					log("Filling gas 1");
					control_select.moveTo(3);
					checkForAbort();
					gas_fill_start.moveTo(1);// fill 1
					checkForAbort();
					waitUntilIdle(fillTimeout);

					log("Purge 2");
					control_select.moveTo(4);
					checkForAbort();
					gas_fill_start.moveTo(1);// purge 2
					checkForAbort();
					waitUntilIdle(fillTimeout);
				}

				log("Filling gas 2");
				control_select.moveTo(5);
				checkForAbort();
				gas_fill_start.moveTo(1);// fill 2
				checkForAbort();
				waitUntilIdle(fillTimeout);

			} else
				log("Voltage too high");

			if (getFillStatus().equals("idle")) {
				log("Setting voltage to " + original_voltage + "v");

				int voltageToSet = Math.abs((int) original_voltage);
				setVoltage(voltageToSet);// raise voltage to original voltage
				int voltageTimeout = 30;
				while ((!checkVoltageInRange(-((int) original_voltage - 5), -((int) original_voltage + 5)))
						&& !checkVoltageInRange(((int) original_voltage - 5), ((int) original_voltage + 5))
						&& voltageTimeout > 0) {
					try {
						Thread.sleep(1000);
					} catch (InterruptedException e) {
						e.printStackTrace();
					}
					voltageTimeout--;
				}
			} else
				log("Gas fill did not complete as expected. Voltage will not be set automatically.");

		} catch (DeviceException e1) {
			e1.printStackTrace();
		} catch (Exception e) {
			e.printStackTrace();
			log("Gas fill did not complete as expected. It was probably aborted from epics.");
		}
		// Chris, as a suggestion, for feedback in the GUI try creating a 'job' so that feedback from the
		// control lights in the gas fill control edm screen
		// can be sent to the GDA client.
	}

	public void checkForAbort() throws Exception {
		if (getFillStatus().equals("aborted"))
			throw new Exception();
	}

	public void waitUntilIdle(int timeout) {
		// Extra sleep added to make sure previous move has finished, and gasFillStatus has time to update.
		logger.debug("waitUntilIdle({})", timeout);
		try {
			Thread.sleep(1000);
		} catch(InterruptedException e) {
			logger.debug("Exception caught while sleeping", e);
		}

		while ((getFillStatus().contains("gas") || getFillStatus().contains("helium")) && timeout > 0) {
			try {
				Thread.sleep(1000);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			timeout--;
		}
		logger.debug("waitUntilIdle finished");
	}

	public String getFillStatus() {
		double status = -1;
		String status_string = "unknown status";

		try {
			status = Double.parseDouble(gas_injection_status.getPosition().toString());
		} catch (NumberFormatException e) {
			e.printStackTrace();
		} catch (DeviceException e) {
			e.printStackTrace();
		}

		if (status == 0)
			status_string = "idle";
		else if (status == 4)
			status_string = "purging gas";
		else if (status == 8)
			status_string = "filling gas";
		else if (status == 16)
			status_string = "purging helium";
		else if (status == 32)
			status_string = "filling helium";
		else if (status == 256)
			status_string = "timeout";
		else if (status == 512)
			status_string = "aborted";
		return status_string;
	}

	public void setVoltage(int voltage) {
		try {
			power_supply.asynchronousMoveTo(voltage);
			// check if BL18B-EA-ISEG-01:V1_START is "1" then try again for 10secs and try set again
			// try 3 times
			for (int i = 0; i < 3; i++) {
				try {
					Thread.sleep(10000);
				} catch (InterruptedException e) {
				}
				hvstatus = hvStatusScannable.getPosition().toString();
				if (hvstatus.equals("1")) {
					log("Comms error with hv supply. Waiting for 10 seconds.");
					try {
						Thread.sleep(10000);
					} catch (InterruptedException e) {
					}
					log("Apply voltage change retry.");
					power_supply.asynchronousMoveTo(voltage);
				} else
					break;
			}


		} catch (DeviceException e) {
			e.printStackTrace();
		}
	}

	public boolean checkVoltageInRange(int min, int max) {
		double voltage;
		try {
			voltage = Double.parseDouble(power_supply.getPosition().toString());
			log("Voltage = " + voltage);
			if (voltage >= min && voltage <= max)
				return true;
			return false;
		} catch (Exception e) {
			e.printStackTrace();
			return false;
		}
	}

	@Override
	public Object rawGetPosition() {
		Object[] positions = new Object[8];
		try {
			positions[0] = purge_pressure.getPosition();
			positions[1] = purge_period.getPosition();
			positions[2] = gas_fill1_pressure.getPosition();
			positions[3] = gas_fill1_period.getPosition();
			positions[4] = gas_fill2_pressure.getPosition();
			positions[5] = gas_fill2_period.getPosition();
			positions[6] = gas_select.getPosition();
		} catch (Exception e) {
			e.printStackTrace();
		}
		positions[7] = getFillStatus();
		return positions;
	}

	public Scannable getPurge_pressure() {
		return purge_pressure;
	}

	public void setPurge_pressure(Scannable purgePressure) {
		purge_pressure = purgePressure;
	}

	public Scannable getPurge_period() {
		return purge_period;
	}

	public void setPurge_period(Scannable purgePeriod) {
		purge_period = purgePeriod;
	}

	public Scannable getPurge_timeout() {
		return purge_timeout;
	}

	public void setPurge_timeout(Scannable purgeTimeout) {
		purge_timeout = purgeTimeout;
	}

	public Scannable getGas_fill1_pressure() {
		return gas_fill1_pressure;
	}

	public void setGas_fill1_pressure(Scannable gasFill1Pressure) {
		gas_fill1_pressure = gasFill1Pressure;
	}

	public Scannable getGas_fill1_period() {
		return gas_fill1_period;
	}

	public void setGas_fill1_period(Scannable gasFill1Period) {
		gas_fill1_period = gasFill1Period;
	}

	public Scannable getGas_fill1_timeout() {
		return gas_fill1_timeout;
	}

	public void setGas_fill1_timeout(Scannable gasFill1Timeout) {
		gas_fill1_timeout = gasFill1Timeout;
	}

	public Scannable getGas_fill2_pressure() {
		return gas_fill2_pressure;
	}

	public void setGas_fill2_pressure(Scannable gasFill2Pressure) {
		gas_fill2_pressure = gasFill2Pressure;
	}

	public Scannable getGas_fill2_period() {
		return gas_fill2_period;
	}

	public void setGas_fill2_period(Scannable gasFill2Period) {
		gas_fill2_period = gasFill2Period;
	}

	public Scannable getGas_fill2_timeout() {
		return gas_fill2_timeout;
	}

	public void setGas_fill2_timeout(Scannable gasFill2Timeout) {
		gas_fill2_timeout = gasFill2Timeout;
	}

	public Scannable getGas_fill_start() {
		return gas_fill_start;
	}

	public void setGas_fill_start(Scannable gasFillStart) {
		gas_fill_start = gasFillStart;
	}

	public Scannable getGas_select() {
		return gas_select;
	}

	public void setGas_select(Scannable gasSelect) {
		gas_select = gasSelect;
	}

	public Scannable getControl_select() {
		return control_select;
	}

	public void setControl_select(Scannable controlSelect) {
		control_select = controlSelect;
	}

	public Scannable getIon_chamber_select() {
		return ion_chamber_select;
	}

	public void setIon_chamber_select(Scannable ionChamberSelect) {
		ion_chamber_select = ionChamberSelect;
	}

	public Scannable getGas_injection_status() {
		return gas_injection_status;
	}

	public void setGas_injection_status(Scannable gasInjectionStatus) {
		gas_injection_status = gasInjectionStatus;
	}

	public Scannable getPower_supply() {
		return power_supply;
	}

	public void setPower_supply(Scannable powerSupply) {
		power_supply = powerSupply;
	}

	public String getIon_chamber() {
		return ion_chamber;
	}

	public void setIon_chamber(String ionChamber) {
		ion_chamber = ionChamber;
	}

	public Scannable getBase_pressure() {
		return base_pressure;
	}

	public void setBase_pressure(Scannable basePressure) {
		base_pressure = basePressure;
	}

	public Scannable getHvStatusScannable() {
		return hvStatusScannable;
	}

	public void setHvStatusScannable(Scannable hvStatusScannable) {
		this.hvStatusScannable = hvStatusScannable;
	}


}