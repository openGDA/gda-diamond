/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

import uk.ac.gda.ede.data.ClientConfig;

public enum ExperimentUnit {
	HOUR(ClientConfig.UnitSetup.HOUR, 60L * 60L * 1000L * 1000L * 1000L),
	MINUTE(ClientConfig.UnitSetup.MINUTE, 60L * 1000L * 1000L * 1000L),
	SEC(ClientConfig.UnitSetup.SEC, 1000L * 1000L * 1000L),
	MILLI_SEC(ClientConfig.UnitSetup.MILLI_SEC, 1000L * 1000L),
	MIRCO_SEC(ClientConfig.UnitSetup.MICRO_SEC, 1000L),
	NANO_SEC(ClientConfig.UnitSetup.NANO_SEC, 1L);

	public static final ExperimentUnit DEFAULT_EXPERIMENT_UNIT = ExperimentUnit.NANO_SEC;
	public static final ExperimentUnit DEFAULT_EXPERIMENT_UNIT_FOR_I0_IREF = ExperimentUnit.MILLI_SEC;
	public static final int MAX_RESOLUTION_IN_NANO_SEC = 20;

	private final ClientConfig.UnitSetup unit;
	private final long conversionUnit;

	private ExperimentUnit(ClientConfig.UnitSetup unit, long conversionUnit) {
		this.unit = unit;
		this.conversionUnit = conversionUnit;
	}

	public ExperimentUnit getWorkingUnit() {
		if (this.ordinal() != ExperimentUnit.values().length - 1) {
			return ExperimentUnit.values()[this.ordinal() + 1];
		}
		return this;
	}

	public double convertTo(double value, ExperimentUnit unitToConvert) {
		return (value * conversionUnit) / unitToConvert.conversionUnit;
	}

	public double convertToDefaultUnit(double value) {
		return (value * conversionUnit);
	}

	public double convertFromDefaultUnit(double value) {
		return (value * DEFAULT_EXPERIMENT_UNIT.conversionUnit) / conversionUnit;
	}

	public String getUnitText() {
		return unit.getText();
	}

	public boolean canConvertToFrame(double value) {
		return (this.convertFromDefaultUnit(value) % MAX_RESOLUTION_IN_NANO_SEC == 0);
	}

	public double convertToNearestFrame(double value) {
		double defaultValue = this.convertFromDefaultUnit(value);
		if (defaultValue < MAX_RESOLUTION_IN_NANO_SEC) {
			return MAX_RESOLUTION_IN_NANO_SEC;
		}
		double remainder = defaultValue % MAX_RESOLUTION_IN_NANO_SEC;
		if (remainder == 0) {
			return value;
		}
		defaultValue = Math.ceil(defaultValue);
		remainder =  defaultValue% MAX_RESOLUTION_IN_NANO_SEC;
		return defaultValue - remainder;
	}
}