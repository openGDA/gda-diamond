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

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

public class TimingGroupToolDataModel {
	private final IObservableList spectra = new WritableList(new ArrayList<SpectrumToolDataModel>(), SpectrumToolDataModel.class);
	private final String name;
	private final double timePerFrame;

	public TimingGroupToolDataModel(String name, double timePerFrame, List<SpectrumToolDataModel> spectraData) {
		this.timePerFrame = timePerFrame;
		spectra.addAll(spectraData);
		this.name = "Group " + name;
	}

	public IObservableList getSpectra() {
		return spectra;
	}

	public double getTimePerFrame() {
		return timePerFrame;
	}

	@Override
	public String toString() {
		return name;
	}
}
