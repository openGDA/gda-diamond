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

package uk.ac.diamond.daq.beamline.k11.imaging.views;

import java.util.Optional;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.daq.client.gui.camera.CameraHelper;
import uk.ac.diamond.daq.client.gui.camera.CameraStreamsManager;
import uk.ac.diamond.daq.client.gui.camera.ICameraConfiguration;
import uk.ac.diamond.daq.client.gui.camera.liveview.CameraImageComposite;
import uk.ac.gda.client.exception.GDAClientException;
import uk.ac.gda.client.live.stream.LiveStreamConnection;
import uk.ac.gda.client.live.stream.LiveStreamException;
import uk.ac.gda.client.live.stream.view.StreamType;
import uk.ac.gda.client.properties.acquisition.AcquisitionConfigurationProperties;
import uk.ac.gda.client.properties.acquisition.AcquisitionPropertyType;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.spring.properties.AcquisitionConfigurationPropertiesUtils;

/**
 * Creates a predefined view for the imaging camera stream. It uses the
 * {@link AcquisitionConfigurationProperties#getType()} equal {@link AcquisitionPropertyType#TOMOGRAPHY}
 * and from there extracts the first available, if any, cameraID.
 *
 * @see CameraHelper
 *
 * @author Maurizio Nagni
 */
public class ImagingCameraView extends ViewPart {

	public static final String ID = "uk.ac.diamond.daq.beamline.k11.view.ImagingCameraView";

	private static final Logger logger = LoggerFactory.getLogger(ImagingCameraView.class);

	private CameraImageComposite cic;

	@Override
	public void createPartControl(Composite parent) {
		try {
			cic = new CameraImageComposite(parent, SWT.NONE, getLiveStreamConnection());
		} catch (GDAClientException e) {
			logger.error("Problem creating the CameraImageComposite", e);
		} catch (LiveStreamException e) {
			logger.error("Problem creating the live stream", e);
		}
	}

	@Override
	public void setFocus() {
		// Do not necessary
	}

	private LiveStreamConnection getLiveStreamConnection() throws LiveStreamException {
		var cc = CameraHelper.getCameraConfigurationPropertiesByID(getCameraID(AcquisitionPropertyType.TOMOGRAPHY))
				.map(CameraHelper::createICameraConfiguration)
				.map(ICameraConfiguration::getCameraConfiguration)
				.map(Optional::get)
				.orElseThrow(() -> new LiveStreamException("No Camera Confguration found"));
		return SpringApplicationContextFacade.getBean(CameraStreamsManager.class).getStreamConnection(cc, StreamType.EPICS_ARRAY);
	}

	private String getCameraID(AcquisitionPropertyType acquisitionType) throws LiveStreamException {
		return getAcquisitionConfigurationPropertiesUtils().getCameras(acquisitionType).stream()
				.findFirst()
				.orElseThrow(() -> new LiveStreamException("No Camera Confguration found"));
	}

	private AcquisitionConfigurationPropertiesUtils getAcquisitionConfigurationPropertiesUtils() {
		return SpringApplicationContextFacade.getBean(AcquisitionConfigurationPropertiesUtils.class);
	}
}
