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

package uk.ac.gda.exafs.experiment.ui;

import org.eclipse.swt.custom.SashForm;

import uk.ac.gda.exafs.experiment.ui.data.CyclicExperimentModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentModelHolder;

public class CyclicExperimentView extends TimeResolvedExperimentView {
	public static final String CYCLIC_EXPERIMENT_VIEW_ID = "uk.ac.gda.exafs.ui.views.cyclicExperimentView";

	@Override
	protected CyclicExperimentModel getModel() {
		return ExperimentModelHolder.INSTANCE.getCyclicExperimentModel();
	}

	@Override
	protected void createSections(final SashForm parentComposite) {
		createExperimentPropertiesComposite(parentComposite);
		createStartStopScanSection(parentComposite);
		parentComposite.setWeights(new int[] {8, 2});
	}
}
