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

package uk.ac.gda.exafs.experiment.trigger;

import java.io.Serializable;

import com.google.gson.annotations.Expose;

import uk.ac.gda.beans.ObservableModel;

public class TriggerableObject extends ObservableModel implements Serializable, Comparable<TriggerableObject>{

	private static final long serialVersionUID = 1L;

	public enum TriggerOutputPort {
		USR_OUT_0(0, "USR OUT 0"),
		USR_OUT_1(1, "USR OUT 1"),
		USR_OUT_2(2, "USR OUT 2"),
		USR_OUT_3(3, "USR OUT 3"),
		USR_OUT_4(4, "USR OUT 4"),
		USR_OUT_5(5, "USR OUT 5"),
		USR_OUT_6(6, "USR OUT 6"),
		USR_OUT_7(7, "USR OUT 7");

		private static final int numPorts = 8;
		private final String portName;
		private final int usrPort;

		private TriggerOutputPort(int usrPort, String portName) {
			this.usrPort = usrPort;
			this.portName = portName;
		}

		public String getPortName() {
			return portName;
		}
		public int getUsrPort() {
			return (int) Math.pow(2, usrPort);
		}
		// Added imh 17/9/2015
		public int getUsrPortNumber() {
			return usrPort;
		}
		// Added imh 21/9/2015
		public static int getTotalNumPorts() {
			return numPorts;
		}
	}

	public static final String TRIGGER_DELAY_PROP_NAME = "triggerDelay";
	@Expose
	private double triggerDelay;

	public static final String TRIGGER_PULSE_LENGTH_PROP_NAME = "triggerPulseLength";
	@Expose
	private double triggerPulseLength;

	public static final String TRIGGER_OUTPUT_PORT_PROP_NAME = "triggerOutputPort";
	@Expose
	private TriggerOutputPort triggerOutputPort;

	public static final String NAME_PROP_NAME = "name";
	@Expose
	private String name;

	public static final String TOTAL_DURATION_PROP_NAME = "totalDuration";
	public static final String TOTAL_DELAY_PROP_NAME = "totalDelay";

	//Constructor added. imh 25/9/2015
	public TriggerableObject(  ) {
		triggerDelay = 0;
		triggerPulseLength = 0.0;
		triggerOutputPort = TriggerOutputPort.USR_OUT_0;
	}

	public TriggerableObject( double triggerDelay, double triggerPulseLength, TriggerOutputPort triggerOutputPort ) {
		this.triggerDelay = triggerDelay;
		this.triggerPulseLength = triggerPulseLength;
		this.triggerOutputPort = triggerOutputPort;
	}

	public double getTriggerDelay() {
		return triggerDelay;
	}

	public void setTriggerDelay(double triggerDelay) {
		firePropertyChange(TRIGGER_DELAY_PROP_NAME, this.triggerDelay, this.triggerDelay = triggerDelay);
		firePropertyChange(TOTAL_DELAY_PROP_NAME, null, getTotalDelay());
	}

	public double getTriggerPulseLength() {
		return triggerPulseLength;
	}

	public void setTriggerPulseLength(double triggerPulseLength) {
		firePropertyChange(TRIGGER_PULSE_LENGTH_PROP_NAME, this.triggerPulseLength, this.triggerPulseLength = triggerPulseLength);
		firePropertyChange(TOTAL_DURATION_PROP_NAME, null, getTotalDuration());
		firePropertyChange(TOTAL_DELAY_PROP_NAME, null, getTotalDelay());
	}

	public TriggerOutputPort getTriggerOutputPort() {
		return triggerOutputPort;
	}

	public void setTriggerOutputPort(TriggerOutputPort triggerOutputPort) {
		firePropertyChange(TRIGGER_OUTPUT_PORT_PROP_NAME, this.triggerOutputPort, this.triggerOutputPort = triggerOutputPort);
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		firePropertyChange(NAME_PROP_NAME, this.name, this.name = name);
	}

	public String getDAServerCommand() {
		// TODO
		return "";
	}

	public double getTotalDuration() {
		return getTriggerPulseLength();
	}

	public double getTotalDelay() {
		return this.getTriggerDelay() + getTotalDuration();
	}

	@Override
	public int compareTo(TriggerableObject o) {
		double delayTime=o.getTriggerDelay();
		double diff=triggerDelay-delayTime;
		if (diff<0) {
			return -1;
		} else if (diff>0) {
			return 1;
		} else {
			return 0;
		}
	}
}
