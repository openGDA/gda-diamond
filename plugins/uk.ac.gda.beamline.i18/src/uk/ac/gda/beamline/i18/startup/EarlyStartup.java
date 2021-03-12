/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i18.startup;

import java.util.Arrays;
import java.util.NoSuchElementException;

import org.eclipse.core.commands.ExecutionException;
import org.eclipse.core.commands.NotEnabledException;
import org.eclipse.core.commands.NotHandledException;
import org.eclipse.core.commands.common.NotDefinedException;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IPerspectiveDescriptor;
import org.eclipse.ui.IStartup;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PerspectiveAdapter;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.handlers.IHandlerService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.client.experimentdefinition.components.ExperimentExperimentView;
import uk.ac.gda.client.experimentdefinition.components.ExperimentPerspective;
import uk.ac.gda.client.experimentdefinition.ui.handlers.RefreshProjectCommandHandler;

public class EarlyStartup implements IStartup {

	private static final Logger logger = LoggerFactory.getLogger(EarlyStartup.class);

	@Override
	public void earlyStartup() {
		Display.getDefault().asyncExec(this::attachPerspectiveListener);
	}

	private void attachPerspectiveListener() {
		final IWorkbenchWindow workbenchWindow = PlatformUI.getWorkbench().getActiveWorkbenchWindow();
		if (workbenchWindow != null) {
			workbenchWindow.addPerspectiveListener(new ExperimentPerspectiveAdapter());
		}
	}

	/**
	 * Refreshes the project when the experiment perspective is switched to
	 */
	private class ExperimentPerspectiveAdapter extends PerspectiveAdapter {

		@Override
		public void perspectiveActivated(IWorkbenchPage page, IPerspectiveDescriptor perspective) {
			if (perspective.getId().equals(ExperimentPerspective.ID)) {
				refreshProject(page);
			}
		}

		private void refreshProject(IWorkbenchPage page) {
			try {
				getHandlerService(page).executeCommand(RefreshProjectCommandHandler.ID, null);
			} catch (ExecutionException | NotDefinedException | NotEnabledException | NotHandledException e) {
				logger.error("Error during refresh", e);
			}
		}

		private IHandlerService getHandlerService(IWorkbenchPage page) {
			return Arrays.stream(page.getViewReferences())
				.filter(reference -> reference.getId().equals(ExperimentExperimentView.ID))
				.map(reference -> reference.getView(true))
				.map(ExperimentExperimentView.class::cast)
				.map(IViewPart::getSite)
				.map(site -> site.getService(IHandlerService.class))
				.findFirst().orElseThrow(NoSuchElementException::new);
		}
	}
}
