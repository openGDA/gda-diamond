/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package gda.device.detector.xstrip;

import gda.device.detector.DetectorScanInfo;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

/**
 * Tools for converting between absolute frame number (as data stored in memory in terms of absolute frames) and
 * group/frame number (which is how experiments are defined).
 */
public final class DetectorScanDataUtils {

	private DetectorScanDataUtils() {}

	/**
	 * Given the absolute frame number (zero-based), works out the group number (also zero based)
	 */
	public static Integer getGroupNum(EdeScanParameters edeScan, Integer absoluteFrameNum) {
		if (absoluteFrameNum == 0) {
			return 0;
		}
		int[] groupTotals = getGroupTotals(edeScan);
		int togo = absoluteFrameNum;
		int groupNum = 0;
		while (togo > 0) {
			togo -= groupTotals[groupNum];
			groupNum++;
		}
		if (togo == 0) {
			return groupNum;
		}
		return groupNum - 1;
	}

	/*
	 * The total number of frames in each timing group
	 */
	private static int[] getGroupTotals(EdeScanParameters edeScan) {
		int[] totals = new int[edeScan.getGroups().size()];
		for (int i = 0; i < edeScan.getGroups().size(); i++) {
			totals[i] = edeScan.getGroups().get(i).getNumberOfFrames();
		}
		return totals;
	}

	/**
	 * Given the absolute frame number (zero-based), works out the frame number within the relevant group (also zero
	 * based)
	 */
	public static Integer getFrameNum(EdeScanParameters edeScan, Integer absoluteFrameNum) {

		if (absoluteFrameNum == 0) {
			return 0;
		}
		int[] groupTotals = getGroupTotals(edeScan);
		int togo = absoluteFrameNum;
		int groupNum = 0;
		do {
			// subtract the number in each group in turn
			togo -= groupTotals[groupNum];
			groupNum++;
		} while (togo > 0);

		// if we have dropped to zero or below then we know the group the frame is in, so correct by the number of
		// frames in that group
		if (togo < 0) {
			return togo + groupTotals[groupNum - 1];
		}
		return 0;

	}

	public static Integer getAbsoluteFrameNumber(EdeScanParameters edeScan, DetectorScanInfo loc) {
		int[] groupTotals = getGroupTotals(edeScan);
		int groupNum = 0;
		int absFrameNum = 0;
		while (groupNum < loc.groupNum) {
			absFrameNum += groupTotals[groupNum];
			groupNum++;
		}
		absFrameNum += (loc.frameNum);
		return absFrameNum;
	}

	/**
	 * Given the absolute frame number (zero-based), works out the starting time (in s) since the start of the scan
	 */
	public static Double getFrameTime(EdeScanParameters scanParameters, Integer absoluteFrameNum) {
		int groupNum = getGroupNum(scanParameters, absoluteFrameNum);
		int frameNum = getFrameNum(scanParameters, absoluteFrameNum);
		double totalTime = 0.0;
		for (int group = 0; group < groupNum; group++){
			totalTime += getGroupTotalTime(scanParameters.getGroups().get(group));
		}
		totalTime += getTimeOfFrameInGroup(scanParameters.getGroups().get(groupNum),frameNum);
		return totalTime;
	}

	public static Double getScanTime(EdeScanParameters scanParameters) {
		double totalTime = 0.0;
		for (int group = 0; group < scanParameters.getGroups().size(); group++){
			totalTime += getGroupTotalTime(scanParameters.getGroups().get(group));
		}
		return totalTime;
	}

	private static double getTimeOfFrameInGroup(TimingGroup timingGroup, int frame) {
		Double time = timingGroup.getPreceedingTimeDelay();
		if (timingGroup.getNumberOfScansPerFrame() == 0) {
			time += (timingGroup.getDelayBetweenFrames() + timingGroup.getTimePerFrame())
					* frame;
		} else {
			time += timingGroup.getDelayBetweenFrames() * frame + timingGroup.getNumberOfScansPerFrame()
					* frame;
		}
		return time;
	}

	private static double getGroupTotalTime(TimingGroup timingGroup) {
		return getTimeOfFrameInGroup(timingGroup, timingGroup.getNumberOfFrames());
	}
}
