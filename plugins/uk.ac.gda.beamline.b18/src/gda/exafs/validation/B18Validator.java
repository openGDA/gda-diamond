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

package gda.exafs.validation;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import gda.exafs.scan.ExafsValidator;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.b18.B18SampleParameters;
import uk.ac.gda.beans.exafs.b18.FurnaceParameters;
import uk.ac.gda.beans.validation.InvalidBeanMessage;

public class B18Validator extends ExafsValidator {

	private static final double MINENERGY = 2000; // the lowest value out of I18, B18 and I20
	private static final double MAXENERGY = 40000; // the highest value out of I18, B18 and I20

	@Override
	protected List<InvalidBeanMessage> validateISampleParameters(ISampleParameters sampleParameters) {
		if (sampleParameters instanceof B18SampleParameters) {
			return validateB18SampleParameters((B18SampleParameters) sampleParameters);
		} else {
			return validateGenericISampleParameters(sampleParameters);
		}
	}

	private List<InvalidBeanMessage> validateB18SampleParameters(B18SampleParameters s) {

		if (s == null) {
			return Collections.emptyList();
		}

		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);
		if (!s.isShouldValidate()) {
			return errors;
		}

		if (s.getName() == null) {
			errors.add(new InvalidBeanMessage("Please set a sample name."));
		}
		if (s.getDescription1() == null) {
			errors.add(new InvalidBeanMessage("Please set a sample description."));
		}

		if (s.getName().compareTo("default") == 0) {
			errors.add(new InvalidBeanMessage("Sample Name has not been set in " + bean.getSampleFileName()));
		} else if (!stringCouldBeConvertedToValidUnixFilename(s.getName())) {
			errors.add(new InvalidBeanMessage("The given Sample Name in " + bean.getSampleFileName()
					+ " cannot be converted into a valid file prefix.\nPlease remove invalid characters."));
		}

		final String sampleEnv = s.getTemperatureControl();
		if ("furnace".equalsIgnoreCase(sampleEnv)) {
			final String message = "The furnace parameters are out of bounds.";
			final FurnaceParameters f = s.getFurnaceParameters();
			checkBounds("Temperature", f.getTemperature(), 0, 1372, errors, message);
			checkBounds("Tolerance", f.getTolerance(), 0d, 5d, errors, message);
			checkBounds("Time", f.getTime(), 0d, 400d, errors, message);

		}

		if (bean != null) {
			setFileName(errors, bean.getSampleFileName());
		}

		return errors;
	}

	@Override
	protected double getMinEnergy() {
		return MINENERGY;
	}

	@Override
	protected double getMaxEnergy() {
		return MAXENERGY;
	}
}
