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

package uk.ac.gda.server.exafs.scan.preparers;

import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.StringUtils;

import gda.device.Scannable;
import gda.factory.FindableBase;
import gda.jython.InterfaceProvider;
import gda.scan.ConcurrentScan;
import gda.scan.DataPointCache;
import gda.scan.ScanDataPointCache;
import uk.ac.diamond.scisoft.analysis.fitting.functions.Gaussian;
import uk.ac.gda.beamline.i20.scannable.CurveFitting;

/**
 * Class to run a step scan using, perform a peak fit and then move the scannable
 * to the peak energy. Data is from the scan is cached using a DataPointCache object, to avoid needing to read from hdf file.
 *
 * <li> Scan range used is relative to a centre position (centrePosition+relativeStart to centrePosition+relativeEnd).
 * <li> Detectors used during scan are set the detectorArgs list. Typically a detector object followed by a collection time.
 * <li> Curve fit is done using a Gaussian profile (using the {@link CurveFitting} class).
 *
 */
public class CurveFitScanRunner extends FindableBase {
	private static final Logger logger = LoggerFactory.getLogger(CurveFitScanRunner.class);

	/** Scannable to be moved during scan*/
	private Scannable scannableToMove;

	/** Detector args to be used for the scan command (e.g. [detectorScannable, collection time] */
	private List<Object> detectorArgs;

	/** Name of data (from detector) to be fitted */
	private String fitDataName;

	/** Start position of scan relative to centre */
	private double relativeStart;

	/** End position of scan relative to centre */
	private double relativeEnd;

	/** Scan step size */
	private double stepSize;

	private CurveFitting curveFitter = new CurveFitting();
	private DataPointCache dataCache;

	/**
	 * Run a scan at centrePosition using {@link #runScan(double)}, find the peak value using {@link #fitData()},
	 * then move the scannable to the peak position
	 * @param centrePosition
	 * @throws Exception
	 */
	public void runAndMove(double centrePosition) throws Exception {
		// Run scan and find the peak
		runScan(centrePosition);
		Gaussian fitParams = fitData();

		// Move xes energy scannable to peak position
		double peakPosition = fitParams.getPosition();
		if (peakPosition > centrePosition+relativeStart && peakPosition < centrePosition+relativeEnd) {
			scannableToMove.moveTo(peakPosition);
		} else {
			logger.warn("Fitted peak value {} is out of range of original scan! Not moving {} to fitted peak position.",peakPosition, scannableToMove.getName());
		}
	}

	/**
	 * Run scan :
	 * <li> range is from centreEnergy+relativeStart to centreEnergy+relateiveEnd using steps of 'stepSize'
	 * <li> The detectorArgs list are appended to the step parameters to get the complete scan command
	 *
	 * @param centrePosition
	 * @throws Exception
	 */
	public void runScan(double centrePosition) throws Exception {
		runScan(centrePosition+relativeStart, centrePosition+relativeEnd, stepSize);
	}

	/**
	 * Run a step scan across the specified range and cache the values
	 * @param start
	 * @param stop
	 * @param step
	 * @throws InterruptedException
	 * @throws Exception
	 */
	private void runScan(double start, double stop, double step) throws InterruptedException, Exception {
		try {
			setupDatapointCache();

			// Setup scan args list
			List<Object> argList = new ArrayList<>();
			argList.addAll(List.of(scannableToMove, start, stop, step));
			argList.addAll(detectorArgs);

			ConcurrentScan scan = new ConcurrentScan(argList.toArray());
			scan.setSendUpdateEvents(true);

			scan.runScan();
		} finally {
			disconnectCache(); // so we don't cache data from other scans
		}
	}

	/**
	 * Perform Gaussian fit to the currently cached data
	 * <li> Name of scannableToMove is the name of the x values.
	 * <li> fitDataName parameter gives name of the y values to be fitted. If this is not set, then name of the first detector in detectorArgs is used.
	 *
	 * @return {@link Gaussian} object containing fitted parameters (fitted centre position, FWHM, area)
	 */
	public Gaussian fitData() {
		// Try to determine name of the data to be fitted if it has not been specified.
		String dataToFit = fitDataName;
		if (!StringUtils.hasLength(dataToFit)) {
			dataToFit = detectorArgs.stream()
					.filter(Scannable.class::isInstance)
					.map(Scannable.class::cast)
					.map(Scannable::getName)
					.findFirst()
					.orElseThrow(() -> new IllegalArgumentException("Could not detectormine name of data to be fitted"));

			logger.warn("Name of detector data to fit has not been set - using name of detector as data name ({})", dataToFit);
		}
		// Extract the data from the DataPointCache and run the peak fitting
		List<Double> energyPoints = dataCache.getPositionsFor(scannableToMove.getName());
		List<Double> detPoints = dataCache.getPositionsFor(dataToFit);
		return curveFitter.findPeakOutput(energyPoints.toArray(), detPoints.toArray());
	}

	/**
	 * Make a new cache to store the scan data
	 */
	private void setupDatapointCache() {
		dataCache = new ScanDataPointCache();
		dataCache.configure();
	}

	/**
	 * De-register the data cache - so we don't record data for other scans.
	 */
	private void disconnectCache() {
		if (dataCache != null) {
			InterfaceProvider.getScanDataPointProvider().deleteIScanDataPointObserver(dataCache);
		}
	}

	public Scannable getScannableToMove() {
		return scannableToMove;
	}

	public void setScannableToMove(Scannable xesEnergyScannable) {
		this.scannableToMove = xesEnergyScannable;
	}

	public List<Object> getDetectorArgs() {
		return detectorArgs;
	}

	public void setDetectorArgs(List<Object> detectorList) {
		this.detectorArgs = new ArrayList<>(detectorList);
	}

	public void setFitDataName(String name) {
		fitDataName = name;
	}

	public String getFitDataName() {
		return fitDataName;
	}

	public double getRelativeStart() {
		return relativeStart;
	}

	public void setRelativeStart(double relativeStart) {
		this.relativeStart = relativeStart;
	}

	public double getRelativeEnd() {
		return relativeEnd;
	}

	public void setRelativeEnd(double relativeEnd) {
		this.relativeEnd = relativeEnd;
	}

	public double getStepSize() {
		return stepSize;
	}

	public void setStepSize(double stepSize) {
		this.stepSize = stepSize;
	}

	public CurveFitting getCurveFitter() {
		return curveFitter;
	}
}
