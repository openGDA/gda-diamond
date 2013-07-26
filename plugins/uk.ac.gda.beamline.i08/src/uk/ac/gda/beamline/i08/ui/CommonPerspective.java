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

package uk.ac.gda.beamline.i08.ui;

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;

import uk.ac.gda.beamline.i08.views.CameraView;
import uk.ac.gda.client.microfocus.views.CameraFocusZoomControlView;
import uk.ac.gda.client.microfocus.views.SampleStagePositionControlView;
import uk.ac.gda.exafs.ui.views.scalersmonitor.ScalersMonitorView;
import uk.ac.gda.exafs.ui.views.scalersmonitor.XmapMonitorView;

public class CommonPerspective implements IPerspectiveFactory {

	public static final String ID = "uk.ac.gda.beamline.i08.ui.CommonPerspective";
	@Override
	public void createInitialLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		layout.setEditorAreaVisible(false);
		
		IFolderLayout folderLayout_0 = layout.createFolder("folder10", IPageLayout.LEFT, 0.89f, editorArea);
		folderLayout_0.addView(CameraView.ID);
		
		IFolderLayout folderLayout_2 = layout.createFolder("folder1", IPageLayout.RIGHT, 0.55f,"folder10");	
		folderLayout_2.addView(ScalersMonitorView.ID);
		folderLayout_2.addView(XmapMonitorView.ID);
		IFolderLayout folderLayout = layout.createFolder("folder", IPageLayout.BOTTOM, 0.65f, "folder1");
		folderLayout.addView(SampleStagePositionControlView.ID);
		IFolderLayout folderLayout_3 = layout.createFolder("folder11", IPageLayout.BOTTOM, 0.78f, "folder10");
		folderLayout_3.addView(CameraFocusZoomControlView.ID);
	}

	

}
