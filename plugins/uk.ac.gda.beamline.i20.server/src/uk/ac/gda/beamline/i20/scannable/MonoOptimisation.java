/*-
 * Copyright © 2016 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i20.scannable;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.dawnsci.analysis.api.tree.GroupNode;
import org.eclipse.dawnsci.hdf5.nexus.NexusFileHDF5;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.dawnsci.nexus.NexusFile;
import org.eclipse.january.DatasetException;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.IDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.Scannable;
import gda.device.detector.DAServer;
import gda.device.detector.DetectorBase;
import gda.device.detector.countertimer.TFGCounterTimer;
import gda.device.detector.countertimer.TfgScalerWithDarkCurrent;
import gda.device.enumpositioner.ValvePosition;
import gda.device.scannable.ScannableUtils;
import gda.factory.FindableBase;
import gda.jython.InterfaceProvider;
import gda.scan.ConcurrentScan;
import gda.scan.ScanPlotSettings;
import uk.ac.diamond.scisoft.analysis.fitting.Fitter;
import uk.ac.diamond.scisoft.analysis.fitting.functions.Gaussian;


/**
 * Functions to perform optimisation of monochromator, i.e. adjust bragg offset to maximise throughput
 *
 * @since 26/8/2016
 */
public class MonoOptimisation extends FindableBase {

	private static final Logger logger = LoggerFactory.getLogger(MonoOptimisation.class);
	private static int maxGoldenSectionIterations = 30;

	/** Scannable to be monitored during optimisation scans e.g. ionchamber, or a ScannableGaussian (for testing) */
	private Scannable scannableToMonitor;

	/** Scannable to be moved during optimisation scans e.g. braggOffset */
	private Scannable scannableToMove;

	/** Scannable for the bragg motor that adjusts the monochromator energy */
	private Scannable braggScannable;

	// Parameters controlling range and number of steps used for offset optimisation scan
	private double offsetStart, offsetEnd;
	private int offsetNumPoints;
	private double collectionTime; // used for detectors

	private Gaussian fittedGaussianLowEnergy, fittedGaussianHighEnergy;
	private double lowEnergy, highEnergy;

	/** If true, then curve fitting during optimisation will use a small number of points either side of peak detector value*/
	private boolean fitToPeakPointsOnly;
	/** Number of points either side of peak detector value to use when fitting*/
	private int peakPointRange;

	/** If true, then new scans from optimisation will be selected automatically when they are added to the plot view*/
	private boolean selectNewScansInPlotView;

	private boolean allowOptimisation;

	private Double tfgDarkCurrentCollectionTime;
	private boolean tfgDarkCurrentRequired;

	private EnumPositioner photonShutter;

	public MonoOptimisation(Scannable scannableToMove, Scannable scannableToMonitor) {
		collectionTime = 1.0;
		offsetStart = -10;
		offsetEnd = 10;
		offsetNumPoints = 20;
		allowOptimisation = true;
		this.scannableToMove = scannableToMove;
		this.scannableToMonitor = scannableToMonitor;

		fitToPeakPointsOnly = false;
		peakPointRange = 4;

		selectNewScansInPlotView = true;
		setName(scannableToMove.getName()+"Optimiser");
	}

	public void optimise(double lowEnergy, double highEnergy) throws Exception {
		if (Math.abs(lowEnergy - highEnergy)<1e-3) {
			optimise(braggScannable, lowEnergy);
		} else {
			optimise(braggScannable, lowEnergy, highEnergy);
		}
	}

	private void optimise(Scannable bragg, double lowEnergy) throws Exception {
		if (!allowOptimisation) {
			logger.info("allowOptimisation flag set to false - skipping optimisation.");
			return;
		}

		logger.info("Running optimisation for single energy "+lowEnergy);
		Object initialPos = bragg.getPosition();

		fittedGaussianLowEnergy = runAndFitOffsetScan(bragg, lowEnergy);
		this.lowEnergy = lowEnergy;
		this.highEnergy = lowEnergy;

		moveEnergyScannable(bragg, initialPos);

		// Try to setup the offset parameters for the scannable
		if ( bragg instanceof MonoMoveWithOffsetScannable ) {
			configureOffsetParameters((MonoMoveWithOffsetScannable) bragg);
		}
	}

