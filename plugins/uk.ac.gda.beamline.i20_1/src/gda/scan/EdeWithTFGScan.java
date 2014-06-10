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

package gda.scan;

import gda.device.Scannable;
import gda.device.detector.StripDetector;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.position.EdeScanPosition;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;

public class EdeWithTFGScan extends EdeWithoutTriggerScan implements EnergyDispersiveExafsScan {

	public EdeWithTFGScan(EdeScanParameters scanParameters, EdeScanPosition motorPositions, EdeScanType scanType,
			StripDetector theDetector, Integer repetitionNumber, Scannable shutter) {
		super(scanParameters, motorPositions, scanType, theDetector, repetitionNumber, shutter,null);
		// TODO Auto-generated constructor stub
	}

}
