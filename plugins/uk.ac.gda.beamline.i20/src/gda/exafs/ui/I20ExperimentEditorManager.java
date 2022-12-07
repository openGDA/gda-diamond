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

import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.ui.IEditorPart;
import org.eclipse.ui.PlatformUI;

import gda.exafs.scan.ScanObject;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.client.experimentdefinition.ExperimentEditorManager;
import uk.ac.gda.client.experimentdefinition.IExperimentObject;
import uk.ac.gda.exafs.ui.data.ScanObjectManager;

public class I20ExperimentEditorManager extends ExperimentEditorManager {

	@Override
	protected IEditorPart[] openRequiredEditors(IExperimentObject ob) {

		try {
			IScanParameters theScan = ((ScanObject) ob).getScanParameters();
			if (theScan instanceof XesScanParameters && !ScanObjectManager.isXESOnlyMode()) {
				MessageDialog.openError(PlatformUI.getWorkbench().getActiveWorkbenchWindow().getShell(),
						"Wrong scan type", "You tried to open an XES scan when in XAS/XANES mode");
				return null;
			} else if (ScanObjectManager.isXESOnlyMode() && !(theScan instanceof XesScanParameters)) {
				// throw the same wobbly
				MessageDialog.openError(PlatformUI.getWorkbench().getActiveWorkbenchWindow().getShell(),
						"Wrong scan type", "You tried to open an XAS/XANES scan when in XES mode");
				return null;
			}
		} catch (Exception e) {
			// ignore and pass the problem to the superclass as that will run into the same issue.
		}
		return super.openRequiredEditors(ob);
	}
}
