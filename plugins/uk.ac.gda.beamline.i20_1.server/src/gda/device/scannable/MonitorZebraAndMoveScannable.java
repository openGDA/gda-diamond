/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

import java.util.Map.Entry;
import java.util.SortedMap;
import java.util.TreeMap;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.zebra.controller.Zebra;
import gda.jython.InterfaceProvider;
import uk.ac.diamond.daq.concurrent.Async;

/**
 * Class that monitors the number of captured pulses on Zebra and moves a scannable to positions after
 * certain numbers of spectra have been captured.
 * <li> Set the scannable to be moved using {@link #setScannableToMove(Scannable)}.</li>
 * <li> Add position to move scannable to at end of a spectrum using {@link #addPositionForSpectrum(Integer, Object)}.</li>
 * <p>
 * The spectrum number - position Map is maintained in order of ascending spectrum number and has
 * one position per spectrum. (i.e. adding a new position with same spectrum number as already in the
 * map will overwrite it).
 *
 */
public class MonitorZebraAndMoveScannable extends ScannableBase {
	private static final Logger logger = LoggerFactory.getLogger(MonitorZebraAndMoveScannable.class);

	private Zebra zebra;
	private volatile boolean isRunning = false;
	private Scannable scannableToMove;

	/** Map of position to move scannable to at end of each spectra (key = spectrum number, value = position)*/
	private SortedMap<Integer, Object> positionForSpectrumMap = new TreeMap<>();
	private int numReadoutsPerSpectrum = 0;
	private int timeOutSeconds = 120;

	public MonitorZebraAndMoveScannable() {
		inputNames = new String[] {};
		extraNames = new String[] {};
		outputFormat = new String[] {};
	}

	@Override
	public void atScanLineStart() {
		Async.execute(this::startRunning);
	}

	public void setNumReadoutsPerSpectrum(int numReadoutsPerSpectrum) {
		this.numReadoutsPerSpectrum = numReadoutsPerSpectrum;
	}

	/**
	 * Loop over positionForSpectrumMap and for each entry wait for required number of spectra (pulses)
	   to be captured on Zebra, then move the scannable to the requested position.
	 */
	public void startRunning() {
		if (zebra == null) {
			logger.warn("Zebra has not been set - startRunning cannot continue");
			return;
		}

		if (scannableToMove == null) {
			logger.warn("ScannableToMove has not been set - startRunning cannot continue");
			return;
		}

		if (isRunning) {
			logger.info("startRunning cannot be run again - it is already running!");
			return;
		}

		try {
			isRunning = true;

			// Wait for zebra to arm before starting (this also clears number of captured points from the last run).
			while(!zebra.isPCArmed()) {
				logger.debug("Waiting for zebra to arm...");
				Thread.sleep(500);
			}

			int readoutsPerSpectrum = numReadoutsPerSpectrum;
			if (readoutsPerSpectrum == 0) {
				logger.info("Number of readouts per spectrum has not been set - using 'max pulses' from Zebra pulse settings.");
				readoutsPerSpectrum = zebra.getPCPulseMax();
			}

			// For each entry in positionForSpectrumMap, wait for required number of spectra (pulses)
			// to be captured on Zebra, then move the scannable to the requested position.
			logger.info("Number of readouts per spectrum : {}", readoutsPerSpectrum);
			for( Entry<Integer, Object> entry : positionForSpectrumMap.entrySet()) {
				int numSpectra = entry.getKey();
				int numPulsesToWaitFor = readoutsPerSpectrum*numSpectra;

				// Wait for number of captured pulses to be reached
				logger.info("Waiting for {} pulses ({} spectra) on Zebra", numPulsesToWaitFor, numSpectra);
				zebra.getNumberOfPointsCapturedPV().waitForValue( value -> value>=numPulsesToWaitFor, timeOutSeconds); //listener only get update every ~1sec

				// Move the scannable to new position (block until finished)
				Object position = entry.getValue();
				logger.info("{} pulses captured by Zebra, moving {} to {} after spectrum {}", numPulsesToWaitFor, scannableToMove.getName(), position, numSpectra);
				InterfaceProvider.getTerminalPrinter().print("Moving "+scannableToMove.getName()+" to "+position+" after spectrum "+numSpectra);
				scannableToMove.moveTo(position);
			}
		} catch(InterruptedException e) {
			// An interrupt means the scan wishes to abort, the thread should be
			// re-interrupted so the scanning engine aborts smoothly.
			// See: https://alfred.diamond.ac.uk/documentation/manuals/GDA_Developer_Guide/master/java_development.html#handling-interrupts
			logger.info("Thread waiting for Zebra pulses", e);
			Thread.currentThread().interrupt();
		} catch (Exception e) {
			logger.error("Problem waiting for Zebra pulses", e);
		} finally {
			isRunning = false;
			logger.info("Finished waiting for Zebra pulses");
		}
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return isRunning;
	}

	public Scannable getScannableToMove() {
		return scannableToMove;
	}

	public void setScannableToMove(Scannable scannableToMove) {
		this.scannableToMove = scannableToMove;
	}

	public SortedMap<Integer, Object> getPositionForSpectrumMap() {
		return positionForSpectrumMap;
	}

	public void setPositionForSpectrumMap(SortedMap<Integer, Object> positionForSpectrumMap) {
		if (positionForSpectrumMap != null) {
			this.positionForSpectrumMap.clear();
			this.positionForSpectrumMap.putAll(positionForSpectrumMap);
		}
	}

	/**
	 * Add a position to be moved to at end of a spectrum.
	 * @param spectrum
	 * @param position
	 */
	public void addPositionForSpectrum(Integer spectrum, Object position) {
		positionForSpectrumMap.put(spectrum, position);
	}

	public Zebra getZebra() {
		return zebra;
	}

	public void setZebra(Zebra zebra) {
		this.zebra = zebra;
	}

	public int getTimeOutSeconds() {
		return timeOutSeconds;
	}

	public void setTimeOutSeconds(int timeOutSeconds) {
		this.timeOutSeconds = timeOutSeconds;
	}
}
