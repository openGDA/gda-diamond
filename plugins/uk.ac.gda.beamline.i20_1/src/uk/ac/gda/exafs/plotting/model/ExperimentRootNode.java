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
import uk.ac.gda.client.plotting.ScanDataPlotterComposite;
import uk.ac.gda.client.plotting.model.Node;
import uk.ac.gda.exafs.data.DetectorModel;

/**
 * This is the top level node class that stores data from a series of Ede/TurboXas scans.
 * This is used as the model for the TreeViewer for {@link ScanDataPlotterComposite}.
 * The various classes are linked to one another in the following tree structure :
 * <li> {@link ExperimentRootNode}
 * 		<ul>
 * 		<li>{@link EdeScanNode}
 * 			<ul>
 * 			<li>{@link SpectraNode}
 * 				<ul>
 * 				<li> {@link ScanDataItemNode}
 * 				<li> {@link ScanDataItemNode}
 * 				<li> ...</ul>
 * 			<li>{@link SpectraNode}
 * 			<li> ... </ul>
 *   	<li>{@link EdeScanNode}
 * 		<li>{@link EdeScanNode}
 * 		<li> ... </ul>
 *
 * i.e. The ExperimentRootNode contains a list of EdeScanNodes; each EdeScanNode has a list of SpectraNodes and
 *  each SpectraNode has a list of ScanDataItemNodes. ScanDataItemNodes contains datasets with the x-y values to be plotted
 */
public class ExperimentRootNode extends Node implements IScanDataPointObserver {

	private final DoubleDataset stripsData;
	private final Map<Integer, EdeScanNode> scanNodeMap = new HashMap<>();
	private final IObservableList scanNodeList = new WritableList(new ArrayList<EdeScanNode>(), EdeScanNode.class);

	public static final String USE_STRIPS_AS_X_AXIS_PROP_NAME = "useStripsAsXaxis";
	private boolean useStripsAsXaxis;

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
		for (Object scanObj: scanNodeList) {
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

	// FIXME Changed to linked list or change viewer to reverse the order!
	@SuppressWarnings("unchecked")
	protected void updateDataSetInUI(@SuppressWarnings("unused") Object source, Object arg) {
		if (arg instanceof EdeExperimentProgressBean) {
			final EdeExperimentProgressBean edeExperimentProgress = (EdeExperimentProgressBean) arg;
			final EdeScanProgressBean edeScanProgress = edeExperimentProgress.getProgress();
			final int scanIdentifier = edeScanProgress.getFilename().hashCode(); //should be unique (or at least, unique enough...)
			EdeScanNode datasetNode;
			// Make a new EdeScanNode to store the spectra from the scan
			if (!scanNodeMap.containsKey(scanIdentifier)) {
				boolean isMulti = (edeExperimentProgress.getExperimentCollectionType() == ExperimentCollectionType.MULTI);
				final EdeScanNode newNode = new EdeScanNode(this, FilenameUtils.getBaseName(edeScanProgress.getFilename()), edeScanProgress.getFilename(), isMulti);
				scanNodeMap.put(scanIdentifier, newNode);
				scanNodeList.add(0, newNode);
				datasetNode = newNode;
				this.firePropertyChange(SCAN_ADDED_PROP_NAME, null, datasetNode);
			} else {
				datasetNode = scanNodeMap.get(scanIdentifier);
			}

			Node addedData = datasetNode.updateData((EdeExperimentProgressBean) arg);
			this.firePropertyChange(DATA_ADDED_PROP_NAME, null, addedData);
		}
	}

	@Override
	public IObservableList getChildren() {
		return scanNodeList;
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
