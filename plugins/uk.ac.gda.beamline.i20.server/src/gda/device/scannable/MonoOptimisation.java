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

package gda.device.scannable;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.dawnsci.analysis.api.dataset.IDataset;
import org.eclipse.dawnsci.analysis.api.tree.GroupNode;
import org.eclipse.dawnsci.analysis.dataset.impl.Dataset;
import org.eclipse.dawnsci.analysis.dataset.impl.DatasetFactory;
import org.eclipse.dawnsci.analysis.dataset.impl.DoubleDataset;
import org.eclipse.dawnsci.hdf5.nexus.NexusFileHDF5;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.dawnsci.nexus.NexusFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.DetectorBase;
import gda.device.detector.countertimer.TFGCounterTimer;
import gda.factory.Findable;
import gda.scan.ConcurrentScan;
import gda.scan.ScanPlotSettings;
import uk.ac.diamond.scisoft.analysis.fitting.Fitter;
import uk.ac.diamond.scisoft.analysis.fitting.functions.Gaussian;


/**
 * Functions to perform optimisation of monochromator, i.e. adjust bragg offset to maximise throughput
 *
 * @since 26/8/2016
 */
public class MonoOptimisation implements Findable {

	private static final Logger logger = LoggerFactory.getLogger(MonoOptimisation.class);
	private static int maxGoldenSectionIterations = 30;

	/** Scannable to be monitored during optimisation scans e.g. ionchamber, or a ScannableGaussian (for testing) */
	private Scannable scannableToMonitor;
	/** Scannable to be moved during optimisation scans e.g. braggOffset */
	private Scannable scannableToMove;

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
	private String name;

