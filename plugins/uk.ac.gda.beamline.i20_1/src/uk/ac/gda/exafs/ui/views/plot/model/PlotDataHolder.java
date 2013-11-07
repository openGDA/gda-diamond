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

import gda.jython.IScanDataPointObserver;
import gda.jython.InterfaceProvider;
import gda.scan.IScanDataPoint;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.core.databinding.observable.set.IObservableSet;
import org.eclipse.core.databinding.observable.set.WritableSet;
import org.eclipse.swt.widgets.Display;

public enum PlotDataHolder implements IScanDataPointObserver {
	INSTANCE;

	private final Map<String, DatasetNode> scans = new HashMap<String, DatasetNode>();
	private final IObservableSet dataset = new WritableSet(new ArrayList<DatasetNode>(), DatasetNode.class);

	private final IObservableList selectedNodes = new WritableList(new ArrayList<DataNode>(), DataNode.class);

	private final boolean isInitialised = false;

	private PlotDataHolder() {}

	public IObservableList getSelectedNodes() {
		return selectedNodes;
	}

	public void initialise() {
		if (!isInitialised) {
			InterfaceProvider.getScanDataPointProvider().addIScanDataPointObserver(this);
		}
	}

	public IObservableSet getDataset() {
		return dataset;
	}

	@Override
	public void update(Object source, Object arg) {
		if (arg instanceof IScanDataPoint) {
			DatasetNode datasetNode;
			if (!scans.containsKey(((IScanDataPoint) arg).getScanIdentifier())) {
				final DatasetNode newNode = new DatasetNode();
				scans.put(((IScanDataPoint) arg).getScanIdentifier(), newNode);
				Display.getDefault().asyncExec(new Runnable() {
					@Override
					public void run() {
						dataset.add(newNode);
					}
				});
				datasetNode = newNode;
			} else {
				datasetNode = scans.get(((IScanDataPoint) arg).getScanIdentifier());
			}
			datasetNode.updateData((IScanDataPoint) arg);
		}
	}

}
