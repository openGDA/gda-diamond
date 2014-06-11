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

package uk.ac.gda.plotting.model;

import gda.rcp.GDAClientActivator;
import gda.scan.IScanDataPoint;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.core.databinding.observable.list.ListDiffVisitor;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.swt.widgets.Display;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceReference;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.client.liveplot.IPlotLineColorService;
import uk.ac.gda.plotting.model.LineTraceProvider.TraceStyleDetails;

import com.google.gson.annotations.Expose;

public class ScanDataNode extends DataNode {

	private static final String SCAN_DATA_STORE_PREFIX = "scan:";
	private final IObservableList children = new WritableList(new ArrayList<ScanDataItemNode>(), ScanDataItemNode.class);
	private final List<Double> cachedData = Collections.synchronizedList(new ArrayList<Double>());

	@Expose
	private final String identifier;
	@Expose
	private final String fileName;
	@Expose
	private final List<String> detectorScanItemNames;
	@Expose
	private final List<String> positionScanItemNames;
	private final String xAxisName;

	public ScanDataNode(String identifier, String fileName, List<String> positionScanItemNames, List<String> detectorScanItemNames, DataNode parent) {
		super(parent);
		this.identifier = identifier;
		this.fileName = fileName;
		this.detectorScanItemNames = detectorScanItemNames;
		this.positionScanItemNames = positionScanItemNames;
		xAxisName = this.positionScanItemNames.get(0);
		createScanDataItems();
	}

	public List<String> getDetectorScanItemNames() {
		return detectorScanItemNames;
	}

	public List<String> getPositionScanItemNames() {
		return positionScanItemNames;
	}

	private void createScanDataItems() {
		// TODO Currently detectorScanItemNames are added then positionScanItemNames, needs reviewing on how they are shown
		if (positionScanItemNames != null) {
			for (int i = 1; i < positionScanItemNames.size(); i++) { // 0 is reserved for x-axis
				createScanDataItem(positionScanItemNames.get(i));
			}
		}
		if (detectorScanItemNames != null) {
			for (String scanItemName : detectorScanItemNames) {
				createScanDataItem(scanItemName);
			}
		}
		children.addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {

					@Override
					public void handleRemove(int index, Object element) {
						((ScanDataItemNode) element).disposeResources();
					}

					@Override
					public void handleAdd(int index, Object element) {}
				});
			}
		});
	}

	private void createScanDataItem(String scanItemName) {
		String dataItemIdentifier = createIdentifier(scanItemName);
		TraceStyleDetails traceStyle = createDefaultTraceStyle(scanItemName);
		ScanDataItemNode scanDataItemNode = new ScanDataItemNode(dataItemIdentifier, scanItemName, this, traceStyle);
		children.add(scanDataItemNode);
	}

	private TraceStyleDetails createDefaultTraceStyle(String scanDataItem) {
		TraceStyleDetails traceStyle = null;
		RootDataNode experimentDataNode = (RootDataNode) this.getParent();
		if ((experimentDataNode.getChildren().size() - experimentDataNode.getChildren().indexOf(this)) % 2 == 0) {
			traceStyle = TraceStyleDetails.createDefaultSolidTrace();
		} else {
			traceStyle = TraceStyleDetails.createDefaultDashTrace();
		}
		traceStyle.setColorHexValue(getColorInHex(scanDataItem));
		return  traceStyle;
	}

	private String getColorInHex(String scanDataItem) {
		BundleContext context = GDAClientActivator.getBundleContext();
		ServiceReference<IPlotLineColorService> serviceRef = context.getServiceReference(IPlotLineColorService.class);
		if (serviceRef != null) {
			String colorValue = (String) serviceRef.getProperty(scanDataItem);
			if (colorValue != null) {
				return colorValue;
			}
		}
		return null;
	}

	private String createIdentifier(String scanDataItem) {
		return "Scan@" + identifier + "@" + scanDataItem;
	}

	public DoubleDataset getData() {
		synchronized (cachedData) {
			if (cachedData.isEmpty()) {
				loadCachedDataFromFile();
			}
			DoubleDataset dataset = (DoubleDataset) AbstractDataset.createFromList(cachedData);
			dataset.setName(xAxisName);
			return dataset;
		}
	}

	private void loadCachedDataFromFile() {
		List<Double> storedList = PlottingDataStore.INSTANCE.getPreferenceDataStore().loadArrayConfiguration(getStoredIdentifier(), Double.class);
		cachedData.addAll(storedList);
	}

	@Override
	public IObservableList getChildren() {
		return children;
	}

	@Override
	public String getIdentifier() {
		return identifier;
	}

	@Override
	public String toString() {
		return getIdentifier();
	}

	public void clearCache() {
		synchronized (cachedData) {
			cachedData.clear();
		}
		for (Object obj : children) {
			((ScanDataItemNode) obj).clearCache();
		}
	}

	private String getStoredIdentifier() {
		return SCAN_DATA_STORE_PREFIX + identifier;
	}

	public String getFileName() {
		return fileName;
	}

	private final Runnable saveData = new Runnable() {
		@Override
		public void run() {
			synchronized (cachedData) {
				PlottingDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(getStoredIdentifier(), cachedData);
			}
		}
	};

	public void update(IScanDataPoint scanDataPoint) {
		synchronized (cachedData) {
			cachedData.add(scanDataPoint.getPositionsAsDoubles()[0]);
		}
		Display.getDefault().asyncExec(saveData);
		// TODO Currently detectorScanItemNames are added then positionScanItemNames, needs reviewing on how they are shown
		for (int i = 0; i < scanDataPoint.getPositionsAsDoubles().length - 1; i ++) {
			((ScanDataItemNode) children.get(i)).update(scanDataPoint.getPositionsAsDoubles()[i + 1]);
		}

		int offset = scanDataPoint.getPositionsAsDoubles().length - 1;
		if (detectorScanItemNames != null) {
			for (int i = 0; i < scanDataPoint.getDetectorDataAsDoubles().length; i++) {
				((ScanDataItemNode) children.get(i + offset)).update(scanDataPoint.getDetectorDataAsDoubles()[i]);
			}
		}
	}

	@Override
	public void removeChild(DataNode dataNode) {
		// Not supported
	}

	@Override
	public void disposeResources() {
		PlottingDataStore.INSTANCE.getPreferenceDataStore().removeConfiguration(getStoredIdentifier());
	}
}
