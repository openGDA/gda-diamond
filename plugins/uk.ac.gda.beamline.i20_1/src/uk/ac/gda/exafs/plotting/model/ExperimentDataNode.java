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

package uk.ac.gda.exafs.plotting.model;

import gda.device.detector.XHDetector;
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

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.client.plotting.model.DataNode;

public class ExperimentDataNode extends DataNode implements IScanDataPointObserver {

	public final static DoubleDataset stripsData = new DoubleDataset(XHDetector.getStripsInDouble());

	private final Map<Integer, ScanDataNode> scans = new HashMap<Integer, ScanDataNode>();
	private final IObservableList dataset = new WritableList(new ArrayList<ScanDataNode>(), ScanDataNode.class);

	private DataNode changedData;

	public static final String USE_STRIPS_AS_X_AXIS_PROP_NAME = "useStripsAsXaxis";
	private boolean useStripsAsXaxis;

	private DataNode addedData;

	public ExperimentDataNode() {
		super(null);
		((IObservable) Finder.getInstance().findNoWarn(EdeExperiment.PROGRESS_UPDATER_NAME)).addIObserver(this);
		InterfaceProvider.getScanDataPointProvider().addIScanDataPointObserver(this);
	}

	public boolean isUseStripsAsXaxis() {
		return useStripsAsXaxis;
	}

	public void setUseStripsAsXaxis(boolean useStripsAsXaxis) {
		this.firePropertyChange(USE_STRIPS_AS_X_AXIS_PROP_NAME, this.useStripsAsXaxis, this.useStripsAsXaxis = useStripsAsXaxis);
		updateScansData();
	}

	private void updateScansData() {
		for (Object scanObj: dataset) {
			for (Object spectraObj: ((ScanDataNode) scanObj).getChildren()) {
				SpectraNode spectraNode = (SpectraNode) spectraObj;
				for (Object scanDataObj: spectraNode.getChildren()) {
					this.firePropertyChange(DATA_CHANGED_PROP_NAME, null, scanDataObj);
				}
			}
		}
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

	public DataNode getAddedData() {
		return addedData;
	}

	// FIXME Changed to linked list or change viewer to reverse the order!
	@SuppressWarnings("unchecked")
	protected void updateDataSetInUI(@SuppressWarnings("unused") Object source, Object arg) {
		if (arg instanceof EdeExperimentProgressBean) {
			final EdeExperimentProgressBean edeExperimentProgress = (EdeExperimentProgressBean) arg;
			final EdeScanProgressBean edeScanProgress = edeExperimentProgress.getProgress();
			final int scanIdentifier = edeScanProgress.getThisPoint().getScanIdentifier();
			ScanDataNode datasetNode;
			if (!scans.containsKey(scanIdentifier)) {
				boolean isMulti = (edeExperimentProgress.getExperimentCollectionType() == ExperimentCollectionType.MULTI);
				final ScanDataNode newNode = new ScanDataNode(Integer.toString(scanIdentifier), isMulti, this);
				scans.put(scanIdentifier, newNode);
				dataset.add(0, newNode);
				datasetNode = newNode;
			} else {
				datasetNode = scans.get(scanIdentifier);
			}
			addedData = datasetNode.updateData((EdeExperimentProgressBean) arg);
			this.firePropertyChange(DATA_ADDED_PROP_NAME, null, addedData);
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
