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

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableUtils;
import uk.ac.gda.api.remoting.ServiceInterface;

/**
 * Implementation of {@link SampleMovementService} that uses scannables.
 */
@ServiceInterface(SampleMovementService.class)
public class ScannableSampleMovementService extends SampleMovementServiceBase {
	
	private Scannable sampleXyz;
	
	public void setSampleXyz(Scannable sampleXyz) {
		this.sampleXyz = sampleXyz;
	}
	
	private Scannable omega;
	
	public void setOmegaScannable(Scannable omega) {
		this.omega = omega;
	}
	
	@Override
	public void afterPropertiesSet() throws Exception {
		super.afterPropertiesSet();
		if (sampleXyz == null) {
			throw new IllegalArgumentException("The 'sampleXyz' property is required");
		}
		if (omega == null) {
			throw new IllegalArgumentException("The 'omegaScannable' property is required");
		}
	}
	
	@Override
	protected double getOmega() throws DeviceException {
		return (Double) omega.getPosition();
	}
	
	@Override
	protected double[] getPosition() throws DeviceException {
		return ScannableUtils.getCurrentPositionArray(sampleXyz);
	}
	
	@Override
	protected void setPosition(double[] position) throws DeviceException {
		sampleXyz.moveTo(position);
	}
	
}