	/**
	 * Do scans of {scannableToMove} with {scannableToMonitor} as the detector and perform gaussian fits to the
	 * 1-dimensional profile. Do this twice, at lowEnergy and highEnergy positions of {bragg} scannable.
	 * Gaussian fit parameters are stored and used by {@link #configureOffsetParameters(MonoMoveWithOffsetScannable)} to configure offset parameters.
	 * @param bragg
	 * @param lowEnergy
	 * @param highEnergy
	 * @throws Exception
	 */
	private void optimise(Scannable bragg, double lowEnergy, double highEnergy) throws Exception {
		if (!allowOptimisation) {
			logger.info("allowOptimisation flag set to false - skipping optimisation.");
			return;
		}

		logger.info("Running optimisation for energies "+lowEnergy+" and "+highEnergy);
		Object initialPos = bragg.getPosition();

		fittedGaussianHighEnergy = runAndFitOffsetScan(bragg, highEnergy);
		this.highEnergy = highEnergy;

		fittedGaussianLowEnergy = runAndFitOffsetScan(bragg, lowEnergy);
		this.lowEnergy = lowEnergy;

		moveEnergyScannable(bragg, initialPos);

		// Try to setup the offset parameters for the scannable
		if ( bragg instanceof MonoMoveWithOffsetScannable ) {
			configureOffsetParameters((MonoMoveWithOffsetScannable) bragg);
		}
	}

	/**
	 * Move bragg scannable to given energy, run offset scan and find best fit parameters for the profile.
	 * @param bragg
	 * @param energy
	 * @return Gaussian best fit parameters.
	 * @throws Exception
	 */
	private Gaussian runAndFitOffsetScan(Scannable bragg, double energy) throws Exception {
		moveEnergyScannable(bragg, energy);
		String filename = runOffsetScan();
		Dataset data = loadDataFromNexusFile(filename);
		return findPeakOutput(data);
	}

	/**
	 * Move energy scannable. If a {@link MonoMoveWithOffsetScannable} scannable is passed in,
	 * move just the bragg motor to avoid also changing the offset.
	 * @param braggScannable
	 * @param energy
	 * @throws DeviceException
	 */
	private void moveEnergyScannable(Scannable energyScannable, Object energy) throws DeviceException {
		if (energyScannable instanceof MonoMoveWithOffsetScannable) {
			((MonoMoveWithOffsetScannable) energyScannable).getBragg().moveTo(energy);
		} else {
			energyScannable.moveTo(energy);
		}
	}

	private DAServer daServerForTfg;
	public void setDaServer(DAServer daServerForTfg) {
		this.daServerForTfg = daServerForTfg;
	}

	public DAServer getDaServer() {
		return daServerForTfg;
	}

	/** Normal output on Veto 0 */
	private static String NORMAL_VETO_OUTPUT_COMMAND = "tfg alternate-veto veto0-normal";
	/** No output on Veto0 : 'Veto0 is given by DC level from veto0-inv-bit' (not set, never used in scan -> no veto signal!) */
	private static String NO_VETO_OUTPUT_COMMAND = "tfg alternate-veto veto0-dc";

	/**
	 * Send DAServer commands to switch between normal and no veto output
	 * (Veto output is used for for triggering detectors such as Xspress2, XMap, Medipix)
	 * {@link #NORMAL_VETO_OUTPUT_COMMAND}, {@link #NO_VETO_OUTPUT_COMMAND} are the commands sent
	 * to DAServer to switch Veto output on and off.
	 * @param vetoOn true = veto output, false no veto output
	 */
	public void setProduceVetoOutput(boolean vetoOn) {
		if (daServerForTfg==null) {
			return;
		}

		Object ret = null;
		String command = "";
		try {
			command = vetoOn ? NORMAL_VETO_OUTPUT_COMMAND : NO_VETO_OUTPUT_COMMAND;
			ret = daServerForTfg.sendCommand(command);
		} catch (DeviceException e) {
			logger.error("Problem setting veto output to {} using command '{}'. DAServer returned {}", vetoOn, command,	ret);
		}
	}

