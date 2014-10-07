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

package org.dawnsci.plotting.tools.profile.model;

import org.eclipse.dawnsci.plotting.api.trace.ITrace;


public class SpectrumDataNode {
	private final double endTime;
	private final int index;
	private final String name;
	private final boolean isAveraged;
	private ITrace trace;

	public SpectrumDataNode(int index, double endTime, boolean isAveraged) {
		this.endTime = endTime;
		this.index = index;
		this.isAveraged = isAveraged;
		name = "Spectrum " + index;
	}

	public double getEndTime() {
		return endTime;
	}

	public int getIndex() {
		return index;
	}

	@Override
	public String toString() {
		return Integer.toString(index);
	}

	public ITrace getTrace() {
		return trace;
	}

	public void setTrace(ITrace trace) {
		this.trace = trace;
	}

	public boolean isAveraged() {
		return isAveraged;
	}

	public void clearTrace() {
		trace = null;
	}
}
