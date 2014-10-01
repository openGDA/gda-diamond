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

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

public class TimingGroupDataNode {
	private final IObservableList spectra = new WritableList(new ArrayList<SpectrumDataNode>(), SpectrumDataNode.class);
	private final String name;
	private final double timePerSpectrum;

	public TimingGroupDataNode(String name, double timePerSpectrum, List<SpectrumDataNode> spectraData) {
		this.timePerSpectrum = timePerSpectrum;
		spectra.addAll(spectraData);
		this.name = "Group " + name;
	}

	public IObservableList getSpectra() {
		return spectra;
	}

	public double getTimePerSpectrum() {
		return timePerSpectrum;
	}

	@Override
	public String toString() {
		return name;
	}
}
