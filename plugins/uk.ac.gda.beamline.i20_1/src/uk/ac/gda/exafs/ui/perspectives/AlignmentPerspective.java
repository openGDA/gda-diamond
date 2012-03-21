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

package uk.ac.gda.exafs.ui.perspectives;

import gda.rcp.views.JythonTerminalView;

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;

import uk.ac.diamond.scisoft.analysis.rcp.views.PlotView;
import uk.ac.gda.client.XYPlotView;
import uk.ac.gda.exafs.ui.views.BeamlineAlignmentView;
import uk.ac.gda.exafs.ui.views.DetectorSetupView;

/**
 * Shows recent data from the XH detector for I20-1 EDE branchline.
 */
public class AlignmentPerspective implements IPerspectiveFactory {
	
	public static final String ID = "uk.ac.gda.beamline.i20_1.SpectraPerspective";
	
	// plot where snapshot spectra placed
	public static String SPECTRAPLOTID =  PlotView.ID + "1";
	public static String SPECTRAPLOTNAME =  "Plot 1";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		layout.setEditorAreaVisible(false);
		
		IFolderLayout alignmentControlsFolder = layout.createFolder("alignmentControls", IPageLayout.LEFT, 0.22f, editorArea);
		alignmentControlsFolder.addView(BeamlineAlignmentView.ID);
		alignmentControlsFolder.addView(DetectorSetupView.ID);

		layout.addView(XYPlotView.ID, IPageLayout.RIGHT, 0.25f, editorArea);
		layout.addView(SPECTRAPLOTID, IPageLayout.BOTTOM, 0.50f, XYPlotView.ID);
		layout.addView(JythonTerminalView.ID, IPageLayout.RIGHT, 0.50f, XYPlotView.ID);
	}
}
