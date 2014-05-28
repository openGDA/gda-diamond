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

package uk.ac.gda.exafs.ui.data;

/**
 * Extra parameters for It scans beyond those used by I0, IRef and Darks.
 */
public class EdeItScanParameters extends EdeScanParameters {

	// TODO need extra options for Sample Environment pulses (duration, rising edge etc.)
	// the nature of the signals to the photon shutter and the detector will be fixed

	// these are all the time between the Top-up completing and when the trigger signal is sent out
	private double delayToSamEnv0Trigger = -1; // USR OUT 0
	private double delayToSamEnv1Trigger = -1; // USR OUT 1
	private double delayToSamEnv2Trigger = -1; // USR OUT 2
	private double delayToSamEnv3Trigger = -1; // USR OUT 3
	private double delayToSamEnv4Trigger = -1; // USR OUT 4
	private double delayToSamEnv5Trigger = -1; // USR OUT 5
	private double delayToShutterOpen = 0;     // USR OUT 6
	private double delayToDetectorTrigger = -1; // USR OUT 7

	public double getDelayToShutterOpen() {
		return delayToShutterOpen;
	}

	public void setDelayToShutterOpen(double delayToShutterOpen) {
		this.delayToShutterOpen = delayToShutterOpen;
	}

	public double getDelayToSamEnv0Trigger() {
		return delayToSamEnv0Trigger;
	}

	public void setDelayToSamEnv0Trigger(double delayToSamEnv0Trigger) {
		this.delayToSamEnv0Trigger = delayToSamEnv0Trigger;
	}

	public double getDelayToSamEnv1Trigger() {
		return delayToSamEnv1Trigger;
	}

	public void setDelayToSamEnv1Trigger(double delayToSamEnv1Trigger) {
		this.delayToSamEnv1Trigger = delayToSamEnv1Trigger;
	}

	public double getDelayToSamEnv2Trigger() {
		return delayToSamEnv2Trigger;
	}

	public void setDelayToSamEnv2Trigger(double delayToSamEnv2Trigger) {
		this.delayToSamEnv2Trigger = delayToSamEnv2Trigger;
	}

	public double getDelayToSamEnv3Trigger() {
		return delayToSamEnv3Trigger;
	}

	public void setDelayToSamEnv3Trigger(double delayToSamEnv3Trigger) {
		this.delayToSamEnv3Trigger = delayToSamEnv3Trigger;
	}

	public double getDelayToSamEnv4Trigger() {
		return delayToSamEnv4Trigger;
	}

	public void setDelayToSamEnv4Trigger(double delayToSamEnv4Trigger) {
		this.delayToSamEnv4Trigger = delayToSamEnv4Trigger;
	}

	public double getDelayToSamEnv5Trigger() {
		return delayToSamEnv5Trigger;
	}

	public void setDelayToSamEnv5Trigger(double delayToSamEnv5Trigger) {
		this.delayToSamEnv5Trigger = delayToSamEnv5Trigger;
	}

	public double getDelayToDetectorTrigger() {
		return delayToDetectorTrigger;
	}

	public void setDelayToDetectorTrigger(double delayToDetectorTrigger) {
		this.delayToDetectorTrigger = delayToDetectorTrigger;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = super.hashCode();
		long temp;
		temp = Double.doubleToLongBits(delayToDetectorTrigger);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(delayToSamEnv0Trigger);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(delayToSamEnv1Trigger);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(delayToSamEnv2Trigger);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(delayToSamEnv3Trigger);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(delayToSamEnv4Trigger);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(delayToSamEnv5Trigger);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(delayToShutterOpen);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj) {
			return true;
		}
		if (!super.equals(obj)) {
			return false;
		}
		if (getClass() != obj.getClass()) {
			return false;
		}
		EdeItScanParameters other = (EdeItScanParameters) obj;
		if (Double.doubleToLongBits(delayToDetectorTrigger) != Double.doubleToLongBits(other.delayToDetectorTrigger)) {
			return false;
		}
		if (Double.doubleToLongBits(delayToSamEnv0Trigger) != Double.doubleToLongBits(other.delayToSamEnv0Trigger)) {
			return false;
		}
		if (Double.doubleToLongBits(delayToSamEnv1Trigger) != Double.doubleToLongBits(other.delayToSamEnv1Trigger)) {
			return false;
		}
		if (Double.doubleToLongBits(delayToSamEnv2Trigger) != Double.doubleToLongBits(other.delayToSamEnv2Trigger)) {
			return false;
		}
		if (Double.doubleToLongBits(delayToSamEnv3Trigger) != Double.doubleToLongBits(other.delayToSamEnv3Trigger)) {
			return false;
		}
		if (Double.doubleToLongBits(delayToSamEnv4Trigger) != Double.doubleToLongBits(other.delayToSamEnv4Trigger)) {
			return false;
		}
		if (Double.doubleToLongBits(delayToSamEnv5Trigger) != Double.doubleToLongBits(other.delayToSamEnv5Trigger)) {
			return false;
		}
		if (Double.doubleToLongBits(delayToShutterOpen) != Double.doubleToLongBits(other.delayToShutterOpen)) {
			return false;
		}
		return true;
	}

}
