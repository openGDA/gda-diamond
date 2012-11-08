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

package uk.ac.gda.beamline.b16.experimentdefinition;

import gda.factory.Findable;
import gda.factory.Finder;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.microfocus.MicroFocusScanParameters;
import uk.ac.gda.beans.validation.AbstractValidator;
import uk.ac.gda.beans.validation.InvalidBeanException;
import uk.ac.gda.beans.validation.InvalidBeanMessage;
import uk.ac.gda.client.experimentdefinition.IExperimentObject;

/**
 * A class to check that the XML parameters are sensible. Lots of hard coded values are intentionally added to this
 * class. It is designed to validate beans in a stand-alone fashion based on the current beamline requirements. If those
 * requirements change logic can be added here to make the system more flexible that schema checking alone. For instance
 * bounds and relationships between XML files can be checked. Downside is that it is not data driven. However a java
 * property can be set to configure another validator instance to be returned. This is: uk.ac.gda.exafs.validator
 */
public class B16ExafsValidator extends AbstractValidator {

	private static Logger logger = LoggerFactory.getLogger(B16ExafsValidator.class);

	private static AbstractValidator staticInstance;

	/**
	 * Gets a reference to the current validator. It does not return this concrete validator so that other
	 * implementations of AbstractValidator can be swapped.
	 * 
	 * @return validator
	 */
	public static AbstractValidator getInstance() {

		// Define as class loaded java class.
		if (System.getProperty("uk.ac.gda.exafs.validator") != null) {
			try {
				staticInstance = (AbstractValidator) Class.forName(System.getProperty("uk.ac.gda.exafs.validator"))
						.newInstance();
			} catch (Exception e) {
				logger.error("Cannot load '" + System.getProperty("uk.ac.gda.exafs.validator")
						+ "'. Perhaps this class is not an AbstractValidator or is not loadable by this classloader '"
						+ B16ExafsValidator.class.getClassLoader() + "'. Turning off validation.");
				return new B16ExafsValidator();
			}
		}

		// Define as findable object (might be jython or in server.xml)
		if (System.getProperty("uk.ac.gda.exafs.validator.name") != null) {
			try {
				staticInstance = (AbstractValidator) Finder.getInstance().find(
						System.getProperty("uk.ac.gda.exafs.validator.name"));
			} catch (Exception e) {
				logger.error("Cannot load '" + System.getProperty("uk.ac.gda.exafs.validator.name")
						+ "'. Perhaps this class is not an AbstractValidator. Turning off validation.");
				return new B16ExafsValidator();
			}
		}

		// Default - it you cannot pass these tests but want to continue with the scan,
		// do on of the above.
		if (staticInstance == null)
			staticInstance = new B16ExafsValidator();

		return staticInstance;
	}

	/**
	 * Singleton
	 */
	private B16ExafsValidator() {

	}

	protected B16ScanObject bean;

	/**
	 * Throws various exceptions if the system is not in a valid state.
	 * 
	 * @throws InvalidBeanException
	 */
	@Override
	public void validate(final IExperimentObject b) throws InvalidBeanException {

		this.bean = (B16ScanObject) b;

		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);

