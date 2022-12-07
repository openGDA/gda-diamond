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

package uk.ac.gda.server.exafs.scan.preparers;

import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.server.exafs.scan.BeamlinePreparer;

public class I20BeamlinePreparer implements BeamlinePreparer {

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean,
			ISampleParameters sampleParameters, IOutputParameters outputBean, String experimentFullPath)
			throws Exception {
		// nothing specific for I20 yet

	}

	@Override
	public void prepareForExperiment() throws Exception {
		// nothing specific for I20 yet

	}

	@Override
	public void completeExperiment() throws Exception {
		// nothing specific for I20 yet

	}

}
