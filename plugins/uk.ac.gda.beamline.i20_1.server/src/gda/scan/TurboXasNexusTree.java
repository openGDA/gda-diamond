/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang.ArrayUtils;
import org.dawnsci.ede.EdeDataConstants;
import org.eclipse.dawnsci.hdf5.nexus.NexusFileHDF5;
import org.eclipse.dawnsci.nexus.NexusConstants;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.dawnsci.nexus.NexusFile;
import org.eclipse.dawnsci.nexus.template.NexusTemplate;
import org.eclipse.dawnsci.nexus.template.NexusTemplateService;
import org.eclipse.january.DatasetException;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.january.dataset.RunningAverage;
import org.eclipse.january.dataset.Slice;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.ServiceHolder;
import gda.data.nexus.extractor.NexusGroupData;
import gda.data.nexus.tree.INexusTree;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.data.swmr.SwmrFileReader;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.device.detector.NXDetectorData;
import gda.device.detector.countertimer.BufferedScaler;
import gda.device.scannable.ContinuouslyScannable;
import gda.device.scannable.TurboXasScannable;
import uk.ac.gda.devices.detector.xspress3.Xspress3BufferedDetector;

/**
 * Class to read out from detectors used during {@link TurboXasScan} and return NexusTreeProvider object containing the data.
 * Refactored from {@link TurboXasScan}
 *
 */
public class TurboXasNexusTree {

	private static final Logger logger = LoggerFactory.getLogger(TurboXasNexusTree.class);

	public static final String MOTOR_PARAMS_COLUMN_NAME = "motor_parameters";
	public static final String TIME_COLUMN_NAME = "time";
	public static final String TIME_UTC_COLUMN_NAME = "time_utc_millis";
	public static final String TOPUP_FIELD_NAME = "topup";
	public static final String TIME_BETWEEN_SPECTRA_COLUMN_NAME = "time_between_spectra";
	public static final String ENERGY_COLUMN_NAME = "energy";
	public static final String POSITION_COLUMN_NAME = "position";
	public static final String FRAME_INDEX = "frame_index";
	public static final String ENERGY_UNITS = "eV";
	public static final String TIME_UNITS = "seconds";
	public static final String COUNT_UNITS = "counts";
	public static final String INDEX_UNITS = "index";
	public static final String POSITION_UNITS = "cm";
	public static final String I0_LABEL = "I0";
	public static final String FF_SUM_IO_NAME = "FF_sumI0";
	public static final String FF_SUM_NAME = "FF_sum";

	private boolean reverseDetectorReadout = false;

	// Dataset names for spectrum and timing group index (to match Ede scan data names...)
	public static final String SPECTRUM_INDEX = EdeDataConstants.FRAME_COLUMN_NAME;
	public static final String SPECTRUM_GROUP = EdeDataConstants.TIMINGGROUP_COLUMN_NAME;

	private Dataset i0Data;

	private String frameTimeFieldName;
	private ContinuouslyScannable scanAxis;
	private SwmrFileReader xspress3FileReader;
	private int numReadoutsPerSpectrum;
	private long startTimeUtcMillis = System.currentTimeMillis();
	private List<String> namesForDefaultNXData = Arrays.asList("FF", "It", "lnI0It");

	private List<String> datasetsNamesToAverage = Collections.emptyList();
	private Map<String, RunningAverage> runningAverageDatasets = new HashMap<>();

	private int groupNumber;
	private int spectrumNumber;

	private double timeAtSpectrumStart;

	/**
	 * Add link to external xspress3 hdf file containing detector data
	 * @param nexusFile
	 * @param detector xspress3 detector
	 * @throws URISyntaxException
	 * @throws DeviceException
	 * @throws NexusException
	 */
	public void addDetectorDataLink(NexusFile nexusFile, Xspress3BufferedDetector detector) throws URISyntaxException, DeviceException, NexusException {
		if (detector != null) {
			logger.debug("Adding link to {} MCA data", detector.getName());
			URI hdfFile = new URI(detector.getController().getFullFileName() + "#entry/data/data");
			String nexusLinkName = "/entry1/" + detector.getName() + "/MCAs";
			nexusFile.linkExternal(hdfFile, nexusLinkName, false);
		}
	}

