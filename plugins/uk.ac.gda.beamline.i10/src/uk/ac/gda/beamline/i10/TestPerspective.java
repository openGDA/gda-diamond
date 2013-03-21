/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i10;

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;

public class TestPerspective implements IPerspectiveFactory {
	static final String ID = "uk.ac.gda.beamline.I10ScanPerspective";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		defineLayout(layout);
	}

	private void defineLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		IFolderLayout bottomfolder = layout.createFolder("bottom", IPageLayout.BOTTOM, 0.72f, editorArea); //$NON-NLS-1$
		bottomfolder.addView("ch.qos.logback.eclipse.views.LogbackView");
		bottomfolder.addView("gda.rcp.datavectorview");
		layout.addView("gda.rcp.views.baton.BatonView", IPageLayout.RIGHT, 0.5f, "bottom");
		IFolderLayout rightfolder = layout.createFolder("right", IPageLayout.RIGHT, 0.41f, editorArea); //$NON-NLS-1$
		rightfolder.addView("uk.ac.gda.client.xyplotview");
		IFolderLayout outputfolder = layout.createFolder("top", IPageLayout.TOP, 0.88f, editorArea); //$NON-NLS-1$
		outputfolder.addView("gda.rcp.jythonterminalview");

		layout.addView("gda.rcp.jythoncontrollerview", IPageLayout.TOP, 0.9f, editorArea);

		layout.setEditorAreaVisible(false);
	}

}
