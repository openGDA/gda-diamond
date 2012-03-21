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
import gda.device.Scannable;
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
import uk.ac.gda.beans.exafs.i20.CustomParameter;
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

	private static final double MINENERGY = 2000; // the lowest value out of I18, B18 and I20
	private static final double MAXENERGY = 35000; // the highest value out of I18, B18 and I20

	@Override
	public void validate(final IExperimentObject b) throws InvalidBeanException {

		this.bean = (ScanObject) b;

		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);

		try {
			errors.addAll(validateIScanParameters(bean.getScanParameters(), bean.getDetectorParameters()));
			errors.addAll(validateI20SampleParameters((I20SampleParameters) bean.getSampleParameters()));
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
		if (!s.isShouldValidate()) {
			return errors;
		}

		final String environment = s.getSampleEnvironment();
		if (environment.equalsIgnoreCase(I20SampleParameters.SAMPLE_ENV[1])) {

			final SampleStageParameters p = s.getRoomTemperatureParameters();
			final String message = "The sample stage parameters are out of bounds.";
			checkRangeBounds("x", p.getX(), -15d, 15d, errors, message);
			checkRangeBounds("y", p.getY(), -20.1d, 20.1d, errors, message);
			checkRangeBounds("z", p.getZ(), -15d, 15d, errors, message);

			checkRangeBounds("Rotation", p.getRotation(), 0d, 360d, errors, message);
			checkRangeBounds("Roll", p.getRoll(), -5d, 5d, errors, message);
			checkRangeBounds("Yaw", p.getYaw(), -5d, 5d, errors, message);

		}
		// to be replaced when the hardware is available
		/*
		 * else if (environment.equalsIgnoreCase(I20SampleParameters.SAMPLE_ENV[2])) { final String message =
		 * "The cyrostat parameters are out of bounds."; final CryostatParameters c = s.getCryostatParameters();
		 * checkRangeBounds("Temperature", c.getTemperature(), 0d, 300d, errors, message); checkBounds("Tolerance",
		 * c.getTolerance(), 0d, 5d, errors, message); checkBounds("Wait Time", c.getTime(), 0d, 400d, errors, message);
		 * final String sampleHolder = c.getSampleHolder(); if ("2 samples".equalsIgnoreCase(sampleHolder)) {
		 * checkRangeBounds("Sample Number", c.getSampleNumber(), 1d, 2d, errors, message); } else if
		 * ("3 samples".equalsIgnoreCase(sampleHolder)) { checkRangeBounds("Sample Number", c.getSampleNumber(), 1d, 3d,
		 * errors, message); } else if ("4 samples".equalsIgnoreCase(sampleHolder)) { checkRangeBounds("Sample Number",
		 * c.getSampleNumber(), 1d, 4d, errors, message); } else if ("Liquid Cell".equalsIgnoreCase(sampleHolder)) { //
		 * Sample number is ignored } else { errors.add(new InvalidBeanMessage("Cannot recognise sample holder '" +
		 * sampleHolder + "'")); } checkRangeBounds("Position", c.getPosition(), -15d, 15d, errors, message);
		 * checkRangeBounds("Fine Position", c.getFinePosition(), -1d, 1d, errors, message); checkBounds("Ramp",
		 * c.getRamp(), 0.1d, 100, errors, message); checkBounds("Heater Range", c.getHeaterRange(), 1d, 5d, errors,
		 * message); } else if (environment.equalsIgnoreCase(I20SampleParameters.SAMPLE_ENV[3])) { final String message
		 * = "The furnace parameters are out of bounds."; final FurnaceParameters f = s.getFurnaceParameters();
		 * checkRangeBounds("x", f.getX(), -15d, 15d, errors, message); checkRangeBounds("y", f.getY(), -20d, 20d,
		 * errors, message); checkRangeBounds("z", f.getZ(), -15d, 15d, errors, message);
		 * checkRangeBounds("Temperature", f.getTemperature(), 295, 1300, errors, message); checkBounds("Tolerance",
		 * f.getTolerance(), 0d, 5d, errors, message); checkBounds("Time", f.getTime(), 0d, 400d, errors, message); }
		 */
		else if (environment.equalsIgnoreCase(I20SampleParameters.SAMPLE_ENV[5])) {
			final List<CustomParameter> c = s.getCustomParameters();
			for (CustomParameter cp : c) {
				checkFindable("Device Name", cp.getDeviceName(), Scannable.class, errors);
			}
		}

		if (bean != null) {
			setFileName(errors, bean.getSampleFileName());
		}
		return errors;
	}

//	public List<InvalidBeanMessage> validateXesScanParameters(XesScanParameters x) {
//		return validateXesScanParameters(x, null);
//	}

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

		// Check type
		if (!"Si".equals(x.getAnalyserType()) && !"Ge".equals(x.getAnalyserType())) {
			errors.add(new InvalidBeanMessage("The analyser type is " + x.getAnalyserType() + " which is not "));
		}

		checkBounds("Radius of Curvature", x.getRadiusOfCurvature(), 800d, 1010d, errors);

		if (x.getScanType() == XesScanParameters.SCAN_XES_FIXED_MONO) {

			checkBounds("Integration Time", x.getXesIntegrationTime(), 0d, 25d, errors);
			double initialE = x.getXesInitialEnergy();
			double finalE = x.getXesFinalEnergy();
			if (initialE >= finalE) {
				errors.add(new InvalidBeanMessage("The initial energy is greater than or equal to the final energy."));
			}

			// TODO Actually a function of crystall cut.
			checkBounds("XES Initial Energy", initialE, 0d, finalE, errors);
			checkBounds("XES Final Energy", finalE, initialE, 35000d, errors);

		} else if (x.getScanType() == XesScanParameters.SCAN_XES_SCAN_MONO) {

			checkBounds("Integration Time", x.getXesIntegrationTime(), 0d, 25d, errors);
			double initialE = x.getXesInitialEnergy();
			double finalE = x.getXesFinalEnergy();
			if (initialE >= finalE) {
				errors.add(new InvalidBeanMessage("The initial energy is greater than or equal to the final energy."));
			}

			// TODO Actually a function of crystall cut.
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
						+ bean.getRunFileManager().getContainingFolder().getName() + "/";
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
