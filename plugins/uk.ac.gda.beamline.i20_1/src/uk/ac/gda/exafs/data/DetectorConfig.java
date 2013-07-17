/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.data;

import gda.device.DeviceException;
import uk.ac.gda.exafs.data.ClientConfig.DetectorSetup;

public class DetectorConfig extends ObservableModel {

	public static final DetectorConfig INSTANCE = new DetectorConfig();

	public static final String CURRENT_DETECTOR_SETUP_PROP_NAME = "currentDetectorSetup";
	private DetectorSetup currentDetectorSetup;

	public static final String DETECTOR_CONNECTED_PROP_NAME = "detectorConnected";
	private boolean detectorConnected;

	private DetectorConfig() {}

	public DetectorSetup getCurrentDetectorSetup() {
		return currentDetectorSetup;
	}

	public void setCurrentDetectorSetup(DetectorSetup detectorSetup) throws Exception {
		try {
			if (currentDetectorSetup != null) {
				if (currentDetectorSetup.getDetectorScannable().isConnected()) {
					currentDetectorSetup.getDetectorScannable().disconnect();
				}
			}
			if (!detectorSetup.getDetectorScannable().isConnected()) {
				detectorSetup.getDetectorScannable().connect();
			}
			firePropertyChange(DETECTOR_CONNECTED_PROP_NAME, detectorConnected, detectorConnected = true);
			firePropertyChange(CURRENT_DETECTOR_SETUP_PROP_NAME, currentDetectorSetup, currentDetectorSetup = detectorSetup);
		} catch (DeviceException e) {
			firePropertyChange(DETECTOR_CONNECTED_PROP_NAME, detectorConnected, detectorConnected = false);
			firePropertyChange(CURRENT_DETECTOR_SETUP_PROP_NAME, currentDetectorSetup, currentDetectorSetup = null);
			throw new Exception("DeviceException when connecting / disconnecting detector " + detectorSetup.getDetectorName(), e);
		}
	}

	public boolean isDetectorConnected() {
		return detectorConnected;
	}
}
