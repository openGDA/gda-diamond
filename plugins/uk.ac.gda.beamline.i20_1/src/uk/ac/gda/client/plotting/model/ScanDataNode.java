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

import gda.scan.IScanDataPoint;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;

import com.google.gson.annotations.Expose;

public class ScanDataNode extends DataNode {

	private final IObservableList children = new WritableList(new ArrayList<ScanDataItemNode>(), ScanDataItemNode.class);
	private final List<Double> cachedData = new ArrayList<Double>();
	@Expose
	private final String identifier;
	@Expose
	private final String fileName;
	@Expose
	private final List<String> scanItemNames;

	public List<String> getScanItemNames() {
		return scanItemNames;
	}

	public ScanDataNode(String identifier, String fileName, List<String> scanItemNames, DataNode parent) {
		super(parent);
		this.identifier = identifier;
		this.fileName = fileName;
		this.scanItemNames = scanItemNames;
		createScanDataItems();
	}

	private void createScanDataItems() {
		for (String scanDataItem : scanItemNames) {
			String dataItemIdentifier = createIdentifier(scanDataItem);
			ScanDataItemNode slitscanDataItemNode = new ScanDataItemNode(dataItemIdentifier, scanDataItem, this);
			children.add(slitscanDataItemNode);
		}
	}

	private String createIdentifier(String scanDataItem) {
		return "Scan@" + identifier + "@" + scanDataItem;
	}

	public DoubleDataset getData() throws Exception {
		if (cachedData.isEmpty()) {
			return fileCachedDataFromFile();
		}
		return (DoubleDataset) AbstractDataset.createFromList(cachedData);
	}


	private DoubleDataset fileCachedDataFromFile() throws Exception {
		DataHolder dataHolder = LoaderFactory.getData(fileName);
		return null;
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
		return identifier;
	}

	public void clearCached() {
		cachedData.clear();
		for (Object obj : children) {
			((ScanDataItemNode) obj).clearCached();
		}
	}

	public String getFileName() {
		return fileName;
	}

	public void update(IScanDataPoint scanDataPoint) {
		cachedData.add(scanDataPoint.getPositionsAsDoubles()[0]);
		for (int i = 0; i < scanDataPoint.getDetectorDataAsDoubles().length; i ++) {
			((ScanDataItemNode) children.get(i)).update(scanDataPoint.getDetectorDataAsDoubles()[i]);
		}
	}
}
