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

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.exafs.data.ObservableModel;

public class DataNode extends ObservableModel {
	private DoubleDataset xDoubleDataset;
	private DoubleDataset yDoubleDataset;
	private final String label;
	private final DatasetNode parent;

	public static final String DATA_Y_AXIS_PROP_NAME = "yAxisData";

	public DataNode(String label, DatasetNode parent) {
		this.label = label;
		this.parent = parent;
	}

	public DatasetNode getParent() {
		return parent;
	}

	@Override
	public String toString() {
		return label;
	}

	public String getLabel() {
		return label;
	}

	public String getIdentifier() {
		return parent + "@" + label;
	}

	public DoubleDataset getXAxisData() {
		return xDoubleDataset;
	}

	public DoubleDataset getYAxisData() {
		return yDoubleDataset;
	}

	public void updateData(DoubleDataset xDoubleDataset, DoubleDataset yDoubleDataset) {
		this.xDoubleDataset = xDoubleDataset;
		this.firePropertyChange(DATA_Y_AXIS_PROP_NAME, this.yDoubleDataset, this.yDoubleDataset = yDoubleDataset);
	}
}
