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

package gda.exfas.ui.validation;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import gda.exafs.scan.ExafsValidator;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.i18.I18SampleParameters;
import uk.ac.gda.beans.validation.InvalidBeanMessage;

public class I18Validator extends ExafsValidator {

//	private static final double MINENERGY = 2000; // the lowest value out of I18, B18 and I20
//	private static final double MAXENERGY = 35000; // the highest value out of I18, B18 and I20

	@Override
	protected List<InvalidBeanMessage> validateISampleParameters(ISampleParameters sampleParameters) {
		if (sampleParameters instanceof I18SampleParameters) {
			return validateI18SampleParameters((I18SampleParameters) sampleParameters);
		} else {
			return validateGenericISampleParameters(sampleParameters);
		}
	}

	private List<InvalidBeanMessage> validateI18SampleParameters(I18SampleParameters s) {

		if (s == null) {
			return Collections.emptyList();
		}

		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);

		if (s.getName() == null) {
			errors.add(new InvalidBeanMessage("Please set a sample name."));
		}
		if (s.getDescription() == null) {
			errors.add(new InvalidBeanMessage("Please set a sample description."));
		}

		if (s.getName().compareTo("name") == 0) {
			errors.add(new InvalidBeanMessage("Sample Name has not been set in " + bean.getSampleFileName()));
		} else if (!stringCouldBeConvertedToValidUnixFilename(s.getName())) {
			errors.add(new InvalidBeanMessage("The given Sample Name in " + bean.getSampleFileName()
					+ " cannot be converted into a valid file prefix.\nPlease remove invalid characters."));
		}

		// TODO add some other validation here?

		return errors;
	}

	// for I18 will need our own logic for this
	@Override
	protected List<InvalidBeanMessage> validateXasScanParameters(XasScanParameters x, double beamlineMinEnergy, double beamlineMaxEnergy) {
		return Collections.emptyList();
	}
}
