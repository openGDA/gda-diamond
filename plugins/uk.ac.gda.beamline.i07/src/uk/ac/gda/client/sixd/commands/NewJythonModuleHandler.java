/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

package uk.ac.gda.client.sixd.commands;

import org.eclipse.core.commands.AbstractHandler;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.jface.wizard.WizardDialog;
import org.eclipse.ui.IWorkbenchWizard;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.wizards.IWizardDescriptor;
import org.python.pydev.ui.wizards.files.PythonModuleWizard;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A handler for directly opening the PyDev new Python module wizard
 */
public class NewJythonModuleHandler extends AbstractHandler {

	private static final Logger logger = LoggerFactory.getLogger(NewJythonModuleHandler.class);

	@Override
	public Object execute(ExecutionEvent event) throws ExecutionException {
		var id = PythonModuleWizard.WIZARD_ID;
		var display = PlatformUI.getWorkbench().getDisplay();
		IWizardDescriptor descriptor = PlatformUI.getWorkbench().getNewWizardRegistry().findWizard(id);
		IWorkbenchWizard wizard;
		try {
			wizard = descriptor.createWizard();
			wizard.init(PlatformUI.getWorkbench(), StructuredSelection.EMPTY);
			var wd = new WizardDialog(display.getActiveShell(), wizard);
			wd.setTitle(wizard.getWindowTitle());
			wd.open();
		} catch (CoreException e) {
			logger.error("Could not create new Jython module wizard");
		}
		return null;
	}
}