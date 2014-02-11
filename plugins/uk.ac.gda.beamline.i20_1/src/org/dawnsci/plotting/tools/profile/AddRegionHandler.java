/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package org.dawnsci.plotting.tools.profile;

import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.region.IRegion;
import org.dawnsci.plotting.api.region.IRegion.RegionType;
import org.eclipse.core.commands.AbstractHandler;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.ui.IWorkbenchPart;
import org.eclipse.ui.handlers.HandlerUtil;

public class AddRegionHandler extends AbstractHandler {

	@Override
	public Object execute(ExecutionEvent event) throws ExecutionException {
		//if (event.getTrigger() instanceof AbstractToolPage) {
		try {
			IWorkbenchPart test = HandlerUtil.getActivePart(event);
			IPlottingSystem plottingSystem = ((TimeResolvedToolPage) event.getTrigger()).getPlottingSystem();
			IRegion region = plottingSystem.createRegion("Test", RegionType.YAXIS);
			region.setPlotType(plottingSystem.getPlotType());
		} catch (Exception e) {
			System.out.println(e.getMessage());
			// TODO Auto-generated catch block
		}
		//}
		return null;
	}

}
