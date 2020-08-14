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

package gda.device.scannable;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import org.apache.commons.configuration.ConfigurationException;
import org.apache.commons.configuration.PropertiesConfiguration;
import org.junit.Test;

public class AlignmentStageScannableTest {

	@Test
	public void test() throws IOException, ConfigurationException {
		Path tempFile = Files.createTempFile(null, null);
		PropertiesConfiguration configuration = new PropertiesConfiguration();
		AlignmentStageScannable.AlignmentStageDevice.eye.getLocation().setxPosition(1.0);
		AlignmentStageScannable.AlignmentStageDevice.eye.save(configuration);
		configuration.save(tempFile.toFile());

		tempFile = Files.createTempFile(null, null);
		AlignmentStageScannable.FastShutter.FIRST_SHUTTER_INSTANCE.getInLocation().setxPosition(6.0);
		AlignmentStageScannable.FastShutter.FIRST_SHUTTER_INSTANCE.getInLocation().setyPosition(6.0);
		AlignmentStageScannable.FastShutter.FIRST_SHUTTER_INSTANCE.getOutLocation().setxPosition(9.0);
		AlignmentStageScannable.FastShutter.FIRST_SHUTTER_INSTANCE.getOutLocation().setyPosition(9.0);
		AlignmentStageScannable.FastShutter.FIRST_SHUTTER_INSTANCE.save(configuration);
		configuration.save(tempFile.toFile());
		PropertiesConfiguration configuration2 = new PropertiesConfiguration();
		configuration2.setDelimiterParsingDisabled(true);
		configuration2.load(tempFile.toFile());
		AlignmentStageScannable.FastShutter.FIRST_SHUTTER_INSTANCE.load(configuration2);
	}

}
