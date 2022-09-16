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

package gda.scan;

import static org.junit.Assert.assertEquals;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Paths;

import org.apache.commons.io.FileUtils;
import org.junit.Test;

import gda.scan.ede.TimeResolvedExperimentParameters;

public class TimeResolvedExperimentParametersTest {

	public static final String FOLDER_PATH = "testfiles/parameter-files";

	public void testFile(String fileName) throws IOException {
		String xmlString = getXmlString(fileName);
		var params = TimeResolvedExperimentParameters.fromXML(xmlString);
		String xmlFromParams = params.toXML().trim();

		// Remove the empty motorPositionsDuring scan entry from original string.
		xmlString = xmlString.replaceAll("<motorPositionsDuringScan/>\\s+", "");

		// Remove time between repetitions from newly serialized XML, if original
		// XML doesn't contain it (it's a recently added field)
		xmlFromParams = xmlString.contains("timeBetweenRepetitions") ? xmlFromParams:removeTimeBetweenRepetitions(xmlFromParams);
		assertEquals("String serialized from "+fileName+" is not correct", TimeResolvedExperimentParameters.sanitizeXmlString(xmlString), xmlFromParams);
	}

	private String getXmlString(String fileName) throws IOException {
		return FileUtils.readFileToString(Paths.get(FOLDER_PATH, fileName).toFile(), Charset.defaultCharset());

	}
	private String removeTimeBetweenRepetitions(String str) {
		return str.replaceAll("\\s+<timeBetweenRepetitions>\\S+>", "");
	}

	@Test
	public void testFiles() throws IOException {
		testFile("Ni_pellet_map.xml");
	}

	@Test
	public void testFiles2() throws IOException {
		testFile("cycle_1ms_CuOx.xml");
	}

	@Test
	public void testFiles3() throws IOException {
		testFile("Ni_pellet_map.xml");
	}

	@Test
	public void testFiles4() throws IOException {
		testFile("Rh_map.xml");
	}

	@Test
	public void testFiles5() throws IOException {
		testFile("single_Pd_EDE.xml");
	}

	@Test
	public void testFiles6() throws IOException {
		testFile("CuSO4_beamdamage_linear_15min.xml");
	}
}
