/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction;

import java.net.URL;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.rcp.views.CompositeFactory;
import uk.ac.gda.client.exception.AcquisitionConfigurationException;
import uk.ac.gda.client.properties.acquisition.AcquisitionConfigurationProperties;
import uk.ac.gda.client.properties.acquisition.AcquisitionPropertyType;
import uk.ac.gda.client.properties.acquisition.processing.FrameCaptureProperties;
import uk.ac.gda.client.properties.acquisition.processing.ProcessingRequestProperties;
import uk.ac.gda.core.tool.spring.AcquisitionFileContext;
import uk.ac.gda.core.tool.spring.DiffractionContextFile;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.Reloadable;
import uk.ac.gda.ui.tool.processing.ProcessingRequestComposite;
import uk.ac.gda.ui.tool.processing.context.ProcessingRequestContext;
import uk.ac.gda.ui.tool.processing.keys.ProcessingRequestKeyFactory;
import uk.ac.gda.ui.tool.processing.keys.ProcessingRequestKeyFactory.ProcessKey;
import uk.ac.gda.ui.tool.spring.ClientSpringProperties;

public class ProcessingRequestsControls implements CompositeFactory, Reloadable {

	private static final Logger logger = LoggerFactory.getLogger(ProcessingRequestsControls.class);

	private Reloadable controls;

	@Override
	public Composite createComposite(Composite parent, int style) {
		var composite = new Composite(parent, SWT.NONE);
		GridDataFactory.fillDefaults().align(SWT.FILL, SWT.CENTER).grab(true, false).applyTo(composite);
		GridLayoutFactory.swtDefaults().applyTo(composite);

		new Label(composite, SWT.NONE).setText("Process requests");
		var processingControls = new ProcessingRequestComposite(getProcessingRequestOptions());
		processingControls.createComposite(composite, SWT.NONE);
		controls = processingControls;
		return composite;
	}

	@Override
	public void reload() {
		controls.reload();
	}

	@SuppressWarnings({ "unchecked", "rawtypes" })
	private List<ProcessingRequestContext<?>> getProcessingRequestOptions() {
		return List.of(
				new ProcessingRequestContext(getProcessingRequestKeyFactory().getProcessingKey(ProcessKey.DIFFRACTION_CALIBRATION),
						getDiffractionCalibrationMergeDirectory(), getDefaultDiffractionCalibrationMergeFile(), false),
				new ProcessingRequestContext(getProcessingRequestKeyFactory().getProcessingKey(ProcessKey.DAWN),
						 getDiffractionCalibrationMergeDirectory(), new ArrayList<>(), false),
				new ProcessingRequestContext(getProcessingRequestKeyFactory().getProcessingKey(ProcessKey.FRAME_CAPTURE),
						 null, getCaptureFrameCamera(), false));
	}

	private List<FrameCaptureProperties> getCaptureFrameCamera() {
		List<FrameCaptureProperties> frameRequestDocuments = new ArrayList<>();
		FrameCaptureProperties frameCapture = null;
		try {
			frameCapture = SpringApplicationContextFacade.getBean(ClientSpringProperties.class).getAcquisitions().stream()
					.filter(a -> a.getType().equals(AcquisitionPropertyType.DIFFRACTION))
					.findFirst()
					.map(AcquisitionConfigurationProperties::getProcessingRequest)
					.map(ProcessingRequestProperties::getFrameCapture)
					.orElseThrow(() -> new AcquisitionConfigurationException("There are no properties associated with the acqual acquisition"));
			frameRequestDocuments.add(frameCapture);
		} catch (AcquisitionConfigurationException e1) {
			logger.error("Frame Capture cannot set camera", e1);
		}
		return frameRequestDocuments;
	}

	private URL getDiffractionCalibrationMergeDirectory() {
		return getClientContext().getDiffractionContext().getContextFile(DiffractionContextFile.DIFFRACTION_CALIBRATION_DIRECTORY);
	}

	private List<URL> getDefaultDiffractionCalibrationMergeFile() {
		List<URL> urls = new ArrayList<>();
		urls.add(getClientContext().getDiffractionContext().getContextFile(DiffractionContextFile.DIFFRACTION_DEFAULT_CALIBRATION));
		return urls;
	}

	private AcquisitionFileContext getClientContext() {
		return SpringApplicationContextFacade.getBean(AcquisitionFileContext.class);
	}

	private ProcessingRequestKeyFactory getProcessingRequestKeyFactory() {
		return SpringApplicationContextFacade.getBean(ProcessingRequestKeyFactory.class);
	}

}
