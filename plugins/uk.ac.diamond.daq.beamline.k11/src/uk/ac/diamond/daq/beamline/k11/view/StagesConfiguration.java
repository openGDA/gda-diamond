/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.view;

import java.util.Map;
import java.util.Objects;

import gda.factory.FindableBase;

public class StagesConfiguration extends FindableBase {

	/** {Stage name : {axis name: scannable name}} */
	private final Map<String, Map<String, String>> config;

	/**
	 * @param config {Stage name : {axis name: scannable name}}
	 */
	public StagesConfiguration(Map<String, Map<String, String>> config) {
		this.config = config;
	}

	/**
	 * @return {Stage name : {axis name: scannable name}}
	 */
	public Map<String, Map<String, String>> getStageConfiguration() {
		return config;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = super.hashCode();
		result = prime * result + Objects.hash(config);
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (!super.equals(obj))
			return false;
		if (getClass() != obj.getClass())
			return false;
		StagesConfiguration other = (StagesConfiguration) obj;
		return Objects.equals(config, other.config);
	}

}
