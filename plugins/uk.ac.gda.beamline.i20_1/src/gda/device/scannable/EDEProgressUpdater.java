/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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
import gda.jython.IScanDataPointObserver;
import gda.jython.IScanDataPointProvider;
import gda.jython.InterfaceProvider;
import gda.jython.scriptcontroller.logging.LoggingScriptController;
import gda.scan.ScanDataPoint;

import java.util.concurrent.TimeUnit;

import uk.ac.gda.exafs.data.EDEScanLoggingMessage;

/**
 * A zero input, zero extra names Scannable which should be included in XAS scans to send progress messages to the
 * LogginScriptController.
 */
public class EDEProgressUpdater extends ScannableBase implements Scannable, IScanDataPointObserver {

	private transient final LoggingScriptController controller;
	private final String id;
	private final String scriptName;
	private long timeStarted;
	private String lastPercentComplete = "0%";

	public EDEProgressUpdater(LoggingScriptController controller, EDEScanLoggingMessage msg) {
		this.controller = controller;
		this.id = msg.getUniqueID();
		this.scriptName = msg.getName();
		this.setInputNames(new String[] {});
		this.setExtraNames(new String[] {});
		this.setOutputFormat(new String[] {});
		this.setName("EDE Progress Updater");

	}

	@Override
	public String toFormattedString() {
		return getName();
	}

	@Override
	public String toString() {
		return toFormattedString();
	}

	@Override
	public void atScanStart() throws DeviceException {
		InterfaceProvider.getScanDataPointProvider().addIScanDataPointObserver(this);
		timeStarted = System.currentTimeMillis();
	}

	@Override
	public void atScanEnd() throws DeviceException {
		InterfaceProvider.getScanDataPointProvider().deleteIScanDataPointObserver(this);
		EDEScanLoggingMessage msg = new EDEScanLoggingMessage(id, scriptName, "complete", "100%", getElapsedTime());
		controller.update(this, msg);
	}

	@Override
	public void atCommandFailure() throws DeviceException {
		InterfaceProvider.getScanDataPointProvider().deleteIScanDataPointObserver(this);
		EDEScanLoggingMessage msg = new EDEScanLoggingMessage(id, scriptName, "scan aborted", lastPercentComplete,
				getElapsedTime());
		controller.update(this, msg);
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		return null;
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		// do nothing
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	@Override
	public void update(Object source, Object arg) {
		if (source instanceof IScanDataPointProvider && arg instanceof ScanDataPoint) {
			ScanDataPoint sdp = (ScanDataPoint) arg;
			int currentPoint = sdp.getCurrentPointNumber() + 1;
			int totalPoints = sdp.getNumberOfPoints();
			int percentComplete = (int) Math.round((currentPoint * 100.0) / totalPoints);
			lastPercentComplete = percentComplete + "%";

			EDEScanLoggingMessage msg = new EDEScanLoggingMessage(id, scriptName, "in progress", percentComplete + "%",
					getElapsedTime());
			controller.update(this, msg);
		}
	}

	private String getElapsedTime() {
		long now = System.currentTimeMillis();
		long duration = now - timeStarted;
		long hours = TimeUnit.MILLISECONDS.toHours(duration);
		long minutes = TimeUnit.MILLISECONDS.toMinutes(duration) - TimeUnit.HOURS.toMinutes(hours);
		long seconds = TimeUnit.MILLISECONDS.toSeconds(duration) - TimeUnit.HOURS.toSeconds(hours)
				- TimeUnit.MINUTES.toSeconds(minutes);
		String diff = String.format("%dh%dm%ds", hours, minutes, seconds);
		return diff;
	}

}
