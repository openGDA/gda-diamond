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

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.swt.widgets.Display;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;

public class ScanDataItemNode extends DataNode implements LineTraceProvider {
	private final String identifier;
	private final String label;
	private final List<Double> cachedData = Collections.synchronizedList(new ArrayList<Double>());
	private TraceStyleDetails traceStyle;

	private static final String SCAN_DATA_STORE_PREFIX = "scan_item:";

	public TraceStyleDetails getTraceStyle() {
		return traceStyle;
	}

	public void setTraceStyle(TraceStyleDetails traceStyle) {
		this.traceStyle = traceStyle;
	}

	public ScanDataItemNode(String identifier, String label, DataNode parent, TraceStyleDetails traceStyle) {
		super(parent);
		this.identifier = identifier;
		this.label = label;
		this.traceStyle = traceStyle;
	}

	@Override
	public DoubleDataset getYAxisDataset() {
		synchronized (cachedData) {
			if (cachedData.isEmpty()) {
				fileCachedDataFromFile();
			}
			return (DoubleDataset) AbstractDataset.createFromList(cachedData);
		}
	}

	private void fileCachedDataFromFile() {
		List<Double> storedList = PlottingDataStore.INSTANCE.getPreferenceDataStore().loadArrayConfiguration(getStoredIdentifier(), Double.class);
		cachedData.addAll(storedList);
	}

	@Override
	public DoubleDataset getXAxisDataset() {
		return ((ScanDataNode) parent).getData();
	}

	@Override
	public TraceStyleDetails getTraceStyleDetails() {
		return  traceStyle;
	}

	@Override
	public IObservableList getChildren() {
		return null;
	}

	@Override
	public String getIdentifier() {
		return identifier;
	}

	@Override
	public String toString() {
		return label;
	}

	private final Runnable saveData = new Runnable() {
		@Override
		public void run() {
			synchronized (cachedData) {
				PlottingDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(getStoredIdentifier(), cachedData);
			}
		}
	};

	public void update(Double value) {
		synchronized (cachedData) {
			cachedData.add(value);
		}
		Display.getDefault().asyncExec(saveData);
	}

	public void clearCache() {
		synchronized (cachedData) {
			cachedData.clear();
		}
	}

	private String getStoredIdentifier() {
		return SCAN_DATA_STORE_PREFIX + identifier;
	}

	@Override
	public boolean isPlotByDefault() {
		return !cachedData.isEmpty();
	}

	@Override
	public void removeChild(DataNode dataNode) {
		// Nothing to remove
	}

	@Override
	public void disposeResources() {
		PlottingDataStore.INSTANCE.getPreferenceDataStore().removeConfiguration(getStoredIdentifier());
	}
}
