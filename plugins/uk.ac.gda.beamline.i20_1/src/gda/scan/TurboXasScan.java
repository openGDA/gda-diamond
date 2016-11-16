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

package gda.scan;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.data.metadata.NXMetaDataProvider;
import gda.data.nexus.extractor.NexusExtractor;
import gda.data.nexus.extractor.NexusGroupData;
import gda.data.nexus.tree.INexusTree;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.data.scan.datawriter.NexusDataWriter;
import gda.device.ContinuousParameters;
import gda.device.DeviceException;
import gda.device.detector.BufferedDetector;
import gda.device.detector.DummyNXDetector;
import gda.device.detector.NXDetectorData;
import gda.device.detector.countertimer.BufferedScaler;
import gda.device.scannable.ContinuouslyScannable;
import gda.device.scannable.ScannableUtils;
import gda.device.scannable.TurboXasScannable;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.scriptcontroller.ScriptControllerBase;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.EdeExperimentProgressBean;
import gda.scan.ede.EdeExperimentProgressBean.ExperimentCollectionType;
import gda.scan.ede.EdeScanProgressBean;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.datawriters.EdeDataConstants;
import gda.scan.ede.position.EdePositionType;

/**
 *  A TurboXasScan is a type of Continuous scan which can perform multiple sweeps of a fast slit and collect the spectra for each sweep.
 *  It is designed to used with a {@link TurboXasScannable} object which contains a full definition of the experiment
 *  in a {@link TurboXasParameters} object, including timing group information in a List of {@link TurboSlitTimingGroup}s.
 *  It can also be used with a {@link ContinuouslyScannable}, in which case the behaviour is like a regular {@link ContinuousScan}.
 *  (i.e. a single spectrum is collected).
 * 	<li>A timing group comprises one or more spectra with the same time per spectrum (i.e. motor speed used for scan)
 *  <li>Each timing group can have a different time per spectrum.
 *  <li>The pulse streams for multiple spectra used for hardware triggered data collection are produced from the Zebra.
 *  The Zebra is configured by the {@link TurboXasScannable} being used, or assumed to be already configured before the scan start.
 *  <li>Data is added to the NeXus file one spectrum at a time after the motor move for each has been completed.
 *  by using multiple gates (i.e. one gate per spectrum).
 *  <li>Spectra are sent to Ede scan plot view in the client as they are collected.
 */
public class TurboXasScan extends ContinuousScan {
	private static final Logger logger = LoggerFactory.getLogger(TurboXasScan.class);
	private TurboXasMotorParameters turboXasMotorParams;
	private boolean useAreaDetector;

	public TurboXasScan(ContinuouslyScannable energyScannable, Double start, Double stop, Integer numberPoints,
			Double time, BufferedDetector[] detectors) {
		super(energyScannable, start, stop, numberPoints, time, detectors);
	}

	public TurboXasScan(ContinuouslyScannable energyScannable, TurboXasMotorParameters motorParams, BufferedDetector[] detectors) {
		// don't set scan time here, there may be multiple timing groups...
		super(energyScannable, motorParams.getScanStartPosition(), motorParams.getScanEndPosition(),
				motorParams.getNumReadoutsForScan(), 0.0, detectors);
		turboXasMotorParams = motorParams;
	}

	@Override
	public void doCollection() throws Exception {
		logger.info("Running scan");

		plotUpdater.setCurrentSpectrumNumber(1);
		plotUpdater.setCurrentGroupNumber(1);
		plotUpdater.setEnergyAxisName(ENERGY_COLUMN_NAME);

		ContinuouslyScannable scanAxis = getScanAxis();
		if (scanAxis instanceof TurboXasScannable && turboXasMotorParams != null) {
			collectMultipleSpectra();
		} else {
			logger.info("Setting up scan using ContinuousParameters");
			collectOneSpectrum();
		}

		logger.info("Scan finished");
 	}

	/**
	 * @return Total number of spectra across all timing groups
	 */
	private int getTotalNumSpectra() {
		int totNumSpectra = 1;
		// Determine total number of spectra across all timing groups -
		if (turboXasMotorParams != null) {
			totNumSpectra = 0;
			for( TurboSlitTimingGroup group : turboXasMotorParams.getScanParameters().getTimingGroups() ) {
				totNumSpectra += group.getNumSpectra();
			}
		}
		return totNumSpectra;
	}

