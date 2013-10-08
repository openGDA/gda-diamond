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

package uk.ac.gda.exafs.ui.data.experiment;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.observable.list.WritableList;

public class SpectrumModel extends ExperimentTimingDataModel {

	private final TimingGroupModel parent;

	WritableList accumulationList = new WritableList(new ArrayList<Accumulation>(), Accumulation.class);
	public List<?> getAccumulationList() {
		return accumulationList;
	}

	public SpectrumModel(TimingGroupModel parent) {
		this.parent = parent;
	}

	public TimingGroupModel getParent() {
		return parent;
	}

	@Override
	public void dispose() {
		//
	}
}
