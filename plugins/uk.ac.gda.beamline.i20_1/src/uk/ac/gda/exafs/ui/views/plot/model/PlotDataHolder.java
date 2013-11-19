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

import gda.factory.Finder;
import gda.jython.IScanDataPointObserver;
import gda.observable.IObservable;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.EdeExperimentProgressBean;
import gda.scan.ede.EdeScanProgressBean;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.swt.widgets.Display;

import uk.ac.gda.exafs.data.ObservableModel;

public class PlotDataHolder extends ObservableModel implements IScanDataPointObserver {

	private final Map<String, DatasetNode> scans = new HashMap<String, DatasetNode>();
	private final IObservableList dataset = new WritableList(new ArrayList<DatasetNode>(), DatasetNode.class);

	public static final String DATA_CHANGED_PROP_NAME = "changedData";
	private DataNode changedData;


	public PlotDataHolder() {
		((IObservable) Finder.getInstance().findNoWarn(EdeExperiment.PROGRESS_UPDATER_NAME)).addIObserver(this);
	}

	public IObservableList getDataset() {
		return dataset;
	}

	@Override
	public void update(final Object source, final Object arg) {
		Display.getDefault().asyncExec(new Runnable() {
			@Override
			public void run() {
				updateDataSetInUI(source, arg);
			}
		});
	}

	public DataNode getChangedData() {
		return changedData;
	}

	// TODO Changed to linked list!
	@SuppressWarnings("unchecked")
	protected void updateDataSetInUI(@SuppressWarnings("unused") Object source, Object arg) {
		if (arg instanceof EdeExperimentProgressBean) {
			final EdeExperimentProgressBean edeExperimentProgress = (EdeExperimentProgressBean) arg;
			final EdeScanProgressBean edeScanProgress = edeExperimentProgress.getProgress();
			final String scanIdentifier = edeScanProgress.getThisPoint().getScanIdentifier();
			DatasetNode datasetNode;
			if (!scans.containsKey(scanIdentifier)) {
				final DatasetNode newNode = new DatasetNode(scanIdentifier);
				scans.put(scanIdentifier, newNode);
				dataset.add(0, newNode);
				datasetNode = newNode;
			} else {
				datasetNode = scans.get(scanIdentifier);
			}
			DataNode dataNode = datasetNode.updateData((EdeExperimentProgressBean) arg);
			this.firePropertyChange(DATA_CHANGED_PROP_NAME, null, dataNode);
		}
	}
}
