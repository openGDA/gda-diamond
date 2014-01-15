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
import gda.jython.InterfaceProvider;
import gda.observable.IObservable;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.EdeExperimentProgressBean;
import gda.scan.ede.EdeExperimentProgressBean.ExperimentCollectionType;
import gda.scan.ede.EdeScanProgressBean;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.swt.widgets.Display;

public class ExperimentDataNode extends DataNode implements IScanDataPointObserver {

	private final Map<String, ScanDataNode> scans = new HashMap<String, ScanDataNode>();
	private final IObservableList dataset = new WritableList(new ArrayList<ScanDataNode>(), ScanDataNode.class);

	private DataNode changedData;

	public ExperimentDataNode() {
		super(null);
		((IObservable) Finder.getInstance().findNoWarn(EdeExperiment.PROGRESS_UPDATER_NAME)).addIObserver(this);
		InterfaceProvider.getScanDataPointProvider().addIScanDataPointObserver(this);
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

	// FIXME Changed to linked list or change viewer to reverse the order!
	@SuppressWarnings("unchecked")
	protected void updateDataSetInUI(@SuppressWarnings("unused") Object source, Object arg) {
		if (arg instanceof EdeExperimentProgressBean) {
			final EdeExperimentProgressBean edeExperimentProgress = (EdeExperimentProgressBean) arg;
			final EdeScanProgressBean edeScanProgress = edeExperimentProgress.getProgress();
			final String scanIdentifier = edeScanProgress.getThisPoint().getScanIdentifier();
			ScanDataNode datasetNode;
			if (!scans.containsKey(scanIdentifier)) {
				boolean isMulti = (edeExperimentProgress.getExperimentCollectionType() == ExperimentCollectionType.MULTI);
				final ScanDataNode newNode = new ScanDataNode(scanIdentifier, isMulti, this);
				scans.put(scanIdentifier, newNode);
				dataset.add(0, newNode);
				datasetNode = newNode;
			} else {
				datasetNode = scans.get(scanIdentifier);
			}
			changedData = datasetNode.updateData((EdeExperimentProgressBean) arg);
			this.firePropertyChange(DATA_CHANGED_PROP_NAME, null, changedData);
		}
	}

	@Override
	public IObservableList getChildren() {
		return dataset;
	}

	@Override
	public String getIdentifier() {
		return null;
	}
}
