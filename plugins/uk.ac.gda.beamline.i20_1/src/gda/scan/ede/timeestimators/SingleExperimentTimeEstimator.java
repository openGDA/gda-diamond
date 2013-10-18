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

public class SingleExperimentTimeEstimator extends TimeEstimatorBase implements EdeTimeEstimate {

	@SuppressWarnings("unused")
	private final EdeScanPosition i0Position;
	@SuppressWarnings("unused")
	private final EdeScanPosition itPosition;
	private final EdeScanParameters itScanParameters;

	public SingleExperimentTimeEstimator(EdeScanParameters itScanParameters, EdeScanPosition i0Position,
			EdeScanPosition itPosition) {
		super();
		this.i0Position = i0Position;
		this.itPosition = itPosition;
		this.itScanParameters = itScanParameters;
	}

	@Override
	public Double getTotalDuration() {
		// there will also be two motor movements, so add 6s as a guess for now.
		return 6 + getItDuration() + 3 * estimateOneFrameFromEachGroupDuration(itScanParameters);
	}

	@Override
	public Double getItDuration() {
		return estimateScanDuration(itScanParameters);
	}

	@Override
	public Double getBookendsDuration() {
		return 2 + 2 * estimateOneFrameFromEachGroupDuration(itScanParameters);
	}

}
