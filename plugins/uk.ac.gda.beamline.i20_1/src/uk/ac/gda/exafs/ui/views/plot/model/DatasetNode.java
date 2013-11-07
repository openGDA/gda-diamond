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

import gda.scan.IScanDataPoint;

import java.util.ArrayList;

import org.eclipse.core.databinding.observable.set.IObservableSet;
import org.eclipse.core.databinding.observable.set.WritableSet;
import org.eclipse.swt.widgets.Display;

import uk.ac.gda.exafs.data.ObservableModel;

public class DatasetNode extends ObservableModel {
	private  IObservableSet dataset;

	public DatasetNode() {
		Display.getDefault().asyncExec(new Runnable() {
			@Override
			public void run() {
				dataset = new WritableSet(new ArrayList<DataNode>(), DataNode.class);
				dataset.add(new DataNode());
			}
		});

	}

	public IObservableSet getDataset() {
		return dataset;
	}

	public void updateData(IScanDataPoint arg) {
		//
	}
}
