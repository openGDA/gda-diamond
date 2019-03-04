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

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import org.apache.commons.io.FilenameUtils;
import org.dawnsci.ede.CalibrationDetails;
import org.dawnsci.ede.DataFileHelper;
import org.dawnsci.ede.EdeDataConstants;
import org.eclipse.dawnsci.nexus.NexusFile;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.NumTracker;
import gda.data.nexus.extractor.NexusGroupData;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.data.scan.datawriter.NexusDataWriter;
import gda.device.DeviceException;
import gda.factory.FactoryException;
import gda.jython.InterfaceProvider;
import gda.scan.ScanDataPoint;
import gda.scan.ede.datawriters.ScanDataHelper;
import uk.ac.gda.exafs.data.DetectorSetupType;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;

public abstract class EdeDetectorBase extends DetectorBase implements EdeDetector {

	private static final Logger logger = LoggerFactory.getLogger(EdeDetectorBase.class);

	protected DetectorData detectorData;
	protected EdeScanParameters currentScanParameter;
	protected EdeDetector currentDetector;
	protected boolean dropFirstFrame=false;
	private CalibrationDetails calibration;
	private Integer[] excludedPixels = new Integer[]{}; //list of dead pixel locations
	private int lowerChannel; // lower bound for ROI in energy
	private int upperChannel; //Upper bound for ROI in energy

	private Integer[] pixels;
	private boolean energyCalibrationSet;
	private Roi[] rois=new Roi[EdeDetector.INITIAL_NO_OF_ROIS];

	private DetectorSetupType detectorSetupType = DetectorSetupType.NOT_SET;

	private boolean checkForExcludedStrips;

	public EdeDetectorBase() {
		createPixelData();
	}

	@Override
	public void configure() throws FactoryException {
		setNumberRois(INITIAL_NO_OF_ROIS);
		updateExtraNames(getRois());
	}

	private void createPixelData() {
		pixels = new Integer[getMaxPixel()];
		for (int i = 0; i < pixels.length; i++) {
			pixels[i] = i;
		}
	}

	@Override
	public void prepareDetectorwithScanParameters(EdeScanParameters newParameters) throws DeviceException {
		currentScanParameter = newParameters;
		configureDetectorForCollection();
	}

	protected abstract void configureDetectorForCollection() throws DeviceException;

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

	private NexusGroupData setNexusCompression(NexusGroupData groupData) {
		groupData.compressionType = NexusFile.COMPRESSION_NONE;
		return groupData;
	}

	private NXDetectorData createNXDetectorData(int[] elements) {
		double[] correctedData = performCorrections(elements)[0];
		NXDetectorData thisFrame = new NXDetectorData(this);
		double[] energies = this.getEnergyForChannels();

		thisFrame.addAxis(getName(), EdeDataConstants.ENERGY_COLUMN_NAME, setNexusCompression(new NexusGroupData(energies)), 1, 1, "eV", false);

		NexusGroupData detectorGroupData = new NexusGroupData(correctedData);
		detectorGroupData.isDetectorEntryData = true;
		detectorGroupData.compressionType = NexusFile.COMPRESSION_NONE;
		thisFrame.addData(getName(), EdeDataConstants.DATA_COLUMN_NAME, detectorGroupData, "eV", 1);

		// Add pixel axis. imh 8/12/2015
		int count = 0;
		int[] pixels = new int[getMaxPixel()];
		for( Integer val : this.getPixels() ) {
			pixels[count++] = val;
		}
		thisFrame.addAxis(getName(), EdeDataConstants.PIXEL_COLUMN_NAME, setNexusCompression(new NexusGroupData(pixels)), 1, 2, "pixel number", false);

		double[] extraValues = getExtraValues(elements);
		String[] names = getExtraNames();

		int offset = 0;

		for (int i = offset; i < names.length; i++) {
			thisFrame.setPlottableValue(names[i], extraValues[i - offset]);
			thisFrame.addData(getName(), names[i], new NexusGroupData(extraValues[i]));
		}
		return thisFrame;
	}