	public void optimiseManual(Scannable bragg, double braggEnergy) throws DeviceException {
		if (allowOptimisation==false) {
			logger.info("allowOptimisation flag set to false - skipping optimisation.");
			return;
		}

		logger.info("Running manual optimisation for single energy {}", braggEnergy);

		if ( scannableToMonitor instanceof TFGCounterTimer) {
			((TFGCounterTimer) scannableToMonitor).clearFrameSets();
			((TFGCounterTimer) scannableToMonitor).setCollectionTime(collectionTime);
			// maybe set the frame times here as well ( with .setTimes( [collectionTime, collectionTime, ...] );
		}

		// Switch off Veto output trigger signal, so medipix, xspress detectors are not triggered by the offset scan
		setProduceVetoOutput(false);

		Dataset combinedData = doManualScan();
		fittedGaussianLowEnergy = findPeakOutput(combinedData);
		this.lowEnergy = braggEnergy;
		this.highEnergy = braggEnergy;

		// Try to setup the offset parameters for the scannable
		if ( bragg instanceof MonoMoveWithOffsetScannable ) {
			configureOffsetParameters((MonoMoveWithOffsetScannable) bragg);
		}

		// Switch veto output back on
		setProduceVetoOutput(true);
	}

	/**
	 * Return List of scan params for a braggoffset optimisation scan, suitable for passing to ConcurrentScan
	 * @return scan parameters list
	 * @throws Exception
	 */
	private List<Object> getScanParamsList() throws Exception {
		String message = "";
		if ( scannableToMove == null ) {
			message = "Scannable to move has not been set. ";
		}
		if ( scannableToMonitor == null ) {
			message += "Scannable to monitor has not been set. ";
		}
		if ( !message.isEmpty() ) {
			message += "Cannot do optimisation scan!";
			logger.warn(message);
			throw new Exception(message);
		}

		double offsetStepsize = (offsetEnd - offsetStart)/(offsetNumPoints -1);

		Object []scanParamsBaseList = new Object[] {scannableToMove, offsetStart, offsetEnd, offsetStepsize, scannableToMonitor};
		List<Object> scanParamsList = new ArrayList<Object>();

		for( Object param : scanParamsBaseList ) {
			scanParamsList.add(param);
		}

		if ( scannableToMonitor instanceof DetectorBase ) {
			scanParamsList.add(collectionTime);
		}
		return scanParamsList;
	}

	/**
	 * Do a scan of the bragg offset, record detector output
	 * @return return filename of nxs file produced
	 * @throws Exception
	 */
	private String runOffsetScan() throws Exception {

		if ( scannableToMonitor instanceof TFGCounterTimer) {
			((TFGCounterTimer) scannableToMonitor).clearFrameSets();
			// maybe set the frame times here as well ( with .setTimes( [collectionTime, collectionTime, ...] );
		}
		saveTfgSettings();
		if (scannableToMonitor instanceof TfgScalerWithDarkCurrent) {
			((TfgScalerWithDarkCurrent)scannableToMonitor).setDarkCurrentRequired(false);
		}

		// Try to open shutter before starting the scan
		moveShutter(ValvePosition.OPEN);

		ConcurrentScan scan = new ConcurrentScan(getScanParamsList().toArray());
		scan.setSendUpdateEvents(true);

		// Adjust plot settings so that new data is not automatically selected for plotting in Scan Plot view
		if ( !selectNewScansInPlotView ) {
			ScanPlotSettings scanPlotSettings = new ScanPlotSettings();
			scanPlotSettings.setYAxesShown(new String[] {});
			scan.setScanPlotSettings(scanPlotSettings);
		}

		scan.runScan();

		// wait here until finished
		scan.waitForDetectorReadoutAndPublishCompletion();

		applySavedTfgSettings();

		return scan.getDataWriter().getCurrentFileName();
	}

