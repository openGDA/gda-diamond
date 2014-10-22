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

package gda.device.scannable;

import gda.device.DeviceException;
import gda.device.Scannable;

/**
 * Similar to I18BeamMonitor except that it throws a RedoScanLineThrowable to repeat the line instead of pausing the
 * scan.
 */
public class I18LineRepeatingBeamMonitor extends LineRepeatingBeamMonitor {

	private Scannable beamlineEnergyWithGapScannable;

	public I18LineRepeatingBeamMonitor(Scannable beamlineEnergyWithGapScannable) {
		this.beamlineEnergyWithGapScannable = beamlineEnergyWithGapScannable;
		this.inputNames = new String[0];
		this.extraNames = new String[0];
		this.outputFormat = new String[0];
		this.level = 1;
	}

	@Override
	protected void testShouldPause() throws DeviceException {
		super.testShouldPause();
		
		// set energy to same value so idgap goes to correct position.
		Double beamlineEnergy = (Double) beamlineEnergyWithGapScannable.getPosition();
		beamlineEnergyWithGapScannable.moveTo(beamlineEnergy);

	}
}
