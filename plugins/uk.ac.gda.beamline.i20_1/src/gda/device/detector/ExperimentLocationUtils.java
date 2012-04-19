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

package gda.device.detector;

import uk.ac.gda.exafs.ui.data.EdeScanParameters;

/**
 * Tools for converting between absolute frame number (as data stored in memory in terms of absolute frames) and
 * group/frame number (which is how experiments are defined).
 */
public abstract class ExperimentLocationUtils {
	/*
	 * Given the absolute frame number, works out the group number
	 */
	public static Integer getGroupNum(EdeScanParameters edeScan, Integer absoluteFrameNum) {
		
		if (absoluteFrameNum == 0){
			return 0;
		}
		
		int[] groupTotals = getGroupTotals(edeScan);

		int togo = absoluteFrameNum;
		int groupNum = 0;

		while (togo >= 0) {
			togo -= groupTotals[groupNum];
			groupNum++;
		}
		return groupNum - 1;
	}

	private static int[] getGroupTotals(EdeScanParameters edeScan) {
		int[] totals = new int[edeScan.getGroups().size()];

		for (int i = 0; i < edeScan.getGroups().size(); i++) {
			totals[i] = edeScan.getGroups().get(i).getNumberOfFrames();
		}
		return totals;
	}

	/*
	 * Given the absolute frame number, works out the frame number within the relevant group
	 */
	public static Integer getFrameNum(EdeScanParameters edeScan, Integer absoluteFrameNum) {
		
		if (absoluteFrameNum == 0){
			return 0;
		}
		
		int[] groupTotals = getGroupTotals(edeScan);
		int togo = absoluteFrameNum;
		int groupNum = 0;

		while (togo >= 0) {
			togo -= groupTotals[groupNum];
			groupNum++;
		}
		
		return togo + groupTotals[groupNum -1];
	}

	public static Integer getAbsoluteFrameNumber(EdeScanParameters edeScan, ExperimentLocation loc) {
		
		if (loc.groupNum == -1){
			return -1;
		}
		
		int[] groupTotals = getGroupTotals(edeScan);
		int groupNum = 0;
		int absFrameNum = 0;

		while (groupNum < loc.groupNum) {
			absFrameNum += groupTotals[groupNum];
			groupNum++;
		}
		absFrameNum += loc.frameNum;

		return absFrameNum;
	}

}
