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

package uk.ac.gda.client.plotting.model;

import gda.rcp.GDAClientActivator;

import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.dawnsci.plotting.api.trace.ILineTrace.PointStyle;
import org.dawnsci.plotting.api.trace.ILineTrace.TraceType;
import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.swt.widgets.Display;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceReference;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.client.liveplot.IPlotLineColorService;
import uk.ac.gda.exafs.data.ClientConfig.EdeDataStore;

import com.google.gson.reflect.TypeToken;

public class ScanDataItemNode extends DataNode implements LineTraceProvider {
	private final String identifier;
	private final String label;
	private final List<Double> cachedData = Collections.synchronizedList(new ArrayList<Double>());
	private static final String SCAN_DATA_STORE_PREFIX = "scan_item:";

	public ScanDataItemNode(String identifier, String label, DataNode parent) {
		super(parent);
		this.identifier = identifier;
		this.label = label;
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
		Type listType = new TypeToken<ArrayList<Double>>() {}.getType();
		List<Double> storedList = EdeDataStore.INSTANCE.loadConfiguration(getStoredIdentifier(), listType);
		cachedData.addAll(storedList);
	}

	@Override
	public DoubleDataset getXAxisDataset() {
		return ((ScanDataNode) parent).getData();
	}

	@Override
	public TraceStyleDetails getTraceStyleDetails() {
		TraceStyleDetails traceStyle = new TraceStyleDetails();
		ScanDataNode scanDataNode = (ScanDataNode) this.getParent();
		RootDataNode experimentDataNode = (RootDataNode) scanDataNode.getParent();
		if ((experimentDataNode.getChildren().size() - experimentDataNode.getChildren().indexOf(scanDataNode)) % 2 == 0) {
			traceStyle.setTraceType(TraceType.DASH_LINE);
			traceStyle.setPointStyle(PointStyle.DIAMOND);
			traceStyle.setPointSize(6);
		} else {
			traceStyle.setTraceType(TraceType.SOLID_LINE);
			traceStyle.setPointStyle(PointStyle.NONE);
			traceStyle.setPointSize(0);
		}
		traceStyle.setColorHexValue(getColorInHex());
		return  traceStyle;
	}

	public String getColorInHex() {
		BundleContext context = GDAClientActivator.getBundleContext();
		ServiceReference<IPlotLineColorService> serviceRef = context.getServiceReference(IPlotLineColorService.class);
		if (serviceRef != null) {
			String colorValue = (String) serviceRef.getProperty(label);
			if (colorValue != null) {
				return colorValue;
			}
		}
		return null;
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

	public void update(Double value) {
		synchronized (cachedData) {
			cachedData.add(value);
		}
		Display.getDefault().asyncExec(new Runnable() {
			@Override
			public void run() {
				synchronized (cachedData) {
					EdeDataStore.INSTANCE.saveConfiguration(getStoredIdentifier(), cachedData);
				}
			}
		});
	}

	public void clearCache() {
		cachedData.clear();
	}

	private String getStoredIdentifier() {
		return SCAN_DATA_STORE_PREFIX + identifier;
	}

	@Override
	public boolean isPlotByDefault() {
		return true;
	}
}
