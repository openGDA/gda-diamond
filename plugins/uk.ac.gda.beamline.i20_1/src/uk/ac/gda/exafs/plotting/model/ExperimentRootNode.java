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

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import org.apache.commons.io.FilenameUtils;
import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.swt.widgets.Display;

import gda.factory.Finder;
import gda.jython.IScanDataPointObserver;
import gda.jython.InterfaceProvider;
import gda.observable.IObservable;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.EdeExperimentProgressBean;
import gda.scan.ede.EdeExperimentProgressBean.ExperimentCollectionType;
import gda.scan.ede.EdeScanProgressBean;
import uk.ac.gda.client.plotting.model.Node;
import uk.ac.gda.exafs.data.DetectorModel;

public class ExperimentRootNode extends Node implements IScanDataPointObserver {

	private final DoubleDataset stripsData;
	private final Map<Integer, EdeScanNode> scans = new HashMap<Integer, EdeScanNode>();
	private final IObservableList dataset = new WritableList(new ArrayList<EdeScanNode>(), EdeScanNode.class);

	private Node changedData;

	public static final String USE_STRIPS_AS_X_AXIS_PROP_NAME = "useStripsAsXaxis";
	private boolean useStripsAsXaxis;

	private Node addedData;

	private ExecutorService executorService = Executors.newSingleThreadExecutor();

	public ExperimentRootNode() {
		super(null);
		((IObservable) Finder.getInstance().findNoWarn(EdeExperiment.PROGRESS_UPDATER_NAME)).addIObserver(this);
		InterfaceProvider.getScanDataPointProvider().addIScanDataPointObserver(this);
		stripsData = DetectorModel.INSTANCE.getCurrentDetector().createDatasetForPixel();
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
			for (Object spectraObj: ((EdeScanNode) scanObj).getChildren()) {
				SpectraNode spectraNode = (SpectraNode) spectraObj;
				for (Object scanDataObj: spectraNode.getChildren()) {
					this.firePropertyChange(DATA_CHANGED_PROP_NAME, null, scanDataObj);
				}
			}
		}
	}

	/**
	 * Update the gui synchronously using a separate thread - to avoid locking up the gui for other update events
	 * when adding a large number of plots in quick succession.
	 * @since 27/9/2016
	 */
	@Override
	public void update(final Object source, final Object arg) {
		executorService.submit(new Runnable() {
			@Override
			public void run() {
				updateSyncInGuiThread(source, arg);
			}
		});
	}

	/**
	 * Update the gui with plot data (synchronously)
	 * @param source
	 * @param arg
	 */
	private void updateSyncInGuiThread(final Object source, final Object arg) {
		Display.getDefault().syncExec(new Runnable() {
			@Override
			public void run() {
				updateDataSetInUI(source, arg);
			}
		});
	}

	public Node getChangedData() {
		return changedData;
	}

	public Node getAddedData() {
		return addedData;
	}

	// FIXME Changed to linked list or change viewer to reverse the order!
	@SuppressWarnings("unchecked")
	protected void updateDataSetInUI(@SuppressWarnings("unused") Object source, Object arg) {
		if (arg instanceof EdeExperimentProgressBean) {
			final EdeExperimentProgressBean edeExperimentProgress = (EdeExperimentProgressBean) arg;
			final EdeScanProgressBean edeScanProgress = edeExperimentProgress.getProgress();
			final int scanIdentifier = edeScanProgress.getFilename().hashCode(); //should be unique (or at least, unique enough...)
			EdeScanNode datasetNode;
			if (!scans.containsKey(scanIdentifier)) {
				boolean isMulti = (edeExperimentProgress.getExperimentCollectionType() == ExperimentCollectionType.MULTI);
				final EdeScanNode newNode = new EdeScanNode(FilenameUtils.getBaseName(edeScanProgress.getFilename()), edeScanProgress.getFilename(), isMulti, this);
				scans.put(scanIdentifier, newNode);
				dataset.add(0, newNode);
				datasetNode = newNode;
				this.firePropertyChange(SCAN_ADDED_PROP_NAME, null, datasetNode);
			} else {
				datasetNode = scans.get(scanIdentifier);
			}
			//Force it to check if users want display data in Strips
			if (isUseStripsAsXaxis()) {
				arg=new EdeExperimentProgressBean(edeExperimentProgress.getExperimentCollectionType(), edeScanProgress, edeExperimentProgress.getDataLabel(), edeExperimentProgress.getData(), stripsData);
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

	@Override
	public void removeChild(Node dataNode) {
		// NOt supported
	}

	public DoubleDataset getStripsData() {
		return stripsData;
	}
}
