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

import org.eclipse.core.databinding.observable.list.IObservableList;

import uk.ac.gda.beans.ObservableModel;

public abstract class DataNode extends ObservableModel {

	protected final DataNode parent;

	public static final String DATA_CHANGED_PROP_NAME = "changedData";

	public static final String DATA_ADDED_PROP_NAME = "addedData";

	public DataNode(DataNode parent) {
		this.parent = parent;
	}

	public abstract IObservableList getChildren();

	public DataNode getParent() {
		return parent;
	}

	public String getLabel() {
		return toString();
	}

	public abstract String getIdentifier();
}
