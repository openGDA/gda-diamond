/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

import gda.configuration.properties.LocalProperties;
import gda.data.NumTracker;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.data.scan.datawriter.NexusDataWriter;
import gda.device.DeviceException;
import gda.factory.FactoryException;
import gda.jython.InterfaceProvider;
import gda.scan.ScanDataPoint;
import gda.scan.ede.datawriters.EdeDataConstants;
import gda.scan.ede.datawriters.ScanDataHelper;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.File;
import java.io.FileWriter;
import java.util.List;

import org.apache.commons.configuration.ConfigurationException;
import org.apache.commons.configuration.PropertiesConfiguration;
import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang.ArrayUtils;
import org.dawnsci.plotting.tools.profile.DataFileHelper;
import org.eclipse.dawnsci.analysis.dataset.impl.DoubleDataset;
import org.nexusformat.NexusFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.calibration.data.CalibrationDetails;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;

import com.google.gson.Gson;

public abstract class EdeDetectorBase extends DetectorBase implements EdeDetector {

	private static final Logger logger = LoggerFactory.getLogger(EdeDetectorBase.class);
	private static final int INITIAL_NO_OF_ROIS = 4;
	protected static final Gson GSON = new Gson();
	private static final String PROP_FILE_EXTENSION = ".properties";
	private static final String DETECTOR_DATA = "detectorData";

	protected DetectorData detectorData;
	protected EdeScanParameters currentScanParameter;
	protected EdeDetector currentDetector;

	private Integer[] pixels;

