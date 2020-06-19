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

package gda.scan.ede.timeestimators;

import java.util.List;

import gda.scan.ede.position.EdeScanPosition;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public abstract class TimeEstimatorBase implements EdeTimeEstimate {

	/**
	 * Sum all the integration time of all the delays and integrations, assuming no external delays from external
	 * triggers.
	 *
	 * @param scanParameters
	 * @return time in seconds
	 */
	protected Double estimateScanDuration(EdeScanParameters scanParameters) {
		// TODO add the time it takes to program the TFG here
		Double timeEstimate = 0.0;
		List<TimingGroup> groups = scanParameters.getGroups();
		for (TimingGroup group : groups) {
			// delays
			timeEstimate += group.getPreceedingTimeDelay();
			timeEstimate += ((group.getNumberOfFrames() - 1) * group.getDelayBetweenFrames());

			// integrations
			if (group.getNumberOfScansPerFrame() == 0) {
				timeEstimate += (group.getNumberOfFrames() * group.getTimePerFrame());
			} else {
				timeEstimate += (group.getNumberOfFrames() * group.getTimePerScan() * group.getNumberOfScansPerFrame());
			}
		}
		return timeEstimate;
	}

	/**
	 * Sum of the integration time of one frame from each timing group with no delays and no triggers. These are the
	 * integrations which would be performed to collect dark, I0 or Iref data to normalise the It data.
	 *
	 * @param scanParameters
	 * @return time in seconds
	 */
	protected Double estimateOneFrameFromEachGroupDuration(EdeScanParameters scanParameters) {
		// TODO add the time it takes to program the TFG here
		Double timeEstimate = 0.0;
		List<TimingGroup> groups = scanParameters.getGroups();
		for (TimingGroup group : groups) {
			// integrations
			if (group.getNumberOfScansPerFrame() == 0) {
				timeEstimate += group.getTimePerFrame();
			} else {
				timeEstimate += (group.getTimePerScan() * group.getNumberOfScansPerFrame());
			}
		}
		return timeEstimate;
	}

	/**
	 * Not simply the duration of the actual movement, but includes overhead of communicating to the motors via the
	 * control system.
	 *
	 * @param startPosition
	 * @param endPosition
	 * @return time in seconds
	 */
	protected Double estimateMovementDuration(EdeScanPosition startPosition, EdeScanPosition endPosition) {
		// for the moment simply have a fixed value. Need to make some pratical measurements to see if making a more
		// accurate guess is of value.
		return 2.0;

		// if (startPosition == null && endPosition instanceof AlignmentStageScanPosition) {
		// return 2.0; // FIXME a guess!
		// }
		//
		// if (endPosition == null && startPosition instanceof AlignmentStageScanPosition) {
		// return 2.0; // FIXME a guess!
		// }
		//
		// if (startPosition == null && endPosition instanceof ExplicitScanPositions) {
		//
		// Double currentX = getCurrentMotorPosition(((ExplicitScanPositions)endPosition).getxMotor());
		// Double currentY = getCurrentMotorPosition(((ExplicitScanPositions)endPosition).getyMotor());
		//
		// Double targetX = ((ExplicitScanPositions)endPosition).getxPosition();
		// Double targetY = ((ExplicitScanPositions)endPosition).getyPosition();
		// }
	}

	// private double getCurrentMotorPosition(String motorName) {
	// try {
	// double[] currentPos = ScannableUtils.getCurrentPositionArray((Scannable)Finder.find(motorName));
	// return currentPos[0];
	// } catch (DeviceException e) {
	// // have to use some number, this is only an estimate
	// return 0.0;
	// }
	// }

}