	public void addDataAtEndOfScan(String filename, BufferedDetector[] bufferedDetectors) throws URISyntaxException, DeviceException, NexusException, DatasetException {
		logger.debug("Adding data at end of scan");
		BufferedScaler bufferedScaler = null;
		Xspress3BufferedDetector xspress3Detector = null;
		for(BufferedDetector det : bufferedDetectors) {
			if (det instanceof BufferedScaler) {
				bufferedScaler = (BufferedScaler) det;
			}
			if (det instanceof Xspress3BufferedDetector) {
				xspress3Detector = (Xspress3BufferedDetector) det;
			}
		}

		try(NexusFile file = NexusFileHDF5.openNexusFile(filename)) {
			addNxDataEntry(file, bufferedScaler);
			addDetectorDataLink(file, xspress3Detector);
		}
	}

	private void addNxDataEntry(NexusFile file, Scannable detector) throws NexusException {
		if (!isAddNxDataEntries) {
			return;
		}
		Map<String, Object> map = createYamlMap(detector);
		logger.info("Applying template {} to file {}", map, file.getFilePath());
		final NexusTemplateService templateService = ServiceHolder.getNexusTemplateService();
		NexusTemplate nexusTemplateImpl = templateService.createTemplate("TurboXasNexusTemplate", map);
		nexusTemplateImpl.apply(file);
	}

	/**
	 * Create Yaml map to use with NexusTemplate to add NXData objects with appropriate attributes
	 * and links to original dataset to Nexus file
	 * @param bufferedScaler
	 * @return
	 */
	public Map<String, Object> createYamlMap(Scannable bufferedScaler) {
		Map<String, Object> mapObj = new LinkedHashMap<>();
		mapObj.put(NexusConstants.NXCLASS+"@", NexusConstants.ENTRY);
		// set default signal for /entry1
		mapObj.put(NexusConstants.DEFAULT+"@", bufferedScaler.getName()+"_"+bufferedScaler.getExtraNames()[2]);

		for(String name : bufferedScaler.getExtraNames()) {
			// Create map representing NXdata group
			Map<String,Object> map = new LinkedHashMap<>();
			addAttributesToMap(name, map);
			addAxisDatasetLinksToMap(bufferedScaler.getName(), map);
			// Add a link to original dataset
			map.put(name, "/entry1/"+bufferedScaler.getName()+"/"+name);

			// Add it to the main map
			String groupName = bufferedScaler.getName()+"_"+name+"/";
			mapObj.put(groupName, map);
		}
		// Set attributes on detector group written by old NexusDataWriter
		Map<String,Object> map = new LinkedHashMap<>();
		addAttributesToMap(bufferedScaler.getExtraNames()[2], map);
		mapObj.put(bufferedScaler.getName()+"/", map);

    	return Collections.singletonMap("entry1/", mapObj);
	}

	/**
	 * Add attributes and axis information
	 * @param signalName
	 * @param mapObj
	 * @return
	 */

	private void addAttributesToMap(String signalName, Map<String, Object> mapObj) {
		mapObj.put(NexusConstants.NXCLASS + "@", NexusConstants.DATA);
		getAttributeDataNames().entrySet()
				.forEach(entry -> mapObj.put(entry.getKey() + NexusConstants.DATA_INDICES_SUFFIX + "@", entry.getValue()));
		mapObj.put(NexusConstants.DATA_SIGNAL + "@", signalName);
		mapObj.put(NexusConstants.DATA_AXES + "@", new String[] {TurboXasNexusTree.TIME_COLUMN_NAME, TurboXasNexusTree.ENERGY_COLUMN_NAME});
	}

	/**
	 * Add links to the axis datasets
	 * @param sourceGroupName
	 * @param mapObj
	 * @return
	 */
	private void addAxisDatasetLinksToMap(String sourceGroupName, Map<String, Object> mapObj) {
		getAttributeDataNames()
				.keySet()
				.forEach(name -> mapObj.put(name, "/entry1/"+sourceGroupName+"/"+name));
	}

