/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i14.views.beamlinereadiness;

import java.util.List;

import gda.factory.FindableBase;

/**
 * Parameters for deciding whether the beamline is ready for data collection
 */
public class BeamlineReadinessParameters extends FindableBase {
	/**
	 * Names of scannables of the shutters that must be open
	 */
	private List<String> shutters;

	/**
	 * Name of scannable for ring current
	 */
	private String ringCurrent;

	/**
	 * Minimum ring current (in mA) that constitutes "beam on"
	 */
	private double ringCurrentThreshold = 50;

	/**
	 * Name of scannable for beam's x position
	 */
	private String xPosition;

	/**
	 * Name of scannable for beam's y position
	 */
	private String yPosition;

	/**
	 * Name of scannable for beam intensity
	 */
	private String intensity;

	/**
	 * Name of scannable for beam energy
	 */
	private String energy;

	/**
	 * File containing target beam intensity for various energies
	 */
	private String targetIntensitiesFile;

	/**
	 * Maximum % difference between beam's x position and the corresponding setpoint
	 */
	private double xTolerance = 5.0;

	/**
	 * Maximum % difference between beam's y position and the corresponding setpoint
	 */
	private double yTolerance = 5.0;

	/**
	 * Percentage by which the beam's intensity can fall short of the target
	 */
	private double intensityTolerance = 20.0;

	// -----------------------------------------------------------------------------------------------

	public List<String> getShutters() {
		return shutters;
	}

	public void setShutters(List<String> shutters) {
		this.shutters = shutters;
	}

	public String getRingCurrent() {
		return ringCurrent;
	}

	public void setRingCurrent(String ringCurrent) {
		this.ringCurrent = ringCurrent;
	}

	public double getRingCurrentThreshold() {
		return ringCurrentThreshold;
	}

	public void setRingCurrentThreshold(double ringCurrentThreshold) {
		this.ringCurrentThreshold = ringCurrentThreshold;
	}

	public String getxPosition() {
		return xPosition;
	}

	public void setxPosition(String xPosition) {
		this.xPosition = xPosition;
	}

	public String getyPosition() {
		return yPosition;
	}

	public void setyPosition(String yPosition) {
		this.yPosition = yPosition;
	}

	public String getIntensity() {
		return intensity;
	}

	public void setIntensity(String intensity) {
		this.intensity = intensity;
	}

	public String getEnergy() {
		return energy;
	}

	public void setEnergy(String energy) {
		this.energy = energy;
	}

	public String getTargetIntensitiesFile() {
		return targetIntensitiesFile;
	}

	public void setTargetIntensitiesFile(String targetIntensitiesFile) {
		this.targetIntensitiesFile = targetIntensitiesFile;
	}

	public double getxTolerance() {
		return xTolerance;
	}

	public void setxTolerance(double xTolerance) {
		this.xTolerance = xTolerance;
	}

	public double getyTolerance() {
		return yTolerance;
	}

	public void setyTolerance(double yTolerance) {
		this.yTolerance = yTolerance;
	}

	public double getIntensityTolerance() {
		return intensityTolerance;
	}

	public void setIntensityTolerance(double intensityTolerance) {
		this.intensityTolerance = intensityTolerance;
	}


	@Override
	public String toString() {
		return "BeamlineReadinessParameters [shutters=" + shutters + ", ringCurrent=" + ringCurrent
				+ ", ringCurrentThreshold=" + ringCurrentThreshold + ", xPosition=" + xPosition + ", yPosition="
				+ yPosition + ", intensity=" + intensity + ", energy=" + energy + ", targetIntensitiesFile="
				+ targetIntensitiesFile + ", xTolerance=" + xTolerance + ", yTolerance=" + yTolerance + ", intensityTolerance="
				+ intensityTolerance + "]";
	}

}
