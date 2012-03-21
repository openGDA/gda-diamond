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

import gda.exafs.scan.ExafsValidator;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.i18.I18SampleParameters;
import uk.ac.gda.beans.microfocus.MicroFocusScanParameters;
import uk.ac.gda.beans.validation.InvalidBeanException;
import uk.ac.gda.beans.validation.InvalidBeanMessage;
import uk.ac.gda.client.experimentdefinition.IExperimentObject;
import uk.ac.gda.exafs.ui.data.ScanObject;

public class I18Validator extends ExafsValidator {

	private static final double MINENERGY = 2000; // the lowest value out of I18, B18 and I20
	private static final double MAXENERGY = 35000; // the highest value out of I18, B18 and I20

	@Override
	public void validate(IExperimentObject b) throws InvalidBeanException {
		this.bean = (ScanObject) b;

		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);

		try {
			errors.addAll(validateIScanParameters(bean.getScanParameters()));
			errors.addAll(validateISampleParameters(bean.getSampleParameters()));
			errors.addAll(validateIDetectorParameters(bean.getDetectorParameters()));
			errors.addAll(validateIOutputParameters(bean.getOutputParameters()));
		} catch (Exception e) {
			throw new InvalidBeanException("Exception retrieving parameters objects: " + e.getMessage());
		}

		if (!errors.isEmpty()) {
			for (InvalidBeanMessage invalidBeanMessage : errors) {
				invalidBeanMessage.setFolderName(bean.getRunFileManager().getContainingFolder().getName());
			}
			throw new InvalidBeanException(errors);
		}

	}

	private List<InvalidBeanMessage> validateIScanParameters(IScanParameters scanParams) {
		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);
		if (scanParams instanceof XasScanParameters) {
			errors.addAll(validateXasScanParameters((XasScanParameters) scanParams, MINENERGY, MAXENERGY));
		} else if (scanParams instanceof XanesScanParameters) {
			errors.addAll(validateXanesScanParameters((XanesScanParameters) scanParams));
		} else if (scanParams instanceof MicroFocusScanParameters) {
			errors.addAll(validateMicroFocusParameters((MicroFocusScanParameters) scanParams));
		} else if (scanParams == null) {
			errors.add(new InvalidBeanMessage("Missing or Invalid Scan Parameters"));
		} else {
			errors.add(new InvalidBeanMessage("Unknown Scan Type " + scanParams.getClass().getName()));
		}
		if (bean != null) {
			setFileName(errors, bean.getScanFileName());
		}
		return errors;
	}

	protected List<InvalidBeanMessage> validateISampleParameters(ISampleParameters sampleParameters) {

		if (sampleParameters instanceof I18SampleParameters) {
			return validateI18SampleParameters((I18SampleParameters) sampleParameters);
		}
		InvalidBeanMessage invalidBeanMessage;
		if (sampleParameters == null) {
			try {
				if (bean != null && bean.isMicroFocus()) {
					// do not have a sample file for microfocus scans
					return Collections.emptyList();
				}
				// else its missing
				invalidBeanMessage = new InvalidBeanMessage("Missing or Invalid Sample Parameters");
			} catch (Exception e) {
				invalidBeanMessage = new InvalidBeanMessage(
						"Error testing if bean is a microfocus scan when testing Scan parameters from bean");
			}
		} else {
			invalidBeanMessage = new InvalidBeanMessage("Unknown Sample Type " + sampleParameters.getClass().getName());
		}
		if (bean != null) {
			invalidBeanMessage.setFileName(bean.getSampleFileName());
		}
		ArrayList<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>();
		errors.add(invalidBeanMessage);
		return errors;
	}

	protected List<InvalidBeanMessage> validateI18SampleParameters(@SuppressWarnings("unused") I18SampleParameters s) {
		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);
		// TODO
		return errors;
	}

	protected List<InvalidBeanMessage> validateMicroFocusParameters(MicroFocusScanParameters x) {
		if (x == null) {
			return Collections.emptyList();
		}
		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);
		// TODO add validation for MicroFocus
		return errors;
	}

}