	/**
	 * Load a dataset from Nexus a file
	 * @param filename
	 * @param dataGroupPath - full path to the data group
	 * @return IDataset first dataset from the data group.
	 * @throws NexusException
	 * @throws DatasetException
	 */
	private IDataset getDataFromFile(String filename, String dataGroupPath) throws NexusException, DatasetException {
		try(NexusFile file = NexusFileHDF5.openNexusFileReadOnly(filename)) {
			GroupNode groupNode = file.getGroup(dataGroupPath,false);

			// Return first dataset from data group
			String nodeName = groupNode.getNodeNameIterator().next();
			return groupNode.getDataNode(nodeName).getDataset().getSlice(null, null, null).squeeze();
		}
	}

	/**
	 * Load optimisation scan data from nexus file. Combine position and detector values into a single Dataset..
	 * @param filename
	 * @return Dataset with position data in 1st column, detector data in 2nd.
	 * @throws NexusException
	 * @throws DatasetException
	 */
	public Dataset loadDataFromNexusFile(String filename) throws NexusException, DatasetException {
		// Y values (ionchambers or other scannable)
		Dataset detectorData = (Dataset) getDataFromFile(filename, "/entry1/instrument/"+scannableToMonitor.getName());

		// X values (bragg offset motor)
		Dataset positionData = (Dataset) getDataFromFile(filename, "/entry1/instrument/"+scannableToMove.getName());

		int numRows = detectorData.getSize();
		Dataset combinedData = DatasetFactory.zeros(detectorData.getSize(), 2); //  DatasetFactory.create(detectorData.getSize(), 2);
		for(int i = 0; i<numRows; i++) {
			combinedData.set(positionData.getObject(i), i, 0);
			combinedData.set(detectorData.getObject(i), i, 1);
		}

		return combinedData;
	}

	/**
	 * Extract dataset containing values near to the peak value in column of dataset
	 * @param dataFromFile
	 * @Param peakRange number of rows either side of peak in column 2 to extract
	 * @return Dataset with several rows of data near peak detector value
	 */
	private Dataset extractDataNearPeak(Dataset dataFromFile, int peakRange) {
		int maxPosIndex = dataFromFile.maxPos()[0]; // this array seems backwards, why is max index for column 2 not in index 0?
		int numDatapoints = dataFromFile.getShape()[0];
		int numColumns = dataFromFile.getShape()[1];
		int startIndex = Math.max(maxPosIndex - peakRange, 0);

		int endIndex = Math.min(maxPosIndex + peakRange+1, numDatapoints);
		return dataFromFile.getSlice(new int[] {startIndex, 0}, new int[]{endIndex, numColumns}, null).squeeze();
	}

	private Dataset getColumnFromDataSet(Dataset dataset, int columnIndex) {
		int numRows = dataset.getShape()[0];
		return dataset.getSlice(new int[]{0, columnIndex}, new int[]{numRows, columnIndex+1}, null).squeeze();
	}

	/**
	 * Find peak position in x, y profile by fitting a Gaussian to it
	 * @param dataToFit (column 0 = x values, column 1 = y values)
	 * @return Gaussian object of 'best fit' parameters
	 */
	public Gaussian findPeakOutput(Dataset dataToFit) {

		logger.debug("Attempting to fit Gaussian to data.");

		//  If only fitting to peak points of the data replace data with subset
		if ( fitToPeakPointsOnly) {
			dataToFit = extractDataNearPeak(dataToFit, peakPointRange);
		}

		// Extract x, y data as separate datasets
		Dataset positionData = getColumnFromDataSet(dataToFit, 0);
		Dataset detectorData = getColumnFromDataSet(dataToFit, 1);

		// Normalised detector data
		Dataset normDetectorData = getNormalisedDataset(detectorData);

		// Create Gaussian to use for fitting
		double centre = positionData.getDouble(positionData.getSize() / 2);
		Gaussian fitFunc = new Gaussian(centre, 1, 1);
		// restrict horizontal fit range to match range of x values
		fitFunc.getParameter(0).setLimits(positionData.min().doubleValue(), positionData.max().doubleValue());

		try {
			Fitter.ApacheNelderMeadFit(new Dataset[] {positionData}, normDetectorData, fitFunc);
			logger.debug("Curve fitting completed sucessfully.");
		} catch( Exception exception) {
			// If fitting fails for some reason, just use position of the peak value
			logger.debug("Curve fitting failed, using maximum detector value for peak position instead.");
			int maxPosIndex = normDetectorData.maxPos()[0];
			double peakPos = positionData.getDouble(maxPosIndex);
			fitFunc.setParameterValues(peakPos, 1.0, 1.0);
		}
		logger.debug("Fitted peak position = {}", fitFunc.getPosition());
		return fitFunc;
	}

