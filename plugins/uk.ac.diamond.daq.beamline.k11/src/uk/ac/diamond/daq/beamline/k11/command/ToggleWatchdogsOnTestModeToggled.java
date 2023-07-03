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

import org.springframework.context.ApplicationListener;

import gda.jython.InterfaceProvider;
import uk.ac.gda.client.properties.mode.TestModeToggled;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.spring.ClientSpringProperties;

public class ToggleWatchdogsOnTestModeToggled implements ApplicationListener<TestModeToggled> {

	public void attachListener() {
		SpringApplicationContextFacade.addApplicationListener(this);
	}

	@Override
	public void onApplicationEvent(TestModeToggled event) {
		var testModeActive = getClientProperties().getModes().getTest().isActive();
		var command = testModeActive ? "disable_watchdogs()" : "enable_watchdogs()";
		InterfaceProvider.getCommandRunner().runCommand(command);
	}

	private ClientSpringProperties getClientProperties() {
		return SpringApplicationContextFacade.getBean(ClientSpringProperties.class);
	}

}