	private boolean isAddNxDataEntries = true;

	public boolean isAddNxDataEntries() {
		return isAddNxDataEntries;
	}

	public void setAddNxDataEntries(boolean isAddNxDataEntries) {
		this.isAddNxDataEntries = isAddNxDataEntries;
	}

	public Map<String, Integer> getAttributeDataNames() {
		Map<String, Integer> dataNames = new LinkedHashMap<>();
		dataNames.put(TIME_COLUMN_NAME, 0);
		dataNames.put(SPECTRUM_INDEX, 0);
		dataNames.put(ENERGY_COLUMN_NAME, 1);
		dataNames.put(POSITION_COLUMN_NAME, 1);
		return dataNames;
	}

	/**
	 * Make energy and frame index axes. If scan axis is {@link TurboXasScannable} also add an axis for position.
	 * @param detector
	 * @param lowFrame
	 * @param highFrame
	 * @return NXDetectorData with axes for energy, frame index and position values
	 * @throws DeviceException
	 */
	private NXDetectorData createAxisData(BufferedDetector detector, int lowFrame, int highFrame) throws DeviceException {
		int numFramesRead = highFrame - lowFrame;
		if (numFramesRead<numReadoutsPerSpectrum) {
			logger.info("Expected {} frames for spectrum, {} frames available - padding with zeros...", numReadoutsPerSpectrum, numFramesRead );
		}

		int numAxisPoints = numFramesRead;

		// Setup arrays of frame index and energy of each frame
		int[] frameIndex = new int[numAxisPoints];
		for(int i=0; i<numAxisPoints; i++) {
			frameIndex[i] = i;
		}

		// Add frame and energy axis data
		NXDetectorData frame = new NXDetectorData(detector);
		frame.addAxis(detector.getName(), FRAME_INDEX, new NexusGroupData(frameIndex), 2, 1, INDEX_UNITS, false);

		// Add position axis data if using TurboXasScannable
		if (scanAxis instanceof TurboXasScannable) {
			double[] position = new double[numAxisPoints];
			double[] energy = new double[numAxisPoints];

			TurboXasScannable txasScannable = (TurboXasScannable)scanAxis;
			TurboXasMotorParameters motorParams = txasScannable.getMotorParameters();
			// size of each frame (constant for scan)
			for(int i=0; i<numAxisPoints; i++) {
				position[i] = txasScannable.calculatePosition(i);

				// energy for midpoint of frame
				double midPointPosition = 0.5*(position[i] + txasScannable.calculatePosition(i+1));
				energy[i] = motorParams.getEnergyForPosition(midPointPosition);
			}
			frame.addAxis(detector.getName(), POSITION_COLUMN_NAME, new NexusGroupData(position), 3, 1, POSITION_UNITS, false);
			frame.addAxis(detector.getName(), ENERGY_COLUMN_NAME, new NexusGroupData(energy), 1, 1, ENERGY_UNITS, false);
		} else {
			double[] energy = new double[numAxisPoints];
			for(int i=0; i<numAxisPoints; i++) {
				energy[i] = scanAxis.calculateEnergy(i);
			}
			frame.addAxis(detector.getName(), ENERGY_COLUMN_NAME, new NexusGroupData(energy), 1, 1, ENERGY_UNITS, false);
		}
		return frame;
	}

	private NexusGroupData createDetectorNexusGroupData(double[] detData) {
		// Copy the original data, add extra element with NaN at the end.
		double[] arrayCopy = Arrays.copyOf(detData, detData.length+1);
		arrayCopy[arrayCopy.length-1] = Double.NaN;

		if (!reverseDetectorReadout) {
			return new NexusGroupData(arrayCopy);
		}
		// Reverse the dataset
		ArrayUtils.reverse(arrayCopy);
		return new NexusGroupData(arrayCopy);
	}

