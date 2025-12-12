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
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.exafs.scan.ExafsValidator;
import gda.exafs.scan.ScanObject;
import gda.exafs.xes.IXesEnergyScannable;
import gda.exafs.xes.XesUtils;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.ScanColourType;
import uk.ac.gda.beans.exafs.SpectrometerScanParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.exafs.i20.I20SampleParameters;
import uk.ac.gda.beans.validation.InvalidBeanException;
import uk.ac.gda.beans.validation.InvalidBeanMessage;
import uk.ac.gda.beans.validation.WarningType;
import uk.ac.gda.client.experimentdefinition.IExperimentObject;
import uk.ac.gda.util.beans.xml.XMLHelpers;

/**
 * A class to check that the XML parameters are sensible. This is an additional check which is beyond that which the
 * schema can test the xml file.
 */
public class I20Validator extends ExafsValidator {
	private static final Logger logger = LoggerFactory.getLogger(I20Validator.class);

	private static final String DEFAULT_SAMPLE_NAME = "Please set a sample name";
	private static final double MINENERGY = 2000; // the lowest value out of I18, B18 and I20
	private static final double MAXENERGY = 35000; // the highest value out of I18, B18 and I20
	private static final double MIN_XES_INTEGRATIONTIME = 0.01;

	@Override
	public void validate(final IExperimentObject b) throws InvalidBeanException {

		this.bean = (ScanObject) b;

		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);

		try {
			errors.addAll(validateIScanParameters(bean.getScanParameters(), bean.getDetectorParameters()));
		} catch (Exception e) {
			logger.error("Problem validating scan parameters", e);
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
			logger.error("Problem validating detector parameters", e);
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

		if (s.getName().startsWith(DEFAULT_SAMPLE_NAME) || s.getName().isEmpty()){
			errors.add(new InvalidBeanMessage(WarningType.HIGH, "Sample Name has not been set in " + bean.getSampleFileName()));
		} else if (!stringCouldBeConvertedToValidUnixFilename(s.getName())){
			errors.add(new InvalidBeanMessage(WarningType.HIGH, "The given Sample Name in " + bean.getSampleFileName() + " cannot be converted into a valid file prefix.\nPlease remove invalid characters."));
		}
		return errors;
	}

	@Override
	public List<InvalidBeanMessage> validateXesScanParameters(XesScanParameters x, IDetectorParameters detParams) {

		if (x == null || !x.isShouldValidate()) {
			return Collections.emptyList();
		}

		final List<InvalidBeanMessage> errors = new ArrayList<>();

		// check the detector type XES has been chosen
		if (detParams != null && detParams.getDetectorConfigurations() == null &&
				!DetectorParameters.XES_TYPE.equalsIgnoreCase(detParams.getExperimentType())) {
			errors.add(new InvalidBeanMessage(WarningType.HIGH, "The experiment type in the detector parameters file is "
					+ detParams.getExperimentType() + " which should be XES"));
		}
		ScanColourType scanColour = x.getScanColourType();
		if (scanColour == null || scanColour.useRow1()) {
			errors.addAll(checkXesParameters(x, 0));
		}
		if (scanColour != null && scanColour.useRow2() && scanColour != ScanColourType.ONE_COLOUR) {
			errors.addAll(checkXesParameters(x, 1));
		}
		return errors;
	}

	private List<InvalidBeanMessage> checkXesParameters(XesScanParameters xesScanParams, int index) {

		List<InvalidBeanMessage> errors = new ArrayList<>();

		int scanType = xesScanParams.getScanType();
		SpectrometerScanParameters specParams = xesScanParams.getSpectrometerScanParameters().get(index);

		double[] energyRange = {getMinEnergy(), getMaxEnergy()};

		// Try to get the allowed energy range from the XES energy scannable
		Optional<IXesEnergyScannable> xesEnergy = Finder.findOptionalOfType(specParams.getScannableName(), IXesEnergyScannable.class);
		if (xesEnergy.isPresent()) {
			try {
				energyRange = xesEnergy.get().getEnergyRange();
			} catch (DeviceException e) {
				logger.error("Problemm look up energy range from "+xesEnergy.get().getName()+" - using default range "+Arrays.asList(energyRange), e);
			}
		}
		if (scanType == XesScanParameters.SCAN_XES_FIXED_MONO || scanType == XesScanParameters.SCAN_XES_SCAN_MONO) {

			// find the allowed range of energy transfer values
			if (xesScanParams.isScanEnergyTransfer()) {
				List<Double> allowedRange;
				if (scanType == XesScanParameters.SCAN_XES_FIXED_MONO) {
					allowedRange = XesUtils.convertToEnergyTransfer(List.of(energyRange[0], energyRange[1]), xesScanParams.getMonoEnergy());
				} else {
					List<Double> monoRange = List.of(xesScanParams.getMonoInitialEnergy(), xesScanParams.getMonoFinalEnergy());
					allowedRange = XesUtils.convertToEnergyTransfer(List.of(energyRange[0], energyRange[1]),  monoRange);
				}
				energyRange[0] = Collections.min(allowedRange);
				energyRange[1] = Collections.max(allowedRange);
			}

			checkBounds("Integration Time", specParams.getIntegrationTime(), MIN_XES_INTEGRATIONTIME, 25d, errors);
			checkBounds("XES Initial energy", specParams.getInitialEnergy(), energyRange[0], energyRange[1], errors);
			checkBounds("XES Final energy", specParams.getFinalEnergy(), energyRange[0], energyRange[1], errors);

			if (scanType == XesScanParameters.SCAN_XES_SCAN_MONO) {
				checkEnergyRange("Mono", xesScanParams.getMonoInitialEnergy(), xesScanParams.getMonoFinalEnergy(), errors);
			}

		} else if (bean != null) {
			// Fixed XES and XAS or XANES, or SCAN_XES_REGION_FIXED_MONO
			String xmlFolderName = InterfaceProvider.getPathConstructor().createFromDefaultProperty() + "/xml/"
					+ bean.getFolder().getName() + "/";

			String scanFileName = xesScanParams.getScanFileName();
			if (scanType == XesScanParameters.SCAN_XES_REGION_FIXED_MONO) {
				scanFileName = specParams.getScanFileName();
			}
			checkFileExists("Scan file name", scanFileName, xmlFolderName, errors);

			try {
				Object energyScanBean = XMLHelpers.getBeanObject(xmlFolderName, scanFileName);
				if (scanType == XesScanParameters.FIXED_XES_SCAN_XAS) {
					errors.addAll(validateXasScanParameters((XasScanParameters) energyScanBean, MINENERGY, MAXENERGY));
				} else {
					errors.addAll(validateXanesScanParameters((XanesScanParameters) energyScanBean));
				}
			} catch (Exception e) {
				InvalidBeanMessage msg = new InvalidBeanMessage(WarningType.HIGH, e.getMessage());
				errors.add(msg);
				return errors;
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
