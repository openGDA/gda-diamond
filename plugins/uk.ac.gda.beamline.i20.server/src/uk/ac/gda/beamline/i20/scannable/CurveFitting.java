/*-
 * Copyright © 2023 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i20.scannable;

import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.fitting.Fitter;
import uk.ac.diamond.scisoft.analysis.fitting.functions.Gaussian;

public class CurveFitting {

	private static final Logger logger = LoggerFactory.getLogger(CurveFitting.class);

	/** Number of points either side of peak detector value to use when fitting*/
	private int peakPointRange = 4;

	/** If true, then curve fitting during optimisation will use a small number of points either side of peak detector value*/
	private boolean fitToPeakPointsOnly;

	public Gaussian findPeakOutput(Object[] xvalues, Object[] yvalues) {
		int numValues = Math.min(xvalues.length, yvalues.length);
		Dataset combined = DatasetFactory.zeros(numValues, 2);
		for(int i=0; i<numValues; i++) {
			combined.set(xvalues[i], i, 0);
			combined.set(yvalues[i], i, 1);
		}
		return findPeakOutput(combined);
	}

	/**
	 * Find peak position in x, y profile by fitting a Gaussian to it
	 * @param dataToFit (column 0 = x values, column 1 = y values)
	 * @return Gaussian object of 'best fit' parameters
	 */
	public Gaussian findPeakOutput(Dataset dataToFit) {

		logger.debug("Attempting to fit Gaussian to data.");

		//  If only fitting to peak points of the data replace data with subset
		if (fitToPeakPointsOnly) {
			dataToFit = extractDataNearPeak(dataToFit, peakPointRange);
		}

		// Extract x, y data as separate datasets
		Dataset positionData = getColumnFromDataSet(dataToFit, 0);
		Dataset detectorData = getColumnFromDataSet(dataToFit, 1);

		// Normalised detector data
		Dataset normDetectorData = getNormalisedDataset(detectorData);

		// Create Gaussian to use for fitting
		double centre = positionData.getDouble(positionData.getSize() / 2);
		Gaussian fitFunc = new Gaussian(centre, 1, 1);

		// restrict horizontal range of the fitted positions to match range of x values
		fitFunc.getParameter(0).setLimits(positionData.min().doubleValue(), positionData.max().doubleValue());

		try {
			Fitter.ApacheNelderMeadFit(new Dataset[] {positionData}, normDetectorData, fitFunc);
			logger.debug("Curve fitting completed sucessfully.");
		} catch( Exception exception) {
			// If fitting fails for some reason, just use position of the peak value
			logger.debug("Curve fitting failed, using maximum detector value for peak position instead.");
			int maxPosIndex = normDetectorData.maxPos()[0];
			double peakPos = positionData.getDouble(maxPosIndex);
			fitFunc.setParameterValues(peakPos, 1.0, 1.0);
		}
		logger.debug("Fitted peak position = {}", fitFunc.getPosition());
		return fitFunc;
	}

	/**
	 * Extract dataset containing values near to the peak value in column of dataset
	 * @param dataFromFile
	 * @Param peakRange number of rows either side of peak in column 2 to extract
	 * @return Dataset with several rows of data near peak detector value
	 */
	private Dataset extractDataNearPeak(Dataset dataFromFile, int peakRange) {

		// Find the indices of the maximum values, get result for column 2
		int maxPosIndex = dataFromFile.argMax(0, true).getInt(1);

		int numColumns = dataFromFile.getShape()[1];
		int startIndex = Math.max(maxPosIndex - peakRange, 0);

		int numDatapoints = dataFromFile.getShape()[0];
		int endIndex = Math.min(maxPosIndex + peakRange+1, numDatapoints);

		return dataFromFile.getSlice(new int[] {startIndex, 0}, new int[]{endIndex, numColumns}, null).squeeze();
	}

	private Dataset getColumnFromDataSet(Dataset dataset, int columnIndex) {
		int numRows = dataset.getShape()[0];
		return dataset.getSlice(new int[]{0, columnIndex}, new int[]{numRows, columnIndex+1}, null).squeeze();
	}

	/**
	 * Return normalised version of dataset (i.e. rescaled to cover range  [0, 1] )
	 * @param data 1-dimensional dataset
	 * @return dataset
	 */
	private Dataset getNormalisedDataset(Dataset data) {
		// Make a copy of the dataset
		Dataset dataset = DatasetFactory.createFromObject(data);
		double maxVal = dataset.max().doubleValue();
		double minVal = dataset.min().doubleValue();
		double range = maxVal - minVal;
		dataset.isubtract(minVal);
		dataset.imultiply(1.0/range);
		return dataset;
	}

	public int getPeakPointRange() {
		return peakPointRange;
	}

	public void setPeakPointRange(int peakPointRange) {
		this.peakPointRange = peakPointRange;
	}

	public boolean isFitToPeakPointsOnly() {
		return fitToPeakPointsOnly;
	}

	public void setFitToPeakPointsOnly(boolean fitToPeakPointsOnly) {
		this.fitToPeakPointsOnly = fitToPeakPointsOnly;
	}
}
