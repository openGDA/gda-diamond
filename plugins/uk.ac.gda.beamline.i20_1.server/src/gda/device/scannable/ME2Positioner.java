/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

import static gda.device.EnumPositionerStatus.IDLE;
import static gda.device.EnumPositionerStatus.MOVING;

import java.util.Arrays;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.EnumPositionerStatus;
import gda.device.enumpositioner.EnumPositionerBase;
import uk.ac.diamond.daq.concurrent.Async;
import uk.ac.gda.api.remoting.ServiceInterface;

@ServiceInterface(EnumPositioner.class)
public class ME2Positioner extends EnumPositionerBase implements EnumPositioner {

	private static final Logger logger = LoggerFactory.getLogger(ME2Positioner.class);
	private EnumPositioner stripeScannable;
	private EnumPositioner yScannable;

	public enum Positions {
		RHODIUM("Rhodium"), SILICON("Silicon"), OUT("Out of beam");

		private final String userName;
		private Positions(String userName) {
			this.userName = userName;
		}

		@Override
		public String toString() {
			return userName;
		}

		public static Positions findByUserName(String userName) {
			for(Positions position : Positions.values()) {
				if (position.userName.equals(userName)) {
					return position;
				}
			}
			return null;
		}
	}

	private enum Me2yPosition {
		IN("In"), OUT("Out");

		private final String userName;
		private Me2yPosition(String userName) {
			this.userName = userName;
		}

		@Override
		public String toString() {
			return userName;
		}
	}

	public ME2Positioner() {
		setPositionsInternal(Arrays.asList(Positions.RHODIUM.toString(),
				Positions.SILICON.toString(), Positions.OUT.toString()));
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		setStatus(MOVING);
		Async.execute(() -> {
			try {
				moveTo(position);
			} catch (DeviceException e) {
				logger.error("Error moving {} to position {}", getName(), position, e);
			} finally {
				setStatus(IDLE);
			}
		});
	}

	@Override
	public void moveTo(Object position) throws DeviceException {
		setStatus(EnumPositionerStatus.MOVING);
		Positions targetPosition = Positions.findByUserName(position.toString());
		if (targetPosition == null) {
			logger.warn("Could not move {} to position {}", getName(), position);
			setStatus(EnumPositionerStatus.IDLE);
			return;
		}

		logger.debug("Moving {} to {}", getName(), targetPosition);
		switch (targetPosition) {
			case RHODIUM:
				stripeScannable.asynchronousMoveTo(Positions.RHODIUM.toString());
				yScannable.asynchronousMoveTo(Me2yPosition.IN.toString());
				break;
			case SILICON:
				stripeScannable.asynchronousMoveTo(Positions.SILICON.toString());
				yScannable.asynchronousMoveTo(Me2yPosition.IN.toString());
				break;
			case OUT:
				yScannable.asynchronousMoveTo(Me2yPosition.OUT.toString());
				break;
		}

		try {
			stripeScannable.waitWhileBusy();
			yScannable.waitWhileBusy();
		} catch (InterruptedException e) {
			Thread.currentThread().interrupt();
			throw new DeviceException(e);
		} finally {
			setStatus(EnumPositionerStatus.IDLE);
		}
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		if (yScannable.getPosition().toString().equals(Me2yPosition.IN.toString())) {
			return stripeScannable.getPosition().toString();
		} else if (yScannable.getPosition().toString().equals(Me2yPosition.OUT.toString())) {
			return Positions.OUT.toString();
		}
		return "unknown";
	}

	private void setStatus(EnumPositionerStatus status) {
		if (status != getPositionerStatus()) {
			setPositionerStatus(status);
			notifyIObservers(this, status);
		}
	}

	public EnumPositioner getStripeScannable() {
		return stripeScannable;
	}

	public void setStripeScannable(EnumPositioner stripeScannable) {
		this.stripeScannable = stripeScannable;
	}

	public EnumPositioner getyScannable() {
		return yScannable;
	}

	public void setyScannable(EnumPositioner yScannable) {
		this.yScannable = yScannable;
	}
}
