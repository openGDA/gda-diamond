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

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.beans.ObservableModel;

public class DataNode extends ObservableModel {
	private DoubleDataset xDoubleDataset;

	public static final String DATA_SET_Y_AXIS_PROP_NAME = "yDoubleDataset";
	private final IObservableList yDoubleDataset = new WritableList(new ArrayList<DataItemNode>(), DataItemNode.class);
	private final String label;
	private final DatasetNode parent;
	private final String identifier;

	public static final String DATA_Y_AXIS_PROP_NAME = "yAxisData";
	private DataItemNode yAxisData;

	public DataNode(String identifier, String label, DatasetNode parent) {
		this.label = label;
		this.identifier = identifier;
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
		return identifier;
	}

	public DoubleDataset getXAxisData() {
		return xDoubleDataset;
	}

	public DataItemNode getYAxisData() {
		return yAxisData;
	}

	public IObservableList getYDoubleDataset() {
		return yDoubleDataset;
	}

	public DataItemNode updateData(DoubleDataset xDoubleDataset, DoubleDataset yDoubleDataset, String identifier, String label) {
		this.xDoubleDataset = xDoubleDataset;
		yAxisData = new DataItemNode(identifier, label, yDoubleDataset, this);
		this.yDoubleDataset.add(yAxisData);
		this.firePropertyChange(DATA_Y_AXIS_PROP_NAME, null, yAxisData);
		return yAxisData;
	}

	public static class DataItemNode extends ObservableModel {
		private final String identifier;
		private final DoubleDataset data;
		private final DataNode parent;
		private final String label;

		public DataItemNode(String identifier, String label, DoubleDataset data, DataNode parent) {
			this.identifier = identifier;
			this.data = data;
			this.parent = parent;
			this.label = label;
		}
		public DoubleDataset getData() {
			return data;
		}
		public String getIdentifier() {
			return identifier;
		}
		public DataNode getParent() {
			return parent;
		}
		@Override
		public String toString() {
			return label;
		}
	}
}
