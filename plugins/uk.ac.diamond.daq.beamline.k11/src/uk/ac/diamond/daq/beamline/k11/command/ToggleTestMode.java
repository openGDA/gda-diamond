/*-
 * Copyright © 2023 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.command;

import org.eclipse.core.commands.AbstractHandler;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.widgets.Display;

import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.spring.ClientSpringProperties;

public class ToggleTestMode extends AbstractHandler {

	@Override
	public Object execute(ExecutionEvent event) throws ExecutionException {

		var testMode = getClientProperties().getModes().getTest();

		var question = String.format("Test mode is currently %s; are you sure you want to change this?",
				testMode.isActive() ? "enabled" : "disabled");

		var confirmed = MessageDialog.openConfirm(Display.getDefault().getActiveShell(), "Test mode", question);
		if (confirmed) {
			testMode.setActive(!testMode.isActive());
		}

		return null;
	}

	private ClientSpringProperties getClientProperties() {
		return SpringApplicationContextFacade.getBean(ClientSpringProperties.class);
	}
}
