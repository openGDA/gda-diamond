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

package uk.ac.diamond.daq.beamline.k11.pointandshoot;

import java.util.Dictionary;
import java.util.Hashtable;

import org.dawnsci.mapping.ui.IMapClickEvent;
import org.dawnsci.mapping.ui.MapPlotManager;
import org.eclipse.dawnsci.plotting.api.axis.ClickEvent;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceRegistration;
import org.osgi.service.event.Event;
import org.osgi.service.event.EventConstants;
import org.osgi.service.event.EventHandler;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.daq.beamline.k11.Activator;
import uk.ac.diamond.daq.experiment.api.structure.ExperimentController;
import uk.ac.diamond.daq.experiment.api.structure.ExperimentControllerException;
import uk.ac.diamond.daq.mapping.ui.services.MappingServices;
import uk.ac.gda.client.UIHelper;

/**
 * Controls the lifecycle of a Point and Shoot session
 *
 * When a session is running, this controller activates the 'Ctrl+Click to Scan' handler,
 * which submits the currently selected scan centred at the click coordinates.
 *
 * At the end of a session, a request is made to the server for the creation of a single
 * encapsulating session file with links to the individual acquisitions.
 */
public class PointAndShootController {

	private static final Logger logger = LoggerFactory.getLogger(PointAndShootController.class);

	/** generates correct URLs for each sub-scan */
	private final ExperimentController experimentController;

	/** Common name root for all sub-scans */
	private final String sessionName;

	/**
	 * Handler for CtrlClick events from MappedDataView.
	 * Used to position a centred region (with the current settings) at
	 * the clicked point and then immediately run the corresponding scan.
	 */
	private EventHandler ctrlClickToScan = this::handleMapClickEvent;

	/** Cached for disposal */
	private ServiceRegistration<?> serviceRegistration;


	/**
	 * Instantiates the controller and immediately starts the session with the given name.
	 * You <b>must</b> call {@link #endSession()} to ensure consistent experiment structure
	 * and dispose internal listeners.
	 *
	 * @throws ExperimentControllerException if the session cannot be started
	 */
	public PointAndShootController(String sessionName, ExperimentController experimentControllerSupplier) throws ExperimentControllerException{
		this.sessionName = sessionName;
		this.experimentController = experimentControllerSupplier;

		startSession();
	}

	private void startSession() throws ExperimentControllerException {
		experimentController.startMultipartAcquisition(sessionName);
		registerClickEventHandler();
		logger.info("Point and Shoot session '{}' started", sessionName);
	}

	public void endSession() throws ExperimentControllerException {
		unregisterClickEventHandler();
		experimentController.stopMultipartAcquisition();
		logger.info("Point and Shoot session '{}' ended", sessionName);
	}

	/**
	 * Since the controller is instantiated on demand,
	 * the handler for OSGi {@link IMapClickEvent}s
	 * must be registered manually
	 */
	private void registerClickEventHandler() {
		Dictionary<String, String> prop = new Hashtable<>();
		prop.put(EventConstants.EVENT_TOPIC, MapPlotManager.EVENT_TOPIC_MAPVIEW_CLICK);
		BundleContext ctx = Activator.getDefault().getBundle().getBundleContext();
		serviceRegistration = ctx.registerService(EventHandler.class.getName(), ctrlClickToScan, prop);
	}

	private void unregisterClickEventHandler() {
		serviceRegistration.unregister();
		serviceRegistration = null;
	}

	private void handleMapClickEvent(Event event) {
		ClickEvent mapClickEvent = ((IMapClickEvent) event.getProperty("event")).getClickEvent();
		if (mapClickEvent.isControlDown()) {
			try {
				MappingServices.getRegionAndPathController().createRegionWithCurrentRegionValuesAt(mapClickEvent.getxValue(),
						mapClickEvent.getyValue());
				MappingServices.getScanManagementController().submitScan(experimentController.prepareAcquisition(sessionName), null);
			} catch (Exception e) {
				logger.error("Scan submission failed", e);
				String detail = e.getMessage() == null ? "See log for details" : e.getMessage();
				UIHelper.showError("Error submitting scan", detail);
			}
		}
	}

}
