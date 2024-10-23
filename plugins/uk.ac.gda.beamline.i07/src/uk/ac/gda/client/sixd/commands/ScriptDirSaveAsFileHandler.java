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
import org.eclipse.ui.PlatformUI;

import gda.rcp.SaveAsLocalFileAction;

/**
 * This uses a custom implementation of SaveAsLocalFileAction from
 * the core plugin which causes the save file dialog to default
 * to a script directory rather than the user's home directory
 * on the first time it is opened (subsequent times will remember
 * the previous script location).
 */
public class ScriptDirSaveAsFileHandler extends AbstractHandler {

	private SaveAsLocalFileAction action;

	@Override
	public Object execute(ExecutionEvent event) throws ExecutionException {
		if (action == null) {
			action = new SaveAsLocalFileAction();
			action.init(PlatformUI.getWorkbench().getActiveWorkbenchWindow());
		}
		action.run();
		return null;
	}
}
