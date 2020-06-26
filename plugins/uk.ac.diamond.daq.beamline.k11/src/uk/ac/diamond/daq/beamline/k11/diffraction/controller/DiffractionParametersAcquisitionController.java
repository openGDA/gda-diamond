/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.controller;

import java.net.URL;
import java.util.List;
import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationEvent;
import org.springframework.context.ApplicationListener;
import org.springframework.stereotype.Controller;

import uk.ac.diamond.daq.beamline.k11.diffraction.event.DiffractionRunAcquisitionEvent;
import uk.ac.diamond.daq.beamline.k11.diffraction.service.message.DiffractionRunMessage;
import uk.ac.diamond.daq.mapping.api.document.DetectorDocument;
import uk.ac.diamond.daq.mapping.api.document.DocumentMapper;
import uk.ac.diamond.daq.mapping.api.document.diffraction.DiffractionConfiguration;
import uk.ac.diamond.daq.mapping.api.document.diffraction.DiffractionParameterAcquisition;
import uk.ac.diamond.daq.mapping.api.document.diffraction.DiffractionParameters;
import uk.ac.diamond.daq.mapping.ui.properties.DetectorHelper;
import uk.ac.diamond.daq.mapping.ui.properties.DetectorHelper.AcquisitionType;
import uk.ac.gda.api.acquisition.AcquisitionController;
import uk.ac.gda.api.acquisition.AcquisitionControllerException;
import uk.ac.gda.api.acquisition.resource.AcquisitionConfigurationResource;
import uk.ac.gda.api.exception.GDAException;
import uk.ac.gda.client.properties.DetectorProperties;
import uk.ac.gda.tomography.stage.IStageController;
import uk.ac.gda.ui.tool.spring.SpringApplicationContextProxy;

@Controller
public class DiffractionParametersAcquisitionController
		implements AcquisitionController<DiffractionParameterAcquisition>, ApplicationListener<ApplicationEvent> {
	private static final Logger logger = LoggerFactory.getLogger(DiffractionParametersAcquisitionController.class);

	@Autowired
	private IStageController stageController;

	private DiffractionParameterAcquisition acquisition;

	// private TomographyFileService fileService;
	// @Autowired
	// private TomographyService tomographyService;

	@Autowired
	private DocumentMapper documentMapper;

	public DiffractionParametersAcquisitionController() {

	}

	@Override
	public DiffractionParameterAcquisition getAcquisition() {
		if (acquisition == null) {
			acquisition = DiffractionParametersAcquisitionController.createNewAcquisition();
		}
		return acquisition;
	}

	@Override
	public void saveAcquisitionConfiguration() throws AcquisitionControllerException {
		// TBD
	}

	@Override
	public void runAcquisition(URL outputPath) throws AcquisitionControllerException {
		runAcquisition();
	}

	@Override
	public void runAcquisition() throws AcquisitionControllerException {
		publishRun(createRunMessage());
	}

	private void publishRun(DiffractionRunMessage runMessage) {
		SpringApplicationContextProxy.publishEvent(new DiffractionRunAcquisitionEvent(this, runMessage));
	}

	@Override
	public void loadAcquisitionConfiguration(URL url) throws AcquisitionControllerException {
		// TBD
	}

	@Override
	public void loadAcquisitionConfiguration(DiffractionParameterAcquisition acquisition)
			throws AcquisitionControllerException {
		this.acquisition = acquisition;
	}

	@Override
	public AcquisitionConfigurationResource<DiffractionParameterAcquisition> parseAcquisitionConfiguration(URL url)
			throws AcquisitionControllerException {
		// return new AcquisitionConfigurationResource(url, parseJsonData(getAcquisitionBytes(url)).getAcquisition());
		return new AcquisitionConfigurationResource(url, null);
	}

	@Override
	public void onApplicationEvent(ApplicationEvent event) {
		// TomographyParametersAcquisitionControllerHelper.onApplicationEvent(event, this);
	}

	@Override
	public void deleteAcquisitionConfiguration(URL url) throws AcquisitionControllerException {
		throw new AcquisitionControllerException("Delete not implemented");
		// SpringApplicationContextProxy.publishEvent(new AcquisitionConfigurationResourceSaveEvent(url));
	}

	public static DiffractionParameterAcquisition createNewAcquisition() {
		DiffractionParameterAcquisition newConfiguration = new DiffractionParameterAcquisition();

		newConfiguration.setAcquisitionConfiguration(new DiffractionConfiguration());
		DiffractionParameters acquisitionParameters = new DiffractionParameters();
		Optional<List<DetectorProperties>> dp = DetectorHelper.getAcquistionDetector(AcquisitionType.DIFFRACTION);
		int index = 0; // in future may be parametrised
		if (dp.isPresent()) {
			DetectorDocument dd = new DetectorDocument(dp.get().get(index).getDetectorBean(), 0);
			acquisitionParameters.setDetector(dd);
		}
		newConfiguration.setName("Default name");
		newConfiguration.getAcquisitionConfiguration().setAcquisitionParameters(acquisitionParameters);
		return newConfiguration;
	}

	private DiffractionRunMessage createRunMessage() throws AcquisitionControllerException {
		return new DiffractionRunMessage(dataToJson(getAcquisition()));
	}

	private String dataToJson(Object acquisition) throws AcquisitionControllerException {
		// --- all this should be externalised to a service
		try {
			return documentMapper.toJSON(acquisition);
		} catch (GDAException e) {
			throw new AcquisitionControllerException(e);
		}
	}
}
