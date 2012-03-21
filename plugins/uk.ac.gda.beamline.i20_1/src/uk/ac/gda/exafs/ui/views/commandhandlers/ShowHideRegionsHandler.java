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

package uk.ac.gda.exafs.ui.views.commandhandlers;

import org.eclipse.core.commands.AbstractHandler;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.core.commands.IHandler;

import uk.ac.gda.exafs.ui.views.DetectorSetupView;

public class ShowHideRegionsHandler extends AbstractHandler implements IHandler {

	public static final String ID = "uk.ac.gda.beamline.i20_1.ShowHideRegionsHandler";

	@Override
	public Object execute(ExecutionEvent event) throws ExecutionException {
//		boolean show = HandlerUtil.toggleCommandState(event.getCommand());
		((DetectorSetupView)DetectorSetupView.findMe().getPart(true)).showHideOverlay();
		return null;
	}

}
