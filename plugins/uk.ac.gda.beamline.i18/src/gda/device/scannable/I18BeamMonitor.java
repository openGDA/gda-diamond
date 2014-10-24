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
import gda.epics.connection.InitializationListener;

/**
 * I18 specific.
 * <p>
 * This will pause scans if the ring current goes below 1mA or if the front-end shutter is closed.
 * <p>
 * When the beam comes back it moves the energy scannable to its current position so that the ID gap is definitely at
 * the right place.
 */
public class I18BeamMonitor extends BeamMonitor implements InitializationListener {

	private Scannable beamlineEnergyWithGapScannable;

	public I18BeamMonitor(Scannable beamlineEnergyWithGapScannable) {
		super();
		this.inputNames = new String[0];
		this.extraNames = new String[0];
		this.outputFormat = new String[0];
		this.level = 1;
		this.beamlineEnergyWithGapScannable = beamlineEnergyWithGapScannable;
	}

	@Override
	protected void testShouldPause() throws DeviceException {
		super.testShouldPause();

		// set energy to same value so idgap goes to correct position.
		Double beamlineEnergy = (Double) beamlineEnergyWithGapScannable.getPosition();
		beamlineEnergyWithGapScannable.moveTo(beamlineEnergy);
	}

	@Override
	public void initializationCompleted() {
	}
}
