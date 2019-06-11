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

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;

/**
 * Used to create data to plot in graph of when acquiring and not acquiring data
 */
public class EdeTimingCalculator {

	private static double[] xValues;
	private static double[] yValues;
	private static double[] inputTrigPoints;
	private static double[] outputTrigPoints;
	private static double timeTracker;

	/**
	 * @param scanBean
	 * @return DoubleDataset[4] - xDataSet, yDataSet, inputsDataSet, outputsDataset
	 */
	public static DoubleDataset[] calculateTimePoints(EdeScanParameters scanBean) {

		resetArrays();

		for (TimingGroup group : scanBean.getGroups()) {
			addGroup(group, scanBean);
		}

		Integer numRepetitions = scanBean.getNumberOfRepetitions();
		repeatGroups(numRepetitions);

		return returnArraysAsDatasets();
	}

	private static DoubleDataset[] returnArraysAsDatasets() {
		DoubleDataset xDataSet = DatasetFactory.createFromObject(DoubleDataset.class, xValues);
		DoubleDataset yDataSet = DatasetFactory.createFromObject(DoubleDataset.class, yValues);
		DoubleDataset inputsDataSet = DatasetFactory.createFromObject(DoubleDataset.class, inputTrigPoints);
		DoubleDataset outputsDataset = DatasetFactory.createFromObject(DoubleDataset.class, outputTrigPoints);
		return new DoubleDataset[] { xDataSet, yDataSet, inputsDataSet, outputsDataset };
	}

	private static void resetArrays() {
		// reset stored values
		xValues = new double[0];
		yValues = new double[0];
		inputTrigPoints = new double[0];
		outputTrigPoints = new double[0];
		timeTracker = 0.0; // in s
	}

	public static DoubleDataset[] calculateTimingGroupPoints(EdeScanParameters bean, int selectedGroup) {
		resetArrays();
		TimingGroup group = bean.getGroups().get(selectedGroup);
		addGroup(group, bean);
		return returnArraysAsDatasets();
	}

	private static void repeatGroups(Integer numRepetitions) {
		double[] newYValues = new double[0];
		newYValues = ArrayUtils.addAll(newYValues, yValues);
		for (int i = 1; i < numRepetitions; i++) {
			newYValues = ArrayUtils.addAll(newYValues, yValues);
		}
		yValues = newYValues;

		double timePerRepetition = xValues[xValues.length - 1];
		xValues = repeatArray(numRepetitions, xValues, timePerRepetition);
		inputTrigPoints = repeatArray(numRepetitions, inputTrigPoints, timePerRepetition);
		outputTrigPoints = repeatArray(numRepetitions, outputTrigPoints, timePerRepetition);
		timeTracker = xValues[xValues.length - 1];
	}

	protected static double[] repeatArray(Integer numRepetitions, double[] valuesArray, double timePerRepetition) {
		double[] returnValues = valuesArray;
		double currentTime = timeTracker;
		for (int i = 1; i < numRepetitions; i++) {
			double[] valuesToAdd = new double[valuesArray.length];
			for (int j = 0; j < valuesArray.length; j++) {
				valuesToAdd[j] = valuesArray[j] + currentTime;
			}
			returnValues = ArrayUtils.addAll(returnValues, valuesToAdd);
			currentTime += timePerRepetition;
		}
		return returnValues;
	}

	private static void addGroup(TimingGroup group, EdeScanParameters scanBean) {

		if (group.isGroupTrig()) {
			markInputTrig(0);
		}

		markOutputTrig(group, scanBean, EdeScanParameters.TRIG_GROUP_BEFORE);

		double groupDelay = group.getPreceedingTimeDelay();
		if (groupDelay > 0.0) {
			addOffTime(groupDelay);
		}

		markOutputTrig(group, scanBean, EdeScanParameters.TRIG_GROUP_AFTER);

		double timePerScan = group.getTimePerScan();
		if (timePerScan <= 0.0) {
			return;
		}

		double delayBetweenFrames = group.getDelayBetweenFrames();
		long assumedNumberOfScans = Math.round(Math.floor(group.getTimePerFrame() / timePerScan));

		for (int frameNum = 0; frameNum < group.getNumberOfFrames(); frameNum++) {

			markOutputTrig(group, scanBean, EdeScanParameters.TRIG_FRAME_BEFORE);

			if (group.isAllFramesTrig()) {
				markInputTrig(1);
			}

			if (frameNum > 0 && group.isFramesExclFirstTrig()) {
				markInputTrig(2);
			}

			// no delay for first frame in group
			if (frameNum != 0) {
				addOffTime(delayBetweenFrames);
			}

			markOutputTrig(group, scanBean, EdeScanParameters.TRIG_FRAME_AFTER);

			for (int scanNum = 0; scanNum < assumedNumberOfScans; scanNum++) {

				markOutputTrig(group, scanBean, EdeScanParameters.TRIG_SCAN_BEFORE);

				if (group.isScansTrig()) {
					markInputTrig(3);
				}

				addOnTime(timePerScan);
				addOffTime(1E-7); // 100ns delay between scans
			}
		}
	}

	private static void markOutputTrig(TimingGroup group, EdeScanParameters scanBean, String trigGroupBefore) {
		// loop through enabled trig outs
		boolean[] enabledOuts = group.getOutLemos();
		String[] outputChoices = scanBean.getOutputsChoices();
		for (int i = 0; i < 7; i++) {
			if (enabledOuts[i]) {
				// if enabled, does the out type for that LEMO match where we are in time (the trigGroupBefore string)
				if (outputChoices[i].equals(trigGroupBefore)) {
					double time = timeTracker;
					outputTrigPoints = ArrayUtils.add(outputTrigPoints, time);
				}
			}
		}
	}

	private static void markInputTrig(int type) {
		inputTrigPoints = ArrayUtils.add(inputTrigPoints, timeTracker);
	}

	private static void addOnTime(Double timeOn) {
		addPoint(0.0, 1.0);
		addPoint(timeOn, 1.0);
	}

	private static void addOffTime(Double timeOff) {
		addPoint(0.0, 0.0);
		addPoint(timeOff, 0.0);
	}

	private static void addPoint(double x, double y) {
		timeTracker += x;
		xValues = ArrayUtils.add(xValues, timeTracker);
		yValues = ArrayUtils.add(yValues, y);
	}

}
