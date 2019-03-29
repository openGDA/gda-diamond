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
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang.ArrayUtils;
import org.dawnsci.ede.EdeDataConstants;
import org.eclipse.dawnsci.analysis.api.io.ScanFileHolderException;
import org.eclipse.dawnsci.analysis.tree.TreeFactory;
import org.eclipse.dawnsci.hdf5.nexus.NexusFileHDF5;
import org.eclipse.dawnsci.nexus.NXdata;
import org.eclipse.dawnsci.nexus.NXentry;
import org.eclipse.dawnsci.nexus.NXroot;
import org.eclipse.dawnsci.nexus.NexusConstants;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.dawnsci.nexus.NexusFile;
import org.eclipse.dawnsci.nexus.NexusNodeFactory;
import org.eclipse.january.DatasetException;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DatasetUtils;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.january.dataset.ILazyDataset;
import org.eclipse.january.dataset.IntegerDataset;
import org.eclipse.january.dataset.LongDataset;
import org.eclipse.january.dataset.Slice;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

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
	private List<String> extraScannables = new ArrayList<>();
	private List<String> namesForDefaultNXData = Arrays.asList("FF", "It", "lnI0It");

	/**
	 * Add time axis dataset to Nexus file (after scan has finished).
	 * This creates a new dataset with the start time for each spectrum, based on cumulative
	 * sum of time frame length for each readout of each spectrum.
	 * @param filename
	 * @param detectorName
	 * @throws NexusException
	 * @throws DatasetException
	 */
	public void addTimeAxis(NexusFile file, String detectorName) throws NexusException, DatasetException {
		// Read 'frame_time' and 'time between spectra' datasets from Nexus file
		String detectorEntry = "/entry1/"+detectorName+"/";

		ILazyDataset times = file.getData(detectorEntry+frameTimeFieldName).getDataset();
		ILazyDataset timeBetweenSpectra = file.getData(detectorEntry+TIME_BETWEEN_SPECTRA_COLUMN_NAME).getDataset();
		DoubleDataset timeBetweenSpectraVals = (DoubleDataset) timeBetweenSpectra.getSlice(null, null, null).squeeze();

		int numSpectra = times.getShape()[0];
		int numReadouts = times.getShape()[1];

		// Create datasets to store start time of each spectrum :

		// Time relative to start of first spectrum [seconds]
		Dataset absoluteTime = DatasetFactory.zeros(DoubleDataset.class, numSpectra);

		// Absolute start time of each spectrum [UTC, milliseconds]
		Dataset absoluteTimeUtc = DatasetFactory.zeros(LongDataset.class, numSpectra);

		// First spectrum starts at t=0
		double timeAtSpectrumStart = 0;
		absoluteTime.set(timeAtSpectrumStart, 0);
		absoluteTimeUtc.set(startTimeUtcMillis, 0);

		// Calculate start time for each spectrum
		for (int i = 0; i < numSpectra - 1; i++) {
			// Take slice along time for current spectrum, find sum and add to time-between-spectra
			Dataset row = DatasetUtils.convertToDataset(times.getSlice(new int[] { i, 0 }, new int[] { i + 1, numReadouts }, null));
			double rowSum = ((Number) row.sum(true)).doubleValue();
			double timeForSpectra = rowSum + timeBetweenSpectraVals.get(i);
			timeAtSpectrumStart += timeForSpectra;
			absoluteTime.set(timeAtSpectrumStart, i + 1);
			absoluteTimeUtc.set(timeAtSpectrumStart*1000+startTimeUtcMillis, i+1);
		}
		file.createData(detectorEntry, TIME_COLUMN_NAME, absoluteTime, true);
		file.createData(detectorEntry, TIME_UTC_COLUMN_NAME, absoluteTimeUtc, true);
	}


	/**
	 * Add sum of topup scaler counts for each spectrum :
	 * 2D topup data ([numspectra, numReadouts]) is read from TOPUP_FIELD_NAME in detector entry
	 * and counts for each spectrum summed, creating 1D new data entry TOPUP_FIELD_NAME+"_counts" [numspectra]
	 * @param file
	 * @param detectorName
	 * @throws NexusException
	 * @throws DatasetException
	 */
	public void addTopupData(NexusFile file, String detectorName) throws NexusException, DatasetException {
		String detectorEntry = "/entry1/"+detectorName+"/";
		String topupEntry = detectorEntry+TOPUP_FIELD_NAME;
		ILazyDataset topupScalerValues = null;
		try {
			if (file.isPathValid(topupEntry)) {
				topupScalerValues = file.getData(topupEntry).getDataset();
			} else {
				logger.info("Not processing topup scaler counts for spectra. Topup data {} not in Nexus file.", topupScalerValues);
			}
		}catch(NexusException ne) {
			logger.info("Problem getting topup dataset {} from Nexus file", topupEntry, ne);
		}
		if (topupScalerValues!=null) {
			DoubleDataset topupValues = (DoubleDataset) topupScalerValues.getSlice(null, null, null);
			int numSpectra = topupValues.getShape()[0];
			int numReadouts = topupValues.getShape()[1];

			Dataset topupValuePerSpectra = DatasetFactory.zeros(DoubleDataset.class, numSpectra);
			for(int i=0; i<numSpectra; i++) {
				Dataset row = topupValues.getSlice(new int[] { i, 0 }, new int[] { i + 1, numReadouts }, null);
				double sum = ((Number)row.sum()).doubleValue();
				topupValuePerSpectra.set(sum, i);
			}

			file.createData(detectorEntry, TOPUP_FIELD_NAME+"_counts", topupValuePerSpectra, true);
		}
	}

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
			URI hdfFile = new URI(detector.getController().getFullFileName() + "#entry/data/data");
			String nexusLinkName = "/entry1/" + detector.getName() + "/MCAs";
			nexusFile.linkExternal(hdfFile, nexusLinkName, false);
		}
	}

	public void addGroupData(NexusFile nexusFile, String detectorName) throws NexusException {
		TurboXasMotorParameters motorParams = getMotorParameters();
		if (motorParams==null) {
			return;
		}
		List<TurboSlitTimingGroup> timingGroups = motorParams.getScanParameters().getTimingGroups();

		String detectorEntry = "/entry1/"+detectorName+"/";

		// Determine total number of spectra recorded in Nexus file from shape of timeframe data
		int[] shape = nexusFile.getData(detectorEntry+frameTimeFieldName).getDataset().getShape();
		int totNumSpectra = shape[0];

		// Create datasets of spectrum index and timing group index.
		Dataset groupIndexDataset = DatasetFactory.zeros(IntegerDataset.class, totNumSpectra);
		Dataset spectrumIndexDataset = DatasetFactory.zeros(IntegerDataset.class, totNumSpectra);
		int startIndex = 0;
		for(int timingIndex = 0; timingIndex<timingGroups.size(); timingIndex++) {
			int endIndex = startIndex + timingGroups.get(timingIndex).getNumSpectra();
			endIndex = Math.min(totNumSpectra, endIndex);
			for(int i=startIndex; i<endIndex; i++) {
				spectrumIndexDataset.set(i-startIndex, i);
				groupIndexDataset.set(timingIndex, i);
			}
			startIndex = endIndex;
		}

		// Write to Nexus file
		nexusFile.createData(detectorEntry, SPECTRUM_INDEX, spectrumIndexDataset, true);
		nexusFile.createData(detectorEntry, SPECTRUM_GROUP, groupIndexDataset, true);
	}

	public void addDataAtEndOfScan(String filename, BufferedDetector[] bufferedDetectors) throws URISyntaxException, DeviceException, NexusException, DatasetException {
		String bufferedScalerName = "";
		BufferedScaler bufferedScaler = null;
		Xspress3BufferedDetector xspress3Detector = null;
		for(BufferedDetector det : bufferedDetectors) {
			if (det instanceof BufferedScaler) {
				bufferedScalerName = det.getName();
				bufferedScaler = (BufferedScaler) det;
			}
			if (det instanceof Xspress3BufferedDetector) {
				xspress3Detector = (Xspress3BufferedDetector) det;
			}
		}

		try(NexusFile file = NexusFileHDF5.openNexusFile(filename)) {
			if (!bufferedScalerName.isEmpty() && bufferedScaler != null) {
				addTimeAxis(file, bufferedScalerName);
				addGroupData(file, bufferedScalerName);
				addTopupData(file, bufferedScalerName);
				addNxDataEntry(file, bufferedScaler);
			}
			addDetectorDataLink(file, xspress3Detector);
		}
	}

	/**
	 * Create new NXdata entry in /entry1/ for each of the additional datasets produced by
	 * BufferedScaler, using dataset names from 'extraNames'(i.e. It, It, FF etc).
	 * See {@link #addNxDataEntry(NexusFile, String, String, boolean)}.
	 * @param file
	 * @param bufferedScaler
	 * @throws NexusException
	 */
	private void addNxDataEntry(NexusFile file, BufferedScaler bufferedScaler) throws NexusException {
		String[] datasetNames = bufferedScaler.getExtraNames();
		boolean defaultHasBeenSet = false;
		for(String datasetName : datasetNames) {
			// See if this dataset is suitable for using as NXdata default
			String defaultName = namesForDefaultNXData.stream().filter(datasetName::endsWith).findFirst().orElse("");

			// Only set the NXdata default for first matching dataset name
			if (!defaultHasBeenSet && !defaultName.isEmpty()) {
				addNxDataEntry(file, bufferedScaler.getName(), datasetName, true);
				defaultHasBeenSet = true;
			} else {
				addNxDataEntry(file, bufferedScaler.getName(), datasetName, false);
			}
		}
	}

	/**
	 * Create new NXdata group in /entry1/ to store data and axis information a single plot.
	 * The name of the new group is {@code <detGroupName>_<datasetName>}.
	 * Links are made to the original datasets in the detector group and
	 * Attributes for the group are set to record the signal name and axis information.
	 * The 'default' attribute of the parent and root node is created to point to the newly created group
	 * if {@code setDefaultAttributes} is set to true.
	 *
	 * @param file NexusFile handle
	 * @param detGroupName name of detector group (in /entry1/) to read data from
	 * @param datasetName name of dataset to read in detector group
	 * @param setDefaultAttributes - if true, set the default attribute of the parent group and root node
	 * @throws NexusException
	 */
	private void addNxDataEntry(NexusFile file, String detGroupName, String datasetName, boolean setDefaultAttributes) throws NexusException {
		// Name of new NXdata entry to be created
		String entryName = detGroupName+"_"+datasetName;
		String sourceGroupName = "/entry1/"+detGroupName;
		List<String> axesList = Arrays.asList(TIME_COLUMN_NAME, ENERGY_COLUMN_NAME);
		Map<String, Integer> dataNames = new LinkedHashMap<>();
		dataNames.put(TIME_COLUMN_NAME, 0);
		dataNames.put(SPECTRUM_INDEX, 0);
		dataNames.put(ENERGY_COLUMN_NAME, 1);
		dataNames.put(POSITION_COLUMN_NAME, 1);

		// Create new nxData node to contain the data links and set its attributes
		NXdata nxDataNode = NexusNodeFactory.createNXdata();
		nxDataNode.setAttributeSignal(datasetName);
		nxDataNode.addAttribute(TreeFactory.createAttribute(NexusConstants.DATA_AXES, axesList.toArray(new String[] {})));
		dataNames.forEach((dataName, axisIndex) ->
			nxDataNode.addAttribute(TreeFactory.createAttribute(dataName + NexusConstants.DATA_INDICES_SUFFIX, axisIndex)));

		// Create parent nodes ...
		NXroot rootNode = NexusNodeFactory.createNXroot();
		NXentry entryNode = NexusNodeFactory.createNXentry();
		rootNode.setEntry("entry1", entryNode);
		entryNode.addGroupNode(entryName, nxDataNode);

		// Set default attribute of root node to point to the newly created NXdata node
		if (setDefaultAttributes) {
			rootNode.setAttributeDefault(entryName);
			entryNode.setAttributeDefault(entryName);
		}

		// Add nxData node to the file
		file.addNode("/", rootNode);

		// Datasets to link to inside NXdata group
		List<String> datasetNamesToLink = new ArrayList<>();
		datasetNamesToLink.add(datasetName);
		datasetNamesToLink.addAll(dataNames.keySet() );
		datasetNamesToLink.addAll(extraScannables);
		// Add links to original datasets
		for(String name : datasetNamesToLink) {
			file.link(sourceGroupName+"/"+name, "/entry1/"+entryName+"/"+name);
		}
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
	 * @throws ScanFileHolderException
	 */
	private NXDetectorData createNXDetectorData(Xspress3BufferedDetector detector, int lowFrame, int highFrame) throws DeviceException, ScanFileHolderException {

		NXDetectorData frame = createAxisData(detector, lowFrame, highFrame);

		INexusTree detTree = frame.getDetTree(detector.getName());

		Dataset ffSum = null;

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

				ffSum = DatasetFactory.zeros(highFrame - lowFrame -1);
				ffSum.setName("FF_sum");
				for (Dataset dataset : xspress3FileReader.readDatasets(start, shape, step)) {
					NXDetectorData.addData(detTree, dataset.getName(), createDetectorNexusGroupData(dataset), "counts", 1);
					if (dataset.getName().startsWith("FF")) {
						boolean excludeInSum = exludedElementSuffixList.stream()
							.filter(elementSuffix -> dataset.getName().endsWith(elementSuffix))
							.findFirst().isPresent();

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

				// last dataset from readFrames is total FF (i.e. sum over all detector elements)
				if (i==names.length-1) {
					ffSum = dataset;
				}
			}
		}

		// Add ff/I0 values
		if (ffSum!=null && i0Data!=null) {
			int numI0Values = i0Data.getShape()[0];
			Dataset ffSumSlice = ffSum.getSlice(null, new int[]{numI0Values}, null).squeeze();
			Dataset ffi0 = ffSumSlice.idivide(i0Data);
			ffi0.setName(FF_SUM_IO_NAME);
			NXDetectorData.addData(detTree, ffi0.getName(), createDetectorNexusGroupData(ffi0), "counts", 1);
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

		int readoutsPerCycle = ((BufferedScaler)detector).getContinuousParameters().getNumberDataPoints();
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
//
//		// Number of frames to be stored in Nexus file
//		// Don't record last frame of data (this corresponds to the long timeframe when
//		// the motor moves back to start position)
		int numFramesToStore = numFramesRead-1;

		NXDetectorData frame = createAxisData(detector, lowFrame, highFrame);

		// Frame data from detector
		Object[] detectorFrameData = detector.readFrames(lowFrame, highFrame);

		// clear the frames (ready for next cycle)
		detector.clearMemoryFrames(lowFrame,  highFrame);

		double[][] frameDataArray = (double[][]) detectorFrameData;

		// Names of data fields on the detector
		String[] fieldNames = detector.getExtraNames();

		String frameTimeName = getFrameTimeFieldName();

		// Copy data for each field and add to detector data
		INexusTree detTree = frame.getDetTree(detector.getName());
		int maxField = Math.min(fieldNames.length, frameDataArray[0].length);
		i0Data = null;
		for(int fieldIndex=0; fieldIndex<maxField; fieldIndex++) {
			double[] detData = new double[numFramesToStore];
			for(int i=0; i<numFramesToStore; i++) {
				detData[i] = frameDataArray[i][fieldIndex];
			}
			String fieldName = fieldNames[fieldIndex];
			String units = fieldName.equals(frameTimeName) ? TIME_UNITS : COUNT_UNITS;
			NXDetectorData.addData(detTree, fieldName, createDetectorNexusGroupData(detData), units, 1);

			// Save the I0 dataset, so can calculate (and plot) FF/I0 after xspress3 data has been collected
			if (fieldName.equals(I0_LABEL)){
				i0Data = DatasetFactory.createFromObject(detData);
			}
		}

		// Store the length of last timeframe as separate dataset ('time between spectra')
		int timeFieldIndex = Arrays.asList(fieldNames).indexOf(frameTimeName);
		if (timeFieldIndex>-1) {
			double[] timeBetweenSpectra = new double[] {frameDataArray[numFrames-1][timeFieldIndex]};
			NXDetectorData.addData(detTree, TIME_BETWEEN_SPECTRA_COLUMN_NAME, new NexusGroupData(timeBetweenSpectra), TIME_UNITS, 1);
		}

		// Add XML string of motor parameters
		TurboXasMotorParameters motorParams = getMotorParameters();
		if (motorParams != null) {
			NXDetectorData.addData(detTree, MOTOR_PARAMS_COLUMN_NAME, new NexusGroupData(motorParams.toXML()), "", 1);
		}
		return frame;
	}

	public NexusTreeProvider[] readFrames(BufferedDetector detector, int lowFrame, int highFrame) throws Exception, DeviceException {
		NexusTreeProvider[] results = new NexusTreeProvider[1];
		if (detector instanceof BufferedScaler) {
			results[0] = createNXDetectorData( (BufferedScaler)detector, lowFrame, highFrame);
		} else if (detector instanceof Xspress3BufferedDetector) {
			results[0] = createNXDetectorData( (Xspress3BufferedDetector)detector, lowFrame, highFrame);
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
		this.startTimeUtcMillis = startTimeUtcMillis;
	}

	public long getStartTime() {
		return startTimeUtcMillis;
	}

	public void setExtraScannables(List<Scannable> scannablesToMonitor) {
		extraScannables.clear();
		if (scannablesToMonitor != null) {
			scannablesToMonitor.forEach( scannable -> extraScannables.add(scannable.getName()));
		}
	}

	public List<String> getNamesForDefaultNXData() {
		return namesForDefaultNXData;
	}

	public void setNamesForDefaultNXData(List<String> namesForDefaultNXData) {
		this.namesForDefaultNXData = namesForDefaultNXData;
	}
}
