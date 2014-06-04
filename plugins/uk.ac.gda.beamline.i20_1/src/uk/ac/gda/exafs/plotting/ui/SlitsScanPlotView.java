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

package uk.ac.gda.exafs.plotting.ui;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;

import uk.ac.gda.plotting.ScanDataPlotter;
import uk.ac.gda.plotting.model.RootDataNode;

public class SlitsScanPlotView extends ViewPart {
	public static String ID = "uk.ac.gda.exafs.ui.views.slitsscanplotview";
	ScanDataPlotter scanDataPlotter;
	private RootDataNode rootNode;

	@Override
	public void createPartControl(Composite parent) {
		rootNode = new RootDataNode();
		scanDataPlotter = new ScanDataPlotter(parent, SWT.None, this, rootNode);
	}

	@Override
	public void setFocus() {
		if (!scanDataPlotter.isDisposed()) {
			scanDataPlotter.setFocus();
		}
	}

	@Override
	public void dispose() {
		if (rootNode != null) {
			rootNode.disposeResources();
		}
	}
}
