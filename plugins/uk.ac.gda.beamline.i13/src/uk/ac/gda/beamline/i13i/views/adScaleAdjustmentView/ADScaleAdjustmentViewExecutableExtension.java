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

package uk.ac.gda.beamline.i13i.views.adScaleAdjustmentView;

import gda.device.detector.areadetector.v17.NDStats;
import gda.rcp.views.AbstractFindableExecutableExtension;

import org.eclipse.core.runtime.CoreException;

public class ADScaleAdjustmentViewExecutableExtension extends AbstractFindableExecutableExtension{

	
	String viewTitle;
	private NDStats ndStats;
	
	
	public String getViewTitle() {
		return viewTitle;
	}

	public void setViewTitle(String viewTitle) {
		this.viewTitle = viewTitle;
	}


	@Override
	public Object create() throws CoreException {
		return new ADScaleAdjustmentView(ndStats);
	}

	public void setNdStats(NDStats ndStats) {
		this.ndStats = ndStats;
	}

	@Override
	public void afterPropertiesSet() throws Exception {
	}
}
