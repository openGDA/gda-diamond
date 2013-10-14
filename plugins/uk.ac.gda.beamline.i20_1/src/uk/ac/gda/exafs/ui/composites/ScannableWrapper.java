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

package uk.ac.gda.exafs.ui.composites;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableStatus;
import gda.observable.IObserver;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;

import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.UIObservableModel;

public class ScannableWrapper extends UIObservableModel implements IObserver {

	private static final int CHECK_BUSY_STATUS_IN_MS = 50;
	private static final int WAIT_FOR_MSG_UPDATE_IN_MS = 500;
	private final Scannable scannable;

	public static final String POSITION_PROP_NAME = "position";
	public static final String BUSY_PROP_NAME = "busy";

	public static final String TARGET_POSITION_PROP_NAME = "targetPosition";
	private Double targetPosition;

	private PositionChecker scannablePositionChecker;

	public ScannableWrapper(Scannable scannable) {
		this.scannable = scannable;
		this.scannable.addIObserver(this);
	}

	public Scannable getScannable() {
		return scannable;
	}

	public void setPosition(final double position) throws DeviceException {
		if (scannable.isBusy()) {
			throw new DeviceException(scannable.getName() +" motor is busy");
		}
		final Job job = new Job("Moving " + scannable.getName() + " to " + position + ".") {
			@Override
			protected void canceling() {
				try {
					scannable.stop();
					// TODO add timeouts!
					while (scannable.isBusy()) {
						Thread.sleep(CHECK_BUSY_STATUS_IN_MS);
					}
					firePropertyChange(BUSY_PROP_NAME, true, scannable.isBusy());
					firePropertyChange(TARGET_POSITION_PROP_NAME, targetPosition, targetPosition = null);
					firePropertyChange(POSITION_PROP_NAME, null, scannable.getPosition());
				} catch (final Exception e) {
					UIHelper.showError("Error while stopping the motor", e.getMessage());
					firePropertyChange(BUSY_PROP_NAME, true, false);
				}
				super.canceling();
			}

			@Override
			protected IStatus run(IProgressMonitor monitor) {
				IStatus status;
				try {
					firePropertyChange(TARGET_POSITION_PROP_NAME, targetPosition, targetPosition = new Double(position));
					// TODO add progress monitor and timeouts!
					scannable.asynchronousMoveTo(position);
					while (!scannable.isBusy()) {
						Thread.sleep(CHECK_BUSY_STATUS_IN_MS);
					}
					firePropertyChange(BUSY_PROP_NAME, false, scannable.isBusy());
					while (scannable.isBusy()) {
						firePropertyChange(POSITION_PROP_NAME, null, scannable.getPosition());
						Thread.sleep(WAIT_FOR_MSG_UPDATE_IN_MS);
					}
					status = Status.OK_STATUS;
					firePropertyChange(BUSY_PROP_NAME, true, scannable.isBusy());
					firePropertyChange(TARGET_POSITION_PROP_NAME, targetPosition, targetPosition = null);
					firePropertyChange(POSITION_PROP_NAME, null, scannable.getPosition());
				} catch (final Exception e) {
					UIHelper.showError("Error while moving the motor", e.getMessage());
					status = Status.CANCEL_STATUS;
					firePropertyChange(BUSY_PROP_NAME, true, false);
				}
				return status;
			}
		};
		job.schedule();
	}

	public double getPosition() throws DeviceException {
		return Double.parseDouble(scannable.getPosition().toString());
	}

	public Double getTargetPosition() {
		return targetPosition;
	}

	public boolean isBusy() throws DeviceException {
		return scannable.isBusy();
	}

	@Override
	public void update(Object source, Object arg) {
		if (arg instanceof ScannableStatus) {
			ScannableStatus status = (ScannableStatus) arg;
			if (status.getStatus() == ScannableStatus.BUSY) {
				scannablePositionChecker = new PositionChecker();
				Thread t = new Thread(scannablePositionChecker);
				t.start();
			} else {
				if (scannablePositionChecker != null) {
					scannablePositionChecker.stop();
					scannablePositionChecker = null;
				}
			}
		}
	}

	private class PositionChecker implements Runnable {
		private boolean stopped;

		public void stop() {
			stopped = true;
		}

		@Override
		public void run() {
			while (!stopped) {
				try {
					final Object object = scannable.getPosition();
					firePropertyChange(POSITION_PROP_NAME, null, (double) object);
					Thread.sleep(CHECK_BUSY_STATUS_IN_MS);
				} catch (InterruptedException | DeviceException e) {
					break;
				}
			}
		}
	}
}