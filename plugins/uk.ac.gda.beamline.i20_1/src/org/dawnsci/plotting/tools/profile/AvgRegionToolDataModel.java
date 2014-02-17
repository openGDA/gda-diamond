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

import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.region.IRegion;
import org.dawnsci.plotting.api.trace.IImageTrace;
import org.dawnsci.plotting.api.trace.ILineTrace;
import org.dawnsci.plotting.api.trace.ITrace;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.dataset.IDataset;

public class AvgRegionToolDataModel extends SpectraRegionToolDataModel {
	public AvgRegionToolDataModel(IRegion plotRegion, TimeResolvedToolDataModel parent) {
		super(plotRegion, parent);
	}

	@Override
	public ITrace[] createTraces(IPlottingSystem plottingSystem, IImageTrace imageTrace, IDataset energy) {
		DoubleDataset data = (DoubleDataset) ((DoubleDataset) imageTrace.getData().getSlice(new int[]{this.getStart().getIndex(), 0}, new int[]{this.getEnd().getIndex() + 1, TimeResolvedToolDataModel.NUMBER_OF_STRIPS}, new int[]{1,1})).mean(0);
		ILineTrace trace = plottingSystem.createLineTrace(this.getRegion().getLabel() + " avg(" + this.getStart().getIndex() + ":" + this.getEnd().getIndex() + ")");
		trace.setData(energy, data);
		regionTraces.add(trace);
		return regionTraces.toArray(new ITrace[]{});
	}
}
