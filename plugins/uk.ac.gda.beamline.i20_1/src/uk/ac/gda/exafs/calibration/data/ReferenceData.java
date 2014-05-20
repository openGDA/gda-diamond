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

package uk.ac.gda.exafs.calibration.data;



public class ReferenceData extends CalibrationEnergyData {
	public static final String REF_DATA_COLUMN_NAME = "lnI0It";
	public static final String REF_ENERGY_COLUMN_NAME = "Energy";

	@Override
	public void setDataFile(String fileName) throws Exception {
		setData(fileName, REF_ENERGY_COLUMN_NAME, REF_DATA_COLUMN_NAME);
	}
}
