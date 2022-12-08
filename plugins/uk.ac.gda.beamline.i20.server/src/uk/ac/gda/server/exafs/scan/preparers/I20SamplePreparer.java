/*-
 * Copyright © 2015 Diamond Light Source Ltd.
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

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.i20.I20SampleParameters;
import uk.ac.gda.server.exafs.scan.SampleEnvironmentPreparer;
import uk.ac.gda.server.exafs.scan.iterators.I20SingleSampleIterator;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;

public class I20SamplePreparer implements SampleEnvironmentPreparer {

	private EnumPositioner filterwheel;
	private I20SampleParameters i20SampleParams;

	public I20SamplePreparer(EnumPositioner filterwheel) {
		this.filterwheel = filterwheel;
	}

	@Override
	public void configure(IScanParameters scanParameters, ISampleParameters sampleParameters) throws Exception {
		i20SampleParams = (I20SampleParameters) sampleParameters;

		// TODO is it correct to perform this move at this point?
		if (i20SampleParams.getUseSampleWheel()) {
			_moveSampleWheel();
		}
	}

	@Override
	public SampleEnvironmentIterator createIterator(String experimentType) {
		return new I20SingleSampleIterator(i20SampleParams);
	}

	private void _moveSampleWheel() throws DeviceException {
		String filter_position = i20SampleParams.getSampleWheelPosition();
		// String message = "Setting reference filter wheel to " + filter_position;
		// logger.info(message);
		// print message
		filterwheel.moveTo(filter_position);
	}
}
