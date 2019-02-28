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

package uk.ac.gda.dls.client.views;

import org.eclipse.swt.widgets.Composite;
import org.springframework.beans.factory.InitializingBean;

import gda.jython.ICommandRunner;
import gda.jython.InterfaceProvider;
import gda.rcp.views.CompositeFactory;

public class RunCommandCompositeFactory implements CompositeFactory, InitializingBean {

	private String command;
	private String label;
	private String jobTitle;
	private String tooltip = "";

	@Override
	public Composite createComposite(Composite parent, int style) {
		final ICommandRunner commandRunner = InterfaceProvider.getCommandRunner();
		return new RunCommandComposite(parent, style, commandRunner, label,
				command, jobTitle, tooltip);
	}

	public String getCommand() {
		return command;
	}

	public void setCommand(String command) {
		this.command = command;
	}

	public String getLabel() {
		return label;
	}

	public void setLabel(String label) {
		this.label = label;
	}

	public String getJobTitle() {
		return jobTitle;
	}

	public void setJobTitle(String jobTitle) {
		this.jobTitle = jobTitle;
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		if (command == null)
			throw new IllegalArgumentException("command is null");
		if (label == null)
			throw new IllegalArgumentException("label is null");
		if (jobTitle == null)
			throw new IllegalArgumentException("jobTitle is null");
	}

	public String getTooltip() {
		return tooltip;
	}

	public void setTooltip(String tooltip) {
		this.tooltip = tooltip;
	}

}