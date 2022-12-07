/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package gda.device.detector;

import static org.junit.Assert.assertEquals;

import org.eclipse.january.dataset.IDataset;
import org.junit.Test;

import uk.ac.gda.exafs.detectortemperature.XCHIPTemperatureLogParser;

public class XCHIPTemperatureParserTest {

	public static final String FOLDER_PATH = "testfiles/gda/device/detector/";

	@Test
	public void testReadTemperatureFile() {
		XCHIPTemperatureLogParser parser = new XCHIPTemperatureLogParser(FOLDER_PATH + "xchip_detectors.log");

		IDataset[][] tempLog = parser.getTemperatures();

		assertEquals(2, tempLog.length);
		assertEquals(4, tempLog[0].length);
		assertEquals(3,tempLog[0][0].getShape()[0]);
		assertEquals(38.50, tempLog[1][3].getDouble(0),0.01);
		assertEquals(1392715510, tempLog[0][0].getLong(2));
	}
}