	/**
	 * Set counts for excluded detector channels to zero.
	 * i.e. any pixel index returned by {@link #getExcludedPixels()},
	 * or any pixel outside of lower and upper channel.
	 * @param pixelData
	 */
	private void removeExcludedStrips(double[] pixelData) {
		final int maxPixel = getMaxPixel();
		// Set 'dead pixels' to zero
		for(Integer deadPixelIndex : getExcludedPixels() ) {
			if (deadPixelIndex>0 && deadPixelIndex<maxPixel) {
				pixelData[deadPixelIndex] = 0.0;
			}
		}
		// Set pixels outside of ROI range to zero
		if (currentScanParameter!=null && !currentScanParameter.getIncludeCountsOutsideROIs() ) {
			for(int i=0; i<getLowerChannel(); i++) {
				pixelData[i] = 0.0;
			}
			for(int i=getUpperChannel()+1; i<maxPixel; i++) {
				pixelData[i] = 0.0;
			}
		}
	}

	private double[][] performCorrections(int[] rawData) {
		final int maxPixel = getMaxPixel();
		int frameCount = rawData.length / maxPixel;
		double[][] out = new double[frameCount][maxPixel];
		for (int frame = 0; frame < frameCount; frame++) {
			for (int stripIndex = 0; stripIndex < maxPixel; stripIndex++) {
				out[frame][stripIndex] = rawData[(frame * maxPixel) + stripIndex];
			}
			if (checkForExcludedStrips) {
				removeExcludedStrips(out[frame]);
			}
		}
		return out;
	}

	private double[] getExtraValues(int[] elements) {
		double[] extras = new double[getRois().length + 1];
		for (int elementNum = 0; elementNum < getMaxPixel(); elementNum++) {
			int roi = getRoiFor(elementNum);
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
		CalibrationDetails calibration = getEnergyCalibration();
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
			sdp.setScanDimensions(new int[]{1});

			NumTracker runNumber = new NumTracker("scanbase_numtracker");
			int scanNumber = runNumber.incrementNumber();

			NexusDataWriter writer = new NexusDataWriter();
			writer.configureScanNumber(scanNumber);
			writer.setNexusFileNameTemplate("nexus/%s.nxs");
			writer.addData(sdp);
			writer.completeCollection();

			writeAsciiFile(sdp, writer.getCurrentFileName());
		} catch (Exception e) {
			throw new DeviceException(e.getMessage(), e);
		}
	}

	private void writeAsciiFile(ScanDataPoint sdp, String nexusFilePath) throws Exception {
		DoubleDataset detectorCountData = ScanDataHelper.extractDetectorDataFromSDP(this.getName(), sdp);
		DoubleDataset detectorEnergyData = ScanDataHelper.extractDetectorEnergyFromSDP(this.getName(), sdp);
		String asciiFileFolder = DataFileHelper.convertFromNexusToAsciiFolder(nexusFilePath);
		String asciiFilename = FilenameUtils.getBaseName(nexusFilePath);
		File asciiFile = new File(asciiFileFolder, asciiFilename + "." + EdeDataConstants.ASCII_FILE_EXTENSION);
		if (asciiFile.exists()) {
			throw new Exception("File " + asciiFilename + " already exists!");
		}

		try (FileWriter asciiFileWriter = new FileWriter(asciiFile)) {
			asciiFileWriter.write(String.format("#%s\t%s\t%s", EdeDataConstants.STRIP_COLUMN_NAME,
							EdeDataConstants.ENERGY_COLUMN_NAME, this.getName()+" counts"));

			InterfaceProvider.getTerminalPrinter().print("Writing data to file (Ascii): " + asciiFile.getAbsolutePath());
			String newLine = System.getProperty("line.separator");
			asciiFileWriter.write(newLine);
			for (int i = 0; i < detectorCountData.getSize(); i++) {
				asciiFileWriter.write(String.format("%d\t%f\t%f", i, detectorEnergyData.get(i), detectorCountData.get(i)));
				asciiFileWriter.write(newLine);
			}
		} catch (IOException ex) {
			throw new Exception("Unable to write ascii data", ex);
		}
	}

