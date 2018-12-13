/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package gda.images.camera;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

import java.io.File;

import org.junit.Test;

import gda.device.DeviceException;
import gda.images.camera.BeamDataComponent.BeamData;

public class BeamDataComponentTest {

	@Test
	public void testBeamDataComponent() {
		File displayConfigFile = new File("testfiles/gda/images/camera/display.configuration");

		BeamDataComponent component = BeamDataComponent.getTestingInstance(displayConfigFile.getAbsolutePath());

		Camera camera = new DummyOpticalCamera() {
			@Override
			public double getZoom() throws DeviceException {
				return 1.0;
			}
		};
		component.setOpticalCamera(camera);

		BeamData beamData = component.getCurrentBeamData();
		assertNotNull(beamData);
		assertEquals(512, beamData.xCentre);
		assertEquals(384, beamData.yCentre);
	}

}