	/**
	 * Collect multiple spectra by performing motor moves for several timing groups.
	 * @throws Exception
	 */
	private void collectMultipleSpectra() throws Exception {
		TurboXasScannable turboXasScannable = (TurboXasScannable) getScanAxis();
		logger.info("Setting up scan using TurboXasScannable ({})", turboXasScannable.getName());

		addMetaDataAtScanStart();

		turboXasScannable.resetZebraArmConfigFlags(); // already called by atScanStart()
		turboXasScannable.setDisarmZebraAtScanEnd(false); // don't disarm zebra after first timing group

		List<TurboSlitTimingGroup> timingGroups = turboXasMotorParams.getScanParameters().getTimingGroups();

		// Determine total number of spectra across all timing groups -
		int totNumSpectra = getTotalNumSpectra();

		// Set number of zebra gates
		turboXasScannable.setNumZebraGates(totNumSpectra);

		// Set area detector flag (for timing, encoder position information)
		turboXasScannable.setUseAreaDetector(useAreaDetector); // setAreaDetectorPreparer( getZebraAreaDetectorPreparer(zebraPv) );

		// Prepare detectors (BufferedScalers) for readout of all spectra
		// Do this once at beginning to avoid overhead of clearing out scaler memory etc for each spectra.
		lastFrameRead = 0;
		int totNumReadouts = turboXasScannable.getNumReadoutsForScan()*totNumSpectra;
		prepareDetectors(totNumReadouts);


		// Loop over timing groups...
		for (int i = 0; i < timingGroups.size(); i++) {
			logger.info("Setting motor parameters for timing group {} of {}", i+1, timingGroups.size());
			plotUpdater.setCurrentGroupNumber(i+1);

			// calculate and set the motor parameters for this timing group
			turboXasMotorParams.setMotorParametersForTimingGroup(i);

			// Set flags so we don't reconfigure and rearm zebra for next timing group or scan
			// (each group has same number of readouts etc., only the motor speed changes)

			// Loop over number of spectra (repetitions) ...
			int numRepetitions = timingGroups.get(i).getNumSpectra();
			for (int j = 0; j < numRepetitions; j++) {
				plotUpdater.setCurrentSpectrumNumber(j+1);
				collectOneSpectrum();
				turboXasScannable.setArmZebraAtScanStart(false);
				turboXasScannable.setConfigZebraDuringPrepare(false);
			}
		}
		// flags back to default values
		turboXasScannable.atScanEnd();
 	}

	public void prepareDetectors(int totNumReadouts) throws DeviceException, InterruptedException {

		// Try to set scalert64 mode first, otherwise Scalers seem to return junk. imh 14/9/2016
		BufferedDetector det = getScanDetectors()[0];
		if ( det instanceof BufferedScaler ) {
			Object result = ((BufferedScaler)det).getDaserver().sendCommand("tfg setup-cc-mode scaler64");
			if (!result.toString().equals("0")) {
				logger.info("Problem setting Tfg to use scaler64 mode - scaler readout may not work correctly...");
			}
		}

		// Setup scaler memory to record all frames of data for all spectra across all timing groups
		ContinuousParameters params = createContinuousParameters();
		params.setNumberDataPoints(totNumReadouts);

		// prep the detectors
		for (BufferedDetector detector : getScanDetectors() ) {
			detector.clearMemory(); // Is it necessary to clear scaler memory each time (takes approx 0.3--0.4secs)
			detector.setContinuousParameters(params);
			detector.setContinuousMode(true);
			checkThreadInterrupted();
		}
	}
	/**
	 * Set the ContinuousParameters (and TurboXasMotorParameters) to be used on the scan axis.
	 */
	private void prepareScanAxis() {
		ContinuousParameters params = createContinuousParameters();
		ContinuouslyScannable scanAxis = getScanAxis();
		scanAxis.setContinuousParameters(params);

		// TurboXasScannable is configured using TurboXasMotorParameters rather than ContinuousParameters.
		// However, still need to store continuousParameters as well, since they are used to configure BufferedDetectors
		if (scanAxis instanceof TurboXasScannable && turboXasMotorParams != null) {
			((TurboXasScannable) scanAxis).setTurboXasMotorParameters(turboXasMotorParams);
			// total time is set by createContinuousParameters() but doesn't seem to be used -
			// adjust the value to calculated scan time based on motor moves just in case... :-/
			params.setTotalTime( turboXasMotorParams.getTotalTimeForScan() );
		}
	}

