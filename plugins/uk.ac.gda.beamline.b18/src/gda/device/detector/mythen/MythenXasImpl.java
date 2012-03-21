/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

package gda.device.detector.mythen;

import gda.data.scan.datawriter.XasAsciiDataWriter;

import java.io.File;

/**
 * Version of MythenNexusImpl for spectroscopy beamlines where the data files are written to data directories defined in
 * the experiment configuration xml files.
 */
public class MythenXasImpl extends MythenNexusImpl {

	/**
	 * Returns the same data directory that the XAS file writer is using
	 * 
	 * @return the data directory
	 */
	@Override
	public synchronized File getDataDirectory() {
		dataDirectory = new File(XasAsciiDataWriter.getDataDirectory());
		return dataDirectory;
	}
}
