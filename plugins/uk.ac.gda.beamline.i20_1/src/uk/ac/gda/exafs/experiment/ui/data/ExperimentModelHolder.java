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

import uk.ac.gda.exafs.data.SingleSpectrumCollectionModel;

public enum ExperimentModelHolder {
	INSTANCE;

	private final TimeResolvedExperimentModel linerExperimentModel;
	private final CyclicExperimentModel cyclicExperimentModel;
	private final SingleSpectrumCollectionModel singleSpectrumExperimentModel;
	private final SingleSpectrumCollectionModel singleSpectrumExperimentMappingModel;

	private ExperimentModelHolder() {

		linerExperimentModel = new TimeResolvedExperimentModel();
		linerExperimentModel.setup();

		cyclicExperimentModel = new CyclicExperimentModel();
		cyclicExperimentModel.setup();

		singleSpectrumExperimentModel = new SingleSpectrumCollectionModel();
		singleSpectrumExperimentModel.setup();

		singleSpectrumExperimentMappingModel = new SingleSpectrumCollectionModel();
		singleSpectrumExperimentMappingModel.setDataStoreKeyBase("SINGLE_SPECTRUM_MAPPING");
		singleSpectrumExperimentMappingModel.setup();
	}

	public TimeResolvedExperimentModel getLinerExperimentModel() {
		return linerExperimentModel;
	}

	public CyclicExperimentModel getCyclicExperimentModel() {
		return cyclicExperimentModel;
	}

	public SingleSpectrumCollectionModel getSingleSpectrumExperimentModel() {
		return singleSpectrumExperimentModel;
	}

	public SingleSpectrumCollectionModel getSingleSpectrumExperimentMappingModel() {
		return singleSpectrumExperimentMappingModel;
	}
}
