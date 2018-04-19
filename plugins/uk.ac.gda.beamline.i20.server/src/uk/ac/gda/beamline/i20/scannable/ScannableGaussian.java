/*-
 * Copyright © 2016 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i20.scannable;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableBase;
import uk.ac.diamond.scisoft.analysis.fitting.functions.Gaussian;

/**
 * Simple {@link Scannable} that returns a value from a Gaussian function when getPosition() is called.
 * This is currently used for testing {@link MonoOptimisation}.
 */
public class ScannableGaussian extends ScannableBase {
	protected Scannable scannableForPosition;
	protected Gaussian gaussian;
	protected double currentPos;

	public ScannableGaussian(String name, double centrePos, double fwhm, double area ) {
		setName(name);
		setParams(centrePos, fwhm, area);
		currentPos = 0;
		scannableForPosition = null;
	}

	public void setParams(double centrePos, double fwhm, double area) {
		gaussian = new Gaussian(centrePos, fwhm, area);
	}

	public void setScannableToMonitorForPosition(Scannable mon) {
		scannableForPosition = mon;
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		currentPos = (double) Double.parseDouble(position.toString());
	}

	@Override
	public Object getPosition() throws DeviceException {
		if( scannableForPosition != null )
			rawAsynchronousMoveTo(scannableForPosition.getPosition());

		return gaussian.val(currentPos);
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}
}
