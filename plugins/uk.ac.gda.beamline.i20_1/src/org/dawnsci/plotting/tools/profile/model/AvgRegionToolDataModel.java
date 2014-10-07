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

import org.eclipse.dawnsci.analysis.dataset.impl.DatasetUtils;
import org.eclipse.dawnsci.analysis.dataset.impl.DoubleDataset;
import org.eclipse.dawnsci.plotting.api.region.IRegion;

public class AvgRegionToolDataModel extends SpectraRegionDataNode {
	private int noOfSpectraToAvg;

	public AvgRegionToolDataModel(IRegion plotRegion, TimeResolvedDataNode parent) {
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
	public DoubleDataset getDataset(DoubleDataset fullData) {
		DoubleDataset result = new DoubleDataset(new int[]{0, TimeResolvedDataNode.NUMBER_OF_STRIPS});
		for (int i = this.getStart().getIndex(); i  < this.getEnd().getIndex() + 1; i = i + noOfSpectraToAvg) {
			DoubleDataset data = (DoubleDataset) ((DoubleDataset) fullData.getSliceView(new int[]{i, 0}, new int[]{i + noOfSpectraToAvg, TimeResolvedDataNode.NUMBER_OF_STRIPS}, new int[]{1,1})).mean(0);
			data.setShape(new int[]{1, TimeResolvedDataNode.NUMBER_OF_STRIPS});
			result = (DoubleDataset) DatasetUtils.append(result, data, 0);
		}
		return result;
	}

	@Override
	public String toString() {
		return super.toString() + " avg(" + noOfSpectraToAvg + ")";
	}

	public int getNoOfSpectraToAvg() {
		return noOfSpectraToAvg;
	}
}