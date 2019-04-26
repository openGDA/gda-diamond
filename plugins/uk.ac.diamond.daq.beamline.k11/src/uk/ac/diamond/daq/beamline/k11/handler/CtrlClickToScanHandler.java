/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.handler;

import org.dawnsci.mapping.ui.IMapClickEvent;
import org.eclipse.dawnsci.plotting.api.axis.ClickEvent;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.PlatformUI;
import org.osgi.service.event.Event;
import org.osgi.service.event.EventHandler;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanBeanSubmitter;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;

/**
 * Handler for CtrlClick events from MappedDataView. Used to position a centred region (with the current settings) at
 * the clicked point and then immediately run the corresponding scan. The handler only gets created when the first click
 * is actually performed so it can consume the necessary OSGi services via declarative initialisation.
 *
 * @since GDA 9.13
 */
public class CtrlClickToScanHandler implements EventHandler {

	private static final Logger logger = LoggerFactory.getLogger(CtrlClickToScanHandler.class);

	private ScanBeanSubmitter submitter;
	private RegionAndPathController rapController;
	private ScanManagementController smController;

	public CtrlClickToScanHandler() {
		logger.debug("ClickToScanHandler created");
	}

	@Override
	public void handleEvent(Event event) {
		final ClickEvent mapClickEvent = ((IMapClickEvent) event.getProperty("event")).getClickEvent();
		if (smController.isClickToScanArmed()	&& mapClickEvent.isControlDown()) {
			try {
				rapController.createRegionWithCurrentRegionValuesAt(mapClickEvent.getxValue(), mapClickEvent.getyValue());
				submitter.submitScan(smController.createScanBean());
			} catch (Exception e) {
				logger.error("Scan submission failed", e);
				Shell shell = PlatformUI.getWorkbench().getActiveWorkbenchWindow().getShell();
				MessageDialog.openError(shell, "Error Submitting Scan",
						"The scan could not be submitted. See the error log for more details.");
			}
		}
	}

	// Called by OSGi:
	public void setSubmitterService(ScanBeanSubmitter submitter) {
		this.submitter = submitter;
	}

	public void setRegionAndPathController(RegionAndPathController controller) {
		this.rapController = controller;
	}

	public void setScanManagementController(ScanManagementController controller) {
		this.smController = controller;
	}
}
