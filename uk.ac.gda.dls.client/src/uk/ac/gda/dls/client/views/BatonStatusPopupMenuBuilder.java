/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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

package uk.ac.gda.dls.client.views;

import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;

final class BatonStatusPopupMenuBuilder {

	static IWorkbenchWindow getActiveWorkBenchWindow() {
		var workBench = PlatformUI.getWorkbench();
		return workBench.getActiveWorkbenchWindow();
	}
	static void showView(String viewId) throws PartInitException {
		var activePage = getActiveWorkBenchWindow().getActivePage();
		activePage.showView(viewId);
	}
}
