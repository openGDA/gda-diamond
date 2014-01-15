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

import gda.jython.IScanDataPointObserver;
import gda.jython.InterfaceProvider;
import gda.scan.IScanDataPoint;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.swt.widgets.Display;

public class SlitsScanRootDataNode extends DataNode implements IScanDataPointObserver {

	private final Map<String, SlitsScanDataNode> scans = new HashMap<String, SlitsScanDataNode>();
	private final IObservableList children = new WritableList(new ArrayList<SlitsScanDataNode>(), SlitsScanDataNode.class);

	public SlitsScanRootDataNode() {
		super(null);
		InterfaceProvider.getScanDataPointProvider().addIScanDataPointObserver(this);
	}

	@Override
	public IObservableList getChildren() {
		return children;
	}

	@Override
	public String getIdentifier() {
		return "";
	}

	@Override
	public void update(final Object source, final Object arg) {
		Display.getDefault().asyncExec(new Runnable() {
			@Override
			public void run() {
				if (arg instanceof IScanDataPoint) {
					updateDataSetInUI((IScanDataPoint) arg);
				}
			}
		});

	}

	@SuppressWarnings("unchecked")
	protected void updateDataSetInUI(IScanDataPoint scanDataPoint) {
		// FIXME!
		if (scanDataPoint.getScanPlotSettings() != null && scanDataPoint.getScanPlotSettings().getYAxesShown().length < 1) {
			return;
		}

		SlitsScanDataNode slitsScanDataNode;
		if (!scans.containsKey(scanDataPoint.getScanIdentifier())) {
			slitsScanDataNode = new SlitsScanDataNode(scanDataPoint.getScanIdentifier(), scanDataPoint.getDetectorHeader(), this);
			children.add(0, slitsScanDataNode);
			scans.put(scanDataPoint.getScanIdentifier(), slitsScanDataNode);
		} else {
			slitsScanDataNode = scans.get(scanDataPoint.getScanIdentifier());
		}
		slitsScanDataNode.update(scanDataPoint);
		for (Object object : slitsScanDataNode.getChildren()) {
			this.firePropertyChange(DATA_ADDED_PROP_NAME, null, object);
		}

	}

}
