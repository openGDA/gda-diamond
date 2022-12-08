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
	private final EdeScanParameters i0ScanParameters;
	private final EdeScanParameters iRefScanParameters;

	public LinearExperimentTimeEstimator(
			EdeScanParameters i0ScanParameters,
			EdeScanParameters itScanParameters,
			EdeScanParameters iRefScanParameters,
			EdeScanPosition i0Position,
			EdeScanPosition itPosition,
			EdeScanPosition iRefPosition) {
		this.i0ScanParameters = i0ScanParameters;
		this.itScanParameters = itScanParameters;
		this.iRefScanParameters = iRefScanParameters;
		this.i0Position = i0Position;
		this.itPosition = itPosition;
		this.iRefPosition = iRefPosition;
	}

	@Override
	public Double getItDuration() {
		return estimateScanDuration(itScanParameters);
	}

	@Override
	public Double getBeforeItDuration() {
		if (iRefPosition == null || iRefPosition.equals(i0Position)) {
			return estimateMovementDuration(null, i0Position)
					+ (3 * estimateOneFrameFromEachGroupDuration(itScanParameters)) // I0_dark, it_dark, I0
					+ estimateMovementDuration(i0Position, itPosition);
		}
		return estimateMovementDuration(null, i0Position) + estimateMovementDuration(i0Position, iRefPosition)
				+ estimateMovementDuration(iRefPosition, itPosition)
				+ (5 * estimateOneFrameFromEachGroupDuration(itScanParameters)); // I0_dark, it_dark, Iref_dark, I0, Iref
	}

	@Override
	public Double getAfterItDuration() {
		if (iRefPosition == null || iRefPosition.equals(i0Position)){
			return estimateMovementDuration(null, i0Position) + estimateOneFrameFromEachGroupDuration(itScanParameters);
		}
		return estimateMovementDuration(null, i0Position) + estimateMovementDuration(i0Position,iRefPosition) + 2 * estimateOneFrameFromEachGroupDuration(itScanParameters);
	}

	@Override
	public Double getTotalDuration() {
		return getBeforeItDuration() + getItDuration() + getAfterItDuration();
	}

}
