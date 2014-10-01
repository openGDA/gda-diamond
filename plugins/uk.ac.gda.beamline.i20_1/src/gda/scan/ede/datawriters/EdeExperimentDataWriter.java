/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package gda.scan.ede.datawriters;

import gda.device.detector.StripDetector;
import gda.jython.InterfaceProvider;

import org.eclipse.dawnsci.analysis.dataset.impl.DoubleDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class EdeExperimentDataWriter {

	private static final Logger logger = LoggerFactory.getLogger(EdeExperimentDataWriter.class);

	protected String filenameTemplate = "";
	protected StripDetector theDetector;

	protected final DoubleDataset energyDataSet;

	public abstract String getAsciiFilename();

	public EdeExperimentDataWriter(DoubleDataset energyDataSet) {
		this.energyDataSet = energyDataSet;
	}

	public static Double calcLnI0It(Double i0_corrected, Double it_corrected) {
		Double lni0it = Math.log(i0_corrected / it_corrected);
		if (lni0it.isNaN() || lni0it.isInfinite() /*|| lni0it < 0.0*/) {
			lni0it = .0;
		}
		return lni0it;
	}

	public static DoubleDataset normaliseDatasset(DoubleDataset itRaw, DoubleDataset i0Raw, DoubleDataset dark) {

		double[] itRawArray = itRaw.getData();
		double[] i0RawArray = i0Raw.getData();
		double[] darkArray = dark.getData();

		double[] itNormaliseArray = new double[itRawArray.length];

		for (int channel = 0; channel < itNormaliseArray.length; channel++) {
			itNormaliseArray[channel] = calcLnI0It(i0RawArray[channel]-darkArray[channel],itRawArray[channel]-darkArray[channel]);
		}

		return new DoubleDataset(itNormaliseArray,itNormaliseArray.length);
	}

	public static DoubleDataset normaliseDatasset(DoubleDataset it, DoubleDataset i0) {

		double[] itArray = it.getData();
		double[] i0Array = i0.getData();
		double[] itNormaliseArray = new double[itArray.length];

		for (int channel = 0; channel < itNormaliseArray.length; channel++) {
			itNormaliseArray[channel] = calcLnI0It(i0Array[channel],itArray[channel]);
		}

		return new DoubleDataset(itNormaliseArray,itNormaliseArray.length);

	}

	public abstract String writeDataFile() throws Exception;

	protected void log(String message) {
		InterfaceProvider.getTerminalPrinter().print(message);
		logger.info(message);
	}
}
