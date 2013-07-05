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

import gda.device.detector.StripDetector;
import gda.factory.Finder;
import gda.rcp.views.JythonTerminalView;

import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.IViewLayout;

import uk.ac.diamond.scisoft.analysis.rcp.views.PlotView;
import uk.ac.gda.client.liveplot.LivePlotView;
import uk.ac.gda.exafs.data.ScannableSetup.DetectorSetup;
import uk.ac.gda.exafs.ui.views.BeamlineAlignmentView;
import uk.ac.gda.exafs.ui.views.DetectorSetupView;
import uk.ac.gda.exafs.ui.views.SingleSpectrumView;

/**
 * Shows recent data from the XH detector for I20-1 EDE branchline.
 */
public class AlignmentPerspective implements IPerspectiveFactory {

	public static final String ID = "uk.ac.gda.beamline.i20_1.AlignmentPerspective";

	// plot where snapshot spectra placed
	public static String SPECTRAPLOTID =  PlotView.ID + "1";
	public static String SPECTRAPLOTNAME =  "Plot 1";

	// TODO This view is not needed
	// plot where accumulative rates are plotted
	public static String LINEPLOTID =  PlotView.ID + "2";
	public static String LINEPLOTNAME =  "Plot 2";

	private static final String TOPPLOT_FOLDER_ID = "topplot";
	private static final String ALIGNMENT_CONTROLS_FOLDER_ID = "alignmentControls";

	public AlignmentPerspective() {
		setActiveDetector();
	}

	private void setActiveDetector() {
		// Use the first available detector
		for (DetectorSetup detector : DetectorSetup.values()) {
			Object detectorBean = Finder.getInstance().find(detector.getDetectorName());
			if (detectorBean != null && detectorBean instanceof StripDetector) {
				detector.setDetectorScannable((StripDetector) detectorBean);
				DetectorSetup.setActiveDetectorSetup(detector);
				return;
			}
		}
		MessageDialog.openError(Display.getDefault().getActiveShell(), "Error", "Unable to find installed detector, please ensure the server configuration is setup correctly.");
	}

	@Override
	public void createInitialLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		layout.setEditorAreaVisible(false);

		IFolderLayout alignmentControlsFolder = layout.createFolder(ALIGNMENT_CONTROLS_FOLDER_ID, IPageLayout.LEFT, 0.30f, editorArea);
		alignmentControlsFolder.addView(BeamlineAlignmentView.ID);
		alignmentControlsFolder.addView(SingleSpectrumView.ID);

		// TODO This view is not needed
		// layout.addView(LINEPLOTID, IPageLayout.RIGHT, 0.25f, editorArea);
		layout.addView(DetectorSetupView.ID, IPageLayout.RIGHT, 0.25f, editorArea);
		IViewLayout propertyLayout = layout.getViewLayout(DetectorSetupView.ID);
		propertyLayout.setCloseable(false);

		IFolderLayout topPlotFolder = layout.createFolder(TOPPLOT_FOLDER_ID, IPageLayout.RIGHT, 0.45f, DetectorSetupView.ID);
		topPlotFolder.addView(SPECTRAPLOTID);
		topPlotFolder.addView(LivePlotView.ID);
		layout.addView(JythonTerminalView.ID, IPageLayout.BOTTOM, 0.50f,TOPPLOT_FOLDER_ID);
	}
}
