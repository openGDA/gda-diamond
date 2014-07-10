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

class PhotonShutter extends TriggerableObject implements Serializable {
	public PhotonShutter() {
		this.setName("PhotoShutter");
		this.setTriggerPulseLength(TFGTrigger.DEFAULT_PULSE_WIDTH_IN_SEC);
		this.setTriggerDelay(0.1);
		this.setTriggerOutputPort(TriggerOutputPort.USR_OUT_0);
	}
}