	private NexusGroupData createDetectorNexusGroupData(Dataset detData) {
		// Create copy of the original dataset with extra element at the end set to NaN.
		int numElements = detData.getShape()[0]+1;
		Dataset datasetCopy = detData.clone();
		datasetCopy.resize(numElements);
		datasetCopy.set(Double.NaN, numElements-1);

		if (!reverseDetectorReadout) {
			return NexusGroupData.createFromDataset(datasetCopy);
		}

		// Reverse the dataset by taking a slice
		Dataset reversedDataset = datasetCopy.getSlice(new Slice(null, null, -1));
		return NexusGroupData.createFromDataset(reversedDataset);
	}

	public boolean isReverseDetectorReadout() {
		return reverseDetectorReadout;
	}

	public void setReverseDetectorReadout(boolean reverseDetectorReadout) {
		this.reverseDetectorReadout = reverseDetectorReadout;
	}

	/**
	 * Create NXDetector data from XSpress3 detector; Readout of detector data occurs in two ways :
	 * <li> In the normal way. i.e. by reading arrays of scaler data from PVs.
	 * <li> By reading data from the XSpress3 hdf (SWMR) file (using {@link #xspress3FileReader}).
	 * When using this method, checks should be carried out before calling this function to ensure lowframe and highframe are within current dataset limits.
	 * e.g. by calling {@link SwmrFileReader#getNumAvailableFrames()}.
	 * @param detector
	 * @param lowFrame
	 * @param highFrame
	 * @return
	 * @throws DeviceException
	 */
	private NXDetectorData createNXDetectorData(Xspress3BufferedDetector detector, int lowFrame, int highFrame) throws DeviceException {

		logger.debug("Adding Xspress3 detector data");

		NXDetectorData frame = createAxisData(detector, lowFrame, highFrame);

		INexusTree detTree = frame.getDetTree(detector.getName());

		if (xspress3FileReader!=null) {
			// Add detector data from xspress3 hdf file
			int[] start = new int[] { lowFrame };
			int[] shape = new int[] { highFrame - lowFrame - 1 };
			int[] step = new int[shape.length];
			Arrays.fill(step, 1);
			try {
				logger.info("Adding data from XSpress3 hdf file {}", xspress3FileReader.getFilename());

				// Build list of suffixes of dataset names for detector elements *excluded* from FF sum
				// e.g. "_1", "_2", "_3" etc
				List<String> exludedElementSuffixList = new ArrayList<>();
				for(int i=0; i< detector.getNumberOfElements(); i++) {
					if (!detector.getController().isChannelEnabled(i)) {
						exludedElementSuffixList.add(String.format("_%d", i+1));
					}
				}
				if (!exludedElementSuffixList.isEmpty()) {
					logger.debug("Detector elements excluded from FF sum : {}", exludedElementSuffixList);
				}

				// Calculate the FF sum over non excluded detector elements
				Dataset ffSum = DatasetFactory.zeros(highFrame - lowFrame -1);
				ffSum.setName(FF_SUM_NAME);
				for (Dataset dataset : xspress3FileReader.readDatasets(start, shape, step)) {
					NXDetectorData.addData(detTree, dataset.getName(), createDetectorNexusGroupData(dataset), "counts", 1);
					if (dataset.getName().startsWith("FF")) {
						boolean excludeInSum = exludedElementSuffixList.stream()
							.anyMatch(elementSuffix -> dataset.getName().endsWith(elementSuffix));
						if (!excludeInSum) {
							ffSum.iadd(dataset);
						}
					}
				}
				NXDetectorData.addData(detTree, ffSum.getName(), createDetectorNexusGroupData(ffSum), "counts", 1);
			} catch (NexusException e) {
				logger.error("Problem reading data from hdf file", e);
			}
		} else {
			//Add detector data from xspress3 scaler readout
			logger.info("Adding data from XSpress3 scaler readout");
			NXDetectorData[] detData = detector.readFrames(lowFrame, highFrame-1);
			String[] names = detData[0].getExtraNames();
			int numFrames = highFrame-lowFrame-1; //detData.length;
			for(int i=0; i<names.length; i++) {
				Dataset dataset = DatasetFactory.zeros(DoubleDataset.class, numFrames);
				dataset.setName(names[i]);
				for(int frameIndex = 0; frameIndex<numFrames; frameIndex++) {
					double val = detData[frameIndex].getDoubleVals()[i];
					dataset.set(val, frameIndex);
				}
				NXDetectorData.addData(detTree, dataset.getName(), createDetectorNexusGroupData(dataset), "counts", 1);

				// Last dataset is FF_sum dataset (i.e. sum over all detector elements)
				if (i==names.length-1) {
					NXDetectorData.addData(detTree, FF_SUM_NAME, createDetectorNexusGroupData(dataset), "counts", 1);
				}
			}
		}

		return frame;
	}

