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

import gda.scan.IScanDataPoint;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;


public class SlitsScanDataNode extends DataNode {

	private final IObservableList children = new WritableList(new ArrayList<SlitscanDataItemNode>(), SlitscanDataItemNode.class);

	private final String identifier;
	private final List<Double> data = new ArrayList<Double>();

	public SlitsScanDataNode(String identifier, List<String> scanItems, DataNode parent) {
		super(parent);
		this.identifier = identifier;
		for (String scanDataItem : scanItems) {
			String dataItemIdentifier = createIdentifier(scanDataItem);
			SlitscanDataItemNode slitscanDataItemNode = new SlitscanDataItemNode(dataItemIdentifier, scanDataItem, this);
			children.add(slitscanDataItemNode);
		}
	}

	private String createIdentifier(String scanDataItem) {
		return "Scan@" + identifier + "@" + scanDataItem;
	}

	public DoubleDataset getData() {
		return (DoubleDataset) AbstractDataset.createFromList(data);
	}

	@Override
	public IObservableList getChildren() {
		return children;
	}

	@Override
	public String getIdentifier() {
		return toString();
	}

	@Override
	public String toString() {
		return identifier;
	}

	public void update(IScanDataPoint scanDataPoint) {
		data.add(scanDataPoint.getPositionsAsDoubles()[0]);
		for (int i = 0; i < scanDataPoint.getDetectorDataAsDoubles().length; i ++) {
			((SlitscanDataItemNode) children.get(i)).update(scanDataPoint.getDetectorDataAsDoubles()[i]);
		}
	}
}