		try {
			// only validate what has been supplied
			if (bean.getScanParameters() != null && bean.getDetectorParameters() != null) {
				errors.addAll(validateIScanParameters(bean.getScanParameters()));
			}
			if (bean.getDetectorParameters() != null) {
				errors.addAll(validateIDetectorParameters(bean.getDetectorParameters()));
			}

			if (!errors.isEmpty()) {
				for (InvalidBeanMessage invalidBeanMessage : errors) {
					invalidBeanMessage.setFolderName(b.getFolder().getName());
				}
				throw new InvalidBeanException(errors);
			}
		} catch (Exception e) {
			throw new InvalidBeanException(e.getMessage());
		}

	}

	private List<InvalidBeanMessage> validateIScanParameters(IScanParameters scanParams) {
		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);
		if (scanParams instanceof MicroFocusScanParameters) {
			errors.addAll(validateMicroFocusParameters((MicroFocusScanParameters) scanParams));
		} else if (scanParams == null) {
			errors.add(new InvalidBeanMessage("Missing or Invalid Scan Parameters"));
		} else {
			errors.add(new InvalidBeanMessage("Unknown Scan Type " + scanParams.getClass().getName()));
		}
		if (bean != null)
			setFileName(errors, bean.getScanFileName());
		return errors;
	}

	protected List<InvalidBeanMessage> validateIDetectorParameters(IDetectorParameters iDetectorParams) {

		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);

		if (!(iDetectorParams instanceof DetectorParameters)) {
			if (iDetectorParams == null)
				errors.add(new InvalidBeanMessage("Missing or Invalid Detector Paramters"));
			else
				errors.add(new InvalidBeanMessage("Unknown Detector Type " + iDetectorParams.getClass().getName()));
		} /*else {
			errors.addAll(validateDetectorParameters((DetectorParameters) iDetectorParams));
		}*/

		if (bean != null)
			setFileName(errors, bean.getDetectorFileName());
		return errors;
	}

//	private List<InvalidBeanMessage> validateDetectorParameters(DetectorParameters d) {
//		if (!d.isShouldValidate())
//			return Collections.emptyList();
//
//		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);
//
//		final String exprType = d.getExperimentType();
//		if (("Fluorescence").equalsIgnoreCase(exprType)) {
//
//			final FluorescenceParameters f = d.getFluorescenceParameters();
//			final String message = "The fluorescence parameters are out of bounds.";
//			checkBounds("Working energy", f.getWorkingEnergy(), 0, 35000, errors, message);
//			if (xasScanParams != null) {
//				checkBounds("Working energy", f.getWorkingEnergy(), xasScanParams.getInitialEnergy(),
//						xasScanParams.getFinalEnergy(), errors, message);
//			}
//
//			// checkIonChambers(f.getIonChamberParameters(), f.getWorkingEnergy(), errors);
//
//		}
//
//		return errors;
//	}

	protected List<InvalidBeanMessage> validateMicroFocusParameters(MicroFocusScanParameters x) {
		if (x == null)
			return Collections.emptyList();

		final List<InvalidBeanMessage> errors = new ArrayList<InvalidBeanMessage>(31);
		// TODO add validation for MicroFocus
		return errors;
	}

	private static boolean isCheckingFinables = true;

	/**
	 * Used in testing mode to switch off checking of findables which are not there.
	 * 
	 * @param isChecking
	 */
	public static final void _setCheckingFinables(boolean isChecking) {
		isCheckingFinables = isChecking;
	}

	protected void checkFindable(final String label, final String deviceName, final Class<? extends Findable> clazz,
			final List<InvalidBeanMessage> errors, final String... messages) {

		if (!isCheckingFinables)
			return;

		if (deviceName == null) {
			InvalidBeanMessage msg = new InvalidBeanMessage("The " + label + " has no value and this is not allowed.",
					messages);
			msg.setLabel(label);
			errors.add(msg);
			return;
		}

		try {
			final Findable findable = Finder.getInstance().findNoWarn(deviceName);
			if (findable == null) {
				InvalidBeanMessage msg = new InvalidBeanMessage("Cannot find '" + deviceName + "' for input '" + label
						+ "'.", messages);
				msg.setLabel(label);
				errors.add(msg);
				return;
			}

			if (!clazz.isInstance(findable)) {
				InvalidBeanMessage msg = new InvalidBeanMessage("'" + deviceName + "' should be a '" + clazz.getName()
						+ "' but is a '" + findable.getClass() + "'.", messages);
				msg.setLabel(label);
				errors.add(msg);
			}

		} catch (Exception ne) {
			InvalidBeanMessage msg = new InvalidBeanMessage("Cannot find '" + deviceName + "' for input '" + label
					+ "'.", messages);
			msg.setLabel(label);
			errors.add(msg);
		}

	}

}