	/**
	 * Create NXDetector data from BufferedScaler (from Tfg scaler)
	 * @param detector
	 * @param lowFrame
	 * @param highFrame
	 * @return
	 * @throws DeviceException
	 */
	private NXDetectorData createNXDetectorData(BufferedScaler detector, int lowFrame, int highFrame) throws DeviceException {
		logger.debug("Adding data from Tfg scaler readout");

		int readoutsPerCycle = detector.getContinuousParameters().getNumberDataPoints();
		int cycleNumber = (int) Math.floor(lowFrame/readoutsPerCycle);
		if (cycleNumber > 0) {
			int absFrameCycleStart = cycleNumber * readoutsPerCycle;
			lowFrame -= absFrameCycleStart;
			highFrame -= absFrameCycleStart;
			logger.debug("Adjusting scaler readout frames for cycle {} : absolute start frame for cycle = {}, reading from {} to {}",
							cycleNumber, absFrameCycleStart, lowFrame, highFrame);
		}

		int numFramesRead = highFrame - lowFrame;
		int numFrames = numReadoutsPerSpectrum;

		// Store the frame data from detector
		Object[] detectorFrameData = detector.readFrames(lowFrame, highFrame);
		double[][] frameDataArray = (double[][]) detectorFrameData;

		// clear the frames (ready for next cycle)
		detector.clearMemoryFrames(lowFrame,  highFrame);

		// Names of data fields on the detector
		String[] fieldNames = detector.getExtraNames();

		// Number of frames of scaler data to be stored in Nexus file. Don't record last
		// frame of data (this is the long timeframe between spectra)
		int numFramesToStore = numFramesRead-1;

		// Copy data for each field and add to detector data
		NXDetectorData frame = createAxisData(detector, lowFrame, highFrame);
		INexusTree detTree = frame.getDetTree(detector.getName());
		int maxField = Math.min(fieldNames.length, frameDataArray[0].length);
		for (int fieldIndex = 0; fieldIndex < maxField; fieldIndex++) {
			double[] detData = new double[numFramesToStore];
			for (int i = 0; i < numFramesToStore; i++) {
				detData[i] = frameDataArray[i][fieldIndex];
			}
			String fieldName = fieldNames[fieldIndex];
			String units = fieldName.equals(frameTimeFieldName) ? TIME_UNITS : COUNT_UNITS;
			NXDetectorData.addData(detTree, fieldName, createDetectorNexusGroupData(detData), units, 1);
		}

		// Store the time between spectra and spectrum start time values.
		int timeFieldIndex = Arrays.asList(fieldNames).indexOf(frameTimeFieldName);
		if (timeFieldIndex > -1) {
			double timeBetweenSpectra = frameDataArray[numFrames - 1][timeFieldIndex];
			NXDetectorData.addData(detTree, TIME_BETWEEN_SPECTRA_COLUMN_NAME, new NexusGroupData(timeBetweenSpectra), TIME_UNITS, 1);
			NXDetectorData.addData(detTree, TIME_COLUMN_NAME, new NexusGroupData(timeAtSpectrumStart), TIME_UNITS, 1);
			long absoluteTimeUtc = (long)(timeAtSpectrumStart*1000)+startTimeUtcMillis;
			NXDetectorData.addData(detTree, TIME_UTC_COLUMN_NAME, new NexusGroupData(absoluteTimeUtc), TIME_UNITS, 1);

			// Update start time - this is start time of the *next* spectrum
			double timeForSpectrum = ((Number)detTree.getNode(frameTimeFieldName).getData().toDataset().sum(true)).doubleValue();
			timeAtSpectrumStart += timeBetweenSpectra + timeForSpectrum;
		}

		// Add XML string of motor parameters
		TurboXasMotorParameters motorParams = getMotorParameters();
		if (motorParams != null) {
			NXDetectorData.addData(detTree, MOTOR_PARAMS_COLUMN_NAME, new NexusGroupData(motorParams.toXML()), "", 1);
		}
		return frame;
	}

