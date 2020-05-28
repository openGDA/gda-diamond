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

package uk.ac.diamond.daq.beamline.k11.diffraction.service.impl;

import java.io.File;
import java.net.URI;
import java.net.URL;

import org.eclipse.e4.core.contexts.IEclipseContext;
import org.eclipse.scanning.api.device.IRunnableDeviceService;
import org.eclipse.scanning.api.event.IEventService;
import org.eclipse.scanning.api.event.scan.ScanBean;
import org.eclipse.scanning.api.scan.ScanningException;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import gda.configuration.properties.LocalProperties;
import uk.ac.diamond.daq.beamline.k11.diffraction.event.DiffractionRunAcquisitionEvent;
import uk.ac.diamond.daq.beamline.k11.diffraction.service.DiffractionService;
import uk.ac.diamond.daq.beamline.k11.diffraction.service.DiffractionServiceException;
import uk.ac.diamond.daq.beamline.k11.diffraction.service.message.DiffractionRunMessage;
import uk.ac.diamond.daq.mapping.api.IScanBeanSubmitter;
import uk.ac.diamond.daq.mapping.api.document.DocumentMapper;
import uk.ac.diamond.daq.mapping.api.document.ScanRequestDocument;
import uk.ac.diamond.daq.mapping.api.document.ScanRequestFactory;
import uk.ac.gda.api.exception.GDAException;
import uk.ac.gda.tomography.service.Arrangement;

/**
 * @author Maurizio Nagni
 */
@Component("diffractionService")
public class DiffractionServiceImpl implements DiffractionService {
	private static final Logger logger = LoggerFactory.getLogger(DiffractionServiceImpl.class);

	@Autowired
	private DocumentMapper documentMapper;

	public DiffractionServiceImpl() {
		super();
	}

	@Override
	public void onApplicationEvent(DiffractionRunAcquisitionEvent event) {
		try {
			runAcquisition(event.getRunDiffractionMessage(), null, null, null);
		} catch (DiffractionServiceException e) {
			logger.error("TODO put description of error here", e);
		}
	}

	@Override
	public void runAcquisition(DiffractionRunMessage message, File script, File onError, File onSuccess)
			throws DiffractionServiceException {
		executeCommand(message, script, onError, onSuccess, "doAcquisition");
	}

	@Override
	public void resetInstruments(Arrangement arrangement) throws DiffractionServiceException {
		arrangement.doArrangement();
	}

	@Override
	public URL takeDarkImage(DiffractionRunMessage message, File script) throws DiffractionServiceException {
		return null;
	}

	@Override
	public URL takeFlatImage(DiffractionRunMessage message, File script) throws DiffractionServiceException {
		return null;
	}

	private void executeCommand(DiffractionRunMessage message, File script, File onError, File onSuccess,
			String command) throws DiffractionServiceException {
		submitScan(message);
	}

	private ScanRequestDocument createSRD(DiffractionRunMessage message) throws DiffractionServiceException {
		try {
			return documentMapper.toJSON((String) message.getConfiguration(), ScanRequestDocument.class);
		} catch (GDAException e) {
			throw new DiffractionServiceException("Json error", e);
		}
	}

	/**
	 * Submits the acquisition configuration to the submission service.
	 *
	 * @param filePath
	 *            The filepath of the output NeXus file. If {@code null} it is generated through default properties.
	 */
	private void submitScan(DiffractionRunMessage message) {
		final IScanBeanSubmitter submitter = PlatformUI.getWorkbench().getService(IScanBeanSubmitter.class);
		try {
			ScanRequestDocument srd = createSRD(message);
			// default path name
			String pathName = "Diffraction";
			final ScanBean scanBean = new ScanBean();
			scanBean.setName(String.format("%s - %s Scan", srd.getName(), pathName));
			scanBean.setFilePath(srd.getFilePath().toExternalForm());
			scanBean.setBeamline(System.getProperty("BEAMLINE", "dummy"));

			ScanRequestFactory tsr = new ScanRequestFactory(srd);
			scanBean.setScanRequest(tsr.createScanRequest(getRunnableDeviceService()));
			submitter.submitScan(scanBean);
		} catch (Exception e) {
			// This is a temporary solution. Better will be done when tomo and diffraction will be unified
			logger.error("Cannot submit acquisition", e);
		}
	}

	private IRunnableDeviceService getRunnableDeviceService() throws ScanningException {
		return getRemoteService(IRunnableDeviceService.class);
	}

	private <T> T getRemoteService(Class<T> klass) throws ScanningException {
		IEclipseContext injectionContext = PlatformUI.getWorkbench().getService(IEclipseContext.class);
		IEventService eventService = injectionContext.get(IEventService.class);
		try {
			URI jmsURI = new URI(LocalProperties.getActiveMQBrokerURI());
			return eventService.createRemoteService(jmsURI, klass);
		} catch (Exception e) {
			logger.error("Error getting remote service {}", klass, e);
			throw new ScanningException(e);
		}
	}
}
