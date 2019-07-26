/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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
import gda.device.detector.DetectorBase;
import gda.epics.CAClient;
import gda.factory.FactoryException;
import gov.aps.jca.CAException;
import gov.aps.jca.TimeoutException;

public class PulseTube extends DetectorBase {

	private static final long serialVersionUID = 1L;

	private CAClient ca_client = new CAClient();

	private String t1_pv;
	private String t2_pv;
	private String t3_pv;
	private String target_pv;
	private String error_pv;
	private String prop_gain_pv;
	private String int_gain_pv;
	private String der_gain_pv;
	private String gas_flow_pv;
	private String heater_voltage_pv;
	private String heater_output_pv;
	private String heater_mode_pv;
	private double[] data;

	@Override
	public void configure() throws FactoryException {
		if (isConfigured()) {
			return;
		}
		super.configure();
		this.inputNames = new String[] {};
		this.outputFormat = new String[] { "%.3d", "%.3d", "%.3d", "%.3d", "%.3d", "%.3d", "%.3d", "%.3d",
				"%.3d", "%.3d", "%.3d", "%.3d" };
		this.extraNames = new String[] { "t1", "t2", "t3", "target", "error", "prop_gain", "int_gain", "der_gain",
				"gas_flow", "heater_voltage", "heater_output", "heater_mode" };
		setConfigured(true);
	}

	@Override
	public void asynchronousMoveTo(Object collectionTime) throws DeviceException {
		setTarget(Double.parseDouble(collectionTime.toString()));
	}

	public void setTarget(double val) {
		try {
			ca_client.caput(target_pv + ":SET", val);
		} catch (CAException e) {
		} catch (InterruptedException e) {
		}
	}

	public void setPropGain(double val) {
		try {
			ca_client.caput(prop_gain_pv + ":SET", val);
		} catch (CAException e) {
		} catch (InterruptedException e) {
		}
	}

	public void setIntGain(double val) {
		try {
			ca_client.caput(int_gain_pv + ":SET", val);
		} catch (CAException e) {
		} catch (InterruptedException e) {
		}
	}

	public void setDerGain(double val) {
		try {
			ca_client.caput(der_gain_pv + ":SET", val);
		} catch (CAException e) {
		} catch (InterruptedException e) {
		}
	}

	public void setGasFlow(double val) {
		try {
			ca_client.caput(gas_flow_pv + ":SET", val);
		} catch (CAException e) {
		} catch (InterruptedException e) {
		}
	}

	@Override
	public void collectData() throws DeviceException {
		data = new double[12];
		try {
			data[0] = Double.parseDouble(ca_client.caget(t1_pv).toString());
			data[1] = Double.parseDouble(ca_client.caget(t2_pv).toString());
			data[2] = Double.parseDouble(ca_client.caget(t3_pv).toString());
			data[3] = Double.parseDouble(ca_client.caget(target_pv).toString());
			data[4] = Double.parseDouble(ca_client.caget(error_pv).toString());
			data[5] = Double.parseDouble(ca_client.caget(prop_gain_pv).toString());
			data[6] = Double.parseDouble(ca_client.caget(int_gain_pv).toString());
			data[7] = Double.parseDouble(ca_client.caget(der_gain_pv).toString());
			data[8] = Double.parseDouble(ca_client.caget(gas_flow_pv).toString());
			data[9] = Double.parseDouble(ca_client.caget(heater_voltage_pv).toString());
			data[10] = Double.parseDouble(ca_client.caget(heater_output_pv).toString());
			data[11] = Double.parseDouble(ca_client.caget(heater_mode_pv).toString());
		} catch (NumberFormatException e) {
		} catch (CAException e) {
		} catch (TimeoutException e) {
		} catch (InterruptedException e) {
		}

		try {
			Thread.sleep((long) collectionTime * 1000);
		} catch (InterruptedException e) {
		}
	}

	@Override
	public int getStatus() throws DeviceException {
		return 0;
	}

	@Override
	public Object getPosition() throws DeviceException {
		collectData();
		return readout();
	}

	@Override
	public Object readout() throws DeviceException {
		return data;
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {
		return false;
	}

	@Override
	public String getDescription() throws DeviceException {
		return "pulsetube";
	}

	@Override
	public String getDetectorID() throws DeviceException {
		return "unknown";
	}

	@Override
	public String getDetectorType() throws DeviceException {
		return "unknown";
	}

	public String getT1_pv() {
		return t1_pv;
	}

	public void setT1_pv(String t1_pv) {
		this.t1_pv = t1_pv;
	}

	public String getT2_pv() {
		return t2_pv;
	}

	public void setT2_pv(String t2_pv) {
		this.t2_pv = t2_pv;
	}

	public String getT3_pv() {
		return t3_pv;
	}

	public void setT3_pv(String t3_pv) {
		this.t3_pv = t3_pv;
	}

	public String getTarget_pv() {
		return target_pv;
	}

	public void setTarget_pv(String target_pv) {
		this.target_pv = target_pv;
	}

	public String getError_pv() {
		return error_pv;
	}

	public void setError_pv(String error_pv) {
		this.error_pv = error_pv;
	}

	public String getProp_gain_pv() {
		return prop_gain_pv;
	}

	public void setProp_gain_pv(String prop_gain_pv) {
		this.prop_gain_pv = prop_gain_pv;
	}

	public String getInt_gain_pv() {
		return int_gain_pv;
	}

	public void setInt_gain_pv(String int_gain_pv) {
		this.int_gain_pv = int_gain_pv;
	}

	public String getDer_gain_pv() {
		return der_gain_pv;
	}

	public void setDer_gain_pv(String der_gain_pv) {
		this.der_gain_pv = der_gain_pv;
	}

	public String getGas_flow_pv() {
		return gas_flow_pv;
	}

	public void setGas_flow_pv(String gas_flow_pv) {
		this.gas_flow_pv = gas_flow_pv;
	}

	public String getHeater_voltage_pv() {
		return heater_voltage_pv;
	}

	public void setHeater_voltage_pv(String heater_voltage_pv) {
		this.heater_voltage_pv = heater_voltage_pv;
	}

	public String getHeater_output_pv() {
		return heater_output_pv;
	}

	public void setHeater_output_pv(String heater_output_pv) {
		this.heater_output_pv = heater_output_pv;
	}

	public String getHeater_mode_pv() {
		return heater_mode_pv;
	}

	public void setHeater_mode_pv(String heater_mode_pv) {
		this.heater_mode_pv = heater_mode_pv;
	}
}
