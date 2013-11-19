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

import java.util.ArrayList;
import java.util.List;

import org.dawnsci.plotting.api.trace.ITrace;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.beans.ObservableModel;

public class DataNode extends ObservableModel {
	private DoubleDataset xDoubleDataset;
	private final List<DoubleDataset> yDoubleDataset = new ArrayList<DoubleDataset>();
	private final String label;
	private final DatasetNode parent;
	private final String identifier;

	public static final String DATA_Y_AXIS_PROP_NAME = "yAxisData";

	private List<ITrace> lines;

	public DataNode(String identifier, String label, DatasetNode parent) {
		this.label = label;
		this.identifier = identifier;
		this.parent = parent;
	}

	public DatasetNode getParent() {
		return parent;
	}

	public List<ITrace> getLines() {
		return lines;
	}

	public void setLines(List<ITrace> lines) {
		this.lines = lines;
	}

	@Override
	public String toString() {
		return label;
	}

	public String getLabel() {
		return label;
	}

	public String getIdentifier() {
		return identifier;
	}

	public DoubleDataset getXAxisData() {
		return xDoubleDataset;
	}

	public List<DoubleDataset> getYAxisData() {
		return yDoubleDataset;
	}

	public void updateData(DoubleDataset xDoubleDataset, DoubleDataset yDoubleDataset) {
		this.xDoubleDataset = xDoubleDataset;
		this.yDoubleDataset.add(yDoubleDataset);
		this.firePropertyChange(DATA_Y_AXIS_PROP_NAME, null, this.yDoubleDataset);
	}
}
