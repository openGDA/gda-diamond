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

package uk.ac.gda.exafs.ui.data.experiment;

import uk.ac.gda.exafs.data.ClientConfig;

public enum ExperimentUnit {
	MILLI_SEC(ClientConfig.UnitSetup.MILLI_SEC, 1),
	SEC(ClientConfig.UnitSetup.SEC, 1000),
	MINUTE(ClientConfig.UnitSetup.MINUTE, 60 * 1000),
	HOUR(ClientConfig.UnitSetup.HOUR, 60 * 60 * 1000);

	private final ClientConfig.UnitSetup unit;
	private final double conversionUnit;

	private ExperimentUnit(ClientConfig.UnitSetup unit, double conversionUnit) {
		this.unit = unit;
		this.conversionUnit = conversionUnit;
	}

	public ExperimentUnit getWorkingUnit() {
		if (this.ordinal() > 0) {
			return ExperimentUnit.values()[this.ordinal() - 1];
		}
		return this;
	}

	public double convertToMilli(double value) {
		return value * conversionUnit;
	}

	public double convertToSecond(double value) {
		return value * (conversionUnit / 1000);
	}

	public double convertFromMilli(double value) {
		return value / conversionUnit;
	}

	public String getUnitText() {
		return unit.getText();
	}
}