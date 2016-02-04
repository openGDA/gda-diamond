/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i13i.perspectives;

import gda.rcp.views.JythonTerminalView;

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.IViewLayout;

import uk.ac.gda.beamline.i13i.views.ViewFactoryIds;
import uk.ac.gda.client.CommandQueueViewFactory;
import uk.ac.gda.client.liveplot.LivePlotView;

public class ScriptingPerspective implements IPerspectiveFactory {
	public final static String ID = "uk.ac.gda.beamline.i13i.perspectives.ScriptingPerspective";

	private IPageLayout factory;

	public ScriptingPerspective() {
		super();
	}

	@Override
	public void createInitialLayout(IPageLayout factory) {
		this.factory = factory;
		addViews();
		addActionSets();
		addNewWizardShortcuts();
	}

	private void addViews() {
		// Creates the overall folder layout.
		// Note that each new Folder uses a percentage of the remaining EditorArea.

		factory.addStandaloneView(ViewFactoryIds.StatusViewID, false, IPageLayout.TOP, 0.13f, factory.getEditorArea());
		IViewLayout statusLayout = factory.getViewLayout(ViewFactoryIds.StatusViewID);
		statusLayout.setCloseable(false);
		statusLayout.setMoveable(false);

		IFolderLayout left = factory.createFolder("left", IPageLayout.LEFT, (float) 0.20, factory.getEditorArea()); //$NON-NLS-1$
		left.addView(IPageLayout.ID_PROJECT_EXPLORER);

		IFolderLayout right = factory.createFolder("right", IPageLayout.RIGHT, (float) 0.50, factory.getEditorArea()); //$NON-NLS-1$
		right.addView(LivePlotView.ID);

		IFolderLayout rightBottom = factory.createFolder("rightBottom", IPageLayout.BOTTOM, (float) 0.50, "right");
		rightBottom.addView("uk.ac.gda.beamline.i13i.DetectorPlot");
		rightBottom.addPlaceholder("org.eclipse.ui.browser.view");
		rightBottom.addPlaceholder("data.dispenser.browser");
		rightBottom.addPlaceholder("org.eclipse.ui.browser.view:data.dispenser.browser");
		rightBottom.addPlaceholder("uk.ac.diamond.scisoft.analysis.rcp.plotViewDP");

		IFolderLayout middleBottom = factory.createFolder("middleBottom", // NON-NLS-1
				IPageLayout.BOTTOM, 0.30f, factory.getEditorArea());
		middleBottom.addView(JythonTerminalView.ID);
		middleBottom.addPlaceholder(CommandQueueViewFactory.ID);

	}

	private void addActionSets() {
		factory.addActionSet(IPageLayout.ID_NAVIGATE_ACTION_SET); // NON-NLS-1
	}

	private void addNewWizardShortcuts() {
		factory.addNewWizardShortcut("org.eclipse.ui.wizards.new.folder");// NON-NLS-1
		factory.addNewWizardShortcut("org.eclipse.ui.wizards.new.file");// NON-NLS-1
	}
}
