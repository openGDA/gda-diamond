/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i14.views;

import static uk.ac.gda.beamline.i14.views.I14XanesEdgeParameters.TrackingMethod.REFERENCE;

public class I14XanesEdgeParameters {

	public enum TrackingMethod {
		REFERENCE,
		EDGE
	}

	private String linesToTrack = "";
	private String trackingMethod = REFERENCE.toString();
	private String energySteps = "";

	public String getLinesToTrack() {
		return linesToTrack;
	}

	public void setLinesToTrack(String linesToTrack) {
		this.linesToTrack = linesToTrack;
	}

	public String getTrackingMethod() {
		return trackingMethod;
	}

	public void setTrackingMethod(String trackingMethod) {
		this.trackingMethod = trackingMethod;
	}

	public String getEnergySteps() {
		return energySteps;
	}

	public void setEnergySteps(String energySteps) {
		this.energySteps = energySteps;
	}

	@Override
	public String toString() {
		return "I14XanesEdgeParameters [linesToTrack=" + linesToTrack + ", trackingMethod=" + trackingMethod
				+ ", energySteps=" + energySteps + "]";
	}

}