	public MonoOptimisation(Scannable scannableToMove, Scannable scannableToMonitor) {
		collectionTime = 1.0;
		offsetStart = -10;
		offsetEnd = 10;
		offsetNumPoints = 20;
		this.scannableToMove = scannableToMove;
		this.scannableToMonitor = scannableToMonitor;

		fitToPeakPointsOnly = false;
		peakPointRange = 4;

		selectNewScansInPlotView = true;
		setName(scannableToMove.getName()+"Optimiser");
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
	public void optimise(Scannable bragg, double lowEnergy, double highEnergy) throws Exception {
		logger.info("Running optimisation for energies "+lowEnergy+" and "+highEnergy);
		Object initialPos = bragg.getPosition();

		bragg.moveTo(lowEnergy);
		String filename = doOffsetScan();
		Dataset dataFromFile = loadDataFromNexusFile(filename);
		fittedGaussianLowEnergy = findPeakOutput(dataFromFile);
		this.lowEnergy = lowEnergy;

		bragg.moveTo(highEnergy);
		filename = doOffsetScan();
		dataFromFile = loadDataFromNexusFile(filename);
		fittedGaussianHighEnergy = findPeakOutput(dataFromFile);
		this.highEnergy = highEnergy;

		bragg.moveTo(initialPos);

		// Try to setup the offset parameters for the scannable
		if ( bragg instanceof MonoMoveWithOffsetScannable ) {
			configureOffsetParameters((MonoMoveWithOffsetScannable) bragg);
		}
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
	public String doOffsetScan() throws Exception {
		if ( scannableToMonitor instanceof TFGCounterTimer) {
			((TFGCounterTimer) scannableToMonitor).clearFrameSets();
			// maybe set the frame times here as well ( with .setTimes( [collectionTime, collectionTime, ...] );
		}
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

		return scan.getDataWriter().getCurrentFileName();
	}

	/**
	 * Load a dataset from Nexus a file
	 * @param filename
	 * @param dataGroupPath - full path to the data group
	 * @return IDataset first dataset from the data group.
	 * @throws NexusException
	 */
	public IDataset getDataFromFile(String filename, String dataGroupPath) throws NexusException {
		NexusFile file = NexusFileHDF5.openNexusFileReadOnly(filename);
		GroupNode groupNode = file.getGroup(dataGroupPath,false);

		// Return first dataset from data group
		String nodeName = groupNode.getNodeNameIterator().next();
		Dataset dataset = (Dataset) groupNode.getDataNode(nodeName).getDataset().getSlice(null, null, null);
		file.close();
		return dataset;
	}

	/**
	 * Load optimisation scan data from nexus file. Combine position and detector values into a single Dataset..
	 * @param filename
	 * @return Dataset with position data in 1st column, detector data in 2nd.
	 * @throws NexusException
	 */
	public Dataset loadDataFromNexusFile(String filename) throws NexusException {
		// Y values (ionchambers or other scannable)
		Dataset detectorData = (Dataset) getDataFromFile(filename, "/entry1/instrument/"+scannableToMonitor.getName());

		// X values (bragg offset motor)
		Dataset positionData = (Dataset) getDataFromFile(filename, "/entry1/instrument/"+scannableToMove.getName());

		int numRows = detectorData.getSize();
		Dataset combinedData = new DoubleDataset(detectorData.getSize(), 2);
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
	public Dataset extractDataNearPeak(Dataset dataFromFile, int peakRange) {
		int maxPosIndex = dataFromFile.maxPos()[0]; // this array seems backwards, why is max index for column 2 not in index 0?
		int numDatapoints = dataFromFile.getShape()[0];
		int numColumns = dataFromFile.getShape()[1];

		int startIndex = Math.max(maxPosIndex - peakRange, 0);
		int endIndex = Math.min(maxPosIndex + peakRange+1, numDatapoints);
		// Slice slice = new Slice( startIndex, endIndex, 1);

		return dataFromFile.getSlice(new int[] {startIndex, 0}, new int[]{endIndex, numColumns}, null);
	}

	private Dataset getColumnFromDataSet(Dataset dataset, int columnIndex) {
		int numRows = dataset.getShape()[0];
		return dataset.getSlice(new int[]{0, columnIndex}, new int[]{numRows, columnIndex+1}, null);
	}

	/**
	 * Load scan data from nexus file, find position of scannableToMove that gives peak output on scannableToMonitor
	 * @param dataToFit
	 * @return Gaussian object of 'best fit' parameters
	 */
	public Gaussian findPeakOutput(Dataset dataToFit) {

		logger.debug("Attempting to fit Gaussian to data.");

		//  If only fitting to peak points of the data replace data with subset
		if ( fitToPeakPointsOnly) {
			dataToFit = extractDataNearPeak(dataToFit, peakPointRange);
		}

		// List<CompositeFunction> fittedGaussian = Generic1DFitter.fitPeakFunctions(positionData, normScanData, Gaussian.class, 1);

		// Extract x, y data as separate datasets
		Dataset positionData = getColumnFromDataSet(dataToFit, 0);
		Dataset detectorData = getColumnFromDataSet(dataToFit, 1);

		// Normalised detector data
		Dataset normDetectorData = getNormalisedDataset(detectorData);
		Gaussian fitFunc = new Gaussian(1,1,1);
		try {
			Fitter.ApacheNelderMeadFit(new Dataset[] {positionData}, normDetectorData, fitFunc);
			logger.debug("Curve fitting comleted sucessfully.");
		} catch( Exception exception) {
			// If fitting fails for some reason, just use position of the peak value
			logger.debug("Curve fitting failed, using maximum detector value for peak position instead.");
			int maxPosIndex = normDetectorData.maxPos()[0];
			double peakPos = positionData.getDouble(maxPosIndex);
			fitFunc.setParameterValues(peakPos, 1.0, 1.0);
		}
		return fitFunc;
	}

	/**
	 * Normalised version of dataset
	 * @param data
	 * @return dataset
	 */
	public Dataset getNormalisedDataset(Dataset data) {
		// Make a copy of the datasetb
		Dataset dataset = DatasetFactory.createFromObject(data);
		double maxVal = (double) dataset.max();
		dataset.imultiply(1.0/maxVal);
		return dataset;
	}

	/**
	 * Scan bragg offset without using normal scanning mechanisim (so it can be run in the middle of a scan)
	 * @return Dataset of position and detector values.
	 * @throws DeviceException
	 * @throws InterruptedException
	 */
	public Dataset doManualScan() throws DeviceException, InterruptedException {

		Dataset dataFromScan = new DoubleDataset(offsetNumPoints, 2);
		double offsetStepsize = (offsetEnd - offsetStart)/(offsetNumPoints - 1);
		for(int i=0; i<offsetNumPoints; i++) {
			double pos = offsetStart + i*offsetStepsize;
			scannableToMove.moveTo(pos);
			Double[] detectorReadout = readoutDetector(scannableToMonitor);
			dataFromScan.set(pos, i, 0);
			dataFromScan.set(detectorReadout[0], i, 1);
		}
		return dataFromScan;
	}

	/**
	 * Setup the offset parameters in a {@link MonoMoveWithOffsetScannable} object from the Gaussians fitted during {@link #optimise}.
	 * @param braggWithOffset
	 */
	public void configureOffsetParameters(MonoMoveWithOffsetScannable braggWithOffset) {
		double offsetGradient = (fittedGaussianHighEnergy.getPosition() - fittedGaussianLowEnergy.getPosition())/(highEnergy - lowEnergy);
		braggWithOffset.setOffsetGradient(offsetGradient);
		braggWithOffset.setEnergyOffsetStart(lowEnergy);
		braggWithOffset.setOffsetStartValue(fittedGaussianLowEnergy.getPosition());
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

	@Override
	public void setName(String name) {
		this.name = name;
	}

	@Override
	public String getName() {
		return name;
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
	static private Double[] readoutDetector(Scannable scannable) throws DeviceException, InterruptedException {
		Object readout = null;
		if ( scannable instanceof Detector ) {
			Detector detector = (Detector) scannable;
			detector.collectData();
			detector.waitWhileBusy();
			readout = detector.readout();
		} else {
			readout = scannable.getPosition();
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
	static public double goldenSectionSearch(Scannable scannableToMove, Scannable scannableToMonitor, double minPos, double maxPos, double tolerance) throws DeviceException, InterruptedException {
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

}
