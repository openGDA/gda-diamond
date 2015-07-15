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

package uk.ac.gda.beamline.i20.ui.handlers;

import org.eclipse.core.commands.AbstractHandler;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IEditorReference;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PlatformUI;

import uk.ac.gda.exafs.ui.data.ScanObjectManager;

/**
 * Changes I20 UI from between XAS/XES mode with confirmation/feedback to user.
 */
public class SwitchExperimentModeHandler extends AbstractHandler {

	@Override
	public Object execute(ExecutionEvent event) throws ExecutionException {

		Display.getCurrent().asyncExec(new Runnable() {
			@Override
			public void run() {

				String newMode = "XES";
				if (ScanObjectManager.isXESOnlyMode()) {
					newMode = "EXAFS/XANES";
				}
				if (!MessageDialog.openConfirm(Display.getCurrent().getActiveShell(), "Confirm experiment mode change",
						"This will change the experiment mode to " + newMode + "\nAre you sure?")) {
					return;
				}

				if (ScanObjectManager.isXESOnlyMode()) {
					ScanObjectManager.setXESOnlyMode(false);
				} else {
					ScanObjectManager.setXESOnlyMode(true);
				}

				// close all editors when changing mode
				IWorkbenchPage activePage = PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage();
				IEditorReference[] openEdRefs = activePage.getEditorReferences();
				activePage.closeEditors(openEdRefs, true);

				String message = "Experiment mode changed to "
						+ newMode
						+ "\n\nImportant: ALL scans need to be switched to the new mode\nor deleted from the Experiment Explorer.\n\nThe options in the editors will now have changed for the new mode.";
				MessageDialog
						.openInformation(Display.getCurrent().getActiveShell(), "Experiment mode changed", message);

//				SynopticControl.switchSynoptic();
			}
		});

		return null;
	}
}
