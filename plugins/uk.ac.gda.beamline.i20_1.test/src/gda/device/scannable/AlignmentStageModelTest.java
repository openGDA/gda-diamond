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

package gda.device.scannable;

import static org.junit.Assert.assertEquals;

import java.util.Arrays;
import java.util.List;

import org.junit.Test;

import gda.scan.ede.position.AlignmentStageModel;
import gda.scan.ede.position.Location;

public class AlignmentStageModelTest {

	private String getExpectedXml(List<Location> locations) {
		StringBuilder strBuilder = new StringBuilder();

		strBuilder.append("<AlignmentStageModel>\n");
		for(Location loc : locations) {
			strBuilder.append(
					"  <Position>\n" +
					"    <name>"+loc.getName()+"</name>\n" +
					"    <displayLabel>"+loc.getDisplayLabel()+"</displayLabel>\n" +
					"    <xPosition>"+loc.getxPosition()+"</xPosition>\n" +
					"    <yPosition>"+loc.getyPosition()+"</yPosition>\n" +
					"    <relative>false</relative>\n" +
					"  </Position>\n");
		}
		strBuilder.append("</AlignmentStageModel>");
		return strBuilder.toString();
	}

	private AlignmentStageModel getModel() {
		AlignmentStageModel model = new AlignmentStageModel();
		List<Location> locations = Arrays.asList(
				Location.create("pos1", "position 1", 0, 1),
				Location.create("pos2", "position 2", 2, 3));
		model.setDeviceLocations(locations);
		return model;
	}

	@Test
	public void testSaveToXml() {
		AlignmentStageModel model = getModel();
		String xmlString = model.toXml();
		String expectedXml = getExpectedXml(model.getDeviceLocations());
		assertEquals("Model serialized to XML string is not correct", expectedXml, xmlString);

		AlignmentStageModel model2 = AlignmentStageModel.fromXml(xmlString);
		assertEquals("Mode de-serialized from XML is not correct", model.getDeviceLocations(), model2.getDeviceLocations());
	}
}
