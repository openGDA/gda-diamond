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

package uk.ac.gda.exafs.ui.data;

import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.january.dataset.IntegerDataset;

/**
 * Used to create data to plot in graph of when acquiring and not acquiring data for a given time frame in a
 * TFGParameters bean.
 */
public final class TFGTimingCalculator {

	/**
	 * @param scanBean
	 * @param frameToReturn
	 * @return Dataset[4] - xDataSet, yDataSet, inputsDataSet, outputsDataset
	 */
	public static  Dataset[] calculateTimePoints(TFGParameters scanBean, int frameToReturn) {
		TimeFrame frame = scanBean.getTimeFrames().get(frameToReturn);

		Double deadTime = frame.getDeadTime();
		Double liveTime = frame.getLiveTime();
		int lemoIn = frame.getLemoIn();
		int lemoOut = frame.getLemoOut();

		double[] xValues = new double[5];
		double[] yValues = new double[5];

		xValues[0] = 0.;
		yValues[0] = 0.;

		xValues[1] = deadTime;
		yValues[1] = 0.;

		xValues[2] = deadTime;
		yValues[2] = 1.0;

		xValues[3] = deadTime + liveTime;
		yValues[3] = 1.0;

		xValues[4] = deadTime + liveTime;
		yValues[4] = 0.;


		DoubleDataset xDataSet = DatasetFactory.createFromObject(DoubleDataset.class, xValues, xValues.length);
		DoubleDataset yDataSet = DatasetFactory.createFromObject(DoubleDataset.class, yValues, yValues.length);
		IntegerDataset inputsDataSet = DatasetFactory.zeros(IntegerDataset.class, 1);
		inputsDataSet.set(lemoIn, 0);
		IntegerDataset outputsDataset = DatasetFactory.zeros(IntegerDataset.class, 1);
		outputsDataset.set(lemoOut, 0);
		return new Dataset[] { xDataSet, yDataSet, inputsDataSet, outputsDataset };
	}
}
