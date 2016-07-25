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

package gda.scan.ede;

import java.io.Serializable;

import org.eclipse.january.dataset.DoubleDataset;

public class EdeExperimentProgressBean implements Serializable {

	public enum ExperimentCollectionType {
		SINGLE, MULTI
	}

	private final EdeScanProgressBean progress;
	private final DoubleDataset data;
	private final DoubleDataset energyData;
	private final String dataLabel;
	private final ExperimentCollectionType experimentCollectionType;
	public EdeExperimentProgressBean(ExperimentCollectionType experimentCollectionType, EdeScanProgressBean progress, String dataLabel, DoubleDataset data, DoubleDataset energyData) {
		this.experimentCollectionType = experimentCollectionType;
		this.progress = progress;
		this.dataLabel = dataLabel;
		this.data = data;
		this.energyData = energyData;
	}

	public EdeScanProgressBean getProgress() {
		return progress;
	}

	public DoubleDataset getData() {
		return data;
	}

	public DoubleDataset getEnergyData() {
		return energyData;
	}

	public String getDataLabel() {
		return dataLabel;
	}

	public ExperimentCollectionType getExperimentCollectionType() {
		return experimentCollectionType;
	}

}
