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

public class I14XanesEdgeParameters {

	private double preEdgeStart;
	private double preEdgeStop;
	private double preEdgeStep;
	private String linesToTrack = "";
	private String trackingMethod = I14XanesEdgeTrackingMethod.REFERENCE.toString();

	public double getPreEdgeStart() {
		return preEdgeStart;
	}
	public void setPreEdgeStart(double preEdgeStart) {
		this.preEdgeStart = preEdgeStart;
	}
	public double getPreEdgeStop() {
		return preEdgeStop;
	}
	public void setPreEdgeStop(double preEdgeStop) {
		this.preEdgeStop = preEdgeStop;
	}
	public double getPreEdgeStep() {
		return preEdgeStep;
	}
	public void setPreEdgeStep(double preEdgeStep) {
		this.preEdgeStep = preEdgeStep;
	}
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
	@Override
	public String toString() {
		return "I14XanesEdgeParameters [preEdgeStart=" + preEdgeStart + ", preEdgeStop=" + preEdgeStop
				+ ", preEdgeStep=" + preEdgeStep + ", linesToTrack=" + linesToTrack + ", trackingMethod="
				+ trackingMethod + "]";
	}
}
