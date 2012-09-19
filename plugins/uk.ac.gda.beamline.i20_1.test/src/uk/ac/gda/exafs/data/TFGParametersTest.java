/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;

import org.eclipse.core.runtime.content.IContentDescriber;
import org.junit.Test;

import uk.ac.gda.exafs.ui.data.TFGParameters;
import uk.ac.gda.exafs.ui.data.TimeFrame;
import uk.ac.gda.exafs.ui.describers.TFGParametersDescriber;

public class TFGParametersTest {

	@Test
	public void testDescriber() {
		try {
			InputStream contents = new FileInputStream(new File("testfiles/uk/ac/gda/exafs/data/TFGParametersTest/TFG_Parameters.xml"));
			TFGParametersDescriber describer = new TFGParametersDescriber();
			assertEquals(IContentDescriber.VALID, describer.describe(contents, null));
		} catch (Exception e) {
			fail(e.getMessage());
		}
	}

	@Test
	public void testCreateFromXML() {
		TFGParameters expectedValue = new TFGParameters();
		expectedValue.setAutoRearm(true);
		
		TimeFrame tf1 = new TimeFrame();
		tf1.setLabel("frame1");
		tf1.setDeadTime(30);
		tf1.setLiveTime(10);
		tf1.setLemoIn(0);
		tf1.setLemoOut(3);
		expectedValue.addTimeFrame(tf1);

		try {
			TFGParameters s = TFGParameters.createFromXML("testfiles/uk/ac/gda/exafs/data/TFGParametersTest/TFG_Parameters.xml");
			if (!expectedValue.equals(s)) {
				fail("Values read are incorrect - " + s.toString());
			}
		} catch (Exception e) {
			fail(e.getMessage());
		}

	}

}
