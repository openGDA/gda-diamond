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

package uk.ac.gda.exafs.ui.perspectives;

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;

import gda.jython.InterfaceProvider;
import gda.rcp.views.JythonTerminalView;
import uk.ac.gda.exafs.alignment.ui.DetectorLiveModeView;
import uk.ac.gda.exafs.experiment.ui.TurboXasExperimentView;
import uk.ac.gda.exafs.plotting.ui.ExperimentDataPlotView;

public class TurboXasPerspective implements IPerspectiveFactory {

	private static final String TURBOXAS_PERSPECTIVE_ID = "turboXasPerspective";
	private static final String TURBOXAS_PLOT_ID = "turboXasPerspectivePlots";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		layout.setEditorAreaVisible(false);

		IFolderLayout turboXasControlsFolder = layout.createFolder(TURBOXAS_PERSPECTIVE_ID, IPageLayout.LEFT, 0, editorArea);
		turboXasControlsFolder.addView(TurboXasExperimentView.ID);

		// the 'ratio' seems to control the fraction of horiz. perspective space the 'folder' doesn't use (i.e. large = leave lots of space).
		IFolderLayout topPlotFolder = layout.createFolder(TURBOXAS_PLOT_ID, IPageLayout.RIGHT, 0.35f, TURBOXAS_PERSPECTIVE_ID);
		topPlotFolder.addView(DetectorLiveModeView.ID);
		topPlotFolder.addView(ExperimentDataPlotView.ID);
		layout.addView(JythonTerminalView.ID, IPageLayout.BOTTOM, 0.65f,TURBOXAS_PLOT_ID);

		InterfaceProvider.getScanDataPointProvider().addScanEventObserver(new PlotStyleUpdater());
	}
}