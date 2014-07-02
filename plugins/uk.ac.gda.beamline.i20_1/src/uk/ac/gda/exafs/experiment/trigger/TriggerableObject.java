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

import uk.ac.gda.beans.ObservableModel;

public class TriggerableObject extends ObservableModel {

	public enum TriggerOutputPort {
		USR_OUT_0(0, "USR OUT 0"),
		USR_OUT_1(1, "USR OUT 1"),
		USR_OUT_2(2, "USR OUT 2"),
		USR_OUT_3(3, "USR OUT 3"),
		USR_OUT_4(4, "USR OUT 4"),
		USR_OUT_5(5, "USR OUT 5"),
		USR_OUT_6(6, "USR OUT 6"),
		USR_OUT_7(7, "USR OUT 7");

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
			return usrPort;
		}
	}

	public static final String TRIGGER_DELAY_PROP_NAME = "triggerDelay";
	private double triggerDelay;

	public static final String TRIGGER_PAUSE_LENGTH_PROP_NAME = "triggerPauseLength";
	private double triggerPauseLength;

	public static final String TRIGGER_OUTPUT_PORT_PROP_NAME = "triggerOutputPort";
	private TriggerOutputPort triggerOutputPort;

	public static final String NAME_PROP_NAME = "name";
	private String name;

	public double getTriggerDelay() {
		return triggerDelay;
	}

	public void setTriggerDelay(double triggerDelay) {
		this.triggerDelay = triggerDelay;
	}

	public double getTriggerPauseLength() {
		return triggerPauseLength;
	}

	public void setTriggerPauseLength(double triggerPauseLength) {
		this.triggerPauseLength = triggerPauseLength;
	}

	public TriggerOutputPort getTriggerOutputPort() {
		return triggerOutputPort;
	}

	public void setTriggerOutputPort(TriggerOutputPort triggerOutputPort) {
		this.triggerOutputPort = triggerOutputPort;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getDAServerCommand() {
		// TODO
		return "";
	}
}