	/**
	 * Return normalised version of dataset (i.e. rescaled to cover range  [0, 1] )
	 * @param data
	 * @return dataset
	 */
	private Dataset getNormalisedDataset(Dataset data) {
		// Make a copy of the dataset
		Dataset dataset = DatasetFactory.createFromObject(data);
		double maxVal = dataset.max().doubleValue();
		double minVal = dataset.min().doubleValue();
		double range = maxVal - minVal;
		dataset.isubtract(minVal);
		dataset.imultiply(1.0/range);
		return dataset;
	}

	/**
	 * Scan bragg offset without using normal scanning mechanisim (so it can be run in the middle of a scan)
	 * @return Dataset of position and detector values.
	 * @throws DeviceException
	 * @throws InterruptedException
	 */
	public Dataset doManualScan() throws DeviceException {

		InterfaceProvider.getTerminalPrinter().print("Running bragg offset optimisation scan");
		InterfaceProvider.getTerminalPrinter().print(String.format("%15s\t%15s", scannableToMove.getName(), scannableToMonitor.getName()));
		Dataset dataFromScan =  DatasetFactory.zeros(offsetNumPoints, 2);
		double offsetStepsize = (offsetEnd - offsetStart)/(offsetNumPoints - 1);
		for(int i=0; i<offsetNumPoints; i++) {
			double pos = offsetStart + i*offsetStepsize;
			scannableToMove.moveTo(pos);
			Double[] detectorReadout = readoutDetector(scannableToMonitor);

			dataFromScan.set(pos, i, 0);
			dataFromScan.set(detectorReadout[1], i, 1);
			InterfaceProvider.getTerminalPrinter().print(String.format("%15.4f\t%15.4f", dataFromScan.getDouble(i,0), dataFromScan.getDouble(i,1)));
		}
		return dataFromScan;
	}

	/**
	 * Setup the offset parameters in a {@link MonoMoveWithOffsetScannable} object from the Gaussians fitted during {@link #optimise}.
	 * @param braggWithOffset
	 */
	public void configureOffsetParameters(MonoMoveWithOffsetScannable braggWithOffset) {
		if (fittedGaussianLowEnergy == null) {
			logger.warn("Offset parameter for low energy not set - not applying offset settings to {}.", braggWithOffset.getName());
			return;
		}
		double offsetStartFitted = fittedGaussianLowEnergy.getPosition();
		double offsetEndFitted = offsetStartFitted;
		if (fittedGaussianHighEnergy != null) {
			offsetEndFitted = fittedGaussianHighEnergy.getPosition();
		}

		// Check that start, end fitted offsets are in range of offset scan. If not, don't apply the new parameters
		// to the scannable since something probably went wrong with fitting
		if ( offsetStartFitted < offsetStart || offsetEndFitted > offsetEnd) {
			logger.warn("Fitted offset start or end values ({}, {}) are out of range of offset scan {} ... {} eV!"+
						"Not applying offset settings to {}.",
					offsetStartFitted, offsetEndFitted, offsetStart, offsetEnd, braggWithOffset.getName());
			return;
		}

		double offsetGradient = 0.0;
		if (highEnergy>lowEnergy) {
			offsetGradient = (offsetEndFitted - offsetStartFitted)/(highEnergy - lowEnergy);
		}
		logger.info("Setting bragg offset parameters : start offset = {}, start energy = {}, offset gradient = {}", offsetStartFitted, lowEnergy, offsetGradient);
		braggWithOffset.setOffsetGradient(offsetGradient);
		braggWithOffset.setEnergyOffsetStart(lowEnergy);
		braggWithOffset.setOffsetStartValue(offsetStartFitted);
	}