	/**
	 * Save the buffered scaler I0 values from Nexus tree into a dataset, so FF_sum/I0
	 * can be calculated after xspress3 data has been collected (using {@link #addFFSumI0Data(INexusTree)}).
	 *
	 * @param detTree
	 */
	private void storeI0Data(INexusTree detTree) {
		if (detTree.getNode(I0_LABEL) != null){
			logger.debug("Storing I0 data from {}", detTree.getNodePath());
			i0Data = detTree.getNode(I0_LABEL).getData().toDataset();
		}
	}

	/**
	 * Add Xspress3 FFsum/I0 values to the Nexus tree. The I0 dataset should be present
	 * in the Nexus tree (from the buffered scaler data by first calling {@link #storeI0Data(INexusTree)}.
	 *
	 * @param detTree
	 */
	public void addFFSumI0Data(INexusTree detTree) {
		// Add the ff_sum/I0 values
		if (detTree.getNode(FF_SUM_NAME) != null && i0Data != null) {
			Dataset ffSum = detTree.getNode(FF_SUM_NAME).getData().toDataset();
			int numI0Values = i0Data.getShape()[0];
			Dataset ffSumSlice = ffSum.getSlice(null, new int[]{numI0Values}, null).squeeze();
			Dataset ffi0 = ffSumSlice.idivide(i0Data);
			ffi0.setName(FF_SUM_IO_NAME);
			NXDetectorData.addData(detTree, ffi0.getName(), NexusGroupData.createFromDataset(ffi0), "counts", 1);
		}
	}

	/**
	 * Add topup counts value for the current spectrum to Nexus tree
	 * (i.e. sum over topup counts for each time frame in the spectrum).
	 * @param detTree
	 */
	public void addTopupData(INexusTree detTree) {
		// Add the scaler counts for the topup signal for the spectrum *sum over counts for the frames)
		if (detTree.getNode(TOPUP_FIELD_NAME) != null) {
			Dataset topupCountsForFrames = detTree.getNode(TOPUP_FIELD_NAME).getData().toDataset();
			double topupCountsForSpectrum = ((Number)topupCountsForFrames.sum(true)).doubleValue();
			NXDetectorData.addData(detTree, TOPUP_FIELD_NAME+"_counts", new NexusGroupData(topupCountsForSpectrum), TIME_UNITS, 1);
		}
	}

	/**
	 * Add indices of current spectrum group and number to Nexus tree.
	 * @param detectorData
	 * @param detectorName
	 * @throws NexusException
	 */
	public void addGroupData(INexusTree detTree) {
		NXDetectorData.addData(detTree, SPECTRUM_INDEX, new NexusGroupData(spectrumNumber), TIME_UNITS, 1);
		NXDetectorData.addData(detTree, SPECTRUM_GROUP, new NexusGroupData(groupNumber), TIME_UNITS, 1);
	}

	private void addAverages(INexusTree detectorTree) {
		for(String datasetPath : datasetsNamesToAverage) {

			// Check to see if required dataset is available in detector nexus tree
			String datasetName = FilenameUtils.getName(datasetPath);
			INexusTree datasetNexusTree = detectorTree.getNode(datasetName);
			if (datasetNexusTree == null) {
				continue;
			}

			// Get dataset from Nexus tree
			Dataset dataToAverage = datasetNexusTree.getData().toDataset();
			Dataset averageDataset = null;

			if (!runningAverageDatasets.containsKey(datasetPath)) {
				// Create new running average, add to the map
				RunningAverage runningAverage = new RunningAverage(dataToAverage);
				runningAverageDatasets.put(datasetPath, runningAverage);
				String avgName = datasetName + "_avg";
				averageDataset = runningAverage.getCurrentAverage();
				averageDataset.setName(avgName);
			} else {
				// Compute the new running average value
				RunningAverage runningAverage = runningAverageDatasets.get(datasetPath);
				runningAverage.update(dataToAverage);
				averageDataset = runningAverage.getCurrentAverage();
			}

			// Add the new running average dataset to Nexus tree
			NXDetectorData.addData(detectorTree, averageDataset.getName(), new NexusGroupData(averageDataset), "counts", 1);
		}
	}

