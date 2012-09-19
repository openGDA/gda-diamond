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

import java.io.FileInputStream;
import java.io.InputStream;

import org.eclipse.core.runtime.content.IContentDescriber;
import org.junit.Test;

import uk.ac.gda.exafs.ui.data.UserOptions;
import uk.ac.gda.exafs.ui.describers.UserOptionsDescriber;

public class UserOptionsTest {

	@Test
	public void testDescriber() {
		try {
			InputStream contents = new FileInputStream("testfiles/uk/ac/gda/exafs/data/UserOptionsTest/User_Options.xml");
			UserOptionsDescriber describer = new UserOptionsDescriber();
			assertEquals(IContentDescriber.VALID, describer.describe(contents, null));
		} catch (Exception e) {
			fail(e.getMessage());
		}
	}

	@Test
	public void testCreateFromXML() {
		UserOptions expectedValue = new UserOptions();
		expectedValue.setScriptName("/dls_sw/i01/users/scripts/test_script.py");
		

		try {
			UserOptions s = UserOptions.createFromXML("testfiles/uk/ac/gda/exafs/data/UserOptionsTest/User_Options.xml");
			if (!expectedValue.equals(s)) {
				fail("Values read are incorrect - " + s.toString());
			}
		} catch (Exception e) {
			fail(e.getMessage());
		}

	}

}
