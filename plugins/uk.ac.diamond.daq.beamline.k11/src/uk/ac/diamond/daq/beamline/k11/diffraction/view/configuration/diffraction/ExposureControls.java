/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.ApplicationListener;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.client.gui.camera.CameraHelper;
import uk.ac.diamond.daq.client.gui.camera.ICameraConfiguration;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.gda.api.acquisition.parameters.DetectorDocument;
import uk.ac.gda.client.exception.GDAClientRestException;
import uk.ac.gda.client.widgets.DetectorExposureWidget;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.Reloadable;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;

public class ExposureControls implements CompositeFactory, Reloadable{

	private Composite composite;
	private DetectorExposureWidget exposure;

	private ScanningParameters parameters;

	private static final Logger logger = LoggerFactory.getLogger(ExposureControls.class);

	public ExposureControls() {
		parameters = SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class).getScanningParameters().orElseThrow();
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		composite = new Composite(parent, SWT.NONE);
		GridLayoutFactory.swtDefaults().numColumns(2).equalWidth(true).applyTo(composite);
		GridDataFactory.fillDefaults().align(SWT.FILL, SWT.CENTER).grab(true, false).applyTo(composite);

		new Label(composite, SWT.NONE).setText("Detector exposure (s)");

		exposure = new DetectorExposureWidget(composite, this::updateDetectorDocument, this::getDetectorExposure);

		exposure.updateFromModel(getDetectorDocument().getExposure());

		ScanningAcquisitionListener acquisitionListener = new ScanningAcquisitionListener();
		SpringApplicationContextFacade.addDisposableApplicationListener(composite, acquisitionListener);

		return composite;
	}

	private DetectorDocument getDetectorDocument() {
		return parameters.getDetectors().stream().findFirst().orElseThrow();
	}

	private void updateDetectorDocument(double exposure) {
		var oldDetectorDocument = getDetectorDocument();
		var detectorDocument = new DetectorDocument.Builder()
					.withId(oldDetectorDocument.getId())
					.withMalcolmDetectorName(oldDetectorDocument.getMalcolmDetectorName())
					.withExposure(exposure)
					.build();
		parameters.setDetector(detectorDocument);
		publishUpdate();
	}

	private double getDetectorExposure(){
		var cameraControlClient =  CameraHelper.getCameraConfigurationPropertiesByID(getDetectorDocument().getId())
				.map(CameraHelper::createICameraConfiguration)
				.map(ICameraConfiguration::getCameraControlClient)
				.orElseThrow();
		try {
			if (cameraControlClient.isPresent()) {
				return cameraControlClient.get().getAcquireTime();
			} else {
				return 0.0;
			}
		} catch (GDAClientRestException e) {
			logger.error("Error reading detector exposure {}", e.getMessage());
			return 0.0;
		}
	}

	private void refreshParameters() {
		parameters = SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class).getScanningParameters().orElseThrow();
	}

	private void publishUpdate() {
		SpringApplicationContextFacade.publishEvent(new ScanningAcquisitionChangeEvent(this));
	}

	private class ScanningAcquisitionListener implements ApplicationListener<ScanningAcquisitionChangeEvent> {
		@Override
		public void onApplicationEvent(ScanningAcquisitionChangeEvent event) {
			if (!(event.getSource() instanceof ExposureControls)) {
				refreshParameters();
				Display.getDefault().asyncExec(ExposureControls.this::updateExposureTextFromDocument);
			}
		}
	}

	@Override
	public void reload() {
		if (composite == null || composite.isDisposed()) return;
		refreshParameters();
		updateExposureTextFromDocument();
	}

	private void updateExposureTextFromDocument() {
		if (composite.isDisposed()) return;
		exposure.updateFromModel(getDetectorDocument().getExposure());
	}

}


