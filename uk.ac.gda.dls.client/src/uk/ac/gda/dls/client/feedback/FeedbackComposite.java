/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.dls.client.feedback;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Shell;

public class FeedbackComposite {

	private Composite parent;

	public FeedbackComposite(Composite parent) {
		this.parent = parent;
	}

	public Composite createComponents() {
		
		final Group group = new Group(parent, SWT.NONE);
		group.setText("User feedback");
		
		GridLayoutFactory.swtDefaults().applyTo(group);
		
		final Button sendFeedbackButton = new Button(group, SWT.PUSH);
		GridDataFactory.swtDefaults().applyTo(sendFeedbackButton);
		sendFeedbackButton.setText("Send feedback");
		
		sendFeedbackButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				final Shell shell = parent.getShell();
				final FeedbackDialog dialog = new FeedbackDialog(shell);
				dialog.create();
				dialog.open();
			}
		});
		
		return group;
	}

}