	/**
	 * Perform motor move and collect data for a single spectrum
	 * @throws Exception
	 */
	public void collectOneSpectrum() throws Exception {
		checkThreadInterrupted();

		// Still need to create ContinuousParameters even if scan is setup using TurboXasMotorParams -
		// - it is passed to BufferedDetector so it can set the number of data points...
		prepareScanAxis();
		ContinuouslyScannable scanAxis = getScanAxis();
		ContinuousParameters params = scanAxis.getContinuousParameters();

		// Get motor parameters, return motor to initial run-up position, arm the zebra with gate and pulse parameters (if 'arm at scan start' = true)
		scanAxis.waitWhileBusy(); // to make sure motor is not still moving from last repetition/scan
		scanAxis.prepareForContinuousMove();

		final int numberScanpoints = Math.abs(scanAxis.getNumberOfDataPoints());
		params.setNumberDataPoints(numberScanpoints);
		super.setTotalNumberOfPoints(numberScanpoints);

		scanAxis.performContinuousMove();

		scanAxis.waitWhileBusy();
		// Wait for scan to finish, then readout all frames at end into single ScanDataPoint object

		BufferedDetector[] scanDetectors = getScanDetectors();
		if (scanDetectors.length > 0) {
			collectData(scanDetectors[0]);
		}
	}

	// Dataset names used in NeXus file
	private static final String MOTOR_PARAMS_COLUMN_NAME = "motor_parameters";
	private static final String TIME_COLUMN_NAME = "time";
	private static final String I0_COLUMN_NAME = "I0";
	private static final String IT_COLUMN_NAME = "It";
	private static final String ENERGY_COLUMN_NAME = "energy";
	private static final String FRAME_INDEX = "frame_index";

	private NXDetectorData createNXDetectorData(BufferedDetector detector, int lowFrame, int highFrame) throws DeviceException {

		detectorFrameData = detector.readFrames(lowFrame, highFrame);

		NXDetectorData frame = new NXDetectorData(detector);

		double[][]frameDataArray = (double[][]) detectorFrameData;

		int numFrames = highFrame - lowFrame;
		int[]frameIndex = new int[numFrames];
		double[] energy = new double[numFrames];

		double[] i0Values = new double[numFrames];
		double[] itValues = new double[numFrames];
		double[] irefValues = new double[numFrames];
		double[] timeValues = new double[numFrames];

		ContinuouslyScannable scanAxis = getScanAxis();
		for(int i = 0; i<numFrames; i++) {
			frameIndex[i] = i;
			timeValues[i] = frameDataArray[i][0];
			i0Values[i] = frameDataArray[i][1];
			itValues[i] = frameDataArray[i][2];
			irefValues[i] = frameDataArray[i][3];
			energy[i] = scanAxis.calculateEnergy(i);
		}

		frame.addAxis(detector.getName(), ENERGY_COLUMN_NAME, new NexusGroupData(energy), 1, 1, "eV", false);
		frame.addAxis(detector.getName(), FRAME_INDEX, new NexusGroupData(frameIndex), 2, 1, "index", false);

		frame.addData(detector.getName(), TIME_COLUMN_NAME, new NexusGroupData(timeValues), "seconds", 1);
		frame.addData(detector.getName(), I0_COLUMN_NAME, new NexusGroupData(i0Values), "counts", 1);
		frame.addData(detector.getName(), IT_COLUMN_NAME, new NexusGroupData(itValues), "counts", 1);

		if ( turboXasMotorParams != null )
			frame.addData(detector.getName(), MOTOR_PARAMS_COLUMN_NAME, new NexusGroupData(turboXasMotorParams.toXML()));

		return frame;
	}

	public NexusTreeProvider[] readFrames(BufferedDetector detector, int lowFrame, int highFrame) throws Exception, DeviceException {
		NexusTreeProvider[] results = new NexusTreeProvider[1];
		results[0] = createNXDetectorData(detector, lowFrame, highFrame);
		return results;
	}

	@Override
	public int getDimension() {
		return 1;
	}

	protected Object[][] readDetector(BufferedDetector detector, int lowFrame, int highFrame) throws Exception, DeviceException {
		NexusTreeProvider[][] detData = new NexusTreeProvider[1][];
		logger.info("reading data from detectors from frames {} to {}", lowFrame, highFrame);

		detData[0] = readFrames(detector, lowFrame, highFrame);

		logger.info("data read successfully");
		return detData;
	}

	private PlotUpdater plotUpdater = new PlotUpdater();
	private Object[] detectorFrameData;
	private int lastFrameRead;

