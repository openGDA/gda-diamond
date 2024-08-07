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

import static uk.ac.gda.ui.tool.rest.ClientRestServices.getExperimentController;

import java.util.Dictionary;
import java.util.Hashtable;
import java.util.NoSuchElementException;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import org.dawnsci.mapping.ui.IMapClickEvent;
import org.dawnsci.mapping.ui.MapPlotManager;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.osgi.framework.ServiceRegistration;
import org.osgi.service.event.Event;
import org.osgi.service.event.EventConstants;
import org.osgi.service.event.EventHandler;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.ApplicationListener;

import uk.ac.diamond.daq.beamline.k11.Activator;
import uk.ac.diamond.daq.concurrent.Async;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent.UpdatedProperty;
import uk.ac.diamond.daq.mapping.ui.services.MappingRemoteServices;
import uk.ac.gda.api.acquisition.Acquisition;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.exception.AcquisitionControllerException;
import uk.ac.gda.client.exception.GDAClientRestException;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;
import uk.ac.gda.ui.tool.spring.ClientRemoteServices;

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

	/**
	 * Handler for CtrlClick events from MappedDataView.
	 * Used to position a centred region (with the current settings) at
	 * the clicked point and then immediately run the corresponding scan.
	 */
	private EventHandler ctrlClickToScan = this::handleMapClickEvent;

	/** Cached for disposal */
	private ServiceRegistration<?> serviceRegistration;

	/** Used to wait until acquisition coordinates have changed before starting the acquisition */
	private RegionMovedLatch synchroniser;

	/**
	 * Instantiates the controller and immediately starts the session with the given name.
	 * You <b>must</b> call {@link #endSession()} to ensure consistent experiment structure
	 * and dispose internal listeners.
	 */
	public PointAndShootController() {
		synchroniser = new RegionMovedLatch();
	}

	public void startSession() throws GDAClientRestException {
		try {
			startSession(getSessionName());
		} catch (NoSuchElementException e) {
			UIHelper.showWarning(ClientMessages.NO_CONTROLLER, e);
		}
	}

	private void startSession(String sessionName) throws GDAClientRestException {
		if (!getExperimentController().isExperimentInProgress()) {
			throw new GDAClientRestException("An experiment must be started first");
		}
		SpringApplicationContextFacade.addApplicationListener(synchroniser);
		getMapPlottingSystem().setTitle("Point and Shoot: Ctrl+Click to scan");
		getExperimentController().startMultipartAcquisition(sessionName);
		registerClickEventHandler();
		logger.info("Point and Shoot session '{}' started", sessionName);
	}

	public void endSession() throws GDAClientRestException {
		try {
			endSession(getSessionName());
		} catch (NoSuchElementException e) {
			UIHelper.showWarning(ClientMessages.NO_CONTROLLER, e);
		}
	}

	private void endSession(String sessionName) throws GDAClientRestException {
		unregisterClickEventHandler();
		getExperimentController().stopMultipartAcquisition();
		getMapPlottingSystem().setTitle(" ");
		SpringApplicationContextFacade.removeApplicationListener(synchroniser);
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
		var ctx = Activator.getDefault().getBundle().getBundleContext();
		serviceRegistration = ctx.registerService(EventHandler.class.getName(), ctrlClickToScan, prop);
	}

	private void unregisterClickEventHandler() {
		serviceRegistration.unregister();
		serviceRegistration = null;
	}

	/**
	 * When the event is a ctrl+click event, we
	 * 1) centre the current acquisition around the click coordinates,
	 * 2) run the scan
	 *
	 * We do not change the coordinates of the acquisition controller's acquisition directly;
	 * this is done via a series of events. We therefore use a latch mechanism to prevent a race condition.
	 */
	private void handleMapClickEvent(Event event) {
		var mapClickEvent = ((IMapClickEvent) event.getProperty("event")).getClickEvent();
		if (!mapClickEvent.isControlDown()) return;

		Async.execute(() -> { // we do not want to hold up the messaging thread
			double x = mapClickEvent.getxValue();
			double y = mapClickEvent.getyValue();

			synchroniser.arm();

			SpringApplicationContextFacade.getBean(MappingRemoteServices.class)
				.getRegionAndPathController().createRegionWithCurrentRegionValuesAt(x, y);

			try {
				if (synchroniser.await()) {
					getScanningAcquisitionTemporaryHelper()
						.getAcquisitionControllerElseThrow()
						.runAcquisition();
				} else {
					logger.error("Region change not registered within timeout");
				}
			} catch (InterruptedException e) {
				logger.error("Interrupted while waiting for region to change", e);
				Thread.currentThread().interrupt();
			} catch (AcquisitionControllerException e) {
				logger.error("Scan submission failed", e);
				String detail = e.getMessage() == null ? "See log for details" : e.getMessage();
				UIHelper.showError("Error submitting scan", detail);
			} catch (NoSuchElementException e) {
				UIHelper.showWarning(ClientMessages.NO_CONTROLLER, e);
			}

		});
	}

	private IPlottingSystem<Object> getMapPlottingSystem() {
		return SpringApplicationContextFacade.getBean(ClientRemoteServices.class).getIPlottingService().getPlottingSystem("Map");
	}

	private class RegionMovedLatch implements ApplicationListener<ScanningAcquisitionChangeEvent> {

		private CountDownLatch latch;
		private boolean armed;

		public void arm() {
			latch = new CountDownLatch(1);
			armed = true;
		}

		/**
		 * Blocks until the expected message is received (returning {@code true}),
		 * or the waiting time elapses ({@code false}).
		 */
		public boolean await() throws InterruptedException {
			return latch.await(5, TimeUnit.SECONDS);
		}

		/**
		 * When the required region change is applied, an event is broadcast.
		 * If this is said event, we countdown.
		 */
		@Override
		public void onApplicationEvent(ScanningAcquisitionChangeEvent event) {
			if (armed && event.getProperty().equals(UpdatedProperty.PATH)) {
				latch.countDown();
				armed = false;
			}
		}
	}

	// ------------ UTILS ----
	private ScanningAcquisitionTemporaryHelper getScanningAcquisitionTemporaryHelper() {
		return SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class);
	}

	private String getSessionName() {
		return getScanningAcquisitionTemporaryHelper()
			.getScanningAcquisition()
			.map(Acquisition::getName)
			.orElseThrow();
	}
}
