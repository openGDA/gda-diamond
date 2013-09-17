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

package uk.ac.gda.dls.client;

import org.eclipse.core.commands.AbstractHandler;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.dls.client.feedback.FeedbackDialog;

public class feedbackHandler extends AbstractHandler {
	static final Logger logger = LoggerFactory.getLogger(feedbackHandler.class);

	@Override
	public Object execute(ExecutionEvent event) throws ExecutionException {
		FeedbackDialog feedbackDialog = new FeedbackDialog(PlatformUI.getWorkbench().getActiveWorkbenchWindow().getShell());
		feedbackDialog.create();
		feedbackDialog.open();
		return Boolean.TRUE;
	}

}