	@Override
	public void configure() throws FactoryException {
		createPixelData();

		//		try {
		//			loadDetectorData();
		//		} catch (ConfigurationException e) {
		//			logger.info("create a new default detector data for {}",getName());
		//			setDetectorData(createDetectorData());
		//			getDetectorData().setNumberRois(INITIAL_NO_OF_ROIS);
		//			saveDetectorData(getDetectorData());
		//		}
		getDetectorData().setNumberRois(INITIAL_NO_OF_ROIS);
		getDetectorData().addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				//				saveDetectorData(getDetectorData());
				if (evt.getPropertyName().equals(IDetectorData.ROIS_PROP_NAME)) {
					updateExtraNames((Roi[]) evt.getNewValue());
				}
			}
		});
		updateExtraNames(getDetectorData().getRois());
	}

	private void createPixelData() {
		pixels = new Integer[getMaxPixel()];
		for (int i = 0; i < pixels.length; i++) {
			pixels[i] = i;
		}
	}

	@Override
	public void prepareDetectorwithScanParameters(EdeScanParameters newParameters, boolean liveView) throws DeviceException {
		currentScanParameter = newParameters;
		configureDetectorForCollection(liveView);
	}

	private void updateExtraNames(Roi[] rois) {
		int numROI = rois.length;
		extraNames = new String[numROI + 1];
		outputFormat = new String[numROI + 2];
		outputFormat[0] = "%8.3f";
		extraNames[0] = "Total";
		outputFormat[1] = "%8.3f";
		for (int i = 0; i < numROI; i++) {
			extraNames[i + 1] = rois[i].getName();
			outputFormat[i + 2] = "%8.3f";
		}
	}

	protected abstract DetectorData createDetectorData();
	protected abstract DetectorData createDetectorDataFromJson(String property);

	private void loadDetectorData() throws ConfigurationException {
		PropertiesConfiguration store;
		store = new PropertiesConfiguration();
		store.load(getPropertyFileName());
		List<Object> json = store.getList(DETECTOR_DATA);
		logger.info("{} is {}",DETECTOR_DATA, json );
		// to recover Json string from property
		String property="";
		int i=0;
		for (Object each : json) {
			property += each;
			i++;
			if (i==json.size()) {
				break;
			}
			property+=",";
		}
		logger.info("property value is {}", property);
		if (!property.isEmpty()) {
			setDetectorData(createDetectorDataFromJson(property));
		}
	}

	private void saveDetectorData(DetectorData dd) {
		PropertiesConfiguration store;
		try {
			store = new PropertiesConfiguration();
			store.setProperty(DETECTOR_DATA, GSON.toJson(dd));
			store.save(getPropertyFileName());
		} catch (ConfigurationException e) {
			logger.error("Unable to store connected state", e);
		}
	}

	private String getPropertyFileName() {
		String propertiesFileName = LocalProperties.getVarDir() + getName() + PROP_FILE_EXTENSION;
		return propertiesFileName;
	}

	/**
	 * detector's maximum pixel size in energy direction.
	 *
	 * @return maximum pixels of camera in energy direction
	 */
	@Override
	public abstract int getMaxPixel();

	/**
	 * calculate the number of scans (TFG2 term) or accumulations in a single frame based on detector clock rate.
	 *
	 * @param frameTime
	 * @param scanTime
	 * @param numberOfFrames
	 * @return number of accumulations.
	 * @throws DeviceException
	 */
	@Override
	public abstract int getNumberScansInFrame(double frameTime, double scanTime, int numberOfFrames)
			throws DeviceException;

	/**
	 * configure the timing group and send them to TFG2 server.
	 *
	 * @throws DeviceException
	 */
	protected abstract void configureDetectorForCollection(boolean liveView) throws DeviceException;

	/**
	 * fetch detector status from hardware.
	 *
	 * @return {@link DetectorStatus}
	 * @throws DeviceException
	 */
	@Override
	public abstract DetectorStatus fetchStatus() throws DeviceException;

	@Override
	public DetectorData getDetectorData() {
		return detectorData;
	}

	protected NXDetectorData createNXDetectorData(int[] elements) {
		//TODO sort out excluded string correction
		double[] correctedData = performCorrections(elements, false)[0];
		NXDetectorData thisFrame = new NXDetectorData(this);
		double[] energies = this.getEnergyForChannels();

		thisFrame.addAxis(getName(), EdeDataConstants.ENERGY_COLUMN_NAME, new int[] { getMaxPixel() },NexusFile.NX_FLOAT64, energies, 1, 1, "eV", false);
		thisFrame.addData(getName(), EdeDataConstants.DATA_COLUMN_NAME, new int[] { getMaxPixel() },NexusFile.NX_FLOAT64, correctedData, "eV", 1);

		double[] extraValues = getExtraValues(elements);
		String[] names = getExtraNames();

		int offset = 0;

		for (int i = offset; i < names.length; i++) {
			thisFrame.setPlottableValue(names[i], extraValues[i - offset]);
		}
		return thisFrame;
	}

	protected double[][] performCorrections(int[] rawData, boolean checkForExcludedStrips) {
		int frameCount = rawData.length / getMaxPixel();
		double[][] out = new double[frameCount][getMaxPixel()];
		for (int frame = 0; frame < frameCount; frame++) {
			for (int stripIndex = 0; stripIndex < getMaxPixel(); stripIndex++) {
				if (checkForExcludedStrips) {
					// simply set excluded strips to be zero
					if (ArrayUtils.contains(getDetectorData().getExcludedPixels(), stripIndex)) {
						out[frame][stripIndex] = 0.0;
					} else if (currentScanParameter!=null && !currentScanParameter.getIncludeCountsOutsideROIs()
							&& (stripIndex < getDetectorData().getLowerChannel() || stripIndex > getDetectorData()
									.getUpperChannel())) {
						out[frame][stripIndex] = 0.0;
					} else {
						out[frame][stripIndex] = rawData[(frame * getMaxPixel()) + stripIndex];
					}
				} else {
					out[frame][stripIndex] = rawData[(frame * getMaxPixel()) + stripIndex];
				}
			}
		}
		return out;
	}

	private double[] getExtraValues(int[] elements) {
		double[] extras = new double[getDetectorData().getRois().length + 1];
		for (int elementNum = 0; elementNum < getMaxPixel(); elementNum++) {
			int roi = getDetectorData().getRoiFor(elementNum);
			if (roi >= 0) {
				extras[0] += elements[elementNum];
				extras[roi + 1] += elements[elementNum];
			}
		}
		return extras;
	}

	@Override
	public Integer[] getPixels() {
		return pixels;
	}

	@Override
	public double[] getEnergyForChannels() {
		double[] energy = new double[getMaxPixel()];
		for (int i = 0; i < energy.length; i++) {
			energy[i] = getEnergyForChannel(i);
		}
		return energy;
	}

	private double getEnergyForChannel(int channel) {
		CalibrationDetails calibration = getDetectorData().getEnergyCalibration();
		if (calibration == null) {
			return channel;
		}
		return calibration.getCalibrationResult().value(channel / (double) getMaxPixel());
	}

	@Override
	public void writeLiveDataFile() throws DeviceException {
		try {
			ScanDataPoint sdp = new ScanDataPoint();
			sdp.addDetector(this);
			sdp.addDataFromDetector(this);
			sdp.setCurrentPointNumber(0);
			sdp.setNumberOfPoints(1);
			sdp.setScanDimensions(new int[1]);

			NumTracker runNumber = new NumTracker("scanbase_numtracker");
			int scanNumber = runNumber.incrementNumber();

			NexusDataWriter writer = new NexusDataWriter();
			writer.configureScanNumber(scanNumber);
			writer.addData(sdp);

			writeAsciiFile(sdp, writer.getCurrentFileName());
		} catch (Exception e) {
			throw new DeviceException(e.getMessage(), e);
		}
	}

	private void writeAsciiFile(ScanDataPoint sdp, String nexusFilePath) throws Exception {
		DoubleDataset dataSet = ScanDataHelper.extractDetectorDataFromSDP(this.getName(), sdp);
		String asciiFileFolder = DataFileHelper.convertFromNexusToAsciiFolder(nexusFilePath);
		String asciiFilename = FilenameUtils.getBaseName(nexusFilePath);
		File asciiFile = new File(asciiFileFolder, asciiFilename + "." + EdeDataConstants.ASCII_FILE_EXTENSION);
		if (asciiFile.exists()) {
			throw new Exception("File " + asciiFilename + " already exists!");
		}
		FileWriter asciiFileWriter = null;
		String line = System.getProperty("line.separator");
		try {
			asciiFileWriter = new FileWriter(asciiFile);
			asciiFileWriter.write(String.format("#%s\t%s", EdeDataConstants.STRIP_COLUMN_NAME,
					EdeDataConstants.ENERGY_COLUMN_NAME));
			asciiFileWriter.write(line);
			for (int i = 0; i < dataSet.getSize(); i++) {
				asciiFileWriter.write(String.format("%d\t%f", i, dataSet.get(i)));
				asciiFileWriter.write(line);
			}
		} catch (Exception ex) {
			throw new Exception("Unable to write ascii data");
		} finally {
			if (asciiFileWriter != null) {
				asciiFileWriter.close();
				InterfaceProvider.getTerminalPrinter().print(
						"Writing data to file (Ascii): " + asciiFile.getAbsolutePath());
			}
		}
	}

	@Override
	public DoubleDataset createDatasetForPixel() {
		Integer[] pixelData = getPixels();
		double[] pixelDataArray = new double[pixelData.length];
		for (int i = 0; i < pixelData.length; i++) {
			pixelDataArray[i] = pixelDataArray[i];
		}
		return new DoubleDataset(pixelDataArray);
	}

	@Override
	public int getStatus() throws DeviceException {
		DetectorStatus current = fetchStatus();
		return current.getDetectorStatus();
	}

	/**
	 * Reads the first frame only.
	 */
	@Override
	public NexusTreeProvider readout() throws DeviceException {
		// TODO read data from detector
		return readFrames(1,1)[0];
	}

	/**
	 * returns a list of {@link NexusTreeProvider}, one for each frame in the specified range.
	 *
	 * @param startFrame
	 * @param finalFrame
	 * @return list of {@link NexusTreeProvider}
	 * @throws DeviceException
	 */
	@Override
	public NexusTreeProvider[] readFrames(int startFrame, int finalFrame) throws DeviceException {
		int[] elements = readoutFrames(startFrame, finalFrame);
		int numberOfFrames = finalFrame - startFrame + 1;
		int[][] rawDataInFrames = unpackRawDataToFrames(elements, numberOfFrames);
		NexusTreeProvider[] results = new NexusTreeProvider[rawDataInFrames.length];
		for (int i = 0; i < rawDataInFrames.length; i++) {
			results[i] = createNXDetectorData(rawDataInFrames[i]);
		}
		return results;
	}

	/**
	 * implements the read out of frames from the actual detector used.
	 *
	 * @param startFrame
	 * @param finalFrame
	 * @return an 1D integer array containing all frames concatenated from start frame to the final frame inclusively.
	 * @throws DeviceException
	 */
	protected abstract int[] readoutFrames(int startFrame, int finalFrame) throws DeviceException;

	protected int[][] unpackRawDataToFrames(int[] scalerData, int numFrames) {

		int[][] unpacked = new int[numFrames][getMaxPixel()];
		int iterator = 0;

		for (int frame = 0; frame < numFrames; frame++) {
			for (int datum = 0; datum < getMaxPixel(); datum++) {
				unpacked[frame][datum] = scalerData[iterator];
				iterator++;
			}
		}
		return unpacked;
	}

	public void setDetectorData(DetectorData detectorData) {
		this.detectorData = detectorData;
	}
}