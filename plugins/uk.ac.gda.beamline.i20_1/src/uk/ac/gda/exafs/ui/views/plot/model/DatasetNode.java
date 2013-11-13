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

import gda.scan.ede.EdeExperimentProgressBean;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

import uk.ac.gda.exafs.data.ObservableModel;

public class DatasetNode extends ObservableModel {
	private final Map<String, DataNode> scans = new HashMap<String, DataNode>();
	private final  IObservableList dataNodeList = new WritableList(new ArrayList<DataNode>(), DataNode.class);
	private final String scanIdentifier;

	public DatasetNode(String scanIdentifier) {
		this.scanIdentifier = scanIdentifier;
	}

	public IObservableList getNodeList() {
		return dataNodeList;
	}

	public DataNode updateData(final EdeExperimentProgressBean arg) {
		DataNode dataNode;
		String label = arg.getDataLabel();
		if (!scans.containsKey(label)) {
			final DataNode newNode = new DataNode(label, this);
			scans.put(scanIdentifier, newNode);
			dataNodeList.add(newNode);
			dataNode = newNode;
		} else {
			dataNode = scans.get(label);
		}
		dataNode.updateData(arg.getEnergyData(), arg.getData());
		return dataNode;
	}

	@Override
	public String toString() {
		return "Scan:" + scanIdentifier;
	}
}