	@Override
	public DoubleDataset createDatasetForPixel() {
		Integer[] pixelData = getPixels();
		double[] pixelDataArray = new double[pixelData.length];
		for (int i = 0; i < pixelData.length; i++) {
			pixelDataArray[i] = pixelData[i];
		}
		return DatasetFactory.createFromObject(DoubleDataset.class, pixelDataArray);
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

	@Override
	public boolean isDropFirstFrame() {
		return dropFirstFrame;
	}

	public void setDropFirstFrame(boolean dropFirstFrame) {
		this.dropFirstFrame = dropFirstFrame;
	}

	@Override
	public CalibrationDetails getEnergyCalibration() {
		return calibration;
	}

	@Override
	public void setEnergyCalibration(CalibrationDetails energyCalibration) {
		calibration = energyCalibration;
		setEnergyCalibrationSet(calibration != null);
		this.notifyIObservers(this, CALIBRATION_PROP_KEY);
	}

	@Override
	public boolean isEnergyCalibrationSet() {
		return energyCalibrationSet;
	}

	public void setEnergyCalibrationSet(boolean energyCalibrationSet) {
		this.energyCalibrationSet = energyCalibrationSet;
	}

	@Override
	public Roi[] getRois() {
		return rois;
	}

	@Override
	public void setRois(Roi[] rois) {
		this.rois = rois;
		updateExtraNames(rois);
		this.notifyIObservers(this, EdeDetector.ROIS_PROP_NAME);
	}

	@Override
	public int getNumberOfRois() {
		return rois.length;
	}

	@Override
	public void setNumberRois(int numberOfRois) {
		Roi[] rois = createRois(numberOfRois);
		setRois(rois);
	}

	private Roi[] createRois(int numberOfRois) {
		Roi[] rois = new Roi[numberOfRois];
		int useableRegion = upperChannel - (lowerChannel - 1); // Inclusive of the first
		int increment = useableRegion / numberOfRois;
		int start = lowerChannel;
		for (int i = 0; i < numberOfRois; i++) {
			Roi roi = new Roi();
			roi.setName("ROI_" + (i + 1));
			roi.setLowerLevel(start);
			roi.setUpperLevel(start + increment - 1);
			rois[i] = roi;
			start = start + increment;
		}
		if (rois[rois.length - 1].getUpperLevel() < upperChannel) {
			rois[rois.length - 1].setUpperLevel(upperChannel);
		}
		return rois;
	}

	@Override
	public int getLowerChannel() {
		return lowerChannel;
	}

	@Override
	public void setLowerChannel(int lowerChannel) {
		this.lowerChannel = lowerChannel;
		setNumberRois(getNumberOfRois());
	}

	@Override
	public int getUpperChannel() {
		return upperChannel;
	}

	@Override
	public void setUpperChannel(int upperChannel) {
		this.upperChannel = upperChannel;
		setNumberRois(getNumberOfRois());
	}

	/**
	 * Return array of 'dead pixel' locations.
	 */
	@Override
	public Integer[] getExcludedPixels() {
		return excludedPixels;
	}

	/**
	 * Set array of dead pixel locations
	 */
	@Override
	public void setExcludedPixels(Integer[] excludedPixels) {
		this.excludedPixels = excludedPixels;
	}

	@Override
	public int getRoiFor(int elementIndex) {
		for (int i = 0; i < getRois().length; i++) {
			if (getRois()[i].isInsideRio(elementIndex)) {
				return i;
			}
		}
		return -1;
	}

	@Override
	public abstract void setSynchroniseToBeamOrbit( boolean synchroniseToBeamOrbit ) ;

	@Override
	public abstract boolean getSynchroniseToBeamOrbit();

	@Override
	public abstract void setSynchroniseBeamOrbitDelay( int synchroniseBeamOrbitDelay ) throws DeviceException;

	@Override
	public abstract int getSynchroniseBeamOrbitDelay();

	@Override
	public abstract void setOrbitWaitMethod( String methodString );

	@Override
	public abstract String getOrbitWaitMethod();

	@Override
	public void setDetectorSetupType(DetectorSetupType detectorSetupType){
		this.detectorSetupType = detectorSetupType;
	}

	@Override
	public DetectorSetupType getDetectorSetupType() {
		return detectorSetupType;
	}

	/**
	 * @return true if excluded pixels are set to zero in the detector data.
	 */
	public boolean isCheckForExcludedStrips() {
		return checkForExcludedStrips;
	}

	/**
	 * If set to true, detector data will have counts for 'excluded' pixels set to zero.
	 * Excluded pixels are those defined by {@link #setExcludedPixels(Integer[])} or outside of lower and upper channels.<p>
	 * Note that pixels outside of ROI range are only excluded if {@link #currentScanParameter}.getIncludeCountsOutsideROIs()
	 * also returns true.
	 * @param checkForExcludedStrips
	 */
	public void setCheckForExcludedStrips(boolean checkForExcludedStrips) {
		this.checkForExcludedStrips = checkForExcludedStrips;
	}
}
