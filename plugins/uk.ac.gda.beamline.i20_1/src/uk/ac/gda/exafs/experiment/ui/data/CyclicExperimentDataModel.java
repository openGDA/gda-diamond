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

package uk.ac.gda.exafs.experiment.ui.data;

import uk.ac.gda.beamline.i20_1.utils.DataHelper;

public class CyclicExperimentDataModel extends TimeIntervalDataModel {

	private final CyclicExperimentModel parent;

	public CyclicExperimentDataModel(CyclicExperimentModel parent) {
		this.parent = parent;
	}

	@Override
	public void dispose() {
		// Nothing to dispose
	}

	@Override
	public String toString() {
		String timeResolution = DataHelper.roundDoubletoStringWithOptionalDigits(parent.getUnit().convertFromMilli(this.getEndTime())) + " " + parent.getUnit().getUnitText();
		return this.getName() + "\n" + timeResolution;
	}

}
