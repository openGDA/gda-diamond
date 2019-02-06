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
import org.eclipse.core.databinding.beans.PojoProperties;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.dawnsci.analysis.api.roi.IROI;
import org.eclipse.dawnsci.plotting.api.axis.ClickEvent;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.scanning.api.event.scan.ScanBean;
import org.eclipse.scanning.api.event.scan.ScanRequest;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.PlatformUI;
import org.osgi.service.event.Event;
import org.osgi.service.event.EventHandler;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.daq.mapping.api.IMappingExperimentBean;
import uk.ac.diamond.daq.mapping.api.IMappingExperimentBeanProvider;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanBeanSubmitter;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanRequestConverter;

/**
 * Handler for CtrlClick events from MappedDataView. Used to position a centred region (with the current settings) at
 * the clicked point and then immediately run the corresponding scan
 *
 * @since GDA 9.13
 */
public class CtrlClickToScanHandler implements EventHandler {

	private static final Logger logger = LoggerFactory.getLogger(CtrlClickToScanHandler.class);

	private ScanRequestConverter converter;
	private ScanBeanSubmitter submitter;
	private IMappingExperimentBeanProvider mappingExperimentBeanProvider;
	private RegionAndPathController controller;

	public CtrlClickToScanHandler() {
		logger.debug("ClickToScanHandler created");
	}

	@Override
	public void handleEvent(Event event) {
		final ClickEvent mapClickEvent = ((IMapClickEvent) event.getProperty("event")).getClickEvent();
		if (controller.isClickToScanArmed()	&& mapClickEvent.isControlDown()) {
			try {
				controller.createRegionWithCurrentRegionValuesAt(mapClickEvent.getxValue(), mapClickEvent.getyValue());
				ScanBean scanBean = createScanBean();
				submitter.submitScan(scanBean);
			} catch (Exception e) {
				logger.error("Scan submission failed", e);
				Shell shell = PlatformUI.getWorkbench().getActiveWorkbenchWindow().getShell();
				MessageDialog.openError(shell, "Error Submitting Scan",
						"The scan could not be submitted. See the error log for more details.");
			}
		}
	}

	// Called by OSGi:
	public void setScanRequestConverter(ScanRequestConverter converter) {
		this.converter = converter;
	}

	public void setSubmitterService(ScanBeanSubmitter submitter) {
		this.submitter = submitter;
	}

	public void setMappingExperimentBeanProvider(IMappingExperimentBeanProvider mappingExperimentBeanProvider) {
		this.mappingExperimentBeanProvider = mappingExperimentBeanProvider;
	}

	public void setRegionAndPathController(RegionAndPathController controller) {
		this.controller = controller;
	}

	@SuppressWarnings("unchecked")
	public IObservableValue<Boolean> getIsArmedObservable() {
		return PojoProperties.value("armed").observe(this);
	}

	/**
	 * Creates a {@link ScanBean} using the current {@link IMappingExperimentBean}.
	 *
	 * TODO: this should probably be handled by a central Scan Submission Controller so that is is done in one place
	 * and direct access to the mapping bean is not required.
	 *
	 * @return	The constructed {@link ScanBean}
	 */
	private ScanBean createScanBean() {
		final IMappingExperimentBean mappingBean = mappingExperimentBeanProvider.getMappingExperimentBean();

		final ScanBean scanBean = new ScanBean();
		String sampleName = mappingBean.getSampleMetadata().getSampleName();
		if (sampleName == null || sampleName.length() == 0) {
			sampleName = "unknown sample";
		}
		final String pathName = mappingBean.getScanDefinition().getMappingScanRegion().getScanPath().getName();
		scanBean.setName(String.format("%s - %s Scan", sampleName, pathName));
		scanBean.setBeamline(System.getProperty("BEAMLINE"));


		final ScanRequest<IROI> scanRequest = converter.convertToScanRequest(mappingBean);
		scanBean.setScanRequest(scanRequest);
		return scanBean;
	}
}
