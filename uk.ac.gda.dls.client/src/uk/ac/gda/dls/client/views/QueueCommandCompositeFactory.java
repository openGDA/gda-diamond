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

import gda.commandqueue.JythonCommandCommandProvider;
import gda.commandqueue.Queue;
import gda.rcp.views.CompositeFactory;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.IWorkbenchPartSite;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

import uk.ac.gda.client.CommandQueueViewFactory;

public class QueueCommandCompositeFactory implements CompositeFactory, InitializingBean {

	String command;
	String label;
	String description;

	@Override
	public Composite createComposite(Composite parent, int style, IWorkbenchPartSite iWorkbenchPartSite) {
		return new QueueCommandComposite(parent, style, label, command, description);
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

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		if (description == null)
			throw new IllegalArgumentException("description is null");
		if (command == null)
			throw new IllegalArgumentException("command is null");
		if (label == null)
			throw new IllegalArgumentException("label is null");
	}

}

class QueueCommandComposite extends Composite {
	private static final Logger logger = LoggerFactory.getLogger(QueueCommandComposite.class);

	private Button btn;
	
	QueueCommandComposite(Composite parent, int style, String label, final String command, final String description) {
		super(parent, style);

		GridLayoutFactory.fillDefaults().numColumns(1).applyTo(this);
		GridDataFactory.fillDefaults().applyTo(this);
		btn = new Button(this, SWT.PUSH);
		btn.setText(label);
		btn.setToolTipText(description);
		btn.addSelectionListener(new SelectionAdapter() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				super.widgetSelected(e);
				try {
					Queue queue = CommandQueueViewFactory.getQueue();
					if (queue != null) {
						queue.addToTail(new JythonCommandCommandProvider(command, description, null));
					}
				} catch (Exception e1) {
					logger.error("Error adding command " + command + " to the queue", e1);
				}
			}
		});
	}
	
	@Override
	public void setEnabled(boolean isEnabled) {
		super.setEnabled(isEnabled);
		btn.setEnabled(isEnabled);
	}
}