	public void setSelectNewScansInPlotView(boolean selectNewScansInPlotView) {
		this.selectNewScansInPlotView = selectNewScansInPlotView;
	}

	public boolean getSelectNewScansInPlotView() {
		return this.selectNewScansInPlotView;
	}

	public Gaussian getFittedGaussianLowEnergy() {
		return fittedGaussianLowEnergy;
	}

	public Gaussian getFittedGaussianHighEnergy() {
		return fittedGaussianHighEnergy;
	}

	public Scannable getScannableToMonitor() {
		return scannableToMonitor;
	}

	public void setScannableToMonitor(Scannable scannableToMonitor) {
		this.scannableToMonitor = scannableToMonitor;
	}

	public Scannable getScannableToMove() {
		return scannableToMove;
	}

	public void setScannableToMove(Scannable scannableToMove) {
		this.scannableToMove = scannableToMove;
	}

	public double getOffsetStart() {
		return offsetStart;
	}

	public void setOffsetStart(double offsetStart) {
		this.offsetStart = offsetStart;
	}

	public double getOffsetEnd() {
		return offsetEnd;
	}

	public void setOffsetEnd(double offsetEnd) {
		this.offsetEnd = offsetEnd;
	}

	public int getOffsetNumPoints() {
		return offsetNumPoints;
	}

	public void setOffsetNumPoints(int offsetNumPoints) {
		this.offsetNumPoints = offsetNumPoints;
	}

	public double getCollectionTime() {
		return collectionTime;
	}

	public void setCollectionTime(double collectionTime) {
		this.collectionTime = collectionTime;
	}

	public void setFitToPeakPointsOnly(boolean b) {
		fitToPeakPointsOnly = b;
	}

	public boolean getFitToPeakPointsOnly() {
		return fitToPeakPointsOnly;
	}

	public int getPeakPointRange() {
		return peakPointRange;
	}

	public void setPeakPointRange(int peakPointRange) {
		this.peakPointRange = peakPointRange;
	}

	/**
	 * Collect and readout values from a detector.
	 * If a non-detector scannable (e.g. motor) is passed in, use getPosition method instead to obtain the values.
	 *
	 * @param scannable
	 * @return array of detector readout values
	 * @throws DeviceException
	 * @throws InterruptedException
	 * @since 31/8/2016
	 */
	private static Double[] readoutDetector(Scannable scannable) throws DeviceException {
		Object readout = null;
		try {
			if (scannable instanceof Detector) {
				Detector detector = (Detector) scannable;
				detector.collectData();
				detector.waitWhileBusy();
				readout = detector.readout();
			} else {
				readout = scannable.getPosition();
			}
		} catch (InterruptedException e) {
			// Reset interrupt status
			Thread.currentThread().interrupt();
			throw new DeviceException(e);
		}
		return ScannableUtils.objectToArray(readout);
	}

