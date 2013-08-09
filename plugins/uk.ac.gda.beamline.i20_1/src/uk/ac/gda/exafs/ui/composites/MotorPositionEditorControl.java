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
import gda.device.ScannableMotionUnits;
import gda.device.scannable.ScannableStatus;
import gda.observable.IObserver;

import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;

import uk.ac.gda.exafs.data.ObservableModel;
import uk.ac.gda.exafs.ui.data.UIHelper;

public class MotorPositionEditorControl extends NumberEditorControl {

	private static final String POSITION_PROP_NAME = "position";
	public MotorPositionEditorControl(Composite parent, int style, Scannable scannable, boolean userSpinner) throws Exception {
		super(parent, style, new ScannableWrapper(scannable), POSITION_PROP_NAME, userSpinner);
		ctx.bindValue(
				BeanProperties.value(MotorPositionWidgetModel.EDITABLE_PROP_NAME).observe(controlModel),
				BeanProperties.value(ScannableWrapper.BUSY_PROP_NAME).observe(object),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return !((boolean) value);
					}
				});
		if (scannable instanceof ScannableMotionUnits) {
			this.setUnit(((ScannableMotionUnits) scannable).getUserUnits());
		}
		this.setCommitOnOutOfFocus(false);
	}

	public void setPosition(double value) throws DeviceException {
		((ScannableWrapper) object).setPosition(value);
	}

	@Override
	protected String getFormattedText(Object value) {
		try {
			if (((ScannableWrapper) object).isBusy()) {
				Double targetPosition = ((ScannableWrapper) object).getTargetPosition();
				if (targetPosition == null) {
					return super.getFormattedText(value);
				}
				if (controlModel.getUnit() == null) {
					return super.getFormattedText(value) + " (Moving to " + targetPosition + ")";
				}
				return super.getFormattedText(value) + " (Moving to " + targetPosition + " " + controlModel.getUnit() + ")";
			}
		} catch (DeviceException e) {
			UIHelper.showError("Error while reading the motor position", e.getMessage());
		}
		return super.getFormattedText(value);
	}


	public static class ScannableWrapper extends ObservableModel implements IObserver {
		private static final int CHECK_BUSY_STATUS_IN_MS = 50;
		private static final int WAIT_FOR_MSG_UPDATE_IN_MS = 500;
		private final Scannable scannable;
		public static final String BUSY_PROP_NAME = "busy";
		private Double targetPosition;
		private PositionChecker scannablePositionChecker;
		public ScannableWrapper(Scannable scannable) {
			this.scannable = scannable;
			this.scannable.addIObserver(this);
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
						targetPosition = null;
						updatePosition();
					} catch (final Exception e) {
						Display.getDefault().asyncExec(new Runnable() {
							@Override
							public void run() {
								UIHelper.showError("Error while stopping the motor", e.getMessage());
							}
						});
						firePropertyChange(BUSY_PROP_NAME, true, false);
					}
					super.canceling();
				}

				@Override
				protected IStatus run(IProgressMonitor monitor) {
					IStatus status;
					try {
						targetPosition = new Double(position);
						// TODO add progress monitor and timeouts!
						scannable.asynchronousMoveTo(position);
						while (!scannable.isBusy()) {
							Thread.sleep(CHECK_BUSY_STATUS_IN_MS);
						}
						firePropertyChange(BUSY_PROP_NAME, false, scannable.isBusy());
						while (scannable.isBusy()) {
							updatePosition();
							Thread.sleep(WAIT_FOR_MSG_UPDATE_IN_MS);
						}
						status = Status.OK_STATUS;
						firePropertyChange(BUSY_PROP_NAME, true, scannable.isBusy());
					} catch (final Exception e) {
						Display.getDefault().asyncExec(new Runnable() {
							@Override
							public void run() {
								UIHelper.showError("Error while moving the motor", e.getMessage());
							}
						});
						status = Status.CANCEL_STATUS;
						firePropertyChange(BUSY_PROP_NAME, true, false);
					}
					targetPosition = null;
					updatePosition();
					return status;
				}

				private void updatePosition() {
					Display.getDefault().asyncExec(new Runnable() {
						@Override
						public void run() {
							try {
								ScannableWrapper.this.firePropertyChange(POSITION_PROP_NAME, null, scannable.getPosition());
							} catch (DeviceException e) {
								UIHelper.showError("Error while reading motor position", e.getMessage());
							}
						}
					});
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
						Display.getDefault().asyncExec(new Runnable() {
							@Override
							public void run() {
								firePropertyChange(POSITION_PROP_NAME, null, (double) object);
							}
						});
						Thread.sleep(50);
					} catch (InterruptedException | DeviceException e) {
						// TODO Handle this
					}
				}
			}
		}
	}
}
