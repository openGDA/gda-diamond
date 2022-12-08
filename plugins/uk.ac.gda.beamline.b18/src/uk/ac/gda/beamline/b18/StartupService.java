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

package uk.ac.gda.beamline.b18;

import org.eclipse.ui.IStartup;
import org.eclipse.ui.PlatformUI;

import gda.configuration.properties.LocalProperties;

/**
 * Setting up the data prior to other views connecting to it.
 */
public class StartupService implements IStartup {


	@Override
	public void earlyStartup() {

		if (!LocalProperties.get("gda.factory.factoryName","").equals("b18")) return;
        PlatformUI.getWorkbench().getDisplay().asyncExec(CopyTemplateFiles::copy);
	}


}
