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

package uk.ac.gda.exafs.ui.views;

import uk.ac.gda.exafs.ui.data.experiment.ExperimentModelHolder;
import uk.ac.gda.exafs.ui.data.experiment.TimeResolvedExperimentModel;

public class CyclicExperimentView extends LinearExperimentView {
	public static final String CYCLIC_EXPERIMENT_VIEW_ID = "uk.ac.gda.exafs.ui.views.cyclicExperimentView";

	@Override
	protected TimeResolvedExperimentModel getModel() {
		return ExperimentModelHolder.INSTANCE.getCyclicExperimentModel();
	}
}
