/*-
 * Copyright © 2016 Diamond Light Source Ltd.
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

package gda.scan;

import com.thoughtworks.xstream.annotations.XStreamAlias;

/**
 * Class to specify a single timing group i.e. set of identical sweeps of the slit
 * for a Turbo XAS scan.
 * @since 14/7/2016
 */
@XStreamAlias("TimingGroup")
public class TurboSlitTimingGroup {

	private String name; // TimingGroup.label
	private double timePerSpectrum; // TimingGroup.timePerFrame
	private double timeBetweenSpectra; //
	private int numSpectra; // TimingGroup.numberOfFrames

	/** Create a new timing group for a series of identical Turbo Xas slit scans.
	 * @param name
	 * @param timePerSpectrum
	 * @param timeBetweenSpectra
	 * @param numSpectra
	 */
	public TurboSlitTimingGroup( String name, double timePerSpectrum, double timeBetweenSpectra, int numSpectra) {
		this.setName(name);
		this.setTimePerSpectrum(timePerSpectrum);
		this.setTimeBetweenSpectra(timeBetweenSpectra);
		this.setNumSpectra(numSpectra);
	}

	public TurboSlitTimingGroup() {
		this("default", 1.0, 2.0, 3 );
	}

	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}

	public double getTimeBetweenSpectra() {
		return timeBetweenSpectra;
	}
	public void setTimeBetweenSpectra(double timeBetweenSpectra) {
		this.timeBetweenSpectra = timeBetweenSpectra;
	}

	public double getTimePerSpectrum() {
		return timePerSpectrum;
	}
	public void setTimePerSpectrum(double timePerSpectrum) {
		this.timePerSpectrum = timePerSpectrum;
	}

	public int getNumSpectra() {
		return numSpectra;
	}
	public void setNumSpectra(int numSpectra) {
		this.numSpectra = numSpectra;
	}
}