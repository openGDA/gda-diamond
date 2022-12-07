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

import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import org.apache.commons.io.FilenameUtils;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.swt.widgets.Display;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.factory.Finder;
import gda.jython.IScanDataPointObserver;
import gda.jython.InterfaceProvider;
import gda.observable.IObservable;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.EdeExperimentProgressBean;
import gda.scan.ede.EdeExperimentProgressBean.ExperimentCollectionType;
import gda.scan.ede.EdeScanProgressBean;
import uk.ac.gda.client.plotting.ScanDataPlotterComposite;
import uk.ac.gda.client.plotting.model.ITreeNode;
import uk.ac.gda.client.plotting.model.Node;
import uk.ac.gda.client.plotting.model.ScanNodeProviderFromNexusFile;
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
	private static final Logger logger = LoggerFactory.getLogger(ExperimentRootNode.class);

	private DoubleDataset stripsData = null;

	public static final String DATA_CHANGED_PROP_NAME = "changedData";
	public static final String DATA_ADDED_PROP_NAME = "addedData";
	public static final String SCAN_ADDED_PROP_NAME = "addedScan";
	public static final String USE_STRIPS_AS_X_AXIS_PROP_NAME = "useStripsAsXaxis";
	private boolean useStripsAsXaxis;
	private ScanNodeProviderFromNexusFile scanNodeProvider = new ScanNodeProviderFromNexusFile();
	private ExecutorService executorService = Executors.newSingleThreadExecutor();

	public ExperimentRootNode() {
		super(null);
		((IObservable) Finder.find(EdeExperiment.PROGRESS_UPDATER_NAME)).addIObserver(this);
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
		for(Object node : this.getChildren()) {
			ITreeNode treenode = (ITreeNode) node;
			List<ITreeNode> dataItemNodes = Node.getNodesOfType(treenode,  ScanDataItemNode.class);
			for(ITreeNode dataNode : dataItemNodes) {
				this.firePropertyChange(DATA_CHANGED_PROP_NAME, null, dataNode);
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
		executorService.submit( () -> updateSyncInGuiThread(arg) );
	}

	/**
	 * Update the gui with plot data (synchronously)
	 * @param source
	 * @param arg
	 */
	private void updateSyncInGuiThread(final Object arg) {
		Display.getDefault().syncExec( () -> updateDataSetInUI(arg) );
	}

	protected void updateDataSetInUI(Object arg) {
		if (arg instanceof EdeExperimentProgressBean) {
			final EdeExperimentProgressBean edeExperimentProgress = (EdeExperimentProgressBean) arg;
			final EdeScanProgressBean edeScanProgress = edeExperimentProgress.getProgress();
			final String scanIdentifier = edeScanProgress.getFilename();
			EdeScanNode scanNode;
			// Make a new EdeScanNode to store the spectra from the scan
			if (!hasChild(scanIdentifier)) {
				boolean isMulti = (edeExperimentProgress.getExperimentCollectionType() == ExperimentCollectionType.MULTI);
				final EdeScanNode newNode = new EdeScanNode(this, edeScanProgress.getFilename(), FilenameUtils.getBaseName(edeScanProgress.getFilename()), isMulti);
				addChildNode(0, newNode);
				scanNode = newNode;
				this.firePropertyChange(SCAN_ADDED_PROP_NAME, null, scanNode);
			} else {
				scanNode = (EdeScanNode) getChild(scanIdentifier);
			}

			Node addedData = scanNode.updateData((EdeExperimentProgressBean) arg);
			this.firePropertyChange(DATA_ADDED_PROP_NAME, null, addedData);
		} else if (arg instanceof String[]) {
			//load data from Nexus files
			String[] filenameList = (String[]) arg;
			for (String filename : filenameList) {
				try {
					scanNodeProvider.addEdeScanNode(filename, this);
				} catch (Exception e) {
					logger.error("Problem adding data to tree from Nexus file {} : {}", filename, e.getMessage(), e);
				}
			}
		}
	}

	@Override
	public String getIdentifier() {
		return null;
	}

	public DoubleDataset getStripsData() {
		return DetectorModel.INSTANCE.getCurrentDetector().createDatasetForPixel();
	}
}
