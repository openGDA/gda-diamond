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

package uk.ac.gda.exafs.ui.views.commandhandlers;

import org.eclipse.core.commands.AbstractHandler;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.ui.IWorkbenchPart;
import org.eclipse.ui.handlers.HandlerUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.calibration.ui.CalibrationPlotViewer;

public class ResetCalibrationDataPlot extends AbstractHandler {

	private static final Logger logger = LoggerFactory.getLogger(ResetCalibrationDataPlot.class);

	@Override
	public Object execute(ExecutionEvent event) throws ExecutionException {
		IWorkbenchPart view = HandlerUtil.getActiveWorkbenchWindow(event).getActivePage().getActivePart();
		if (view instanceof CalibrationPlotViewer) {
			CalibrationPlotViewer refView = (CalibrationPlotViewer) view;
			try {
				refView.plotData();
			} catch (Exception e) {
				UIHelper.showError("Unable to reset plot data", e.getMessage());
				logger.error("Unable to reset plot data", e);
			}
		}
		return null;
	}

}
