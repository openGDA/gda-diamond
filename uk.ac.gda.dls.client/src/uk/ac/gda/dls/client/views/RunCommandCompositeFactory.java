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

import java.io.File;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;
import org.springframework.beans.factory.InitializingBean;

import gda.jython.ICommandRunner;
import gda.jython.commandinfo.CommandThreadEvent;
import gda.rcp.views.CompositeFactory;
import swing2swt.layout.BorderLayout;
import uk.ac.gda.ui.utils.SWTUtils;

public class RunCommandCompositeFactory implements CompositeFactory, InitializingBean {

	ICommandRunner commandRunner;
	String command;
	String label;
	String jobTitle;
	String tooltip="";

	public static Composite createComposite(Composite parent, int style,
			final ICommandRunner commandRunner, String label, final String command,
			final String jobTitle, String tooltip) {
		return new RunCommandComposite(parent, style, commandRunner, label, command,
				jobTitle, tooltip);
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		return new RunCommandComposite(parent, style, commandRunner, label,
				command, jobTitle, tooltip);
	}

	public ICommandRunner getCommandRunner() {
		return commandRunner;
	}

	public void setCommandRunner(ICommandRunner commandRunner) {
		this.commandRunner = commandRunner;
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
		if (commandRunner == null)
			throw new IllegalArgumentException("commandRunner is null");
		if (command == null)
			throw new IllegalArgumentException("command is null");
		if (label == null)
			throw new IllegalArgumentException("label is null");
		if (jobTitle == null)
			throw new IllegalArgumentException("jobTitle is null");
	}

	public static void main(String... args) {

		Display display = new Display();
		Shell shell = new Shell(display);
		shell.setLayout(new BorderLayout());

		ICommandRunner iCommandRunner = new ICommandRunner() {

			@Override
			public boolean runsource(String command) {
				return false;
			}

			@Override
			public CommandThreadEvent runScript(File script) {
				return null;
			}

			@Override
			public void runCommand(String command) {
				try {
					System.out.println(command);
					Thread.sleep(1000);
				} catch (InterruptedException e) {
					e.printStackTrace();
				}

			}

			@Override
			public String locateScript(String scriptToRun) {
				return null;
			}

			@Override
			public String evaluateCommand(String command) {
				return null;
			}
		};
		final RunCommandComposite comp = new RunCommandComposite(shell, SWT.NONE, iCommandRunner, "My Label",
				"My Command", "Job Title", "tooltip");
		comp.setLayoutData(BorderLayout.NORTH);
		comp.setVisible(true);
		shell.pack();
		shell.setSize(400, 400);
		SWTUtils.showCenteredShell(shell);
	}

	public String getTooltip() {
		return tooltip;
	}

	public void setTooltip(String tooltip) {
		this.tooltip = tooltip;
	}

}