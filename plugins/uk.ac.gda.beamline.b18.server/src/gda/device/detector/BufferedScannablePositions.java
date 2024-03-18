/*-
 * Copyright © 2024 Diamond Light Source Ltd.
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

package gda.device.detector;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.ContinuousParameters;
import gda.device.DeviceException;
import gda.device.Scannable;

/**
 * This BufferedDetector implementation can be used in a ContinuousScan to record scannable positions
 * at regularly spaced time intervals. The motivation for this class is that the positions of
 * 'extra scannables' added to ContinuousScan are only grabbed when the data is written
 * rather than at the same time as the detector measurements. This class can be used to ensure that
 * scannable positions are measured at *same* time as the detector measurements for time-based continuous scans.
 *
 * <li> At the start of the scan (in {@link #setContinuousMode}) a executor service is created that
 * stores the current position of a scannable in a list.
 * <li> The execution frequency/update interval is set by the time per point for the scan - i.e. from the
 * total time and number of points in the continuous parameters.
 *
 * 11/1/2024
 */
public class BufferedScannablePositions extends DetectorBase implements BufferedDetector {
	private static final Logger logger = LoggerFactory.getLogger(BufferedScannablePositions.class);

	private ContinuousParameters parameters;

	/** Set of scannable position values recorded during scan */
	private List<Object> readoutValues = Collections.emptyList();

	private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
	private ScheduledFuture<?> updateFuture;

	/** The scannable whose position will be recorded */
	private Scannable scannable;

	@Override
	public void collectData() throws DeviceException {
	}

	private void startUpdater() {
		stopUpdater(); // stop any previously running updater
		logger.info("Starting 'collect data' scheduler to store data from {} every {} sec", scannable.getName(), collectionTime);
		readoutValues = new ArrayList<>();
		updateFuture = scheduler.scheduleAtFixedRate(this::storeCurrentPosition, 0, (long)(1000*collectionTime), TimeUnit.MILLISECONDS);
	}

	@Override
	public void atScanEnd() {
		stopUpdater();
	}

	@Override
	public void atScanStart() {
		stopUpdater();
	}

	private void stopUpdater() {
		if (updateFuture != null) {
			logger.info("Stopping 'collect data' scheduler");
			updateFuture.cancel(true);
		}
	}

	private void storeCurrentPosition() {
		try {
			readoutValues.add(scannable.getPosition());
			logger.debug("Stored value from {} ({} values stored so far)", scannable.getName(), readoutValues.size());
		} catch (DeviceException e) {
			logger.error("Problem storing position value for {}", scannable.getName(), e);
		}
	}

	@Override
	public int getStatus() throws DeviceException {
		return 0;
	}

	@Override
	public Object readout() throws DeviceException {
		int lastItem = readoutValues.size()-1;
		if (lastItem >= 0) {
			return readoutValues.get(lastItem);
		}
		return scannable.getPosition();
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {
		return false;
	}

	@Override
	public void clearMemory() throws DeviceException {
	}

	@Override
	public void setContinuousMode(boolean on) throws DeviceException {
		if (on) {
			startUpdater();
		} else {
			stopUpdater();
		}
	}

	@Override
	public boolean isContinuousMode() throws DeviceException {
		return false;
	}

	@Override
	public void setContinuousParameters(ContinuousParameters parameters) throws DeviceException {
		collectionTime = parameters.getTotalTime()/parameters.getNumberDataPoints();
		logger.info("Setting collection time to {} sec using ContinuousParameters", collectionTime);
		this.parameters = parameters;
	}


	@Override
	public ContinuousParameters getContinuousParameters() throws DeviceException {
		return parameters;
	}

	@Override
	public int getNumberFrames() throws DeviceException {
		return readoutValues.size();
	}

	@Override
	public Object[] readFrames(int startFrame, int finalFrame) throws DeviceException {
		return readoutValues.subList(startFrame, finalFrame+1).toArray();
	}

	@Override
	public Object[] readAllFrames() throws DeviceException {
		return readoutValues.toArray();
	}

	@Override
	public int maximumReadFrames() throws DeviceException {
		return 100;
	}

	public Scannable getScannable() {
		return scannable;
	}

	public void setScannable(Scannable scannable) {
		this.scannable = scannable;
	}

	@Override
	public String[] getOutputFormat() {
		return scannable.getOutputFormat();
	}

	@Override
	public String[] getExtraNames() {
		return scannable.getExtraNames();
	}
}
