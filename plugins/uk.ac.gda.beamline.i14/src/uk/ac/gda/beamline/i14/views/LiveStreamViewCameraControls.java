/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i14.views;

import static org.eclipse.swt.events.SelectionListener.widgetSelectedAdapter;

import java.util.Objects;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import uk.ac.gda.api.camera.CameraControl;
import uk.ac.gda.client.live.stream.view.customui.AbstractLiveStreamViewCustomUi;
import uk.ac.gda.client.widgets.LiveStreamExposureTimeComposite;

public class LiveStreamViewCameraControls extends AbstractLiveStreamViewCustomUi {
	private static Logger logger = LoggerFactory.getLogger(LiveStreamViewCameraControls.class);

	private CameraControl cameraControl;

	/**
	 * Scannable to reset camera - the actual camera, not GDA's connection to it (optional)
	 */
	private Scannable cameraResetScannable;

	public LiveStreamViewCameraControls(CameraControl cameraControl) {
		Objects.requireNonNull(cameraControl, "Camera control must not be null");
		this.cameraControl = cameraControl;
	}

	@Override
	public void createUi(Composite composite) {
		final Composite mainComposite = new Composite(composite, SWT.NONE);
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(mainComposite);

		// Exposure control
		final LiveStreamExposureTimeComposite exposureTimeComposite = new LiveStreamExposureTimeComposite(mainComposite, SWT.NONE, cameraControl);
		GridDataFactory.fillDefaults().grab(true, false).applyTo(exposureTimeComposite);

		// Reset button
		if (cameraResetScannable != null) {
			final Button resetButton = new Button(mainComposite, SWT.PUSH);
			GridDataFactory.swtDefaults().align(SWT.RIGHT, SWT.CENTER).applyTo(resetButton);
			resetButton.setText("Reset camera");
			resetButton.addSelectionListener(widgetSelectedAdapter(this::resetCamera));
		}
	}

	private void resetCamera(@SuppressWarnings("unused") SelectionEvent e) {
		try {
			cameraResetScannable.asynchronousMoveTo(1);
		} catch (DeviceException ex) {
			logger.error("Error resetting camera {}", cameraControl.getName(), ex);
		}
	}

	public void setCameraResetScannable(Scannable cameraResetScannable) {
		this.cameraResetScannable = cameraResetScannable;
	}
}