	/**
	 * Peak finding algorithm based on golden section search method.
	 *
	 * @param scannableToMove
	 * @param scannableToMonitor
	 * @param minPos
	 * @param maxPos
	 * @param tolerance
	 * @return position of scannableToMove that gives peak value of scannableToMonitor
	 * @throws DeviceException
	 * @throws InterruptedException
	 *
	 * @since 31/8/2016
	 */
	public static double goldenSectionSearch(Scannable scannableToMove, Scannable scannableToMonitor, double minPos, double maxPos, double tolerance) throws DeviceException, InterruptedException {
		final double goldenR = 0.61803399, goldenC = 1.0 - goldenR; // Golden ratios

		double midPos = minPos + 0.5*(maxPos-minPos);

		// Points used to define different segments within search interval :
		double x0, x1, x2, x3;

		// Add trial point in the larger of the two sections : minPos -> midPos, or midPos->maxPos
		x0 = minPos; x3 = maxPos;
		if ( Math.abs(maxPos - midPos) > Math.abs(midPos - minPos) ) {
			x1 = midPos;
			x2 = midPos + goldenC*(maxPos -midPos);
		} else {
			x2 = midPos;
			x1 = midPos - goldenC*(midPos - minPos);
		}

		int detIndex = 0; // index of detector readout data to use when optimising

		// Get initial values for edge points
		double val1, val2;
		scannableToMove.moveTo(x1);
		val1 = readoutDetector(scannableToMonitor)[detIndex];

		scannableToMove.moveTo(x2);
		val2 = readoutDetector(scannableToMonitor)[detIndex];

		double bestX = x1, bestY = val1;
		boolean converged = false;
		for(int i = 0; i < maxGoldenSectionIterations && !converged; i++) {

			// Convergence criteria based on difference between successive detector evaluations
			double diff = Math.abs(val1 - val2)/val2;
			if ( diff < tolerance )
				converged = true;

			if ( val2 > val1 ) {
				// upper x segment contains peak value, move lower bound up one and subdivide
				x0 = x1;
				x1 = x2;
				x2 = goldenR*x1 + goldenC*x3;
				val1 = val2;
				scannableToMove.moveTo(x2);
				val2 = readoutDetector(scannableToMonitor)[detIndex];
			} else {
				// lower x segment contains peak value, move upper bound down one and subdivide
				x3 = x2;
				x2 = x1;
				x1 = goldenR*x2 + goldenC*x0;
				val2 = val1;
				scannableToMove.moveTo(x1);
				val1 = readoutDetector(scannableToMonitor)[detIndex];
			}

			// Update best peak value and position found so far
			if ( val1 > val2 ) {
				bestX = x1;
				bestY = val1;
			} else {
				bestX = x2;
				bestY = val2;
			}

			String debugString = String.format("%d : %.4e\t %.4e\t %.4e\t %.4e\t ->  %.4e\t %.4e\t %.4e\t %d", i, x0, x1, x2, x3, bestX, bestY, diff, converged==true ? 1 : 0);
			logger.debug(debugString);
		}

		return bestX;
	}

	public Scannable getBraggScannable() {
		return braggScannable;
	}

	public void setBraggScannable(Scannable braggScannable) {
		this.braggScannable = braggScannable;
	}

	public boolean getAllowOptimisation() {
		return allowOptimisation;
	}

	public void setAllowOptimisation(boolean allowOptimisation) {
		this.allowOptimisation = allowOptimisation;
	}

	/**
	 * Save Tfg time frame and dark current collection settings
	 */
	private void saveTfgSettings() {
		if (scannableToMonitor instanceof TfgScalerWithDarkCurrent) {
			TfgScalerWithDarkCurrent tfg = (TfgScalerWithDarkCurrent) scannableToMonitor;
			logger.info("Saving dark current collection settings from Tfg {}", tfg.getName());
			tfgDarkCurrentCollectionTime = tfg.getDarkCurrentCollectionTime();
			tfgDarkCurrentRequired = tfg.isDarkCurrentRequired();
		}
	}

	/**
	 * Apply saved timeframe and dark current collection time settings to tfg
	 * @throws DeviceException
	 */
	private void applySavedTfgSettings() {
		if (scannableToMonitor instanceof TfgScalerWithDarkCurrent) {
			TfgScalerWithDarkCurrent tfg = (TfgScalerWithDarkCurrent) scannableToMonitor;
			logger.info("Applying saved time dark current collection settings to Tfg {}", tfg.getName());
			tfg.setDarkCurrentCollectionTime(tfgDarkCurrentCollectionTime);
			tfg.setDarkCurrentRequired(tfgDarkCurrentRequired);
		}
	}

	/**
	 * Move the photon shutter to the given position.
	 * @param shutterPosition one of {@link ValvePosition#OPEN} , {@link ValvePosition#CLOSE};
	 * @throws DeviceException
	 */
	private void moveShutter(String shutterPosition) throws DeviceException {
		if (photonShutter != null) {
			logger.info("Moving {} to {} position", photonShutter, shutterPosition);
			photonShutter.moveTo(shutterPosition);
		} else {
			logger.warn("Not moving photon shutter to {} position - no photon shutter object has been set");
		}
	}

	public EnumPositioner getPhotonShutter() {
		return photonShutter;
	}

	public void setPhotonShutter(EnumPositioner photonShutter) {
		this.photonShutter = photonShutter;
	}
}
