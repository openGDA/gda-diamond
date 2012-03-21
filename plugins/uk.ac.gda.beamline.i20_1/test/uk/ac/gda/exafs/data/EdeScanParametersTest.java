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
import gda.util.TestUtils;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;

import org.eclipse.core.runtime.content.IContentDescriber;
import org.junit.BeforeClass;
import org.junit.Test;

import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.exafs.ui.describers.EdeScanParametersDescriber;
import uk.ac.gda.util.PackageUtils;

public class EdeScanParametersTest {

	final static String testScratchDirectoryName = TestUtils
			.generateDirectorynameFromClassname(EdeScanParametersTest.class.getCanonicalName());

	/**
	 * @throws Exception
	 */
	@BeforeClass
	public static void beforeClass() throws Exception {
		TestUtils.makeScratchDirectory(testScratchDirectoryName);
	}

	@Test
	public void testDescriber() {
		try {
			InputStream contents = new FileInputStream(new File(PackageUtils.getTestPath(getClass(),"test")
					+ "EdeScan_Parameters.xml"));
			EdeScanParametersDescriber describer = new EdeScanParametersDescriber();
			assertEquals(IContentDescriber.VALID, describer.describe(contents, null));
		} catch (Exception e) {
			fail(e.getMessage());
		}
	}

	@Test
	public void testCreateFromXML() {
		EdeScanParameters expectedValue = new EdeScanParameters();
		expectedValue.setNumberOfRepetitions(1);
		
		TimingGroup group1 = new TimingGroup();
		group1.setDelayBetweenFrames(0);
		group1.setLabel("group1");
		group1.setNumberOfFrames(1);
		group1.setTimePerScan(0.1);
		group1.setTimePerFrame(1);
		group1.setGroupTrig(true);
		expectedValue.addGroup(group1);
		
		expectedValue.setOutputsChoice3(EdeScanParameters.OUTPUT_TRIG_CHOICES[1]);
		expectedValue.setOutputsWidth3(0.1);
		

		try {
			EdeScanParameters s = EdeScanParameters.createFromXML(PackageUtils.getTestPath(getClass(),"test")
					+ "EdeScan_Parameters.xml");
			if (!expectedValue.equals(s)) {
				fail("Values read are incorrect - " + s.toString());
			}
		} catch (Exception e) {
			fail(e.getMessage());
		}

	}

}
