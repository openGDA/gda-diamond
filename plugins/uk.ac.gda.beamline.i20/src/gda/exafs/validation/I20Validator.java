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

import gda.data.PathConstructor;
import gda.exafs.scan.ExafsValidator;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import uk.ac.gda.beans.BeansFactory;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
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
			throw new InvalidBeanException("Error in scan XML file: " + e.getMessage());
		}
		try {
			errors.addAll(validateI20SampleParameters((I20SampleParameters) bean.getSampleParameters()));
		} catch (Exception e) {
			throw new InvalidBeanException("Error in sample environment XML file: " + e.getMessage());
		}
		try {
			errors.addAll(validateIDetectorParameters(bean.getDetectorParameters()));
		} catch (Exception e) {
			throw new InvalidBeanException("Error in detector XML file: " + e.getMessage());
		}
		try {
			errors.addAll(validateIOutputParameters(bean.getOutputParameters()));
		} catch (Exception e) {
			throw new InvalidBeanException("Error in output options XML file: " + e.getMessage());
		}

		if (!errors.isEmpty()) {
			for (InvalidBeanMessage invalidBeanMessage : errors) {
				invalidBeanMessage.setFolderName(bean.getFolder().getName());
			}
			throw new InvalidBeanException(errors);
		}
	}

	private List<InvalidBeanMessage> validateIScanParameters(IScanParameters scanParams, IDetectorParameters detParams) {
		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);
		if (scanParams instanceof XasScanParameters) {
			errors.addAll(validateXasScanParameters((XasScanParameters) scanParams, MINENERGY, MAXENERGY));
		} else if (scanParams instanceof XanesScanParameters) {
			errors.addAll(validateXanesScanParameters((XanesScanParameters) scanParams));
		} else if (scanParams instanceof XesScanParameters) {
			errors.addAll(validateXesScanParameters((XesScanParameters) scanParams, detParams));
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

	public List<InvalidBeanMessage> validateI20SampleParameters(I20SampleParameters s) {

		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);
		
		//none
		if (s.getSampleEnvironment().equalsIgnoreCase(I20SampleParameters.SAMPLE_ENV[0])){
			if (s.getName().startsWith(DEFAULT_SAMPLE_NAME)){
				errors.add(new InvalidBeanMessage("Sample Name has not been set in " + bean.getSampleFileName()));
			} else if (!stringCouldBeConvertedToValidUnixFilename(s.getName())){
				errors.add(new InvalidBeanMessage("The given Sample Name in " + bean.getSampleFileName() + " cannot be converted into a valid file prefix.\nPlease remove invalid characters."));				
			}
		} 
		// room temp
		else if (s.getSampleEnvironment().equalsIgnoreCase(I20SampleParameters.SAMPLE_ENV[1])){
			SampleStageParameters ssp = s.getRoomTemperatureParameters();
			String[] names = ssp.getSampleNames();
			Boolean[] uses = ssp.getUses();
			for (int i = 0; i < names.length; i++) {
				if (uses[i] && !stringCouldBeConvertedToValidUnixFilename(names[i])) {
					errors.add(new InvalidBeanMessage("The name for sample " + (i + 1) + " in "
							+ bean.getSampleFileName()
							+ " cannot be converted into a valid file prefix.\nPlease remove invalid characters."));
				}
			}
		}
		
		return errors;
	}
	
	private boolean stringCouldBeConvertedToValidUnixFilename(String sampleName){
		// ignore spaces as these will have underscores automatically substituted
		if (sampleName.startsWith("-")
		|| sampleName.contains(";") || sampleName.contains("<") || sampleName.contains("\t")
		|| sampleName.contains("'") || sampleName.contains("\"") || sampleName.contains("\\")
		|| sampleName.contains("\n")|| sampleName.contains("..")){
			return false;
		}
		return true;
	}

	public List<InvalidBeanMessage> validateXesScanParameters(XesScanParameters x, IDetectorParameters detParams) {

		if (x == null) {
			return Collections.emptyList();
		}

		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);
		if (!x.isShouldValidate()) {
			return errors;
		}

		// check the detector type XES has been chosen
		if (detParams != null && !detParams.getExperimentType().equalsIgnoreCase("xes")) {
			errors.add(new InvalidBeanMessage("The experiment type in the detector parameters file is "
					+ detParams.getExperimentType() + " which should be XES"));
		}

		checkBounds("Radius of Curvature", x.getRadiusOfCurvature(), 800d, 1010d, errors);

		if (x.getScanType() == XesScanParameters.SCAN_XES_FIXED_MONO) {

			checkBounds("Integration Time", x.getXesIntegrationTime(), 0d, 25d, errors);
			double initialE = x.getXesInitialEnergy();
			double finalE = x.getXesFinalEnergy();
			if (initialE >= finalE) {
				errors.add(new InvalidBeanMessage("The initial energy is greater than or equal to the final energy."));
			}

			checkBounds("XES Initial Energy", initialE, 0d, finalE, errors);
			checkBounds("XES Final Energy", finalE, initialE, 35000d, errors);

		} else if (x.getScanType() == XesScanParameters.SCAN_XES_SCAN_MONO) {

			checkBounds("Integration Time", x.getXesIntegrationTime(), 0d, 25d, errors);
			double initialE = x.getXesInitialEnergy();
			double finalE = x.getXesFinalEnergy();
			if (initialE >= finalE) {
				errors.add(new InvalidBeanMessage("The initial energy is greater than or equal to the final energy."));
			}

			checkBounds("XES Initial Energy", initialE, 0d, finalE, errors);
			checkBounds("XES Final Energy", finalE, initialE, 35000d, errors);

			initialE = x.getMonoInitialEnergy();
			finalE = x.getMonoFinalEnergy();
			if (initialE >= finalE) {
				errors.add(new InvalidBeanMessage("The initial energy is greater than or equal to the final energy."));
			}

			checkBounds("Mono Initial Energy", initialE, 0d, finalE, errors);
			checkBounds("Mono Final Energy", finalE, initialE, 35000d, errors);

		} else { // Fixed XES and XAS or XANES
			if (bean != null) {
				String xmlFolderName = PathConstructor.createFromDefaultProperty() + "/xml/"
						+ bean.getFolder().getName() + "/";
				checkFileExists("Scan file name", x.getScanFileName(), xmlFolderName, errors);

				if (errors.size() == 0) {
					Object energyScanBean;
					try {
						energyScanBean = BeansFactory.getBeanObject(xmlFolderName, x.getScanFileName());
					} catch (Exception e) {
						InvalidBeanMessage msg = new InvalidBeanMessage(e.getMessage());
						errors.add(msg);
						return errors;
					}
					if (x.getScanType() == XesScanParameters.FIXED_XES_SCAN_XAS) {
						validateXasScanParameters((XasScanParameters) energyScanBean, MINENERGY, MAXENERGY);
					} else {
						validateXanesScanParameters((XanesScanParameters) energyScanBean);
					}
				}

			}
		}
		return errors;
	}

}