	public NexusTreeProvider[] readFrames(BufferedDetector detector, int lowFrame, int highFrame) throws Exception, DeviceException {
		NexusTreeProvider[] results = new NexusTreeProvider[1];
		if (detector instanceof BufferedScaler) {
			results[0] = createNXDetectorData((BufferedScaler) detector, lowFrame, highFrame);
			INexusTree detTree = ((NXDetectorData) results[0]).getDetTree(detector.getName());
			addGroupData(detTree);
			addTopupData(detTree);
			storeI0Data(detTree);
		} else if (detector instanceof Xspress3BufferedDetector) {
			results[0] = createNXDetectorData((Xspress3BufferedDetector) detector, lowFrame, highFrame);
			INexusTree detTree = ((NXDetectorData) results[0]).getDetTree(detector.getName());
			addFFSumI0Data(detTree);
		}

		if (datasetsNamesToAverage != null && !datasetsNamesToAverage.isEmpty()) {
			if (lowFrame==0) {
				// remove stored average datasets for this detector on first readout
				runningAverageDatasets.entrySet().removeIf(entry -> entry.getKey().contains(detector.getName()));
			}
			INexusTree detectorTree = ((NXDetectorData)results[0]).getDetTree(detector.getName());
			addAverages(detectorTree);
		}
		return results;
	}

	public String getFrameTimeFieldName() {
		return frameTimeFieldName;
	}

	public void setFrameTimeFieldName(String timeframeFieldName) {
		this.frameTimeFieldName = timeframeFieldName;
	}

	public ContinuouslyScannable getScanAxis() {
		return scanAxis;
	}

	public void setScanAxis(ContinuouslyScannable scanAxis) {
		this.scanAxis = scanAxis;
	}

	public SwmrFileReader getXspress3FileReader() {
		return xspress3FileReader;
	}

	private TurboXasMotorParameters getMotorParameters() {
		if (scanAxis instanceof TurboXasScannable) {
			return ((TurboXasScannable)scanAxis).getMotorParameters();
		} else {
			return null;
		}
	}

	public int getNumReadoutsPerSpectrum() {
		return numReadoutsPerSpectrum;
	}

	public void setNumReadoutsPerSpectrum(int numReadoutsPerSpectrum) {
		this.numReadoutsPerSpectrum = numReadoutsPerSpectrum;
	}

	public void setXspress3FileReader(SwmrFileReader xspress3FileReader) {
		this.xspress3FileReader = xspress3FileReader;
	}

	/**
	 * Absolute start time of first spectrum, measured UTC in milliseconds.
	 * @param startTimeUtcMillis
	 */
	public void setStartTime(long startTimeUtcMillis) {
		timeAtSpectrumStart = 0;
		this.startTimeUtcMillis = startTimeUtcMillis;
	}

	public long getStartTime() {
		return startTimeUtcMillis;
	}

	public List<String> getNamesForDefaultNXData() {
		return namesForDefaultNXData;
	}

	public void setNamesForDefaultNXData(List<String> namesForDefaultNXData) {
		this.namesForDefaultNXData = namesForDefaultNXData;
	}

	public List<String> getDatasetsToAverage() {
		return datasetsNamesToAverage;
	}

	public void setDatasetsToAverage(List<String> datasetsToAverage) {
		this.datasetsNamesToAverage = datasetsToAverage;
	}


	public void clearRunningAverages() {
		runningAverageDatasets.clear();
	}

	public void setGroupSpectrumNumber(int groupNumber, int spectrumNumber) {
		this.spectrumNumber = spectrumNumber;
		this.groupNumber = groupNumber;
	}

}
