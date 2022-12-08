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

public class DetectorDataCollection extends TriggerableObject implements Serializable {

	private static final long serialVersionUID = 1L;

	private static final double XCHIP_START_PULSE_WIDTH_IN_SEC = 0.001;

	private int numberOfFrames;

	public static final String COLLECTION_DURATION_PROP_NAME = "collectionDuration";
	private double collectionDuration;

	public DetectorDataCollection() {
		this.setName("Data collection");
		this.setTriggerOutputPort(TriggerOutputPort.USR_OUT_1);
		this.setTriggerDelay(0.1);
		this.setTriggerPulseLength(XCHIP_START_PULSE_WIDTH_IN_SEC);
	}

	public int getNumberOfFrames() {
		return numberOfFrames;
	}

	public void setNumberOfFrames(int numberOfFrames) {
		this.numberOfFrames = numberOfFrames;
	}

	public double getCollectionDuration() {
		return collectionDuration;
	}

	public void setCollectionDuration(double collectionDuration) {
		firePropertyChange(COLLECTION_DURATION_PROP_NAME, this.collectionDuration, this.collectionDuration = collectionDuration);
		firePropertyChange(TOTAL_DURATION_PROP_NAME, null, getTotalDuration());
		firePropertyChange(TOTAL_DELAY_PROP_NAME, null, getTotalDelay());
	}

	@Override
	public double getTotalDuration() {
		return collectionDuration >= this.getTriggerPulseLength() ? collectionDuration : this.getTriggerPulseLength();
	}
}