/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

package gda.images.camera;

import java.util.Arrays;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.scannable.ScannableMotionBase;

/**
 * Dummy scannable that mimics a 3-axis goniometer.
 */
public class DummySampleStageScannable extends ScannableMotionBase {
	
	private static final Logger logger = LoggerFactory.getLogger(DummySampleStageScannable.class);
	
	public DummySampleStageScannable() {
		setInputNames(new String[] {"x", "y", "z"});
	}
	
	private double[] position = new double[] {0, 0, 0};
	
	/**
	 * Returns the goniometer's position as a 3-element {@code double} array.
	 */
	public double[] getPositionArray() {
		return (position == null) ? null : position;
	}
	
	@Override
	public Object rawGetPosition() throws DeviceException {
		return position;
	}
	
	@Override
	public void moveTo(Object position) throws DeviceException {
		String valid = checkPositionValid(position);
		if (valid != null) {
			throw new DeviceException(valid);
		}
		this.position = (double[]) position;
		logger.debug(String.format("moving to %s", Arrays.toString(this.position)));
	}

}
