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

import gda.scan.ede.position.EdeScanPosition;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;

public class LinearExperimentTimeEstimator extends TimeEstimatorBase {


	private final EdeScanParameters itScanParameters;
	private final EdeScanPosition i0Position;
	private final EdeScanPosition itPosition;
	private final EdeScanPosition iRefPosition;

	public LinearExperimentTimeEstimator(EdeScanParameters itScanParameters, EdeScanPosition i0Position,
			EdeScanPosition itPosition, EdeScanPosition iRefPosition) {
		this.itScanParameters = itScanParameters;
		this.i0Position = i0Position;
		this.itPosition = itPosition;
		this.iRefPosition = iRefPosition;
	}

	@Override
	public Double getTotalDuration() {
		if (iRefPosition == null || iRefPosition.equals(i0Position)) {
			return estimateMovementDuration(null, i0Position) + estimateMovementDuration(i0Position, itPosition)
					+ getItDuration() + estimateMovementDuration(itPosition, i0Position) + (3
							* estimateOneFrameFromEachGroupDuration(itScanParameters));

		}
		return estimateMovementDuration(null, i0Position) + estimateMovementDuration(i0Position,iRefPosition) +
				estimateMovementDuration(i0Position, itPosition)
				+ getItDuration() + estimateMovementDuration(itPosition, i0Position) + estimateMovementDuration(i0Position,iRefPosition)
				+ (5 * estimateOneFrameFromEachGroupDuration(itScanParameters));
	}

	@Override
	public Double getItDuration() {
		return estimateScanDuration(itScanParameters);
	}

	@Override
	public Double getBookendsDuration() {
		if (iRefPosition == null || iRefPosition.equals(i0Position)){
			return estimateMovementDuration(null, i0Position) + 2 * estimateOneFrameFromEachGroupDuration(itScanParameters);
		}
		return estimateMovementDuration(null, i0Position) + estimateMovementDuration(i0Position,iRefPosition) + 3 * estimateOneFrameFromEachGroupDuration(itScanParameters);
	}

}
