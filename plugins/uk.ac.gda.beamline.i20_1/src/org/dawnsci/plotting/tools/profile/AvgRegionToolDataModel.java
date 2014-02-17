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
	private int noOfSpectraToAvg;

	public AvgRegionToolDataModel(IRegion plotRegion, TimeResolvedToolDataModel parent) {
		super(plotRegion, parent);
		noOfSpectraToAvg = this.getTotalSpectra();
	}

	public void setNoOfSpectraToAvg(int noOfSpectraToAvg) throws Exception {
		if (this.getTotalSpectra() % noOfSpectraToAvg != 0) {
			throw new Exception("Does not fit");
		}
		this.noOfSpectraToAvg = noOfSpectraToAvg;
	}

	@Override
	public ITrace[] createTraces(IPlottingSystem plottingSystem, IImageTrace imageTrace, IDataset energy) {
		for (int i = this.getStart().getIndex(); i  < this.getEnd().getIndex() + 1; i = i + noOfSpectraToAvg) {
			DoubleDataset data = (DoubleDataset) ((DoubleDataset) imageTrace.getData().getSlice(new int[]{i, 0}, new int[]{i + noOfSpectraToAvg, TimeResolvedToolDataModel.NUMBER_OF_STRIPS}, new int[]{1,1})).mean(0);
			ILineTrace trace = plottingSystem.createLineTrace(this.getRegion().getLabel() + " avg(" + i + ":" + (i + noOfSpectraToAvg - 1) + ")");
			trace.setData(energy, data);
			regionTraces.add(trace);
		}
		return regionTraces.toArray(new ITrace[]{});
	}


	@Override
	public String getDescription() {
		return "AVG";
	}
}