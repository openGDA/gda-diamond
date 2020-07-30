/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.summary;

import java.util.Optional;
import java.util.function.Consumer;
import java.util.function.Supplier;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.gda.api.acquisition.parameters.DetectorDocument;
import uk.ac.gda.client.UIHelper;

/**
 * A base class common to all the shape reporting.
 *
 * <p>
 * Each shape may contains different properties and, as such, is not possible to have a common {@code toString} for all.
 * For this reason each shape is required to implements its own subclass to match the available data.
 * </p>
 *
 * @author Maurizio Nagni
 */
public class ShapeSummaryBase  {

	protected static final Logger logger = LoggerFactory.getLogger(ShapeSummaryBase.class);
	private final Consumer<String> printOut;

	private final Supplier<ScanningAcquisition> acquisitionSupplier;

	/**
	 * @param printOut a consumer to use the report a summary
	 */
	public ShapeSummaryBase(Consumer<String> printOut, Supplier<ScanningAcquisition> acquisitionSupplier) {
		this.printOut = printOut;
		this.acquisitionSupplier = acquisitionSupplier;
	}

	protected ScanningParameters getScanningParameters() {
		return getAcquisition().getAcquisitionConfiguration().getAcquisitionParameters();
	}

	/**
	 * Uses the consumer to print out the report summary
	 * @param text
	 */
	void printOut(String text) {
		printOut.accept(text);
	}

	protected ScanningAcquisition getAcquisition() {
		return acquisitionSupplier.get();
	}

	protected double getExposure() {
		Optional<Double> exposure = Optional.ofNullable(getScanningParameters().getDetector()).map(DetectorDocument::getExposureTime);
		if (exposure.isPresent()) {
			return exposure.get();
		}
		UIHelper.showWarning("Exposure is zero", "No DetectorDocument is defined");
		return 0d;
	}
}
