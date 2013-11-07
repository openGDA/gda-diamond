/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.ui.views.plot.model;

import org.dawnsci.plotting.api.trace.ILineTrace;
import org.dawnsci.plotting.api.trace.ITrace;

import uk.ac.gda.exafs.data.ObservableModel;

public class DataNode extends ObservableModel {
	private ILineTrace lineTrace;

	@Override
	public String toString() {
		return "Hello";
	}

	public void setLineTrace(ILineTrace lineTrace) {
		this.lineTrace = lineTrace;
	}

	public ITrace getLineTrace() {
		return lineTrace;
	}

	public void clearLineTrace() {
		lineTrace.dispose();
		lineTrace = null;
	}
}