	private void collectData(BufferedDetector detector) throws Exception {

		// each frame is set of scaler values, corresponding to values for single photon energy/zebra pulse/motor position
		// Readout frames from Scaler memory corresponding to latest spectra.
		int framesRead = detector.getNumberFrames();
		Object[][]nxFrameData = readDetector(detector, lastFrameRead, framesRead);
		lastFrameRead = framesRead;

		// Create scan data point and add detector data.
		ScanDataPoint thisPoint = new ScanDataPoint();
		thisPoint.setUniqueName(getName());
		thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());
		thisPoint.setStepIds(getStepIds());
		thisPoint.setScanPlotSettings(getScanPlotSettings());

		int[] dims = getDimensions();
		thisPoint.setScanDimensions(dims);

		// NeXus writing works using NXDetector, so put scaler data in dummy NX detector...
		DummyNXDetector testDet = new DummyNXDetector(detector.getName(), 1);
		thisPoint.addDetector(testDet);
		thisPoint.addDetectorData(nxFrameData[0][0], ScannableUtils.getExtraNamesFormats(detector));

		// If nested scan, determine number of times this scan will be repeated.
		int numPoints = 1;
		if (isChild())
			numPoints = getParent().getDimension();

		numPoints = getTotalNumSpectra();

		thisPoint.setNumberOfPoints(numPoints);
		currentPointCount++;
		thisPoint.setCurrentPointNumber(currentPointCount);

		thisPoint.setInstrument(instrument);
		thisPoint.setCommand(getCommand());
		thisPoint.setScanIdentifier(getScanNumber());
		setScanIdentifierInScanDataPoint(thisPoint);

