/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

package gda.device.robot;

	import static gda.device.EnumPositionerStatus.IDLE;
import static gda.device.EnumPositionerStatus.MOVING;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.EnumPositionerStatus;
import gda.device.enumpositioner.EnumPositionerBase;
import uk.ac.diamond.daq.concurrent.Async;
import uk.ac.gda.api.remoting.ServiceInterface;

/**
 * Wrapper to allow SamplePlateMover to be treated like an Enum positioner
 *
 */
@ServiceInterface(EnumPositioner.class)
public class SamplePlateEnumPositioner extends EnumPositionerBase implements EnumPositioner {

	private static final Logger logger = LoggerFactory.getLogger(SamplePlateEnumPositioner.class);
	private String lastMovePosition = "";
	private SamplePlateMover samplePlateMover;

	public SamplePlateEnumPositioner() {
		super();
	}

	@Override
	public void moveTo(Object position) throws DeviceException {
		setStatus(EnumPositionerStatus.MOVING);
		try {
			lastMovePosition = position.toString();
			samplePlateMover.moveTo(position);
		} finally {
			setStatus(EnumPositionerStatus.IDLE);
		}
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		setStatus(MOVING);
		Async.execute(() -> {
			try {
				moveTo(position);
			} catch (DeviceException e) {
				logger.error("Error moving {} to position {}", getName(), position, e);
				setStatus(IDLE);
			}
		});
	}

	@Override
	public String[] getPositions() throws DeviceException {
		// update with latest positions from underlying scannable
		setPositionsInternal(samplePlateMover.getPlateNames());
		return super.getPositions();
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		return samplePlateMover.getCurrentPlate();
	}

	@Override
	public boolean isInPos() throws DeviceException {
		return lastMovePosition.equals(samplePlateMover.getCurrentPlate());
	}

	private void setStatus(EnumPositionerStatus status) {
		if (status != getPositionerStatus()) {
			setPositionerStatus(status);
			notifyIObservers(this, status);
		}
	}

	public SamplePlateMover getSamplePlateMover() {
		return samplePlateMover;
	}

	public void setSamplePlateMover(SamplePlateMover samplePlateMover) {
		this.samplePlateMover = samplePlateMover;
	}
}
