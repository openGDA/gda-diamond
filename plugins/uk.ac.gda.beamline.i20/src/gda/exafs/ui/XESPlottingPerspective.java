/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package gda.exafs.ui;

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;

import gda.rcp.views.JythonTerminalView;
import uk.ac.diamond.scisoft.analysis.rcp.views.PlotView;
import uk.ac.gda.client.CommandQueueViewFactory;

public class XESPlottingPerspective implements IPerspectiveFactory {

	public static final String ID = "org.diamond.exafs.ui.XESPlottingPerspective";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		layout.setEditorAreaVisible(false);

		IFolderLayout plotterFolder = layout.createFolder("plotterFolder", IPageLayout.LEFT, 0.55f, editorArea);
		plotterFolder.addView(PlotView.ID + "1");

		IFolderLayout rightSideFolder = layout.createFolder("rightSideFolder", IPageLayout.RIGHT, 0.5f, PlotView.ID);
		rightSideFolder.addView(JythonTerminalView.ID);

		/*IFolderLayout topRightFolder = */layout.createFolder("topRightFolder", IPageLayout.TOP, 0.4f, "rightSideFolder");
		// topRightFolder.addView(SidePlotView.ID+ ": Plot 1");
		// topRightFolder.addView(HistogramView.ID);

		// TODO have a perspetive/page listener to look for these views appearing and control where they go

		IFolderLayout bottomLeftFolder = layout.createFolder("bottomLeftFolder", IPageLayout.BOTTOM, 0.85f,
				"plotterFolder");
		bottomLeftFolder.addView(CommandQueueViewFactory.ID);
	}

}
