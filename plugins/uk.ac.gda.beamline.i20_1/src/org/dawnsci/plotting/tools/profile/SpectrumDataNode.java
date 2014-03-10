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

package org.dawnsci.plotting.tools.profile;

import org.dawnsci.plotting.api.trace.ITrace;


public class SpectrumDataNode {
	private final double startTime;
	private final int index;
	private final String name;
	private ITrace trace;

	public SpectrumDataNode(int index, double startTime) {
		this.startTime = startTime;
		this.index = index;
		name = "Spectrum " + index;
	}

	public double getStartTime() {
		return startTime;
	}

	public int getIndex() {
		return index;
	}

	@Override
	public String toString() {
		return name;
	}

	public ITrace getTrace() {
		return trace;
	}

	public void setTrace(ITrace trace) {
		this.trace = trace;
	}

	public void clearTrace() {
		trace = null;
	}
}
