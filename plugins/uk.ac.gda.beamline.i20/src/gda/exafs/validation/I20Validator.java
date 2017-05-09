/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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
import java.util.List;

import gda.exafs.scan.ExafsValidator;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.i20.CryostatParameters;
import uk.ac.gda.beans.exafs.i20.CryostatSampleDetails;
import uk.ac.gda.beans.exafs.i20.I20SampleParameters;
import uk.ac.gda.beans.exafs.i20.SampleStageParameters;
import uk.ac.gda.beans.validation.InvalidBeanException;
import uk.ac.gda.beans.validation.InvalidBeanMessage;
import uk.ac.gda.client.experimentdefinition.IExperimentObject;
import uk.ac.gda.exafs.ui.data.ScanObject;

/**
 * A class to check that the XML parameters are sensible. This is an additional check which is beyond that which the
 * schema can test the xml file.
 */
public class I20Validator extends ExafsValidator {

	private static final String DEFAULT_SAMPLE_NAME = "Please set a sample name";
	private static final double MINENERGY = 2000; // the lowest value out of I18, B18 and I20
	private static final double MAXENERGY = 35000; // the highest value out of I18, B18 and I20

	@Override
	public void validate(final IExperimentObject b) throws InvalidBeanException {

		this.bean = (ScanObject) b;

		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);

		try {
			errors.addAll(validateIScanParameters(bean.getScanParameters(), bean.getDetectorParameters()));
		} catch (Exception e) {
			throw new InvalidBeanException("Error in scan XML file: " + bean.getScanFileName() + ": " + e.getMessage());
		}
		try {
			errors.addAll(validateI20SampleParameters((I20SampleParameters) bean.getSampleParameters()));
		} catch (Exception e) {
			throw new InvalidBeanException("Error in sample environment XML file: "+ bean.getSampleFileName() + ": " + e.getMessage());
		}
		try {
			errors.addAll(validateIDetectorParameters(bean.getDetectorParameters()));
		} catch (Exception e) {
			throw new InvalidBeanException("Error in detector XML file: "+ bean.getDetectorFileName() + ": " + e.getMessage());
		}
		try {
			errors.addAll(validateIOutputParameters(bean.getOutputParameters()));
		} catch (Exception e) {
			throw new InvalidBeanException("Error in output options XML file: "+ bean.getOutputFileName() + ": " + e.getMessage());
		}

		if (!errors.isEmpty()) {
			for (InvalidBeanMessage invalidBeanMessage : errors) {
				invalidBeanMessage.setFolderName(bean.getFolder().getName());
			}
			throw new InvalidBeanException(errors);
		}
	}

	@Override
	protected List<InvalidBeanMessage> validateISampleParameters(ISampleParameters sampleParameters) {
		if (sampleParameters instanceof I20SampleParameters) {
			return validateI20SampleParameters((I20SampleParameters) sampleParameters);
		} else {
			return validateGenericISampleParameters(sampleParameters);
		}
	}

	private List<InvalidBeanMessage> validateI20SampleParameters(I20SampleParameters s) {

		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);

		//none
		if (s.getSampleEnvironment().equalsIgnoreCase(I20SampleParameters.SAMPLE_ENV[0])){
			if (s.getName().startsWith(DEFAULT_SAMPLE_NAME) || s.getName().isEmpty()){
				errors.add(new InvalidBeanMessage("Sample Name has not been set in " + bean.getSampleFileName()));
			} else if (!stringCouldBeConvertedToValidUnixFilename(s.getName())){
				errors.add(new InvalidBeanMessage("The given Sample Name in " + bean.getSampleFileName() + " cannot be converted into a valid file prefix.\nPlease remove invalid characters."));
			}
		}
		// room temp
		else if (s.getSampleEnvironment().equalsIgnoreCase(I20SampleParameters.SAMPLE_ENV[1])){
			List<SampleStageParameters> ssp = s.getRoomTemperatureParameters();
			for (SampleStageParameters position : ssp){
				if (!stringCouldBeConvertedToValidUnixFilename(position.getSample_name())) {
					errors.add(new InvalidBeanMessage("The sample name " + position.getSample_name() + " in "
							+ bean.getSampleFileName()
							+ " cannot be converted into a valid file prefix.\nPlease remove invalid characters."));
				}
			}
		}
		// cryostat
		else if (s.getSampleEnvironment().equalsIgnoreCase(I20SampleParameters.SAMPLE_ENV[2])){
			CryostatParameters ssp = s.getCryostatParameters();
			for (CryostatSampleDetails details : ssp.getSamples()) {
				if (!stringCouldBeConvertedToValidUnixFilename(details.getSample_name()) || details.getSample_name().isEmpty()) {
					errors.add(new InvalidBeanMessage("The sample name " + details.getSample_name() + " in "
							+ bean.getSampleFileName()
							+ " cannot be converted into a valid file prefix.\nPlease remove invalid characters."));
				}
			}
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
