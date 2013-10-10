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

import static org.junit.Assert.*;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.io.OutputStream;

import org.junit.Test;

import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;

public class AlignmentParametersBeanTest {
	@Test
	public void serialisableTest() throws IOException {
		AlignmentParametersModel test = AlignmentParametersModel.INSTANCE;
		ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream("/tmp/test.dat"));
		out.writeObject(test);
		out.close();
	}
}
