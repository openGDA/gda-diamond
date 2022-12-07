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

package uk.ac.gda.beamline.i18;

import gda.configuration.properties.LocalProperties;

import org.eclipse.ui.IStartup;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.contexts.IContextService;

/**
 * Setting up the data prior to other views connecting to it.
 */
public class StartupService implements IStartup {

	@Override
	public void earlyStartup() {

		IContextService contextService = PlatformUI.getWorkbench().getService(IContextService.class);

		contextService.activateContext("I18 product");

		if (!LocalProperties.get("gda.factory.factoryName").equals("i18_local"))
			return;

	}

}