		getDataWriter().addData(thisPoint);
		thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());

		InterfaceProvider.getJythonServerNotifer().notifyServer(this, thisPoint); // for the CommandQueue

		plotUpdater.updateShowAll(thisPoint);

	}

	public void sendScanDataPoints() throws DeviceException{
		ContinuouslyScannable scanAxis = getScanAxis();
		BufferedDetector detector = getScanDetectors()[0];

		for(int i = 0; i<detectorFrameData.length; i++) {
			ScanDataPoint thisPoint = new ScanDataPoint();
			thisPoint.setUniqueName(name);
			thisPoint.setCurrentFilename(getDataWriter().getCurrentFileName());
			this.stepId = new ScanStepId(scanAxis.getName(), i);
			thisPoint.setStepIds(getStepIds());
			thisPoint.setScanPlotSettings(getScanPlotSettings());
			thisPoint.setScanDimensions(new int[]{getDimension()});
			thisPoint.setNumberOfPoints(getDimension());

			Object data = detectorFrameData[i];
			if (data != null) {
				thisPoint.addDetector(detector);
				thisPoint.addDetectorData(data, ScannableUtils.getExtraNamesFormats(detector));
			}

			thisPoint.addScannable(scanAxis);
			thisPoint.addScannablePosition(scanAxis.calculateEnergy(i), scanAxis.getOutputFormat());

			thisPoint.setCurrentPointNumber(i);
			thisPoint.setInstrument(instrument);
			thisPoint.setCommand(getCommand());

			setScanIdentifierInScanDataPoint(thisPoint);

			InterfaceProvider.getJythonServerNotifer().notifyServer(this,thisPoint); // for the CommandQueue
			sendScanEvent(ScanEvent.EventType.UPDATED); // for the ApplicationActionToolBar
		}
	}

	private void addMetaDataAtScanStart() {
		String metashopName = LocalProperties.get(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME,"metashop");
		NXMetaDataProvider metashop = Finder.getInstance().find(metashopName);
		if (metashop != null) {
			metashop.clear();
			metashop.add("TurboXasParameters", turboXasMotorParams.getScanParameters().toXML() );
		}
	}

	private static class PlotUpdater {

		private int currentGroupNumber;
		private int currentSpectrumNumber;
		private String energyAxisName;

		public void setCurrentGroupNumber(int currentGroupNumber) {
			this.currentGroupNumber = currentGroupNumber;
		}

		public void setCurrentSpectrumNumber(int currentSpectrumNumber) {
			this.currentSpectrumNumber = currentSpectrumNumber;
		}

		public void setEnergyAxisName(String energyAxisName) {
			this.energyAxisName = energyAxisName;
		}

		DoubleDataset extractDoubleDatset(NexusGroupData groupData) {
			if (groupData!=null && groupData.getBuffer() instanceof double[]) {
				double[] originalData = (double[]) groupData.getBuffer();
				return (DoubleDataset) DatasetFactory.createFromObject(Arrays.copyOf(originalData, originalData.length), originalData.length);
			} else
				return null;
		}

		/**
		 * Extract detector data from scan data point and send spectra of I0, It, time etc to the progress updater.
		 * Only data from the first detector is extracted.
		 * @param scanDataPoint
		 */
		public void updateShowAll(ScanDataPoint scanDataPoint) {
			ScriptControllerBase controller = Finder.getInstance().find(EdeExperiment.PROGRESS_UPDATER_NAME);
			if ( controller != null ) {
				logger.info("PlotUpdater.updateShowAll() called");
				NXDetectorData data = (NXDetectorData) scanDataPoint.getDetectorData().get(0);

				// Extract numerical (floating point) detector data from Nexus data in scan data point
				List<String> dataNames = new ArrayList<String>();
				List<DoubleDataset> dataSets = new ArrayList<DoubleDataset>();
				INexusTree nexusDetData = data.getNexusTree().getChildNode(0);
				String detectorName = data.getNexusTree().getChildNode(0).getName();

				for(int i = 0; i<nexusDetData.getNumberOfChildNodes(); i++) {
					String dataName = nexusDetData.getChildNode(i).getName();
					NexusGroupData groupData = data.getData(detectorName, dataName, NexusExtractor.SDSClassName);
					DoubleDataset dataset = extractDoubleDatset(groupData);
					if (dataset!=null) {
						dataNames.add(dataName);
						dataSets.add(dataset);
					}
				}

				// Determine index of dataset to use for energy axis
				int energyAxisIndex = dataNames.indexOf(energyAxisName);
				if (energyAxisIndex==-1) {
					logger.info("PlotUpdater could not find energy axis data (axis name = {})",energyAxisName);
					return;
				}

				// Create progress beans and notify plot controller
				EdeScanProgressBean scanProgressBean = new EdeScanProgressBean(currentGroupNumber, currentSpectrumNumber, EdeScanType.LIGHT,
						EdePositionType.INBEAM, scanDataPoint);
				for(int i = 0; i<dataNames.size(); i++) {
					if (i!=energyAxisIndex) {
						controller.update(null, new EdeExperimentProgressBean(ExperimentCollectionType.MULTI, scanProgressBean,
											dataNames.get(i), dataSets.get(i), dataSets.get(energyAxisIndex)));
					}
				}
			}
		}

		/**
		 * Extract I0, It data from scan data point and send spectra to the progress updater
		 * Only data from the first detector is extracted.
		 * @param scanDataPoint
		 */
		/** TODO remove this function if {@link #updateShowAll } is working correctly */
		public void update(ScanDataPoint scanDataPoint) {
			ScriptControllerBase controller = Finder.getInstance().find(EdeExperiment.PROGRESS_UPDATER_NAME);
			if ( controller != null ) {
				logger.info("PlotUpdater.update() called");
				NXDetectorData data = (NXDetectorData) scanDataPoint.getDetectorData().get(0);
				String detectorName = data.getNexusTree().getChildNode(0).getName();
				NexusGroupData i0groupData = data.getData(detectorName, I0_COLUMN_NAME, NexusExtractor.SDSClassName );
				NexusGroupData itgroupData = data.getData(detectorName, IT_COLUMN_NAME, NexusExtractor.SDSClassName );
				NexusGroupData energyData = data.getData(detectorName, ENERGY_COLUMN_NAME, NexusExtractor.SDSClassName );

				DoubleDataset i0Dataset = extractDoubleDatset(i0groupData);
				DoubleDataset itDataset = extractDoubleDatset(itgroupData);
				DoubleDataset energyDataset = extractDoubleDatset(energyData);

				EdeScanProgressBean scanProgressBean = new EdeScanProgressBean(currentGroupNumber, currentSpectrumNumber, EdeScanType.LIGHT,
						EdePositionType.INBEAM, scanDataPoint);

				controller.update(null, new EdeExperimentProgressBean(ExperimentCollectionType.MULTI, scanProgressBean,
						EdeDataConstants.I0_COLUMN_NAME, i0Dataset, energyDataset));
				controller.update(null, new EdeExperimentProgressBean(ExperimentCollectionType.MULTI, scanProgressBean,
						EdeDataConstants.IT_COLUMN_NAME, itDataset, energyDataset));
			}
		}
	}

	public TurboXasMotorParameters getTurboXasMotorParams() {
		return turboXasMotorParams;
	}

	public void setUseAreaDetector(boolean useAreaDetector) {
		this.useAreaDetector = useAreaDetector;
	}

	public boolean getUseAreaDetector() {
		return useAreaDetector;
	}
}
