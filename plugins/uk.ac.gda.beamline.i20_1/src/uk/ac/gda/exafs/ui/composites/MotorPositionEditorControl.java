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
		ctx.bindValue(BeanProperties.value(MotorPositionWidgetModel.EDITABLE_PROP_NAME).observe(controlModel), BeanProperties.value(ScannableWrapper.BUSY_PROP_NAME).observe(object));
		this.setCommitOnOutOfFocus(false);
	}

	@Override
	protected String getFormattedText(Object value) {
		try {
			if (((ScannableWrapper) object).isBusy()) {
				String targetPositionMessage = ((ScannableWrapper) object).getTargetPositionMessage();
				if (controlModel.getUnit() == null) {
					return super.getFormattedText(value) + " (Moving to " + targetPositionMessage + ")";
				}
				return super.getFormattedText(value) + " (Moving to " + targetPositionMessage + " " + controlModel.getUnit() + ")";
			}
		} catch (DeviceException e) {
			UIHelper.showError("Error while reading the motor position", e.getMessage());
		}
		return super.getFormattedText(value);
	}


	public static class ScannableWrapper extends ObservableModel {
		private static final int CHECK_BUSY_STATUS_IN_MS = 50;
		private static final int WAIT_FOR_MSG_UPDATE_IN_MS = 500;
		private final Scannable scannable;
		public static final String BUSY_PROP_NAME = "busy";
		private String targetPositionMessage;
		public ScannableWrapper(Scannable scannable) {
			this.scannable = scannable;
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
						targetPositionMessage = Double.toString(position);
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
			job.setUser(true);
			job.schedule();
		}

		public double getPosition() throws DeviceException {
			return Double.parseDouble(scannable.getPosition().toString());
		}

		public String getTargetPositionMessage() {
			return targetPositionMessage;
		}

		public boolean isBusy() throws DeviceException {
			return scannable.isBusy();
		}
	}
}
