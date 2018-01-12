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
import java.util.Arrays;
import java.util.List;

import org.dawnsci.ede.EdeDataConstants;
import org.eclipse.dawnsci.analysis.api.io.ScanFileHolderException;
import org.eclipse.dawnsci.hdf5.nexus.NexusFileHDF5;
import org.eclipse.dawnsci.nexus.NexusException;
import org.eclipse.dawnsci.nexus.NexusFile;
import org.eclipse.january.DatasetException;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DatasetUtils;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.january.dataset.ILazyDataset;
import org.eclipse.january.dataset.IntegerDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.nexus.extractor.NexusGroupData;
import gda.data.nexus.tree.INexusTree;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.data.swmr.SwmrFileReader;
import gda.device.DeviceException;
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

	// Dataset names for spectrum and timing group index (to match Ede scan data names...)
	public static final String SPECTRUM_INDEX = EdeDataConstants.FRAME_COLUMN_NAME;
	public static final String SPECTRUM_GROUP = EdeDataConstants.TIMINGGROUP_COLUMN_NAME;

	private Dataset i0Data;

	private String frameTimeFieldName;
	private ContinuouslyScannable scanAxis;
	private SwmrFileReader xspress3FileReader;
	private int numReadoutsPerSpectrum;

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

		// Create dataset to store start time of each spectrum
		int numSpectra = times.getShape()[0];
		int numReadouts = times.getShape()[1];
		Dataset absoluteTime = DatasetFactory.zeros(DoubleDataset.class, numSpectra);
		// First spectrum starts at t=0
		double timeAtSpectrumStart = 0;
		absoluteTime.set(timeAtSpectrumStart, 0);

		// Calculate start time for each spectrum
		for (int i = 0; i < numSpectra - 1; i++) {
			// Take slice along time for current spectrum, find sum and add to time-between-spectra
			Dataset row = DatasetUtils.convertToDataset(times.getSlice(new int[] { i, 0 }, new int[] { i + 1, numReadouts }, null));
			double rowSum = ((Number) row.sum()).doubleValue();
			double timeForSpectra = rowSum + timeBetweenSpectraVals.get(i);
			timeAtSpectrumStart += timeForSpectra;
			absoluteTime.set(timeAtSpectrumStart, i + 1);
		}
		file.createData(detectorEntry, TIME_COLUMN_NAME, absoluteTime, true);
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
		Xspress3BufferedDetector xspress3Detector = null;
		for(BufferedDetector det : bufferedDetectors) {
			if (det instanceof BufferedScaler) {
				bufferedScalerName = det.getName();
			}
			if (det instanceof Xspress3BufferedDetector) {
				xspress3Detector = (Xspress3BufferedDetector) det;
			}
		}

		try(NexusFile file = NexusFileHDF5.openNexusFile(filename)) {
			addTimeAxis(file, bufferedScalerName);
			addGroupData(file, bufferedScalerName);
			addDetectorDataLink(file, xspress3Detector);
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

		// Number of frames to be stored in Nexus file
		// Don't record last frame of data (this corresponds to the long timeframe when
		// the motor moves back to start position)
		int numFramesToStore = numFramesRead-1;

		// Setup arrays of frame index and energy of each frame
		int[] frameIndex = new int[numFramesToStore];
		for(int i=0; i<numFramesToStore; i++) {
			frameIndex[i] = i;
		}

		// Add frame and energy axis data
		NXDetectorData frame = new NXDetectorData(detector);
		frame.addAxis(detector.getName(), FRAME_INDEX, new NexusGroupData(frameIndex), 2, 1, INDEX_UNITS, false);

		// Add position axis data if using TurboXasScannable
		if (scanAxis instanceof TurboXasScannable) {
			double[] position = new double[numFramesToStore];
			double[] energy = new double[numFramesToStore];

			TurboXasScannable txasScannable = (TurboXasScannable)scanAxis;
			TurboXasMotorParameters motorParams = txasScannable.getMotorParameters();
			// size of each frame (constant for scan)
			for(int i=0; i<numFramesToStore; i++) {
				position[i] = txasScannable.calculatePosition(i);

				// energy for midpoint of frame
				double midPoint = position[i] + motorParams.getPositionStepsize()*0.5;
				energy[i] = motorParams.getEnergyForPosition(midPoint);
			}
			frame.addAxis(detector.getName(), POSITION_COLUMN_NAME, new NexusGroupData(position), 3, 1, POSITION_UNITS, false);
			frame.addAxis(detector.getName(), ENERGY_COLUMN_NAME, new NexusGroupData(energy), 1, 1, ENERGY_UNITS, false);
		} else {
			double[] energy = new double[numFramesToStore];
			for(int i=0; i<numFramesToStore; i++) {
				energy[i] = scanAxis.calculateEnergy(i);
			}
			frame.addAxis(detector.getName(), ENERGY_COLUMN_NAME, new NexusGroupData(energy), 1, 1, ENERGY_UNITS, false);
		}
		return frame;
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
				logger.info("Adding data from hdf file {}", xspress3FileReader.getFilename());
				ffSum = DatasetFactory.zeros(highFrame - lowFrame -1);
				ffSum.setName("FF_sum");
				for (Dataset dataset : xspress3FileReader.readDatasets(start, shape, step)) {
					NXDetectorData.addData(detTree, dataset.getName(), NexusGroupData.createFromDataset(dataset),
							"counts", 1);
					if (dataset.getName().startsWith("FF")) {
						ffSum.iadd(dataset);
					}
				}
				NXDetectorData.addData(detTree, ffSum.getName(), NexusGroupData.createFromDataset(ffSum), "counts", 1);
			} catch (NexusException e) {
				logger.error("Problem reading data from hdf file", e);
			}
		} else {
			//Add detector data from xspress3 scaler readout
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
				NXDetectorData.addData(detTree, dataset.getName(), NexusGroupData.createFromDataset(dataset), "counts", 1);

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
			// Use u2215 (division slash, ∕) rather than solidus (/), so ratio is displayed nicely and Nexus writer doesn't get confused
			ffi0.setName("FF_sum\u2215I0");
			NXDetectorData.addData(detTree, ffi0.getName(), NexusGroupData.createFromDataset(ffi0), "counts", 1);
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
			NXDetectorData.addData(detTree, fieldName, new NexusGroupData(detData), units, 1);

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
}
